"""모나티엄 방어선 키트 (monatium_defense_kit): 1막 M2 「방어선」 모노레일 전투·시청 방어선, M3 「둠스데이」 마지막 방어선.

도시 키트(monatium_city_kit, mk) 위에 '걸어 다니는' 모듈을 더한다. mk 파일은 고치지 않는다.
  - 궤도: track_beam(궤도 보 연장 + T자 기둥), catwalks(보 양옆 격자 점검 통로 + 난간 + 받침, 이음매 없는 COL)
  - 계단탑: stair_tower(꺾음 계단 4구간 + 참 + 벽, 경사 COL), 정비 계단탑과 중앙역 계단이 같은 함수를 쓴다
  - 중앙역: central_station(양쪽 승강장 + 궤도 사이 격자 + 난간 + 지붕 + 표지, COL)
  - 멈춘 열차: walk_train(2량, 끝 비상문이 경사판으로 내려와 있고 안을 걸어서 지나간다. 창은 뚫려 있어 쏠 수 있다)
  - 선로 위 엄폐물: maint_cart, cable_drum, supply_stack, ammo_crate, weapon_crate, track_gate
  - 시청 방어선: defense_arc(바리케이드 + 모래주머니 호, 빈 건설 자리), command_post(현장 지휘소), jersey_barrier
  - 전쟁 피해: car(멀쩡한/불탄 차), fire, scorch_mark, fallen_lamp, broken_barricade, spilled_sandbags,
    crashed_drone, rubble, r41_barrier, bus_shelter, smoke_plume(촘촘한 연기 기둥)
  - 시청 정문: cityhall_doorway(정문을 열고 안쪽 복도 + 대피소 표지 "시청 지하 대피소 · SHELTER B1–B23")
  - 편집 도구: cut_faces(이미 쌓인 bmesh에서 면 지우기), replace_col(COL 상자 쪼개기), col_obox / col_slab(회전·경사 COL)

[원작] 도시 중앙부를 순환하는 모노레일과 중앙역, 모나티엄 시청(지하 23층), 시청 앞 광장, 진압반(고무탄, 칸나 휘하).
[오리지널] 궤도 점검 통로, 정비 계단탑, 멈춘 열차, 시청 방어선 배치, 현장 지휘소, 시청 지하 대피소 표지와 복도.
문서: docs/art/monatium-city.md, 노드 규칙: docs/LEVELS.md, 전투 마커: docs/COMBAT.md.

체격: 엘프(키 1.2 m, 눈높이 0.92 m, 자동 오르기 0.28 m). 난간 시각 높이 0.88 m, 충돌은 0.62~0.9 m 띠(서서 쏘면 넘어가고
몸은 막힌다). 계단 단 높이 약 0.16 m, 경사 COL 24°.
"""
from __future__ import annotations

import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb
import home_weapons as hw
import monatium_city_kit as mk

# ================================================================== 치수
AV = mk.AVENUE_Y                 # 중앙로(모노레일) 중심선 y
BEAM_Z = 7.5                     # 궤도 보 중심
BEAM_H = 1.3
BEAM_W = 1.0
TRACK_TOP = BEAM_Z + BEAM_H / 2  # 8.15: 보 윗면 = 점검 통로 바닥
CW = 1.2                         # 점검 통로 폭 (한쪽)
EDGE = BEAM_W / 2 + CW           # 1.7: 보 중심에서 통로 바깥 끝
RAIL_H = 0.88                    # 난간 윗대 높이
RAIL_COL = (0.62, 0.9)           # 난간 COL 띠 (통로 바닥 기준)
# 낮은 난간 (low=True, M2 모노레일 전투 구간): 보이는 윗대 0.64 m, 중간대 0.34 m. 탄은 보이는 메시에 맞으므로 선 엘프(눈 0.92 m)는
# 윗대 너머로 쏘고, 앉으면(눈 0.594 m) 윗대가 눈높이라 반쯤 가린다. 떨어지지 않게 이동 전용 COL 띠는 1.1 m까지(탄·시야는 지나간다),
# climb=0이라 넘기·오르기로 넘어 떨어지지 않는다. 띠 아래 끝 0.2 m: 엎드려 기어도 머리 공이 띠 밑으로 들어가지 않는다.
# 중간대는 가는 강선(fine: 탄이 지나간다). 난간에 붙어 아래 길을 내려 쏘는 사선이 0.3 m 언저리로 난간을 지난다
RAIL_LOW_H = 0.64
RAIL_LOW_MID = 0.34
RAIL_SAFE = (0.2, 1.1)
NO_CLIMB = {"climb": 0}

# ================================================================== 팔레트 (런타임에 도시 키트에 더한다)
mk.PAL.update({
    "grate": "#6b6672",      # 격자 바닥 (자줏빛 강철)
    "grate_l": "#a7a1ae",    # 격자 줄
    "rail_y": "#e2b93f",     # 점검 난간 (경고 노랑보다 살짝 짙게)
    "rust": "#9a6248",       # 녹, 탄 금속
    "char": "#3b3438",       # 불탄 차체
    "char_l": "#6d6368",
    "ash": "#8f8a8e",        # 재
    "tire": "#2b282c",
    "car_y": "#e0b04a",      # 시민 차량 (노랑·하늘·흰색·빨강)
    "car_b": "#7fa9cc",
    "car_w": "#ebe6de",
    "car_r": "#c25a4b",
    "jersey": "#c8c1b8",     # 콘크리트 방호벽
    "shelter": "#2f8f5f",    # 대피소 표지 녹색
    "paper": "#efe9d8",      # 지도, 서류
    "rubber_d": "#3d3842",   # 객차 바닥
    "seat": "#4f8f8b",       # 객차 좌석 (청록)
})
mk.GLOW.update({
    "lamp_w": "#fff4dc",     # 복도·객차 천장등
    "exit_g": "#63f2a6",     # 대피소 유도등
    "ember": "#ff7a3a",      # 잉걸불
})
mk._DARK.update({"grate", "char", "tire", "rubber_d"})

_N = [0]


def _uid(prefix):
    _N[0] += 1
    return f"{prefix}{_N[0]:04d}"


# ================================================================== 편집 도구

def cut_faces(C, group, key, kind, test):
    """이미 쌓인 (group, key, kind) bmesh에서 test(face)가 참인 면을 지운다. 지운 면 수를 돌려준다."""
    b = C.acc.get((group, key, kind))
    if b is None:
        return 0
    b.faces.ensure_lookup_table()
    fs = [f for f in b.faces if test(f)]
    if fs:
        bmesh.ops.delete(b, geom=fs, context="FACES")
    return len(fs)


def in_box(x0, x1, y0, y1, z0, z1):
    """면의 모든 정점이 상자 안에 있으면 참인 검사 함수."""
    def t(f):
        return all(x0 <= v.co.x <= x1 and y0 <= v.co.y <= y1 and z0 <= v.co.z <= z1 for v in f.verts)
    return t


def cut_box(C, group, keys, box, kinds=("main", "detail", "fine")):
    """여러 머티리얼·종류에서 상자 안 면을 지운다 (가로등 하나를 뽑을 때 등)."""
    n = 0
    for k in keys:
        for kd in kinds:
            n += cut_faces(C, group, k, kd, in_box(*box))
    return n


def replace_col(C, box, pieces, tol=0.02, tag="split"):
    """C.cols에서 좌표가 box와 같은 COL 상자를 찾아 pieces(상자 목록)로 바꾼다. 찾으면 True."""
    for i, c in enumerate(C.cols):
        if all(abs(a - b) < tol for a, b in zip(c[1:], box)):
            del C.cols[i]
            for p in pieces:
                C.col(*p, name=f"COL_{C.grp}_{_uid(tag)}")
            return True
    return False


def drop_cols_in(C, box):
    """상자 안에 완전히 들어가는 COL을 지운다 (뽑은 장식의 충돌)."""
    x0, x1, y0, y1, z0, z1 = box
    keep = [c for c in C.cols if not (x0 <= c[1] and c[2] <= x1 and y0 <= c[3] and c[4] <= y1 and z0 <= c[5]
                                      and c[6] <= z1)]
    n = len(C.cols) - len(keep)
    C.cols[:] = keep
    return n


def col_mesh(C, verts, faces, hint="m"):
    """임의 모양 COL_ 메시 (회전 상자, 경사판). LevelLoader는 COL_ 메시를 트라이메시 충돌체로 만든다."""
    nm = f"COL_{C.grp}_{_uid(hint)}"
    me = bpy.data.meshes.new(nm)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    o = bpy.data.objects.new(nm, me)
    cb.link(o)
    C.add_node(o)
    return o


_BOX_F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def col_obox(C, center, size, yaw=0.0, hint="o"):
    """Z축으로 yaw(도) 돌린 COL 상자. size = (폭 x, 깊이 y, 높이 z)."""
    cx, cy, cz = center
    sx, sy, sz = (s / 2 for s in size)
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    vs = []
    for dz in (-sz, sz):
        for dx, dy in ((-sx, -sy), (sx, -sy), (sx, sy), (-sx, sy)):
            vs.append((cx + dx * c - dy * s, cy + dx * s + dy * c, cz + dz))
    return col_mesh(C, vs, _BOX_F, hint)


def col_slab(C, top, t=0.3, hint="r"):
    """윗면 사각형 top(4점, 반시계)에서 t만큼 아래로 두께를 준 경사판 COL (계단 경사로, 경사 문짝)."""
    lo = [(p[0], p[1], p[2] - t) for p in top]
    return col_mesh(C, list(lo) + [tuple(p) for p in top], _BOX_F, hint)


def col_hull(C, pts, hint="h"):
    """점 목록(월드 좌표)의 볼록 껍질 COL (LevelLoader가 볼록 충돌체로 만든다). 둥근 기둥·기운 판·더미에 쓴다."""
    C.ccol([tuple(p) for p in pts], name=f"COL_{C.grp}_{_uid(hint)}")


def col_prism(C, pts2d, z0, z1, hint="p"):
    """볼록 다각형(xy)을 z0..z1로 세운 COL (둥근 모서리 건물, 기단)."""
    col_hull(C, [(x, y, z) for (x, y) in pts2d for z in (z0, z1)], hint)


def ngon(x, y, r, segs=12):
    return [(x + r * math.cos(2 * math.pi * i / segs), y + r * math.sin(2 * math.pi * i / segs)) for i in range(segs)]


def col_cyl(C, x, y, r, z0, z1, *, segs=12, r2=None, hint="c"):
    """세운 원기둥(r2면 원뿔대) COL."""
    lo = [(px, py, z0) for px, py in ngon(x, y, r, segs)]
    hi = [(px, py, z1) for px, py in ngon(x, y, r if r2 is None else r2, segs)]
    col_hull(C, lo + hi, hint)


def col_ellipsoid(C, center, radii, *, z_min=None, segs=12, hint="e"):
    """타원체(덤불·생울타리)의 z_min 위쪽을 감싸는 볼록 COL."""
    cx, cy, cz = center
    rx, ry, rz = radii
    z_lo = cz - rz if z_min is None else max(z_min, cz - rz)
    pts = []
    for k in range(6):
        z = z_lo + (cz + rz - z_lo) * k / 5
        s = math.sqrt(max(0.0, 1 - ((z - cz) / rz) ** 2))
        if s < 1e-3:
            pts.append((cx, cy, z))
            continue
        pts += [(cx + rx * s * math.cos(2 * math.pi * i / segs), cy + ry * s * math.sin(2 * math.pi * i / segs), z)
                for i in range(segs)]
    col_hull(C, pts, hint)


def col_seg(C, p0, p1, w, hint="s"):
    """두 점을 잇는 굵기 w의 막대(쓰러진 기둥, 다리) COL: 양 끝 정사각 단면 8점의 볼록 껍질."""
    P0, P1 = Vector(p0), Vector(p1)
    d = (P1 - P0)
    if d.length < 1e-4:
        return
    d.normalize()
    a = d.cross(Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))).normalized()
    b = d.cross(a).normalized()
    h = w / 2
    col_hull(C, [tuple(P + a * sa * h + b * sb * h) for P in (P0, P1) for sa in (-1, 1) for sb in (-1, 1)], hint)


def col_median(C, xa, xb, y, z0, z1, half=1.0):
    """도로 가운데 화단 연석 COL: 옆면을 비탈(약 39°)로 깎은 판. 0.2 m 수직 턱은 비스듬히 오르는 캡슐이 모서리에
    걸렸다 (보이는 연석 끝에서 ±0.1 m 안의 비탈)."""
    col_hull(C, [(x, y + sg * (half + 0.1), z0) for x in (xa, xb) for sg in (-1, 1)] +
             [(x, y + sg * (half - 0.15), z1) for x in (xa, xb) for sg in (-1, 1)], hint="n")


def drop_col(C, box, tol=0.02):
    """C.cols에서 좌표가 box와 같은 COL 상자를 지운다 (다른 모양 COL로 바꿀 때). 찾으면 True."""
    return replace_col(C, box, [], tol=tol)


def _yaw_m(x, y, z, yaw):
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")


def obox(C, key, x, y, z0, z1, w, d, yaw=0.0, *, kind="detail", col=False):
    """바닥 중심 (x, y), 폭 w(로컬 x)·깊이 d(로컬 y), yaw(도) 돌린 상자."""
    mk._bm_box(C.bm(key, kind), -w / 2, w / 2, -d / 2, d / 2, z0, z1, matrix=_yaw_m(x, y, 0, yaw))
    if col:
        col_obox(C, (x, y, (z0 + z1) / 2), (w, d, z1 - z0), yaw)


def wall(C, key, axis, c, t, a0, a1, z0, z1, holes=(), *, kind="main", col=True, visual=True):
    """구멍 뚫린 벽. axis='x'면 x를 따라 뻗는 벽(두께 방향 y: c..c+t), 'y'면 y를 따라(두께 x).
    holes = [(a0, a1, z0, z1), ...]. 세로 띠로 쪼개 남은 부분만 상자(+COL)로 만든다."""
    cuts = sorted({a0, a1} | {h[0] for h in holes if a0 < h[0] < a1} | {h[1] for h in holes if a0 < h[1] < a1})
    for i in range(len(cuts) - 1):
        s0, s1 = cuts[i], cuts[i + 1]
        m = (s0 + s1) / 2
        spans = [(z0, z1)]
        for (h0, h1, hz0, hz1) in holes:
            if h0 <= m <= h1:
                nxt = []
                for (za, zb) in spans:
                    if hz1 <= za or hz0 >= zb:
                        nxt.append((za, zb))
                        continue
                    if hz0 > za:
                        nxt.append((za, hz0))
                    if hz1 < zb:
                        nxt.append((hz1, zb))
                spans = nxt
        for (za, zb) in spans:
            if zb - za < 1e-3:
                continue
            if axis == "x":
                box = (s0, s1, c, c + t, za, zb)
            else:
                box = (c, c + t, s0, s1, za, zb)
            if visual:
                C.box(key, *box, kind=kind)
            if col:
                C.col(*box)


# ================================================================== 궤도

def track_beam(C, x0, x1, *, y=AV, z=BEAM_Z, pillars=(), glow=True, col_pillars=True):
    """궤도 보 (도심 궤도 monorail()과 같은 단면) + T자 기둥(pillars = x 목록). 기둥은 COL."""
    p0, p1 = Vector((x0, y, z)), Vector((x1, y, z))
    C.beam("concrete", p0, p1, BEAM_W, BEAM_H)
    dz = Vector((0, 0, BEAM_H / 2 + 0.08))
    C.beam("concrete_d", p0 - dz, p1 - dz, BEAM_W + 0.2, 0.16, kind="detail")
    if glow:
        C.strip("glow", p0 + Vector((0, 0, BEAM_H / 2)), p1 + Vector((0, 0, BEAM_H / 2)), 0.08, lift=0.01)
    for px in pillars:
        pillar(C, px, y, z=z, col=col_pillars)


def pillar(C, px, y=AV, *, z=BEAM_Z, col=True, visual=True):
    top = z - BEAM_H / 2 - 1.0
    if visual:
        C.cyl("concrete", (px, y, -0.15), (px, y, top), 0.55, segs=14)
        C.beam("concrete", (px, y - 1.3, z - BEAM_H / 2 - 0.6), (px, y + 1.3, z - BEAM_H / 2 - 0.6), 1.1, 0.9)
    if col:
        # 둥근 기둥은 원기둥 COL (상자면 모서리가 15 cm 비어 보이지 않는 벽이 된다) + T자 팔
        col_cyl(C, px, y, 0.55, -0.15, top, segs=14)
        C.col(px - 0.55, px + 0.55, y - 1.3, y + 1.3, top - 0.05, top + 0.85)


def catwalks(C, x0, x1, *, y=AV, top=TRACK_TOP, post=4.0, bracket=5.33, openings=(), col=True, seed=0, low=False):
    """궤도 보 양옆 점검 통로: 격자 바닥(폭 CW) + 노란 난간 + 발판 띠 + 받침대 + 케이블 받침.
    openings = [(side ±1, xa, xb), ...]: 난간을 비우는 구간(다리, 승강장 이음). COL: 보 윗면과 두 통로를 한 상자로
    (이음매 없음), 난간은 0.62~0.9 m 띠. low: 낮은 난간(RAIL_LOW_H, 위 '낮은 난간')과 1.1 m 안전 띠(climb=0)."""
    rh, rm = (RAIL_LOW_H, RAIL_LOW_MID) if low else (RAIL_H, 0.48)
    band, bprops = (RAIL_SAFE, NO_CLIMB) if low else (RAIL_COL, None)
    for s in (-1, 1):
        v0, v1 = sorted((y + s * BEAM_W / 2, y + s * EDGE))
        C.box("grate", x0, x1, v0, v1, top - 0.08, top, kind="detail")
        # 격자 줄: 가로 0.8 m, 세로 두 줄
        k = x0 + 0.2
        while k < x1 - 0.1:
            C.strip("grate_l", (k, v0 + 0.06, top), (k, v1 - 0.1, top), 0.05, lift=0.006)
            k += 0.8
        for f in (0.33, 0.66):
            vv = v0 + (v1 - v0) * f
            C.strip("grate_l", (x0, vv, top), (x1, vv, top), 0.035, lift=0.007)
        # 바깥 발판 띠
        e0, e1 = sorted((y + s * (EDGE - 0.05), y + s * EDGE))
        C.box("rail_y", x0, x1, e0, e1, top, top + 0.12, kind="detail")
        # 보 옆 케이블 받침 (남색)
        c0, c1 = sorted((y + s * (BEAM_W / 2), y + s * (BEAM_W / 2 + 0.14)))
        C.box("navy", x0, x1, c0, c1, BEAM_Z - 0.35, BEAM_Z - 0.2, kind="detail")
        # 난간 (열린 구간은 비움)
        segs = [(x0, x1)]
        for (os_, oa, ob) in openings:
            if os_ != s:
                continue
            nxt = []
            for (a, b) in segs:
                if ob <= a or oa >= b:
                    nxt.append((a, b))
                    continue
                if oa > a:
                    nxt.append((a, oa))
                if ob < b:
                    nxt.append((ob, b))
            segs = nxt
        vr = y + s * (EDGE - 0.03)
        for (a, b) in segs:
            if b - a < 0.05:
                continue
            for zz, key, w_, kd in ((rh, "rail_y", 0.06, "detail"), (rm, "steel", *((0.02, "fine") if low else (0.04, "detail")))):
                C.beam(key, (a, vr, top + zz), (b, vr, top + zz), w_, w_, kind=kd)
            n = max(1, int(round((b - a) / post)))
            for i in range(n + 1):
                px = a + (b - a) * i / n
                # 기둥은 윗대(0.06)·발판 띠보다 1 cm 안쪽으로: 바깥면이 1 cm 물러나고 안쪽면은 1 cm 나온다
                # (5 mm면 24비트 깊이로 50 m 밖에서 깜빡인다)
                vp = y + s * (EDGE - 0.04)
                C.box("steel", px - 0.03, px + 0.03, vp - 0.03, vp + 0.03, top, top + rh, kind="detail")
            if col:
                r0, r1 = sorted((y + s * (EDGE - 0.08), y + s * (EDGE + 0.02)))
                C.col(a, b, r0, r1, top + band[0], top + band[1], props=bprops)
        # 받침대: 보 옆에서 통로 바깥 아래로 비스듬한 버팀 + 장선
        n = max(1, int((x1 - x0) / bracket))
        for i in range(n + 1):
            bx = x0 + (x1 - x0) * i / n
            C.beam("metal", (bx, y + s * (BEAM_W / 2 + 0.03), BEAM_Z - 0.45), (bx, y + s * (EDGE - 0.12), top - 0.1),
                   0.07, 0.07, kind="detail")
    if col:
        C.col(x0, x1, y - EDGE, y + EDGE, BEAM_Z - BEAM_H / 2, top)


def track_gate(C, x, *, y=AV, top=TRACK_TOP, face=-1, text=("선로 손상 · 통행 금지", "TRACK DAMAGED · NO ENTRY")):
    """궤도 위 통행 금지 문 (점검 통로 두 쪽 + 보 위). face = 표지가 보는 x 방향(±1). COL로 막는다."""
    for s in (-1, 1):
        v = y + s * (EDGE - 0.05)
        C.box("rail_y", x - 0.06, x + 0.06, v - 0.05, v + 0.05, top, top + 1.5, kind="detail")
    C.box("rail_y", x - 0.05, x + 0.05, y - EDGE, y + EDGE, top + 1.42, top + 1.5, kind="detail")
    C.box("rail_y", x - 0.05, x + 0.05, y - EDGE, y + EDGE, top + 0.7, top + 0.76, kind="detail")
    for k in range(9):
        yy = y - EDGE + 0.2 + k * (2 * EDGE - 0.4) / 8
        C.beam("dark", (x, yy - 0.18, top + 0.08), (x, yy + 0.18, top + 1.38), 0.03, 0.03, kind="detail")
    N = (face, 0, 0)
    c = Vector((x + face * 0.07, y, top + 1.05))
    C.plate("navy", hw.rrect(2.6, 0.5, 0.1, 2), tuple(c), N, 0.03, kind="detail")
    C.text("white", text[0], 0.17, tuple(c + Vector((face * 0.035, 0, 0.07))), N, lift=0.005)
    C.text("rail_y", text[1], 0.09, tuple(c + Vector((face * 0.035, 0, -0.13))), N, lift=0.005)
    C.col(x - 0.08, x + 0.08, y - EDGE - 0.05, y + EDGE + 0.05, top, top + 1.6)


# ================================================================== 계단탑

def stair_tower(C, x0, y0, y1, z_top, *, z0=0.0, flights=4, lw=2.5, run=4.6, top_lane=1, top_end=-1,
                top_open=None, bottom_open=None, style="glass", roof=True, door=None, label=None):
    """꺾음 계단탑 (계단은 x를 따라 오르내리고 두 줄(lane)로 접힌다).
    x0 = 서쪽 끝, 길이 = 2*lw + run. y0..y1 = 탑 폭(두 줄 + 가운데 벽). lane -1 = y0 쪽, +1 = y1 쪽.
    top_lane / top_end(-1 서쪽, +1 동쪽): 맨 위 참의 자리. 계단 구간이 짝수면 맨 아래는 같은 끝, 다른 줄이다.
    top_open / bottom_open = (벽 방향 '-y'|'+y'|'-x'|'+x', a0, a1): 벽에 낼 출입구 (윗참 높이 / 바닥 높이에서 2.2 m).
    style 'glass'(역 계단, 남색 틀 + 반투명 유리) | 'steel'(정비 계단, 노란 틀 + 철망).
    door = (벽 방향, a0, a1) 닫힌 문(COL로 막힘, 표지는 label). 반환: dict(x1, top_landing=(x0,x1,y0,y1,z), bottom=...)."""
    tw = 0.15
    x1 = x0 + 2 * lw + run
    ym = (y0 + y1) / 2
    lanes = {-1: (y0 + tw, ym - 0.1), 1: (ym + 0.1, y1 - tw)}
    h = (z_top - z0) / flights
    zs = [z_top - i * h for i in range(flights + 1)]
    ends = {-1: (x0 + tw, x0 + lw), 1: (x1 - lw, x1 - tw)}
    frame_k = "navy_l" if style == "glass" else "rail_y"
    slab_k = "concrete_d" if style == "glass" else "grate"
    step_k = ("stone", "stone_d") if style == "glass" else ("grate", "grate")
    H_top = z_top + 2.6
    # 바닥판
    C.box(slab_k, x0, x1, y0, y1, z0 - 0.25, z0 + 0.02, kind="detail")
    C.col(x0, x1, y0, y1, z0 - 0.25, z0 + 0.02)
    # 참
    def landing(end, lane, z, *, both=True, ext=None):
        xa, xb = ends[end]
        if both:
            ya, yb = y0 + tw, y1 - tw
        else:
            ya, yb = lanes[lane]
        if ext:
            ya, yb = min(ya, ext[0]), max(yb, ext[1])
        C.box(slab_k, xa, xb, ya, yb, z - 0.3, z, kind="detail")
        C.col(xa, xb, ya, yb, z - 0.3, z)
        C.strip("hazard", (xb if end < 0 else xa, ya, z), (xb if end < 0 else xa, yb, z), 0.08, lift=0.008)
        return (xa, xb, ya, yb, z)
    out = {"x1": x1, "flights": []}
    other = {-1: 1, 1: -1}
    # 맨 위 참: top_lane 줄만 (윗참 출입구 쪽으로 늘림)
    ext = None
    if top_open and top_open[0] in ("-y", "+y"):
        ext = (y0 - 0.25, y0) if top_open[0] == "-y" else (y1, y1 + 0.25)
    out["top_landing"] = landing(top_end, top_lane, zs[0], both=False, ext=ext)
    end, lane = top_end, top_lane
    for i in range(flights):
        z_hi, z_lo = zs[i], zs[i + 1]
        xs = ends[end][1] if end < 0 else ends[end][0]
        xe = ends[other[end]][0] if end < 0 else ends[other[end]][1]
        d = 1 if xe > xs else -1
        ya, yb = lanes[lane]
        n = max(2, int(round(h / 0.16)))
        rise, tread = h / n, abs(xe - xs) / n
        for k in range(n):
            sa = xs + d * k * tread
            sb = xs + d * (k + 1) * tread
            zt = z_hi - (k + 1) * rise
            C.box(step_k[k % 2], min(sa, sb), max(sa, sb), ya, yb, zt - 0.18, zt, kind="detail")
            if style == "glass":
                C.strip("hazard", (sa + d * 0.05, ya + 0.1, zt), (sa + d * 0.05, yb - 0.1, zt), 0.05, lift=0.006)
        # 계단 밑 경사 슬래브 (시각) + 경사 COL (단 코를 잇는 선). 슬래브는 단보다 양옆 1 cm 좁게(옆면이 겹치지 않게)
        C.beam(slab_k, (xs, (ya + yb) / 2, z_hi - 0.35), (xe, (ya + yb) / 2, z_lo - 0.35), yb - ya - 0.02, 0.22,
               kind="detail")
        # COL 두께는 시각 슬래브 밑면(코 선 - 0.46)까지: 더 얇으면 계단 밑으로 들어간 몸이 슬래브에 묻힌다
        col_slab(C, [(xs, ya, z_hi), (xe, ya, z_lo), (xe, yb, z_lo), (xs, yb, z_hi)] if d > 0 else
                 [(xe, ya, z_lo), (xs, ya, z_hi), (xs, yb, z_hi), (xe, yb, z_lo)], t=0.46)
        if abs(z_lo - z0) < 1e-6:
            # 맨 아래 구간: 슬래브 밑이 앉은 키(0.82 m)보다 낮아지는 곳부터 바닥까지 채운다 (몸이 쐐기 틈에 끼지 않게)
            f = min(1.0, max(0.0, (z_hi - (z0 + 0.82 + 0.46)) / (z_hi - z_lo)))
            xc = xs + (xe - xs) * f
            zc = z_hi + (z_lo - z_hi) * f
            col_hull(C, [(xc, yy, z0) for yy in (ya, yb)] + [(xc, yy, zc) for yy in (ya, yb)] +
                     [(xe, yy, z0) for yy in (ya, yb)], hint="w")
        # 손잡이 (바깥벽 쪽). COL 띠는 두지 않는다: 가슴 높이 띠가 내비메시 통로를 좁혀 병사들이 꺾음 참의 가운데 벽
        # 끝에 걸렸다 (손잡이에 몸이 5 cm 묻히는 편이 낫다)
        hy = (ya + 0.06) if lane < 0 else (yb - 0.06)
        C.beam("metal", (xs, hy, z_hi + 0.78), (xe, hy, z_lo + 0.78), 0.05, 0.05, kind="detail")
        out["flights"].append((xs, xe, ya, yb, z_hi, z_lo))
        end, lane = other[end], other[lane]
        if i < flights - 1:
            landing(end, lane, z_lo)
    out["bottom"] = (*ends[end], *lanes[lane], z0)
    # 가운데 벽 (두 줄 사이, 계단 구간)
    C.box(frame_k if style == "steel" else "concrete", x0 + lw, x1 - lw, ym - 0.1, ym + 0.1, z0, H_top - 0.4,
          kind="detail")
    C.col(x0 + lw, x1 - lw, ym - 0.1, ym + 0.1, z0, H_top - 0.4)
    # 바깥벽: 출입구 구멍
    def holes_for(side):
        hs = []
        for op, zz in ((top_open, zs[0]), (bottom_open, z0)):
            if op and op[0] == side:
                hs.append((op[1], op[2], zz - 0.4, zz + 2.25))
        return hs
    walls = [("-y", "x", y0, x0, x1), ("+y", "x", y1 - tw, x0, x1), ("-x", "y", x0, y0, y1), ("+x", "y", x1 - tw, y0, y1)]
    for side, axis, c, a0, a1 in walls:
        hs = holes_for(side)
        # 충돌: 바닥부터 지붕까지 (구멍 제외)
        wall(C, frame_k, axis, c, tw, a0, a1, z0, H_top, hs, col=True, visual=False)
        # 시각: 틀 기둥 + 층 띠 + 유리/철망 면
        nb = max(1, int(round((a1 - a0) / 2.4)))
        for k in range(nb + 1):
            a = a0 + (a1 - a0) * k / nb
            # 모서리 기둥은 1 cm 안으로 (바닥판 끝면과 같은 평면에 오지 않게)
            a = min(max(a, a0 + 0.09), a1 - 0.09)
            if any(h0 < a < h1 for (h0, h1, _, _) in hs):
                continue
            if axis == "x":
                C.box(frame_k, a - 0.08, a + 0.08, c - 0.02, c + tw + 0.02, z0, H_top, kind="detail")
            else:
                C.box(frame_k, c - 0.02, c + tw + 0.02, a - 0.08, a + 0.08, z0, H_top, kind="detail")
        for zz in [z for z in zs] + [H_top - 0.1]:
            for (sa, sb) in _minus([(a0, a1)], [(h0, h1) for (h0, h1, hz0, hz1) in hs if hz0 < zz < hz1]):
                # 층 띠는 탑 모서리를 감싸 3 cm 나간다 (바닥판 끝면과 겹치지 않게)
                sa = sa - 0.03 if sa <= a0 else sa
                sb = sb + 0.03 if sb >= a1 else sb
                if axis == "x":
                    C.box(frame_k, sa, sb, c - 0.03, c + tw + 0.03, zz - 0.08, zz + 0.04, kind="detail")
                else:
                    C.box(frame_k, c - 0.03, c + tw + 0.03, sa, sb, zz - 0.08, zz + 0.04, kind="detail")
        # 면: 층마다 패널 (구멍 피함)
        N = {"-y": (0, -1, 0), "+y": (0, 1, 0), "-x": (-1, 0, 0), "+x": (1, 0, 0)}[side]
        lv = sorted(zs) + [H_top]
        for za, zb in zip(lv[:-1], lv[1:]):
            # 면은 출입구 가장자리에서 1 cm 물러난다 (끝면이 층 띠 끝면과 같은 평면에 오지 않게: 띠가 문틀처럼 나온다)
            cuts = [(h0 - 0.01, h1 + 0.01) for (h0, h1, hz0, hz1) in hs if hz0 < zb - 0.1 and hz1 > za + 0.1]
            for (sa, sb) in _minus([(a0 + 0.1, a1 - 0.1)], cuts):
                if sb - sa < 0.3:
                    continue
                mid = (sa + sb) / 2
                if axis == "x":
                    ctr = Vector((mid, c + (0 if side == "-y" else tw), (za + zb) / 2))
                else:
                    ctr = Vector((c + (0 if side == "-x" else tw), mid, (za + zb) / 2))
                if style == "glass":
                    C.rect("glass_a", tuple(ctr), N, sb - sa, (zb - za) - 0.14, lift=0.004)
                else:
                    # 철망: 아래 판 + 대각선 살
                    if axis == "x":
                        C.box("steel", sa, sb, c + 0.04, c + tw - 0.04, za, za + 0.15, kind="detail")
                    else:
                        C.box("steel", c + 0.04, c + tw - 0.04, sa, sb, za, za + 0.15, kind="detail")
                    for zz in (za + 0.5, za + 0.9):
                        if zz > zb - 0.1:
                            continue
                        p0 = (sa, c + tw / 2, zz) if axis == "x" else (c + tw / 2, sa, zz)
                        p1 = (sb, c + tw / 2, zz) if axis == "x" else (c + tw / 2, sb, zz)
                        C.beam("metal", p0, p1, 0.04, 0.04, kind="detail")
    # 닫힌 문
    if door:
        side, a0, a1 = door
        N = {"-y": Vector((0, -1, 0)), "+y": Vector((0, 1, 0)), "-x": Vector((-1, 0, 0)), "+x": Vector((1, 0, 0))}[side]
        if side in ("-y", "+y"):
            c = Vector(((a0 + a1) / 2, y0 if side == "-y" else y1, z0))
        else:
            c = Vector((x0 if side == "-x" else x1, (a0 + a1) / 2, z0))
        if side in ("+y", "+x"):
            c = c - N * tw
        for j, (NN, dc) in enumerate(((N, c + N * 0.01 + Vector((0, 0, 1.0))),
                                      (-N, c - N * (tw + 0.01) + Vector((0, 0, 1.0))))):
            C.plate("navy", hw.rrect(a1 - a0, 2.0, 0.1, 2), tuple(dc), tuple(NN), 0.06, kind="detail")
            C.rect("hazard", tuple(dc + Vector((0, 0, -0.75))), tuple(NN), a1 - a0 - 0.2, 0.12, lift=0.07)
            if label and j == 1:
                C.text("white", label[0], 0.13, tuple(dc + Vector((0, 0, 0.55))), tuple(NN), lift=0.07)
                if len(label) > 1:
                    C.text("rail_y", label[1], 0.07, tuple(dc + Vector((0, 0, 0.38))), tuple(NN), lift=0.07)
    # 지붕
    if roof:
        C.box("navy_l" if style == "glass" else "metal", x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, H_top, H_top + 0.25,
              kind="detail")
        C.col(x0, x1, y0, y1, H_top, H_top + 0.25)
    out["H_top"] = H_top
    return out


def _minus(spans, cuts):
    for (c0, c1) in cuts:
        nxt = []
        for (a, b) in spans:
            if c1 <= a or c0 >= b:
                nxt.append((a, b))
                continue
            if c0 > a:
                nxt.append((a, c0))
            if c1 < b:
                nxt.append((c1, b))
        spans = nxt
    return spans


def bridge(C, x0, x1, y0, y1, *, top=TRACK_TOP, posts=(), low=False, post_floor=-0.15):
    """정비 다리 (y를 따라 뻗는 격자 다리 + 양옆 난간, COL). posts = 받침 기둥 y 목록. low: catwalks와 같은 낮은 난간.
    post_floor = 받침 기둥이 선 바닥 윗면 (차도 -0.15, 보도 0). 기둥 COL은 거기서 선다. 보이는 기둥은 차도 높이(-0.15)부터
    세워 보도 판 속에 밑동을 묻는다(보도 위로는 COL과 같다)."""
    rh, rm = (RAIL_LOW_H, RAIL_LOW_MID) if low else (RAIL_H, 0.48)
    band, bprops = (RAIL_SAFE, NO_CLIMB) if low else (RAIL_COL, None)
    C.box("grate", x0, x1, y0, y1, top - 0.1, top, kind="detail")
    k = y0 + 0.2
    while k < y1 - 0.1:
        C.strip("grate_l", (x0 + 0.06, k, top), (x1 - 0.06, k, top), 0.04, lift=0.006)
        k += 0.35
    for x in (x0, x1):
        xx = x + (0.03 if x == x0 else -0.03)
        C.beam("metal", (xx, y0, top - 0.25), (xx, y1, top - 0.25), 0.1, 0.3, kind="detail")
        C.beam("rail_y", (xx, y0, top + rh), (xx, y1, top + rh), 0.06, 0.06, kind="detail")
        mw, mk_ = (0.02, "fine") if low else (0.04, "detail")
        C.beam("steel", (xx, y0, top + rm), (xx, y1, top + rm), mw, mw, kind=mk_)
        n = max(1, int((y1 - y0) / 1.6))
        for i in range(n + 1):
            # 끝 기둥은 3.5 cm 안으로 (계단탑 층 띠·통로 발판 띠의 바깥면과 같은 평면에 오지 않게)
            yy = min(max(y0 + (y1 - y0) * i / n, y0 + 0.035), y1 - 0.035)
            xp = xx + (0.01 if x == x0 else -0.01)          # 난간 윗대보다 1 cm 안쪽 (바깥면 1 cm 물러남)
            C.box("steel", xp - 0.03, xp + 0.03, yy - 0.03, yy + 0.03, top, top + rh, kind="detail")
        C.col(xx - 0.05, xx + 0.05, y0, y1, top + band[0], top + band[1], props=bprops)
    for py in posts:
        for x in (x0 + 0.2, x1 - 0.2):
            C.cyl("metal", (x, py, -0.15), (x, py, top - 0.4), 0.09, segs=8, kind="detail")
            C.col(x - 0.1, x + 0.1, py - 0.1, py + 0.1, post_floor, top - 0.4)
    C.col(x0, x1, y0, y1, top - 0.3, top)


# ================================================================== 중앙역

def central_station(C, a0, a1, *, y=AV, posts=(-24.0, -8.0), width=3.4, gap=1.45, north_open=None,
                    name="모노레일 중앙역", en="CENTRAL STATION · 시청 앞", west_catwalk=True, low=False):
    """시청 앞 모노레일 중앙역 (원작: 모노레일 중앙역). mk.station_platform과 같은 단면을 걸을 수 있게 다시 만든다.
    양쪽 승강장(윗면 = 궤도 윗면 + 0.05) + 궤도와 승강장 사이 격자(보 윗면 높이) + 바깥 난간(COL 띠) + 지붕 + 표지.
    north_open = (xa, xb): 북쪽 난간을 비우는 구간(계단탑 이음). 서쪽 끝은 점검 통로 폭만 열고 나머지는 막는다.
    low: 낮은 난간(윗대 RAIL_LOW_H, 유리 0.2~0.6 m)과 1.1 m 안전 띠(climb=0, 위 '낮은 난간').
    반환: dict(top, roof, edge)."""
    top = TRACK_TOP + 0.05
    rh = RAIL_LOW_H if low else 0.92                 # 윗대 가운데 높이 (유리는 0.2 m에서 윗대 밑까지)
    gh = rh - 0.22
    # 낮은 윗대는 가는 손잡이 (6 cm): 난간에 붙어 내려다보면 눈 0.26 m 아래라 넓은 띠는 아래 시야·사선을 넓게 가린다
    rw, rt = (0.06, 0.06) if low else (0.12, 0.08)
    band = (RAIL_SAFE[0], RAIL_SAFE[1]) if low else (RAIL_COL[0], RAIL_COL[1] + 0.02)
    bprops = NO_CLIMB if low else None
    edge = gap + width
    for s in (-1, 1):
        v0, v1 = sorted((y + s * gap, y + s * edge))
        C.box("concrete_d", a0, a1, v0, v1, top - 0.45, top, kind="main")
        C.col(a0, a1, v0, v1, top - 0.45, top)
        # 승강장 끝 노란 선 + 점자 띠
        C.strip("hazard", (a0, y + s * (gap + 0.22), top), (a1, y + s * (gap + 0.22), top), 0.2, lift=0.012)
        C.strip("pave_d", (a0, y + s * (gap + 0.5), top), (a1, y + s * (gap + 0.5), top), 0.3, lift=0.011)
        # 바깥 난간: 아래 판 + 유리 + 윗대
        segs = [(a0, a1)]
        if s > 0 and north_open:
            segs = _minus(segs, [north_open])
        vr = y + s * (edge - 0.08)
        for (sa, sb) in segs:
            r0, r1 = sorted((y + s * (edge - 0.14), y + s * (edge - 0.02)))
            # 아래 판은 동쪽 문 턱(ex-0.1..ex) 앞에서 끝난다 (밑면·끝면이 문 턱과 겹치지 않게)
            C.box("steel", sa, min(sb, a1 - 0.1), r0, r1, top, top + 0.18, kind="detail")
            C.beam("navy_l", (sa, vr, top + rh), (sb, vr, top + rh), rw, rt, kind="detail")
            C.rect("glass_a", ((sa + sb) / 2, vr, top + 0.2 + gh / 2), (0, s, 0), sb - sa - 0.1, gh, lift=0.0)
            n = max(1, int(round((sb - sa) / 2.6)))
            for i in range(n + 1):
                px = sa + (sb - sa) * i / n
                # 기둥은 승강장에 2 cm 박는다 (밑면이 아래 판 밑면과 같은 평면에 오지 않게)
                C.box("navy_l", px - 0.05, px + 0.05, vr - 0.05, vr + 0.05, top - 0.02, top + rh, kind="detail")
            C.col(sa, sb, r0, r1, top, top + 0.18)
            C.col(sa, sb, r0, r1, top + band[0], top + band[1], props=bprops)
        # 서쪽 끝: 점검 통로 폭 바깥은 막는다 (난간)
        w0, w1 = sorted((y + s * (EDGE if west_catwalk else gap), y + s * edge))
        C.box("steel", a0, a0 + 0.12, w0, w1, top, top + 0.18, kind="detail")
        C.beam("navy_l", (a0 + 0.06, w0, top + rh), (a0 + 0.06, w1, top + rh), *((rw, rt) if low else (0.08, 0.12)), kind="detail")
        C.rect("glass_a", (a0 + 0.06, (w0 + w1) / 2, top + 0.2 + gh / 2), (-1, 0, 0), w1 - w0, gh, lift=0.0)
        C.col(a0, a0 + 0.12, w0, w1, top, top + (RAIL_SAFE[1] if low else 1.0), props=bprops)
    # 궤도와 승강장 사이 격자 (보 윗면 높이) + 보 윗면 COL
    for s in (-1, 1):
        v0, v1 = sorted((y + s * BEAM_W / 2, y + s * gap))
        C.box("grate", a0, a1, v0, v1, TRACK_TOP - 0.06, TRACK_TOP, kind="detail")
        k = a0 + 0.2
        while k < a1:
            C.strip("grate_l", (k, v0 + 0.05, TRACK_TOP), (k, v1 - 0.05, TRACK_TOP), 0.04, lift=0.006)
            k += 0.35
    C.col(a0, a1, y - gap, y + gap, BEAM_Z - BEAM_H / 2, TRACK_TOP)
    # 동쪽 끝: 문
    ex = a1
    C.box("navy_l", ex - 0.1, ex, y - edge, y + edge, top, top + 0.12, kind="detail")
    for k in range(13):
        yy = y - edge + 0.2 + k * (2 * edge - 0.4) / 12
        C.box("navy_l", ex - 0.08, ex - 0.02, yy - 0.04, yy + 0.04, TRACK_TOP, top + 1.5, kind="detail")
    C.beam("navy_l", (ex - 0.05, y - edge, top + 1.5), (ex - 0.05, y + edge, top + 1.5), 0.1, 0.1, kind="detail")
    C.text("white", "관계자 외 출입 금지 · STAFF ONLY", 0.14, (ex - 0.11, y, top + 1.2), (-1, 0, 0), lift=0.01)
    C.col(ex - 0.12, ex, y - edge, y + edge, TRACK_TOP, top + 1.6)
    # 받침 보 (기존 궤도 기둥 자리) + 양끝 기둥
    zr = top + 3.2
    for u in posts:
        C.box("concrete", u - 0.6, u + 0.6, y - edge, y + edge, top - 1.25, top - 0.45)
    for u in (a0 + 1.2, a1 - 1.2):
        C.box("concrete", u - 0.5, u + 0.5, y - edge, y + edge, top - 1.15, top - 0.45)
        for s in (-1, 1):
            py = y + s * (edge - 0.9)
            C.cyl("concrete", (u, py, -0.15), (u, py, top - 1.15), 0.42, segs=12)
            C.col(u - 0.4, u + 0.4, py - 0.4, py + 0.4, -0.15, top - 1.15)
    # 지붕 + 지붕 기둥
    roof_u = list(posts) + [a0 + 1.2, a1 - 1.2]
    for u in roof_u:
        for s in (-1, 1):
            v = y + s * (edge - 0.35)
            C.box("metal", u - 0.13, u + 0.13, v - 0.13, v + 0.13, top, zr, kind="detail")
            C.col(u - 0.15, u + 0.15, v - 0.15, v + 0.15, top, zr)
    C.box("white", a0 - 1.0, a1 + 1.0, y - edge - 0.6, y + edge + 0.6, zr, zr + 0.35)
    C.box("glass_d", a0 + 2.0, a1 - 2.0, y - 0.9, y + 0.9, zr + 0.35, zr + 0.6, kind="detail")
    # 지붕 띠는 지붕보다 사방 2 cm 나온다 (끝면이 지붕 끝면과 같은 평면에 오지 않게)
    C.box("navy", a0 - 1.02, a1 + 1.02, y - edge - 0.62, y + edge + 0.62, zr - 0.05, zr + 0.06, kind="detail")
    C.col(a0 - 1.0, a1 + 1.0, y - edge - 0.6, y + edge + 0.6, zr, zr + 0.35)
    # 역명 (지붕 바깥 띠 + 승강장마다 걸이 표지 하나, 궤도 쪽 면)
    mid = (a0 + a1) / 2
    for s in (-1, 1):
        N = (0, s, 0)
        C.text("navy", name, 0.32, (mid, y + s * (edge + 0.63), zr + 0.18), N, lift=0.01)
        u = mid - 6.0 * s
        c = Vector((u, y + s * (gap + 1.6), zr - 0.75))
        C.beam("metal", c + Vector((-0.9, 0, 0.3)), c + Vector((-0.9, 0, 0.75)), 0.04, 0.04, kind="detail")
        C.beam("metal", c + Vector((0.9, 0, 0.3)), c + Vector((0.9, 0, 0.75)), 0.04, 0.04, kind="detail")
        C.box("navy", u - 1.4, u + 1.4, c.y - 0.06, c.y + 0.06, c.z - 0.32, c.z + 0.32, kind="detail")
        C.text("white", name, 0.2, (u, c.y - s * 0.065, c.z + 0.08), (0, -s, 0), lift=0.005)
        C.text("glow", en, 0.1, (u, c.y - s * 0.065, c.z - 0.17), (0, -s, 0), lift=0.005)
    # 승강장 가구: 벤치, 운행 표시판, 휴지통
    for s in (-1, 1):
        vb = y + s * (edge - 0.7)
        for u in (mid - 4.0, mid + 3.0):
            mk.bench(C, u, vb, yaw=0 if s > 0 else 180, z=top, length=1.6)
            C.col(u - 0.8, u + 0.8, vb - 0.25, vb + 0.25, top, top + 0.33)
        mk.trash_bin(C, mid - 6.2, vb, z=top)
        # 운행 표시판 (경보 붉은 글자: 전 노선 운행 중지)
        c = Vector((mid + 0.5, y + s * (gap + 1.6), zr - 1.4))
        C.box("dark", c.x - 0.9, c.x + 0.9, c.y - 0.05, c.y + 0.05, c.z - 0.28, c.z + 0.28, kind="detail")
        C.beam("metal", c + Vector((0, 0, 0.28)), c + Vector((0, 0, 1.4)), 0.04, 0.04, kind="detail")
        C.text("alert", "전 노선 운행 중지", 0.15, (c.x, c.y - s * 0.056, c.z + 0.05), (0, -s, 0), lift=0.004)
        C.rect("alert", (c.x, c.y - s * 0.056, c.z - 0.16), (0, -s, 0), 1.4, 0.04, lift=0.004)
    return {"top": top, "roof": zr, "edge": edge}


# ================================================================== 멈춘 열차 (걸어서 지나간다)

def walk_train(C, x_mid, *, y=AV, deck=TRACK_TOP, cars=2, length=9.0, w=2.6, h=2.1, gap=0.8, lit=False,
               broken=(), seed=3):
    """멈춘 모노레일 열차 (흰 몸체 + 남색 창 띠 + 시안 띠, monorail_car와 같은 색). 안을 걸어서 지나간다.
    양 끝 비상문이 경사판으로 보 위에 내려와 있고, 차량 사이는 통로(bellows)로 이어진다. 창은 뚫려 있어 쏠 수 있다.
    COL: 바닥, 벽(창 아래 띠·창 사이 기둥·창 위 띠), 끝벽(문 제외), 지붕, 좌석. 차체 옆은 난간까지 0.3 m라 못 지나간다.
    반환: dict(floor, roof, cars=[(xa, xb)], west_door, east_door)."""
    rng = random.Random(seed)
    zf = deck + 0.2
    zr = zf + h
    hw_ = w / 2
    t = 0.1
    spans = []
    for i in range(cars):
        cx = x_mid + (cars - 1) * (length + gap) / 2 - i * (length + gap)
        spans.append((cx - length / 2, cx + length / 2))
    spans.sort()
    dw = 0.5                                   # 끝문 반폭
    dz = 1.85
    side_doors = (-length / 4, length / 4)
    win_z = (0.82, 1.52)
    for ci, (xa, xb) in enumerate(spans):
        cx = (xa + xb) / 2
        # 바닥 + 아래 치마(보를 감싼다) + 대차
        C.box("rubber_d", xa, xb, y - hw_, y + hw_, zf - 0.3, zf, kind="detail")
        C.col(xa, xb, y - hw_, y + hw_, deck - 0.1, zf)
        for s in (-1, 1):
            v0, v1 = sorted((y + s * 0.56, y + s * hw_))
            C.box("white", xa + 0.3, xb - 0.3, v0, v1, BEAM_Z - 0.2, zf - 0.3, kind="detail")
            C.strip("glow" if lit else "glow_off", (xa + 0.6, y + s * (hw_ + 0.001), zf + 0.28),
                    (xb - 0.6, y + s * (hw_ + 0.001), zf + 0.28), 0.12, (0, s, 0), lift=0.015)
        for bx in (xa + 1.8, xb - 1.8):
            C.box("dark", bx - 0.9, bx + 0.9, y - 0.62, y + 0.62, BEAM_Z - 0.75, BEAM_Z + 0.2, kind="detail")
        # 옆벽 (창·문 구멍)
        for s in (-1, 1):
            c = y + s * hw_ - (t if s > 0 else 0)
            holes = []
            for du in side_doors:
                holes.append((cx + du - 0.48, cx + du + 0.48, zf, zf + dz))
            wins = [(xa + 0.75, cx - length / 4 - 0.7), (cx - length / 4 + 0.7, cx - 0.12),
                    (cx + 0.12, cx + length / 4 - 0.7), (cx + length / 4 + 0.7, xb - 0.75)]
            for (wa, wb) in wins:
                holes.append((wa, wb, zf + win_z[0], zf + win_z[1]))
            # 흰 아래·위 띠, 남색 창 띠(기둥)
            wall(C, "white", "x", c, t, xa, xb, zf, zf + win_z[0], holes, kind="detail")
            wall(C, "navy", "x", c, t, xa, xb, zf + win_z[0], zf + win_z[1], holes, kind="detail")
            wall(C, "white", "x", c, t, xa, xb, zf + win_z[1], zr, holes, kind="detail")
            # 유리 (깨진 창은 비우고 가장자리에 조각)
            for k, (wa, wb) in enumerate(wins):
                key = (ci, s, k)
                N = (0, s, 0)
                gy = y + s * (hw_ - 0.05)
                z_lo, z_hi = zf + win_z[0], zf + win_z[1]
                if key in broken:
                    # 깨진 창: 모서리에 남은 유리 조각 둘
                    C.poly("glass_a", [(wa, gy, z_lo), (wa + (wb - wa) * 0.35, gy, z_lo), (wa, gy, z_lo + 0.3)],
                           normal=N)
                    C.poly("glass_a", [(wb, gy, z_hi), (wb - (wb - wa) * 0.3, gy, z_hi), (wb, gy, z_hi - 0.35)],
                           normal=N)
                else:
                    C.rect("glass_a", ((wa + wb) / 2, gy, (z_lo + z_hi) / 2), N, wb - wa, z_hi - z_lo, lift=0.0)
            # 열린 옆문 짝 (밖으로 밀려 벽 앞에 겹침)
            for du in side_doors:
                ox = cx + du + (0.97 if du > 0 else -0.97)
                v0, v1 = sorted((y + s * hw_, y + s * (hw_ + 0.05)))
                C.box("white", ox - 0.46, ox + 0.46, v0, v1, zf + 0.02, zf + dz, kind="detail")
                C.rect("glass_d", (ox, y + s * (hw_ + 0.05), zf + 1.3), (0, s, 0), 0.5, 0.6, lift=0.004)
            # 로고
            C.logo((cx + (length / 2 - 1.1) * (1 if ci == 0 else -1), y + s * hw_, zf + 1.17), 0.36, (0, s, 0),
                   key="gold", lift=0.02)
        # 지붕 (+ 냉방기)
        C.box("white", xa, xb, y - hw_, y + hw_, zr, zr + 0.14, kind="detail")
        C.box("steel", cx - 1.6, cx + 1.6, y - 0.75, y + 0.75, zr + 0.14, zr + 0.42, kind="detail")
        C.box("white", xa + 0.25, xb - 0.25, y - hw_ + 0.28, y + hw_ - 0.28, zr + 0.14, zr + 0.24, kind="detail")
        C.col(xa, xb, y - hw_, y + hw_, zr, zr + 0.14)
        # 지붕 위 (적이 선다): 가운데 판과 냉방기도 COL (발이 판에 묻히지 않게)
        C.col(xa + 0.25, xb - 0.25, y - hw_ + 0.28, y + hw_ - 0.28, zr + 0.14, zr + 0.24)
        C.col(cx - 1.6, cx + 1.6, y - 0.75, y + 0.75, zr + 0.24, zr + 0.42)
        # 끝벽: 문 구멍
        # 시각 끝벽은 옆벽 안쪽 면 사이에만 (옆면이 옆벽 바깥면·창 띠와 같은 평면에 오지 않게), COL은 차체 폭 그대로
        for (ex, sg) in ((xa, 1), (xb - t, -1)):
            wall(C, "white", "y", ex, t, y - hw_, y + hw_, zf, zr, [(y - dw, y + dw, zf, zf + dz)], kind="detail",
                 visual=False)
            wall(C, "white", "y", ex, t, y - hw_ + t, y + hw_ - t, zf, zr, [(y - dw, y + dw, zf, zf + dz)],
                 kind="detail", col=False)
        # 실내: 긴 좌석, 손잡이 기둥, 천장등, 광고, 바닥 줄
        for s in (-1, 1):
            vin = y + s * (hw_ - t)
            vs0, vs1 = sorted((vin, vin - s * 0.44))
            for (sa, sb) in _minus([(xa + 0.25, xb - 0.25)], [(cx + du - 0.62, cx + du + 0.62) for du in side_doors]):
                C.box("seat", sa, sb, vs0, vs1, zf + 0.22, zf + 0.32, kind="detail")
                C.box("metal", sa + 0.05, sb - 0.05, vs0 + 0.05, vs1 - 0.05, zf, zf + 0.22, kind="detail")
                b0, b1 = sorted((vin, vin - s * 0.08))
                C.box("seat", sa, sb, b0, b1, zf + 0.32, zf + 0.72, kind="detail")
                C.col(sa, sb, vs0, vs1, zf, zf + 0.32)
                C.col(sa, sb, b0, b1, zf + 0.32, zf + 0.72)
            # 옆문 손잡이 기둥: 좌석 등받이에서 0.64 m 띄운다 (예전 벽 안쪽 0.5 m면 등받이 앞면과 0.39 m라, 좌석 끝에서 뛰면
            # 아래 반구가 기둥과 등받이 윗모서리 사이에 걸려 발이 뜬 채 박혔다: scripts/wedgecheck.mjs m2_track)
            py = y + s * (hw_ - 0.85)
            for du in side_doors:
                for e in (-0.5, 0.5):
                    C.cyl("steel", (cx + du + e, py, zf), (cx + du + e, py, zr), 0.025, segs=6, kind="detail")
                    C.col(cx + du + e - 0.03, cx + du + e + 0.03, py - 0.03, py + 0.03, zf, zr)
            C.beam("steel", (xa + 0.3, y + s * 0.62, zr - 0.25), (xb - 0.3, y + s * 0.62, zr - 0.25), 0.03, 0.03,
                   kind="detail")
            C.rect("holo_l" if lit else "paper", (cx - length / 4 + 0.0, y + s * (hw_ - t - 0.01), zr - 0.28),
                   (0, -s, 0), 1.1, 0.32, lift=0.002)
        C.box("lamp_w" if lit else "lamp_off", xa + 0.4, xb - 0.4, y - 0.12, y + 0.12, zr - 0.04, zr - 0.01,
              kind="fine")
        C.strip("seat", (xa + 0.2, y, zf), (xb - 0.2, y, zf), 0.12, lift=0.006)
        # 흩어진 짐
        for k in range(3):
            bx = rng.uniform(xa + 1.0, xb - 1.0)
            by = y + rng.choice((-1, 1)) * rng.uniform(0.62, 0.78)
            C.blob(rng.choice(("violet", "tarp", "coral", "olive")), (bx, by, zf + 0.12), 0.2, (1.3, 0.9, 0.6),
                   segs=8, rings=4, rot_z=rng.uniform(0, 3))
        for k in range(5):
            bx = rng.uniform(xa + 0.6, xb - 0.6)
            by = y + rng.uniform(-0.7, 0.7)
            C.decal("paper", hw.rrect(0.21, 0.29, 0.01, 1), (bx, by, zf), (0, 0, 1), up=(math.cos(k), math.sin(k), 0),
                    lift=0.008 + k * 0.001)
    # 차량 사이 통로 (주름막)
    for i in range(len(spans) - 1):
        ga, gb = spans[i][1], spans[i + 1][0]
        # 통로 바닥은 주름막 벽 아래까지 (옆면이 궤도 보 옆면 y±0.5와 같은 평면에 오지 않게)
        C.box("rubber_d", ga, gb, y - dw - 0.12, y + dw + 0.12, zf - 0.25, zf, kind="detail")
        C.col(ga - 0.05, gb + 0.05, y - dw, y + dw, deck - 0.1, zf)
        for s in (-1, 1):
            v0, v1 = sorted((y + s * dw, y + s * (dw + 0.12)))
            C.box("dark", ga, gb, v0, v1, zf, zf + dz + 0.1, kind="detail")
            C.col(ga, gb, v0, v1, zf, zf + dz + 0.1)
            for k in range(4):
                xx = ga + (gb - ga) * (k + 0.5) / 4
                C.box("metal", xx - 0.03, xx + 0.03, v0 - 0.02, v1 + 0.02, zf, zf + dz + 0.1, kind="detail")
        C.box("dark", ga, gb, y - dw - 0.12, y + dw + 0.12, zf + dz + 0.1, zf + dz + 0.2, kind="detail")
        C.col(ga, gb, y - dw - 0.12, y + dw + 0.12, zf + dz + 0.1, zf + dz + 0.2)
    # 양 끝 운전실: 앞창·전조등·코, 비상문이 경사판으로 내려와 있다
    for (ex, d) in ((spans[0][0], -1), (spans[-1][1], 1)):
        N = Vector((d, 0, 0))
        f = Vector((ex, y, 0))
        for s in (-1, 1):
            C.decal("glass_d", hw.rrect(0.62, 0.72, 0.12, 2), (ex, y + s * 0.88, zf + 1.38), tuple(N), lift=0.02)
            C.decal("lamp", hw.circle(0.1, 12), (ex, y + s * 0.95, zf + 0.42), tuple(N), lift=0.02)
            C.box("white", min(ex, ex + d * 0.35), max(ex, ex + d * 0.35), *sorted((y + s * (hw_ - 0.18),
                                                                                   y + s * hw_)), zf - 0.3, zr,
                  kind="detail")
            C.col(min(ex, ex + d * 0.35), max(ex, ex + d * 0.35), *sorted((y + s * (hw_ - 0.18), y + s * hw_)),
                  zf - 0.3, zr)
        C.box("white", min(ex, ex + d * 0.3), max(ex, ex + d * 0.3), y - hw_, y + hw_, zr - 0.25, zr + 0.1,
              kind="detail")
        C.box("dark", min(ex, ex + d * 0.4), max(ex, ex + d * 0.4), y - hw_ + 0.1, y + hw_ - 0.1, zf - 0.35, zf - 0.1,
              kind="detail")
        C.logo((ex, y, zf + 2.0), 0.3, tuple(N), key="gold", disc="navy", lift=0.03)
        # 비상문 경사판: 바닥(zf)에서 보 윗면까지
        L = 1.15
        p0 = Vector((ex, y, zf))
        p1 = Vector((ex + d * L, y, deck + 0.02))
        C.beam("navy_l", p0 - Vector((0, 0, 0.03)), p1 - Vector((0, 0, 0.03)), 2 * dw - 0.04, 0.05, kind="detail")
        for k in range(5):
            q = p0 + (p1 - p0) * ((k + 0.5) / 5)
            C.strip("hazard", (q.x, y - dw + 0.08, q.z + 0.005), (q.x, y + dw - 0.08, q.z + 0.005), 0.05, lift=0.004)
        top4 = [(ex - d * 0.05, y - dw, zf), (ex + d * L, y - dw, deck + 0.02), (ex + d * L, y + dw, deck + 0.02),
                (ex - d * 0.05, y + dw, zf)]
        if d < 0:
            top4 = [top4[1], top4[0], top4[3], top4[2]]
        col_slab(C, top4, t=0.25)
    return {"floor": zf, "roof": zr + 0.14, "cars": spans,
            "west_door": (spans[0][0], y, zf), "east_door": (spans[-1][1], y, zf)}


# ================================================================== 선로·광장 엄폐물

def ammo_crate(C, x, y, z=0.0, yaw=0.0, *, key="olive", col=True, text="탄약 · AMMO"):
    """탄약 상자 (0.8 x 0.46 x 0.36). 반환: 윗면 z (PICKUP_ 마커는 +0.04)."""
    Mx = _yaw_m(x, y, z, yaw)
    mk._bm_box(C.bm(key, "detail"), -0.4, 0.4, -0.23, 0.23, 0, 0.36, matrix=Mx)
    for u in (-0.3, 0.3):
        mk._bm_box(C.bm("metal", "detail"), u - 0.03, u + 0.03, -0.24, 0.24, 0.02, 0.37, matrix=Mx)
    N = Mx.to_3x3() @ Vector((0, -1, 0))
    c = Mx @ Vector((0, -0.23, 0.2))
    C.text("hazard", text, 0.06, tuple(c), tuple(N), lift=0.006)
    if col:
        col_obox(C, (x, y, z + 0.18), (0.8, 0.46, 0.36), yaw)
    return z + 0.36


def weapon_crate(C, x, y, z=0.0, yaw=0.0, *, col=True, text="U.S. ARMY · 노획품"):
    """긴 화기 상자 (1.3 x 0.5 x 0.34, 뚜껑 열림). 반환: 윗면 z."""
    Mx = _yaw_m(x, y, z, yaw)
    mk._bm_box(C.bm("olive", "detail"), -0.65, 0.65, -0.25, 0.25, 0, 0.32, matrix=Mx)
    mk._bm_box(C.bm("dark", "detail"), -0.6, 0.6, -0.2, 0.2, 0.30, 0.325, matrix=Mx)
    lid = Mx @ Matrix.Translation((0, 0.27, 0.32)) @ Matrix.Rotation(math.radians(-100), 4, "X")
    mk._bm_box(C.bm("olive", "detail"), -0.65, 0.65, 0, 0.5, -0.02, 0.02, matrix=lid)
    N = Mx.to_3x3() @ Vector((0, -1, 0))
    C.text("white", text, 0.06, tuple(Mx @ Vector((0, -0.25, 0.17))), tuple(N), lift=0.006)
    if col:
        col_obox(C, (x, y, z + 0.17), (1.3, 0.5, 0.34), yaw)
    return z + 0.33


def supply_stack(C, x, y, z=0.0, yaw=0.0, *, n=3, seed=0, col=True):
    """보급 상자 더미 (높은 엄폐 1.1 m 안팎). 반환: 높이."""
    rng = random.Random(seed)
    Mx = _yaw_m(x, y, z, yaw)
    hmax = 0.0
    ups = []
    for k in range(n):
        u = -0.45 + (k % 2) * 0.9
        zz = 0.0 if k < 2 else 0.55
        if k >= 2:
            u = rng.uniform(-0.3, 0.3)
            ups.append(u)
        key = rng.choice(("olive", "violet", "olive", "teal"))
        mk._bm_box(C.bm(key, "detail"), u - 0.42, u + 0.42, -0.3, 0.3, zz, zz + 0.55, matrix=Mx)
        # 끈은 상자를 감싼다 (위아래로 5 mm·1 cm 나와 밑면이 상자 밑면과 같은 평면에 오지 않게)
        mk._bm_box(C.bm("metal", "detail"), u - 0.43, u + 0.43, -0.04, 0.04, zz - 0.005, zz + 0.56, matrix=Mx)
        hmax = max(hmax, zz + 0.55)
    if col:
        # 층마다 상자 (윗단은 한두 개라 통째 상자면 양옆 위가 빈 벽)
        w0 = 1.74 if n >= 2 else 0.84
        C.lcol(x, y, z, yaw, -w0 / 2 if n >= 2 else -0.87, w0 / 2 if n >= 2 else -0.03, -0.3, 0.3, 0.0, 0.55)
        for u in ups:
            C.lcol(x, y, z, yaw, u - 0.42, u + 0.42, -0.3, 0.3, 0.55, 1.1)
    return hmax


def cable_drum(C, x, y, z=0.0, yaw=0.0, *, r=0.55, col=True):
    """케이블 드럼 (옆으로 세운 나무 얼레). 낮은 엄폐."""
    Mx = _yaw_m(x, y, z, yaw)
    ax = Mx.to_3x3() @ Vector((1, 0, 0))
    c = Vector((x, y, z + r))
    for s in (-1, 1):
        C.cyl("wood", tuple(c + ax * s * 0.3), tuple(c + ax * s * 0.36), r, segs=14, kind="detail")
    C.cyl("dark", tuple(c - ax * 0.3), tuple(c + ax * 0.3), r * 0.72, segs=14, kind="detail")
    if col:
        # 옆으로 세운 얼레: 원판 두 장 사이의 원기둥 (상자면 네 모서리가 빈 벽)
        rim = [Mx.to_3x3() @ Vector((0, math.cos(2 * math.pi * i / 14), math.sin(2 * math.pi * i / 14))) * r
               for i in range(14)]
        col_hull(C, [tuple(c + ax * sx * 0.36 + q) for sx in (-1, 1) for q in rim], hint="r")


def maint_cart(C, x, y=AV, *, top=TRACK_TOP, col=True):
    """궤도 점검차 (보 위에 걸친 작은 수레, 노란 몸체 + 공구함). 통로를 반쯤 막는 높은 엄폐."""
    C.box("hazard", x - 1.3, x + 1.3, y - 0.95, y + 0.95, top + 0.28, top + 0.9, kind="detail")
    C.box("dark", x - 1.2, x + 1.2, y - 0.6, y + 0.6, top, top + 0.28, kind="detail")
    for s in (-1, 1):
        C.cyl("dark", (x + s * 0.9, y - 0.58, top + 0.15), (x + s * 0.9, y + 0.58, top + 0.15), 0.14, segs=10,
              kind="detail")
    C.box("navy", x - 1.1, x - 0.1, y - 0.7, y + 0.7, top + 0.9, top + 1.25, kind="detail")
    C.box("metal", x + 0.2, x + 1.1, y - 0.5, y + 0.5, top + 0.9, top + 1.05, kind="detail")
    C.cyl("metal", (x + 1.25, y - 0.8, top + 0.9), (x + 1.25, y - 0.8, top + 1.7), 0.03, segs=6, kind="detail")
    C.cyl("alert_d", (x + 1.25, y - 0.8, top + 1.7), (x + 1.25, y - 0.8, top + 1.85), 0.07, segs=8, kind="detail")
    # 운영사 도장 (양옆): 모나티엄 엠블럼 → 모나티엄 철도공사 → 남색 띠에 업무 표시 두 줄 (공공 작업차처럼)
    for s in (-1, 1):
        N = Vector((0, s, 0))
        R, _, _ = mk.frame(tuple(N))
        f = Vector((x, y + s * 0.95, 0))
        C.logo(tuple(f - R * 0.86 + Vector((0, 0, top + 0.6))), 0.42, tuple(N), key="gold", disc="navy", lift=0.006)
        C.text("navy", "모나티엄 철도공사", 0.12, tuple(f + R * 0.38 + Vector((0, 0, top + 0.79))), tuple(N), lift=0.005)
        C.text("navy", "MONATIUM RAILWAY CORP.", 0.062, tuple(f + R * 0.38 + Vector((0, 0, top + 0.655))), tuple(N),
               lift=0.005)
        # 업무 표시 두 줄 (줄이지 않는다): 궤도 점검 차량 / TRACK MAINTENANCE VEHICLE
        C.rect("navy", tuple(f + R * 0.38 + Vector((0, 0, top + 0.425))), tuple(N), 1.76, 0.25, lift=0.004)
        C.text("white", "궤도 점검 차량", 0.095, tuple(f + R * 0.38 + Vector((0, 0, top + 0.47))), tuple(N), lift=0.009)
        C.text("white", "TRACK MAINTENANCE VEHICLE", 0.066, tuple(f + R * 0.38 + Vector((0, 0, top + 0.355))), tuple(N),
               lift=0.009)
    if col:
        # 몸체(0.9 m) + 위의 공구함 (한 상자로 1.25 m까지 덮으면 몸체 위 오른쪽이 빈 벽)
        C.col(x - 1.3, x + 1.3, y - 0.95, y + 0.95, top, top + 0.9)
        C.col(x - 1.1, x - 0.1, y - 0.7, y + 0.7, top + 0.9, top + 1.25)
        C.col(x + 0.2, x + 1.1, y - 0.5, y + 0.5, top + 0.9, top + 1.05)


def jersey_barrier(C, x, y, z=0.0, yaw=0.0, *, length=2.0, col=True, key="jersey"):
    """콘크리트 방호벽 (높이 0.82, 아래가 넓은 단면). 낮은 엄폐."""
    Mx = _yaw_m(x, y, z, yaw)
    prof = [(-0.3, 0.0), (0.3, 0.0), (0.3, 0.08), (0.14, 0.3), (0.1, 0.82), (-0.1, 0.82), (-0.14, 0.3), (-0.3, 0.08)]
    rot = Matrix.Rotation(math.radians(90), 4, "Y")
    b = C.bm(key, "detail")
    f0 = [b.verts.new(Mx @ Vector((-length / 2, py, pz))) for py, pz in prof]
    f1 = [b.verts.new(Mx @ Vector((length / 2, py, pz))) for py, pz in prof]
    faces = [b.faces.new(list(reversed(f0))), b.faces.new(f1)]
    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        faces.append(b.faces.new((f0[i], f0[j], f1[j], f1[i])))
    bmesh.ops.recalc_face_normals(b, faces=faces)
    for s in (-1, 1):
        q = Mx @ Vector((0, s * 0.125, 0.55))
        C.strip("hazard", tuple(Mx @ Vector((-length / 2 + 0.1, s * 0.125, 0.55))),
                tuple(Mx @ Vector((length / 2 - 0.1, s * 0.125, 0.55))), 0.08,
                tuple(Mx.to_3x3() @ Vector((0, s, 0.15)).normalized()), lift=0.01)
    if col:
        # 단면이 무릎(0.3 m)에서 오목하다: 아래 넓은 판 + 위 좁은 판 두 볼록 COL
        for part in (prof[:4] + prof[6:], [prof[3], prof[4], prof[5], prof[6]]):
            col_hull(C, [tuple(Mx @ Vector((sx * length / 2, py, pz))) for sx in (-1, 1) for py, pz in part], hint="j")


# ================================================================== 방어선

def defense_arc(C, center, R, plan, *, z=0.0, start=-45.0, step=7.5, col=True):
    """시청 방어선 호. center = 호 중심(x, y), R = 반지름. plan = 각 자리 종류 문자열 목록:
    'S' 모래주머니 벽, 'B' 바리케이드, 's'/'b' 빈 건설 자리(모래주머니/바리케이드), '-' 빈칸.
    자리 θ = start + i*step (0 = 정남, 양수 = 동쪽). 앞면(-Y)은 바깥(적 쪽).
    반환: [{kind, pos, yaw, normal, theta}]."""
    out = []
    for i, k in enumerate(plan):
        th = math.radians(start + i * step)
        n = Vector((math.sin(th), -math.cos(th), 0))
        p = Vector((center[0], center[1], 0)) + n * R
        yaw = math.degrees(mk.yaw_to(p, p + n))
        e = {"kind": k, "pos": Vector((p.x, p.y, z)), "yaw": yaw, "normal": n, "theta": start + i * step}
        if k == "S":
            sandbags(C, p.x, p.y, yaw=yaw, z=z, n=4, rows=3, col=col)
        elif k == "B":
            riot_barricade(C, p.x, p.y, yaw=yaw, z=z, col=col)
        elif k in ("s", "b"):
            # 빈 자리 표시: 바닥 테이프 사각형
            R_ = Vector((-n.y, n.x, 0))
            w = 2.4 if k == "s" else 1.8
            corners = [p + R_ * (sx * w / 2) + n * (sy * 0.4) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            for j in range(4):
                a_, b_ = corners[j], corners[(j + 1) % 4]
                C.strip("hazard", (a_.x, a_.y, z), (b_.x, b_.y, z), 0.07, lift=0.014)
        out.append(e)
    return out


def sandbags(C, x, y, *, yaw=0.0, z=0.0, n=4, rows=3, col=True):
    """모래주머니 벽 (mk.sandbag_wall과 같은 쌓기, 주머니를 낮은 분할로). 정면 -Y. 높이 0.14+rows*0.24."""
    Mx = _yaw_m(x, y, z, yaw)
    for row in range(rows):
        for k in range(n - row % 2):
            off = -0.31 * (n - 1) + k * 0.62 + (0.31 if row % 2 else 0)
            p = Mx @ Vector((off, 0, 0.14 + row * 0.24))
            C.blob("sand", tuple(p), 0.34, (1, 0.6, 0.42), segs=6, rings=3, kind="main", rot_z=math.radians(yaw))
    C.strip("sand_d", tuple(Mx @ Vector((-0.31 * n, -0.21, 0.16 + (rows - 1) * 0.12))),
            tuple(Mx @ Vector((0.31 * n, -0.21, 0.16 + (rows - 1) * 0.12))), 0.03,
            tuple(Mx.to_3x3() @ Vector((0, -1, 0))), lift=0.0)
    if col:
        # 주머니 깊이 ±0.2, 맨 윗줄 윗면 0.14+(rows-1)*0.24+0.14 (상자를 더 크게 잡으면 위·앞뒤가 빈 벽)
        top = 0.14 + (rows - 1) * 0.24 + 0.13
        C.lcol(x, y, z, yaw, -0.31 * n - 0.03, 0.31 * n + 0.03, -0.21, 0.21, 0.0, top)


def drop_text(C, group, test):
    """아직 합치지 않은 글자 오브젝트 중 test(normal)이 참인 것을 뺀다 (아무도 못 보는 뒷면 글자)."""
    keep, n = [], 0
    for item in C.objs:
        g, key, kind, o = item
        N = Vector(o.matrix_world.col[2][:3]).normalized()
        if g == group and test(N):
            data = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if data and data.users == 0:
                bpy.data.meshes.remove(data)
            n += 1
            continue
        keep.append(item)
    C.objs[:] = keep
    return n


def command_post(C, x, y, z=0.0, *, yaw=0.0, col=True):
    """진압반 현장 지휘소 (칸나): 접이 탁자 + 도시 지도 + 무전기 + 안테나 + 상자 + 낮은 모래주머니 + 표지.
    정면 -Y(지휘관이 보는 쪽 = 광장). 반환: dict(stand=지휘관 자리, table=탁자 중심, radio)."""
    Mx = _yaw_m(x, y, z, yaw)
    L = lambda u, v, w=0.0: Mx @ Vector((u, v, w))  # noqa: E731
    N = (Mx.to_3x3() @ Vector((0, -1, 0))).normalized()
    # 탁자 (윗면 0.62, 엘프)
    tb = C.bm("dark", "detail")
    mk._bm_box(C.bm("navy_l", "detail"), -0.8, 0.8, 0.0, 0.8, 0.58, 0.62, matrix=Mx @ Matrix.Translation((0, 0.3, 0)))
    for u, v in ((-0.72, 0.38), (0.72, 0.38), (-0.72, 1.02), (0.72, 1.02)):
        mk._bm_box(tb, u - 0.03, u + 0.03, v - 0.03, v + 0.03, 0, 0.58, matrix=Mx)
    # 지도 + 표시
    C.decal("paper", hw.rrect(1.2, 0.62, 0.02, 1), tuple(L(0, 0.7, 0.62)), (0, 0, 1), up=tuple(Mx.to_3x3() @ Vector((0, 1, 0))),
            lift=0.006)
    for (u, v, k) in ((-0.3, 0.6, "alert"), (0.1, 0.75, "alert"), (0.35, 0.55, "teal"), (-0.05, 0.85, "teal"),
                      (0.0, 0.62, "navy")):
        C.decal(k, hw.circle(0.035, 8), tuple(L(u, v, 0.62)), (0, 0, 1), lift=0.01)
    C.strip("navy", tuple(L(-0.5, 0.5, 0.62)), tuple(L(0.5, 0.9, 0.62)), 0.015, lift=0.013)  # 표시 원(0.01) 위 3 mm
    # 무전기 + 안테나 + 송수화기
    obox(C, "olive", *L(0.55, 1.35)[:2], z, z + 0.5, 0.55, 0.35, yaw)
    C.rect("glow", tuple(L(0.55, 1.17, 0.4)), tuple(N), 0.2, 0.06, lift=0.01)
    C.cyl("metal", tuple(L(0.75, 1.45, 0.5)), tuple(L(0.75, 1.45, 2.6)), 0.02, segs=6, kind="detail")
    C.blob("dark", tuple(L(0.75, 1.45, 2.6)), 0.05, segs=6, rings=4, kind="detail")
    obox(C, "dark", *L(0.3, 0.55)[:2], z + 0.62, z + 0.68, 0.18, 0.08, yaw + 20)
    # 태블릿 거치대
    C.cyl("metal", tuple(L(-0.95, 0.5, 0)), tuple(L(-0.95, 0.5, 0.95)), 0.025, segs=6, kind="detail")
    C.rbox("dark", tuple(L(-0.95, 0.47, 1.05)), (0.36, 0.03, 0.26), rot=(-20, 0, yaw), kind="detail")
    C.rect("glow", tuple(L(-0.95, 0.455, 1.05)), tuple(N), 0.3, 0.2, lift=0.004)
    # 상자 + 깃대 현수막 + 표지판
    ammo_crate(C, *L(-1.25, 1.25)[:2], z, yaw + 90, key="violet", text="진압반\nSUPPRESSION UNIT")
    supply_stack(C, *L(1.35, 1.0)[:2], z, yaw + 90, n=2, seed=7)
    C.cyl("metal", tuple(L(-1.6, 1.5, 0)), tuple(L(-1.6, 1.5, 3.0)), 0.03, segs=6, kind="detail")
    mk.banner(C, tuple(L(-1.6, 1.47, 2.9)), tuple(N), 0.7, 1.6)
    sc = L(1.4, -0.35, 0.0)
    C.cyl("metal", tuple(sc), tuple(sc + Vector((0, 0, 1.25))), 0.03, segs=6, kind="detail")
    C.plate("navy", hw.rrect(0.95, 0.42, 0.08, 2), tuple(sc + Vector((0, 0, 1.15))), tuple(N), 0.03, kind="detail")
    C.text("white", "현장 지휘소", 0.12, tuple(sc + Vector((0, 0, 1.2)) + N * 0.035), tuple(N), lift=0.003)
    C.text("teal", "SUPPRESSION UNIT CP", 0.07, tuple(sc + Vector((0, 0, 1.04)) + N * 0.035), tuple(N), lift=0.003)
    # 앞쪽 낮은 모래주머니 (가운데 틈)
    for u in (-1.1, 1.1):
        p = L(u, -0.75)
        sandbags(C, p.x, p.y, yaw=yaw, z=z, n=3, rows=2, col=col)
    if col:
        col_obox(C, tuple(L(0, 0.7, 0.31)), (1.6, 0.8, 0.62), yaw)
        # 무전기, 태블릿 거치대, 깃대, 표지판 기둥 (머리 높이 표지판 판은 COL을 두지 않는다: 밑으로 앉아 들어가면
        # 일어서지 못한다)
        C.lcol(x, y, z, yaw, 0.55 - 0.275, 0.55 + 0.275, 1.35 - 0.175, 1.35 + 0.175, 0.0, 0.5)
        C.lcol(x, y, z, yaw, -0.98, -0.92, 0.47, 0.53, 0.0, 0.92)
        C.lcol(x, y, z, yaw, -1.13, -0.77, 0.42, 0.53, 0.92, 1.2)
        C.lcol(x, y, z, yaw, -1.64, -1.56, 1.46, 1.54, 0.0, 3.0)
        C.lcol(x, y, z, yaw, 1.36, 1.44, -0.39, -0.31, 0.0, 1.36)
    return {"stand": L(0, -0.15, 0), "table": L(0, 0.7, 0.62), "radio": L(0.55, 1.35, 0.5)}


# ================================================================== 전쟁 피해

def car(C, x, y, yaw=0.0, *, z=-0.15, color="car_b", burned=False, seed=0, col=True):
    """시민 차량 (엘프 체격 소형차 3.4 x 1.55 x 1.25). burned면 그을린 차체·빈 창·녹·바퀴 없음(림)."""
    rng = random.Random(seed)
    Mx = _yaw_m(x, y, z, yaw)
    body = "char" if burned else color
    trim = "char_l" if burned else "dark"
    tilt = Matrix.Rotation(math.radians(rng.uniform(-2.5, 2.5) if burned else 0), 4, "X")
    M_ = Mx @ tilt
    b = C.bm(body, "detail")
    mk._bm_box(b, -0.77, 0.77, -1.7, 1.7, 0.28, 0.78, matrix=M_)
    # 객실 (위가 좁은 판)
    cab = [(-0.68, -0.85, 0.78), (0.68, -0.85, 0.78), (0.68, 1.15, 0.78), (-0.68, 1.15, 0.78),
           (-0.58, -0.45, 1.25), (0.58, -0.45, 1.25), (0.58, 0.95, 1.25), (-0.58, 0.95, 1.25)]
    vs = [b.verts.new(M_ @ Vector(p)) for p in cab]
    for f in _BOX_F:
        b.faces.new([vs[i] for i in f])
    # 창 (불탄 차는 검은 구멍)
    wk = "soot" if burned else "glass_d"
    for s in (-1, 1):
        n = (M_.to_3x3() @ Vector((s, 0, 0))).normalized()
        c = M_ @ Vector((s * 0.64, 0.15, 1.0))
        C.rect(wk, tuple(c), tuple(n), 1.5, 0.34, up=tuple((M_.to_3x3() @ Vector((0, 0, 1))).normalized()), lift=0.02)
    for (vv, zz, nv) in ((-0.65, 1.02, (0, -1, 0.55)), (1.05, 1.02, (0, 1, 0.7))):
        n = (M_.to_3x3() @ Vector(nv)).normalized()
        C.rect(wk, tuple(M_ @ Vector((0, vv, zz))), tuple(n), 1.05, 0.36, lift=0.02)
    # 범퍼, 등
    for v in (-1.72, 1.72):
        mk._bm_box(C.bm(trim, "detail"), -0.78, 0.78, v - 0.06, v + 0.06, 0.25, 0.45, matrix=M_)
    if not burned:
        for s in (-1, 1):
            C.rect("lamp_off", tuple(M_ @ Vector((s * 0.55, -1.71, 0.62))), tuple(M_.to_3x3() @ Vector((0, -1, 0))),
                   0.26, 0.12, lift=0.02)
            C.rect("red", tuple(M_ @ Vector((s * 0.55, 1.71, 0.62))), tuple(M_.to_3x3() @ Vector((0, 1, 0))), 0.26,
                   0.12, lift=0.02)
    else:
        for k in range(4):
            C.decal("rust", hw.circle(rng.uniform(0.15, 0.35), 8), tuple(M_ @ Vector((rng.choice((-0.78, 0.78)),
                                                                                       rng.uniform(-1.4, 1.4),
                                                                                       rng.uniform(0.4, 0.7)))),
                    tuple(M_.to_3x3() @ Vector((1 if k % 2 else -1, 0, 0))), lift=0.02)
    # 바퀴
    for u in (-0.72, 0.72):
        for v in (-1.1, 1.1):
            p = M_ @ Vector((u, v, 0.28))
            ax = M_.to_3x3() @ Vector((1, 0, 0))
            if burned:
                # 림 바깥면이 차체 옆면(±0.77)보다 1 cm 나오게 (같은 평면이면 깜빡인다)
                C.cyl("rust", tuple(p - ax * 0.06), tuple(p + ax * 0.06), 0.2, segs=8, kind="detail")
            else:
                C.cyl("tire", tuple(p - ax * 0.09), tuple(p + ax * 0.09), 0.28, segs=8, kind="detail")
    if burned:
        C.decal("soot", [(math.cos(a) * 2.4 * rng.uniform(0.8, 1.1), math.sin(a) * 1.6 * rng.uniform(0.8, 1.1))
                         for a in [2 * math.pi * k / 12 for k in range(12)]], (x, y, z), (0, 0, 1),
                up=(math.sin(math.radians(yaw)), math.cos(math.radians(yaw)), 0), lift=0.026)  # 옆 scorch_mark(0.022) 위
    if col:
        # 차체(바닥~0.78) + 위가 좁은 객실 (한 상자면 보닛·트렁크 위 0.4 m가 빈 벽)
        col_hull(C, [tuple(M_ @ Vector((sx * 0.78, sy * 1.72, sz))) for sx in (-1, 1) for sy in (-1, 1)
                     for sz in (0.0, 0.78)], hint="v")
        col_hull(C, [tuple(M_ @ Vector(p)) for p in cab], hint="v")


def fire(C, x, y, z=0.0, *, s=1.0, seed=0):
    """불꽃 덩어리 (UNLIT 주황 + 밝은 속). 연기는 smoke_plume으로 따로."""
    rng = random.Random(seed)
    for k in range(3):
        a = rng.uniform(0, 6.28)
        C.blob("fire", (x + math.cos(a) * 0.3 * s, y + math.sin(a) * 0.3 * s, z + 0.25 * s), 0.45 * s,
               (1, 1, rng.uniform(1.2, 1.7)), segs=7, rings=4)
    C.blob("fire_c", (x, y, z + 0.25 * s), 0.3 * s, (1, 1, 1.3), segs=6, rings=3)
    C.blob("ember", (x, y, z + 0.05), 0.6 * s, (1, 1, 0.12), segs=8, rings=3)


def burning_wreck(C, x, y, yaw=0.0, *, z=-0.15, seed=0, smoke_h=28.0, drift=(-0.3, 0.12)):
    """불타는 차 잔해 + 작은 연기 기둥."""
    car(C, x, y, yaw, z=z, burned=True, seed=seed)
    fire(C, x, y, z + 0.6, s=0.9, seed=seed)
    smoke_plume(C, x, y, z=z + 1.0, h=smoke_h, r=1.3, drift=drift, seed=seed, dark=0.75, segs=6, rings=4)


def smoke_plume(C, x, y, *, z=0.0, h=40.0, r=2.0, drift=(-0.3, 0.12), seed=0, dark=0.45, segs=7, rings=4,
                key="smoke_l", key_d="smoke_d"):
    """연기 기둥 (덩어리가 위아래로 겹치게 쌓고 먹선을 뺀다: mk.smoke_column처럼 떠 있는 돌로 보이지 않는다).
    아래쪽 dark 비율은 검은 연기, 위로 갈수록 굵어지고 바람(drift, 높이 1 m당 수평 m) 쪽으로 기운다."""
    rng = random.Random(seed)
    zz = z + r * 0.6
    while zz < z + h:
        t = (zz - z) / h
        rr = r * (0.55 + 1.35 * t) * rng.uniform(0.9, 1.1)
        cx = x + drift[0] * (zz - z) + rng.uniform(-0.12, 0.12) * rr
        cy = y + drift[1] * (zz - z) + rng.uniform(-0.12, 0.12) * rr
        C.blob(key_d if t < dark else key, (cx, cy, zz), rr, (1.0, 1.0, 1.25), segs=segs, rings=rings,
               rot_z=rng.uniform(0, 3), kind="fine")
        zz += max(rr * 1.3, h / 11.0)


def scorch_mark(C, x, y, r, *, z=0.0, seed=0, debris=True):
    """폭발 그을음 (불규칙한 검은 자국 + 재 고리 + 파편 몇 개)."""
    rng = random.Random(seed)
    pts = [(math.cos(2 * math.pi * i / 16) * r * rng.uniform(0.65, 1.2), math.sin(2 * math.pi * i / 16) * r *
            rng.uniform(0.65, 1.2)) for i in range(16)]
    C.decal("ash", [(u * 1.25, v * 1.25) for u, v in pts], (x, y, z), (0, 0, 1), up=(0, 1, 0), lift=0.018)
    C.decal("soot", pts, (x, y, z), (0, 0, 1), up=(0, 1, 0), lift=0.022)
    if debris:
        for k in range(int(3 + r * 2)):
            a = rng.uniform(0, 6.28)
            d = rng.uniform(r * 0.6, r * 1.6)
            C.blob(rng.choice(("concrete_d", "ash", "char")), (x + math.cos(a) * d, y + math.sin(a) * d, z + 0.06),
                   rng.uniform(0.08, 0.2), (1.3, 1, 0.6), segs=5, rings=3, kind="detail", rot_z=a)


# 바닥 유리 조각 높이: 보도 띠(0.012), 그을음 재(0.018)·검댕(0.022)·차/드론 그을음(0.026)보다 위에 조각마다 1.5 mm씩
GLASS_LIFT = 0.03


def fallen_lamp(C, x, y, yaw=0.0, *, z=0.0, h=3.6, col=True):
    """쓰러진 가로등 (밑동만 남고 기둥이 yaw 쪽으로 누움)."""
    C.cyl("dark", (x, y, z), (x, y, z + 0.35), 0.16, r2=0.12, segs=8, kind="detail")
    C.cyl("gold", (x, y, z + 0.35), (x, y, z + 0.45), 0.1, segs=8, kind="detail", cap=False)
    d = Vector((math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)), 0))
    p0 = Vector((x, y, z + 0.4)) + d * 0.15
    p1 = p0 + d * (h - 0.4) + Vector((0, 0, -0.32))
    C.cyl("dark", tuple(p0), tuple(p1), 0.065, segs=6, kind="detail")
    C.cyl("dark", tuple(p1), tuple(p1 + d * 0.12), 0.22, segs=8, kind="detail")
    C.cyl("lamp_off", tuple(p1 + d * 0.12), tuple(p1 + d * 0.45), 0.2, r2=0.17, segs=8, kind="detail")
    if col:
        # 밑동 + 누운 기둥 + 등 머리. 2026-11-03 (M3 격자 걷기): 기둥 COL이 기둥을 따라 기운 막대(윗면 0.47 → 0.15 m)라 윗면이
        # 자동 오르기(0.28) 언저리인 가운데에서 캡슐이 반쯤 올라 섰다 → 윗면이 수평인 상자 두 토막(0.47·0.32 m, 땅부터)으로
        # 확실히 막고(넘으려면 점프), 윗면이 0.22 m 아래로 낮아지는 끝 23 %는 COL 없이 그냥 넘는다. 등 머리도 땅부터 0.32 m 상자
        col_cyl(C, x, y, 0.16, z, z + 0.45, segs=8, r2=0.12, hint="l")
        ang = math.degrees(math.atan2(d.y, d.x))
        for t0, t1, top in ((0.0, 0.5, 0.47), (0.5, 0.77, 0.32)):
            a_ = p0 + (p1 - p0) * t0
            b_ = p0 + (p1 - p0) * t1
            m_ = (a_ + b_) / 2
            col_obox(C, (m_.x, m_.y, z + top / 2), ((b_ - a_).length, 0.13, top), ang, hint="l")
        hm = p1 + d * 0.225
        col_obox(C, (hm.x, hm.y, z + 0.16), (0.45, 0.42, 0.32), ang, hint="l")
    for k in range(5):
        q = p1 + d * 0.6 + Vector((math.cos(k * 1.7) * 0.4, math.sin(k * 1.7) * 0.4, -0.08))
        C.decal("glass_a", hw.circle(0.07, 5), (q.x, q.y, z), (0, 0, 1), lift=GLASS_LIFT + k * 0.0015)


def broken_barricade(C, x, y, yaw=0.0, *, z=0.0, seed=0, col=True):
    """넘어진 진압반 바리케이드 (판이 기울어 쓰러지고 다리가 꺾였다)."""
    rng = random.Random(seed)
    Mx = _yaw_m(x, y, z, yaw)
    tilt = rng.uniform(55, 80)
    M_ = Mx @ Matrix.Translation((0, 0.05, 0.12)) @ Matrix.Rotation(math.radians(-tilt), 4, "X")
    N = (M_.to_3x3() @ Vector((0, -1, 0))).normalized()
    c = M_ @ Vector((0, 0, 0.32))
    C.plate("violet", hw.rrect(1.8, 0.62, 0.12, 3), tuple(c), tuple(N), 0.06, kind="detail", back=0.03,
            up=tuple((M_.to_3x3() @ Vector((0, 0, 1))).normalized()))
    C.strip("teal", tuple(M_ @ Vector((-0.8, -0.032, 0.2))), tuple(M_ @ Vector((0.8, -0.032, 0.2))), 0.1,
            tuple(N), lift=0.004)
    C.decal("soot", hw.circle(0.35, 9), tuple(c - N * 0.0), tuple(N), lift=0.06)
    legs = []
    for s_ in (-1, 1):
        foot = Mx @ Vector((s_ * 0.75, rng.uniform(-0.4, 0.2), 0))
        tip = foot + Vector((rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0.5))
        C.beam("steel", tuple(foot), tuple(tip), 0.05, 0.05, kind="detail")
        legs.append((foot, tip))
    if col:
        # 판: 예전 COL은 기운 판 그대로(+바닥까지)라 판이 걸을 수 있는 경사(10~35°)가 되어, 캡슐이 판 끝(0.25~0.3 m)까지 올라가
        # 앉아 걷기로 2.7초씩 섰다 (2026-11-03 M3 봇 걷기) → 판 발자국을 덮는 윗면 수평 상자. 윗면이 0.22 m 아래면 그 높이(그냥
        # 넘는다), 0.22~0.3 m면 0.32 m(확실히 막는다), 그 위면 판 꼭대기 높이 (판 밑 틈은 몸이 못 들어간다)
        corners = [M_ @ Vector((u, v, w)) for u in (-0.9, 0.9) for v in (-0.03, 0.03) for w in (0.01, 0.63)]
        inv = Mx.inverted()
        loc = [inv @ p for p in corners]
        lx0, lx1 = min(p.x for p in loc), max(p.x for p in loc)
        ly0, ly1 = min(p.y for p in loc), max(p.y for p in loc)
        top = max(p.z for p in corners) - z
        top = top if top <= 0.22 else max(top, 0.32)
        cen = Mx @ Vector(((lx0 + lx1) / 2, (ly0 + ly1) / 2, 0))
        col_obox(C, (cen.x, cen.y, z + top / 2), (lx1 - lx0, ly1 - ly0, top), yaw, hint="k")
        # 꺾인 다리: 땅(발)에서 0.5 m(끝)로 기운 가는 막대라, 막대 COL은 윗면이 자동 오르기(0.28) 언저리인 데서 캡슐이 막대에
        # 올라서 섰다 (2026-11-03 M3 격자 걷기). 0.3 m 아래 아랫부분(60 %)은 COL 없이 넘고, 윗부분만 땅부터 끝 높이까지 얇은 판
        for foot, tip in legs:
            a_ = foot + (tip - foot) * 0.6
            m_ = (a_ + tip) / 2
            hl = math.hypot(tip.x - a_.x, tip.y - a_.y)
            col_obox(C, (m_.x, m_.y, z + (tip.z - z) / 2), (max(hl, 0.06), 0.06, tip.z - z),
                     math.degrees(math.atan2(tip.y - a_.y, tip.x - a_.x)), hint="k")


def spilled_sandbags(C, x, y, *, z=0.0, n=7, r=1.4, seed=0, col=True, yaw=0.0):
    """무너진 모래주머니 (흩어진 주머니 + 낮은 더미)."""
    rng = random.Random(seed)
    tops = []
    for k in range(n):
        a = rng.uniform(0, 6.28)
        d = rng.uniform(0, r)
        px, py = x + math.cos(a) * d, y + math.sin(a) * d * 0.6
        lay = 0 if k < n * 0.6 else 1
        rz = rng.uniform(0, 3)
        C.blob("sand", (px, py, z + 0.13 + lay * 0.2), 0.34, (1, 0.6, 0.42), segs=8, rings=4, rot_z=rz)
        if lay:
            tops.append((px, py, rz))
    C.decal("sand", hw.circle(0.35, 7), (x + r * 0.9, y - 0.3, z), (0, 0, 1), lift=0.015)  # 보도 띠(0.012)와 그을음 재(0.018) 사이
    if col:
        # 흩어진 주머니라 한 상자로 덮으면 빈 벽이 된다 (yaw도 주머니 배치와 맞지 않았다): 아랫줄(0.27 m)은 넘어가고
        # 윗줄 주머니만 바닥부터 COL
        for (px, py, rz) in tops:
            C.lcol(px, py, z, math.degrees(rz), -0.32, 0.32, -0.19, 0.19, 0.0, 0.46)


def crashed_drone(C, x, y, yaw=0.0, *, z=0.0, s=1.0, seed=0, col=True):
    """추락한 R41 드론 (각진 검은 몸체가 기울어 박힘, 부러진 회전날개 팔, 꺼진 렌즈). R41 형태 언어: 45° 모따기."""
    rng = random.Random(seed)
    Mx = _yaw_m(x, y, z, yaw) @ Matrix.Rotation(math.radians(rng.uniform(12, 25)), 4, "X") @ \
        Matrix.Rotation(math.radians(rng.uniform(-15, 15)), 4, "Y")
    body = [(-0.45, -0.7), (0.45, -0.7), (0.62, -0.35), (0.62, 0.45), (0.35, 0.75), (-0.35, 0.75), (-0.62, 0.45),
            (-0.62, -0.35)]
    pts = [(u * s, v * s) for u, v in body]
    mk._bm_prism(C.bm("r41_shell", "detail"), pts, 0.05 * s, 0.42 * s, matrix=Mx)
    mk._bm_prism(C.bm("r41_metal", "detail"), [(u * 0.7, v * 0.7) for u, v in pts], 0.42 * s, 0.55 * s, matrix=Mx)
    hull = [tuple(Mx @ Vector((u, v, zz))) for u, v in pts for zz in (0.05 * s, 0.42 * s)]
    hull += [tuple(Mx @ Vector((u * 0.7, v * 0.7, 0.55 * s))) for u, v in pts]
    lens = Mx @ Vector((0, -0.71 * s, 0.25 * s))
    C.decal("soot", hw.circle(0.1 * s, 10), tuple(lens), tuple(Mx.to_3x3() @ Vector((0, -1, 0))), lift=0.01)
    for k, (u, v) in enumerate(((-0.9, -0.6), (0.9, -0.6), (-0.9, 0.7), (0.9, 0.7))):
        a = Mx @ Vector((u * 0.55 * s, v * 0.6 * s, 0.3 * s))
        bnt = Mx @ Vector((u * s * rng.uniform(0.8, 1.15), v * s * rng.uniform(0.7, 1.1), 0.3 * s - rng.uniform(0, 0.25)))
        C.beam("r41_metal", tuple(a), tuple(bnt), 0.07 * s, 0.07 * s, kind="detail")
        if k % 2 == 0:
            C.cyl("r41_light", tuple(bnt), tuple(bnt + Vector((0, 0, 0.05 * s))), 0.32 * s, segs=10, kind="detail")
            if col:
                # 부러진 팔 끝 회전날개 원판 (몸통 밖 0.3~0.5 m 높이): 따로 COL, 바닥부터 (원판만 COL이면 COL이 없는 팔이
                # 받쳐 공중에 뜬 판이 된다: floatcheck. 캡슐은 원판 높이에서 어차피 막힌다)
                col_cyl(C, bnt.x, bnt.y, 0.32 * s, min(bnt.z, z), bnt.z + 0.05 * s, segs=10, hint="d")
    C.decal("soot", hw.circle(1.6 * s, 12), (x, y, z), (0, 0, 1), lift=0.026)  # scorch_mark 재·검댕(0.018/0.022) 위
    scorch_mark(C, x, y, 1.3 * s, z=z, seed=seed, debris=True)
    if col:
        # 기울어 박힌 몸통 그대로 (바닥 아래로 들어간 부분은 바닥에서 자른다)
        col_hull(C, [(p[0], p[1], max(p[2], z)) for p in hull], hint="d")


def rubble(C, x, y, *, z=0.0, r=1.2, h=0.6, seed=0, col=True, key="concrete_d"):
    """콘크리트 잔해 더미 (덩어리 + 철근).
    COL (2026-11-03, M3 방어선 양 날개에서 끼던 것): 예전 볼록 껍질은 덩어리 바닥 둘레(z 0)에서 꼭대기로 바로 이어
    옆면이 40~50°였다. 오르기 한계(46°) 언저리라 캡슐이 반쯤 오르다 미끄러지며 섰고, 더미 밖으로 0.8 m 뻗은 철근 COL
    (무릎~허리 높이)과 경사 사이 V자에 끼었다. 이제 옆면은 덩어리가 가장 넓은 둘레(0.95배)에서 0.34 m까지 곧게 서고
    (자동 오르기 0.28 m로 못 올라 벽처럼 비켜 간다, 점프로는 오른다), 윗면만 30° 안팎으로 기운다. 철근은 덩어리 꼭대기에서
    위로 솟게 해 COL이 더미 둘레 안에 있다."""
    rng = random.Random(seed)
    hull = []
    tops = []
    hs = 0.34 * h / 0.6
    for k in range(6):
        a = rng.uniform(0, 6.28)
        d = rng.uniform(0, r * 0.7)
        bx, by = x + math.cos(a) * d, y + math.sin(a) * d
        bk = rng.choice((key, "concrete", "ash"))          # (난수 순서는 예전 그대로: 재질 다음 크기)
        br = rng.uniform(0.25, 0.5) * r
        C.blob(bk, (bx, by, z + h * 0.3), br, (1.2, 1, 0.6 * h / 0.6), segs=6, rings=4, kind="detail", rot_z=a)
        # 덩어리가 가장 넓은 둘레 (타원 8방향, 0.95배): 바닥과 hs 높이 → 곧은 옆면
        for i in range(8):
            t = 2 * math.pi * i / 8
            u, v = math.cos(t) * br * 1.2 * 0.95, math.sin(t) * br * 0.95
            px, py = bx + u * math.cos(a) - v * math.sin(a), by + u * math.sin(a) + v * math.cos(a)
            hull += [(px, py, z), (px, py, z + hs)]
        top = z + h * 0.3 + br * h
        hull.append((bx, by, top))
        tops.append((bx, by, top))
    for k in range(3):
        a = rng.uniform(0, 6.28)
        rise = rng.uniform(0.1, 0.5)
        bx, by, top = tops[int(a / 6.28 * 6) % 6]
        p = Vector((bx, by, top - 0.05))
        q = p + Vector((math.cos(a + 1) * 0.22, math.sin(a + 1) * 0.22, 0.25 + rise))
        C.beam("rust", tuple(p), tuple(q), 0.03, 0.03, kind="detail")
        if col:
            col_seg(C, p, q, 0.05, hint="u")          # 덩어리 꼭대기에서 솟은 철근 (더미 둘레 안)
    if col:
        col_hull(C, hull, hint="u")


def r41_barrier(C, x, y, yaw=0.0, *, z=-0.15, col=True):
    """R41 이동식 방벽 (검은 판 + 45° 모따기 + 앰버 줄). 거리 위 적의 엄폐물. 정면 -Y."""
    Mx = _yaw_m(x, y, z, yaw)
    prof = [(-1.0, 0.0), (1.0, 0.0), (1.0, 0.75), (0.8, 0.95), (-0.8, 0.95), (-1.0, 0.75)]
    rot = Matrix.Rotation(math.radians(90), 4, "X")
    mk._bm_prism(C.bm("r41_shell", "detail"), prof, -0.12, 0.12, matrix=Mx @ rot)
    for s in (-1, 1):
        C.strip("amber", tuple(Mx @ Vector((-0.85, s * 0.125, 0.7))), tuple(Mx @ Vector((0.85, s * 0.125, 0.7))), 0.05,
                tuple(Mx.to_3x3() @ Vector((0, s, 0))), lift=0.005)
        foot = Mx @ Vector((s * 0.7, 0, 0))
        C.beam("r41_metal", tuple(foot + Mx.to_3x3() @ Vector((0, -0.4, 0.02))),
               tuple(foot + Mx.to_3x3() @ Vector((0, 0.4, 0.02))), 0.1, 0.06, kind="detail")
    if col:
        col_obox(C, (x, y, z + 0.47), (2.0, 0.3, 0.95), yaw)


def bus_shelter(C, x, y, *, yaw=0.0, z=0.0, col=True, broken=False):
    """버스 정류장 (지붕 + 뒷유리 + 벤치 + 표지). 정면 -Y(차도 쪽)."""
    Mx = _yaw_m(x, y, z, yaw)
    N = (Mx.to_3x3() @ Vector((0, -1, 0))).normalized()
    for u in (-1.6, 1.6):
        for v in (-0.5, 0.6):
            C.cyl("metal", tuple(Mx @ Vector((u, v, 0))), tuple(Mx @ Vector((u, v, 2.2))), 0.05, segs=6, kind="detail")
    mk._bm_box(C.bm("navy_l", "detail"), -1.8, 1.8, -0.75, 0.75, 2.2, 2.32, matrix=Mx)
    mk._bm_box(C.bm("teal", "detail"), -1.81, 1.81, -0.77, -0.7, 2.12, 2.36, matrix=Mx)  # 지붕 끝보다 1 cm 나옴
    if not broken:
        C.rect("glass_a", tuple(Mx @ Vector((0, 0.6, 1.2))), tuple(N), 3.1, 1.8, lift=0.0)
    else:
        C.poly("glass_a", [tuple(Mx @ Vector(p)) for p in ((-1.55, 0.6, 0.3), (0.2, 0.6, 0.3), (-1.55, 0.6, 1.6))],
               normal=tuple(N))
        for k in range(6):
            C.decal("glass_a", hw.circle(0.06, 5), tuple(Mx @ Vector((-1 + k * 0.4, -0.2 + (k % 3) * 0.2, 0))),
                    (0, 0, 1), lift=GLASS_LIFT + k * 0.0015)
    mk.bench(C, *(Mx @ Vector((0, 0.3, 0)))[:2], yaw=yaw, z=z, length=2.4)
    sc = Mx @ Vector((1.95, -0.4, 0))
    C.cyl("metal", tuple(sc), tuple(sc + Vector((0, 0, 2.5))), 0.04, segs=6, kind="detail")
    C.plate("navy", hw.rrect(0.5, 0.5, 0.25, 4), tuple(sc + Vector((0, 0, 2.3))), tuple(N), 0.03, kind="detail")
    C.text("white", "정류장", 0.1, tuple(sc + Vector((0, 0, 2.34)) + N * 0.035), tuple(N), lift=0.003)
    C.text("glow", "BUS", 0.08, tuple(sc + Vector((0, 0, 2.2)) + N * 0.035), tuple(N), lift=0.003)
    if col:
        col_obox(C, tuple(Mx @ Vector((0, 0.6, 1.1))), (3.3, 0.1, 2.2), yaw)
        col_obox(C, tuple(Mx @ Vector((0, 0.25, 0.17))), (2.4, 0.45, 0.34), yaw)
        for u in (-1.6, 1.6):                     # 앞 기둥 (뒤 기둥은 유리 COL 안)
            C.lcol(x, y, z, yaw, u - 0.05, u + 0.05, -0.55, -0.45, 0.0, 2.2)
        C.lcol(x, y, z, yaw, 1.91, 1.99, -0.44, -0.36, 0.0, 2.5)   # 표지 기둥


def stretcher(C, x, y, *, z=0.0, yaw=0.0):
    """구급 들것 (부상자 옆 장식)."""
    Mx = _yaw_m(x, y, z, yaw)
    mk._bm_box(C.bm("teal", "detail"), -0.28, 0.28, -0.85, 0.85, 0.12, 0.16, matrix=Mx)
    for u in (-0.3, 0.3):
        # 손잡이 대는 천(0.12..0.16)보다 5 mm 높게: 윗면·밑면이 천과 같은 평면에 오지 않게
        C.beam("steel", tuple(Mx @ Vector((u, -1.05, 0.145))), tuple(Mx @ Vector((u, 1.05, 0.145))), 0.04, 0.04,
               kind="detail")


# ================================================================== 시청 정문 + 대피소 복도

def cityhall_doorway(C, *, cx=0.0, cy=26.0, lit=True, depth=8.0, shelter=True, group="cityhall"):
    """시청 정문을 연다 (city_hall()이 만든 앞면을 오려 문을 뚫고) 안쪽 복도 + 대피소 표지를 만든다.
    [원작] 모나티엄 시청은 지하 23층. [오리지널] 정문 안 대피소 유도 복도, 표지 "시청 지하 대피소 · SHELTER B1–B23".
    downtown()을 부른 뒤에 쓴다(시청 날개 앞면 y=cy-7, 기단 높이 0.9). 반환: dict(door=(x, y, z), inside, end)."""
    prev = C.grp
    C.group(group)
    WW, WD, WH, PZ = 34.0, 14.0, 11.4, 0.9
    yf = cy - WD / 2                    # 19.0
    dw, dh = 1.3, 2.7                    # 문 반폭, 높이 (엘프 문 1.8 m보다 큰 정문)
    # 1) 날개 앞면 사각형 지우기 → 문 구멍을 낸 벽으로 다시
    n1 = cut_faces(C, group, "stone", "main",
                   lambda f: all(abs(v.co.y - yf) < 1e-3 for v in f.verts) and f.normal.y < -0.9
                   and max(v.co.x for v in f.verts) - min(v.co.x for v in f.verts) > 10)
    wall(C, "stone", "x", yf, 0.3, cx - 13.2, cx + 13.2, PZ, WH, [(cx - dw, cx + dw, PZ, PZ + dh)], col=False)
    # 2) 정문 판(남색)과 문짝 유리 지우기 → 가운데가 뚫린 문틀
    n2 = cut_faces(C, group, "navy", "detail", in_box(cx - 2.1, cx + 2.1, yf - 0.4, yf + 0.01, PZ - 0.05, PZ + 4.5))
    n3 = cut_faces(C, group, "glass_d", "fine", in_box(cx - 1.75, cx + 1.75, yf - 0.4, yf + 0.01, PZ - 0.05, PZ + 3.5))
    hw2, top = 2.0, 4.4
    r = 1.2
    # 문틀 안쪽 구멍은 벽 구멍보다 사방 2 cm 작다: 틀의 문설주·상인방 면이 벽 구멍 면보다 2 cm 나와
    # 벽 면과 이어진 한 평면이 되지 않는다 (문틀 깜빡임, docs/art/zfight-audit.md)
    fw, fh = dw - 0.02, dh - 0.02
    pts = [(-fw, 0.0), (-hw2, 0.0)]
    for i in range(7):
        a = math.pi - (math.pi / 2) * i / 6
        pts.append((-hw2 + r + math.cos(a) * r, top - r + math.sin(a) * r))
    for i in range(7):
        a = math.pi / 2 - (math.pi / 2) * i / 6
        pts.append((hw2 - r + math.cos(a) * r, top - r + math.sin(a) * r))
    pts += [(hw2, 0.0), (fw, 0.0), (fw, fh), (-fw, fh)]
    C.plate("navy", list(reversed(pts)), (cx, yf, PZ), (0, -1, 0), 0.25, kind="detail")
    for sgn in (-1, 1):                  # 문틀 기둥 (벽에서 25 cm 나온다)
        C.col(*sorted((cx + sgn * fw, cx + sgn * hw2)), yf - 0.25, yf, PZ, PZ + 3.2)
    C.text("gold", "모나티엄 시청", 0.26, (cx, yf - 0.26, PZ + dh + 0.55), (0, -1, 0), lift=0.01)
    # 3) COL: 날개 상자를 복도만 비우고 쪼갠다, 기단은 그대로(복도 바닥 = 0.9)
    ok = replace_col(C, (cx - WW / 2, cx + WW / 2, yf, cy + WD / 2, PZ, WH), [
        (cx - dw, cx + dw, yf + depth + 0.3, cy + WD / 2, PZ, WH),
        (cx - dw, cx + dw, yf, yf + depth + 0.3, PZ + dh + 0.35, WH),
    ])
    # 날개 양쪽은 둥근 끝(반지름 3.8)을 따른 볼록 COL, 기단(반지름 4.2)도 둥글게: 상자면 모서리 네 곳에 1 m 넘는
    # 빈 벽이 서고 기단 모서리 위에 떠서 걷는다
    wing = hw.rrect(WW, WD, 3.8, 5, cx, cy)
    for sgn in (-1, 1):
        half = [p for p in wing if sgn * (p[0] - cx) >= dw] + [(cx + sgn * dw, yf), (cx + sgn * dw, cy + WD / 2)]
        col_prism(C, half, PZ, WH, hint="g")
    if drop_col(C, (cx - WW / 2 - 1, cx + WW / 2 + 1, cy - WD / 2 - 1, cy + WD / 2 + 1, 0, PZ)):
        col_prism(C, hw.rrect(WW + 2, WD + 2, 4.2, 4, cx, cy), 0.0, PZ, hint="g")
    # 포르티코 기둥: 둥근 기둥 + 밑동(반지름 0.62, 0.5 m)
    PY0 = yf - 5.0
    for k in range(6):
        x = cx - (11 + 4) / 2 + k * (11 + 4) / 5
        if drop_col(C, (x - 0.48, x + 0.48, PY0 + 0.42, PY0 + 1.38, PZ, 8.2)):
            col_cyl(C, x, PY0 + 0.9, 0.62, PZ, PZ + 0.5, segs=16, hint="g")
            col_cyl(C, x, PY0 + 0.9, 0.48, PZ + 0.5, 8.2, segs=16, hint="g")
    # 계단: 단마다 상자(0.15 m) 대신 단 코를 잇는 경사 하나 (기단 COL PY0..yf가 위를 잇는다)
    sw = 11 / 2 + 2.5
    n_st = sum(drop_col(C, (cx - sw, cx + sw, PY0 - (6 - i) * 0.45, PY0 - (6 - i) * 0.45 + 0.45, 0, (i + 1) * 0.15))
               for i in range(6))
    if n_st:
        col_hull(C, [(cx + sx * sw, yy, zz) for sx in (-1, 1)
                     for yy, zz in ((PY0 - 3.15, 0.0), (PY0 - 0.45, PZ), (PY0, PZ), (PY0, 0.0))], hint="g")
    # 4) 복도 (안쪽 벽·천장·바닥, 등, 표지)
    y0, y1 = yf + 0.3, yf + depth
    C.box("stone_d", cx - dw - 0.15, cx - dw, y0 + 0.01, y1 + 0.3, PZ, PZ + dh + 0.35, kind="detail")
    C.box("stone_d", cx + dw, cx + dw + 0.15, y0 + 0.01, y1 + 0.3, PZ, PZ + dh + 0.35, kind="detail")
    C.box("white", cx - dw, cx + dw, y0 - 0.3, y1 + 0.3, PZ + dh + 0.2, PZ + dh + 0.35, kind="detail")
    C.box("pave_d", cx - dw, cx + dw, y0 - 0.3, y1 + 0.3, PZ - 0.05, PZ + 0.005, kind="detail")
    C.strip("exit_g" if lit else "glow_off", (cx, y0, PZ), (cx, y1 - 0.4, PZ), 0.12, lift=0.012)
    k = y0 + 0.8
    while k < y1:
        C.box("lamp_w" if lit else "lamp_off", cx - 0.5, cx + 0.5, k - 0.25, k + 0.25, PZ + dh + 0.18, PZ + dh + 0.2,
              kind="fine")
        for s in (-1, 1):
            C.rect("exit_g" if lit else "glow_off", (cx + s * dw, k, PZ + 0.25), (-s, 0, 0), 0.35, 0.08, lift=0.01)
        k += 1.6
    # 끝: 열린 방폭문 + 내려가는 계단 (어둠 속으로)
    C.box("dark", cx - dw, cx + dw, y1, y1 + 0.3, PZ, PZ + dh + 0.35, kind="detail")
    # 방폭문 틀: 기둥은 복도 벽 속에 10 cm만 박고(벽 바깥면 x=±(dw+0.15)와 같은 평면에 오지 않게) 복도 쪽으로
    # 25 cm 나온다. 밑면은 복도 바닥(PZ+0.005) 속 3 mm 위. 상인방은 두 기둥 사이에만 둔다(윗면이 기둥 윗면과 겹치지 않게).
    C.box("metal", cx - dw - 0.1, cx - dw + 0.25, y1 - 0.25, y1, PZ + 0.003, PZ + dh, kind="detail")
    C.box("metal", cx + dw - 0.25, cx + dw + 0.1, y1 - 0.25, y1, PZ + 0.003, PZ + dh, kind="detail")
    C.box("metal", cx - dw + 0.25, cx + dw - 0.25, y1 - 0.25, y1, PZ + dh - 0.25, PZ + dh, kind="detail")
    for i in range(5):
        zz = PZ - 0.15 * (i + 1)
        C.box("stone_d", cx - dw + 0.3, cx + dw - 0.3, y1 - 0.25 - 0.4 * (i + 1) + 0.0, y1 - 0.25 - 0.4 * i,
              zz - 0.02, zz + 0.0, kind="fine")
    C.rect("dark", (cx, y1 - 0.01, PZ + 0.9), (0, -1, 0), 2 * dw - 0.6, 1.6, lift=0.0)
    C.text("exit_g" if lit else "glow_off", "B1 ↓", 0.35, (cx, y1 - 0.02, PZ + 2.2), (0, -1, 0), lift=0.005)
    C.col(cx - dw, cx + dw, y1 - 0.02, y1 + 0.3, PZ, PZ + dh + 0.35)
    for sgn in (-1, 1):                  # 방폭문 틀 기둥 (복도 쪽으로 25 cm)
        C.col(*sorted((cx + sgn * (dw + 0.1), cx + sgn * (dw - 0.25))), y1 - 0.25, y1, PZ, PZ + dh)
    # 정문 문짝 (안으로 젖혀 열림)
    for s in (-1, 1):
        C.box("navy", cx + s * (dw - 0.06) - 0.06, cx + s * (dw - 0.06) + 0.06, y0, y0 + 1.25, PZ, PZ + dh - 0.05,
              kind="detail")
        C.col(cx + s * (dw - 0.06) - 0.06, cx + s * (dw - 0.06) + 0.06, y0, y0 + 1.25, PZ, PZ + dh - 0.05)
        C.rect("glass_d", (cx + s * (dw - 0.13), y0 + 0.62, PZ + 1.5), (-s, 0, 0), 0.8, 1.6, lift=0.0)
    # 대피소 표지 (문 위, 바깥) + 안쪽 벽 표지
    if shelter:
        sc = Vector((cx, yf - 0.29, PZ + dh + 0.95))
        C.plate("shelter", hw.rrect(5.2, 0.86, 0.18, 2), tuple(sc), (0, -1, 0), 0.06, kind="detail")
        C.text("white", "시청 지하 대피소", 0.3, tuple(sc + Vector((-0.35, -0.065, 0.13))), (0, -1, 0), lift=0.004)
        C.text("white", "SHELTER B1–B23", 0.17, tuple(sc + Vector((-0.35, -0.065, -0.22))), (0, -1, 0), lift=0.004)
        # 대피소 그림 기호 (집 지붕 + 아래 화살표)
        ic = sc + Vector((2.15, -0.065, 0.0))
        C.decal("white", [(-0.3, 0.02), (0.0, 0.3), (0.3, 0.02)], tuple(ic), (0, -1, 0), lift=0.005)
        C.decal("white", [(-0.07, 0.05), (0.07, 0.05), (0.07, -0.12), (0.16, -0.12), (0.0, -0.32), (-0.16, -0.12),
                          (-0.07, -0.12)], tuple(ic), (0, -1, 0), lift=0.005)
        for s in (-1, 1):
            wc = Vector((cx + s * dw, y0 + 2.6, PZ + 1.6))
            C.plate("shelter", hw.rrect(1.6, 0.5, 0.1, 2), tuple(wc), (-s, 0, 0), 0.03, kind="detail")
            C.text("white", "대피소 B1–B23 →", 0.12, tuple(wc + Vector((-s * 0.035, 0, 0.06))), (-s, 0, 0), lift=0.003)
            C.text("exit_g", "SHELTER", 0.08, tuple(wc + Vector((-s * 0.035, 0, -0.12))), (-s, 0, 0), lift=0.003)
    C.group(prev)
    print(f"[mdk] cityhall_doorway: cut faces {n1}/{n2}/{n3}, col split {ok}, step cols {n_st}")
    return {"door": (cx, yf, PZ), "inside": (cx, yf + 1.2, PZ), "end": (cx, y1 - 0.8, PZ), "dw": dw}


# ================================================================== 값싼 블록 (긴 가로의 근경·원경)

def street_block(C, x0, x1, y0, y1, *, floors=4, style="office", front="-y", shop=None, seed=0, h0=3.0, fh=2.7,
                 col=True, roof_units=1):
    """긴 가로용 값싼 근경 건물 (mk.building의 형태 언어를 앞면만으로 줄였다, 250~450 삼각형).
    모서리를 깎은 판(12점) 몸체 + 1층 띠 + 앞면 층 띠·띠창·멀리언 + 앞·옆 파라펫 + 옥상 판. front = '-y'|'+y'.
    반환: dict(top, front_y)."""
    rng = random.Random(seed)
    body, band, gl, gl_d, base = mk.STYLES[style]
    if shop:
        h0 = max(h0, 3.2)
    H = h0 + floors * fh
    cx = (x0 + x1) / 2
    w = x1 - x0
    fp = hw.rrect(w, y1 - y0, 0.9, 2, cx, (y0 + y1) / 2)
    C.prism(base, fp, 0.0, h0, kind="detail")
    C.prism(body, fp, h0, H, kind="main")
    if col:
        # 모서리를 깎은 몸체 그대로 (상자면 모서리마다 0.4 m 빈 벽)
        col_prism(C, fp, 0.0, H, hint="b")
    sgn = -1 if front == "-y" else 1
    yf = y0 if front == "-y" else y1
    N = Vector((0, sgn, 0))
    L = w - 1.8
    for i in range(floors):
        zf = h0 + i * fh
        C.box(band, x0 + 0.6, x1 - 0.6, *sorted((yf, yf + sgn * 0.1)), zf - 0.1, zf + 0.05, kind="detail")
        wc = Vector((cx, yf, zf + 1.37))
        # 띠창: 위 유리(0.7 m)와 아래 짙은 띠(0.5 m)를 나란히 둔다 (겹쳐 4 mm 띄우면 24비트 깊이로 45 m 밖에서 깜빡인다)
        C.rect(gl, tuple(wc + Vector((0, 0, 0.25))), tuple(N), L - 0.4, 0.7, lift=0.02)
        C.rect(gl_d, tuple(wc - Vector((0, 0, 0.35))), tuple(N), L - 0.4, 0.5, lift=0.02)
        n_m = max(1, int(L / 2.6))
        for k in range(1, n_m):
            u = -(L - 0.4) / 2 + k * (L - 0.4) / n_m
            C.rect("mullion" if style != "brick" else band, tuple(wc + Vector((u, 0, 0))), tuple(N), 0.12, 1.2,
                   lift=0.03)
    # 파라펫 (앞·양옆) + 옥상
    C.box(band, x0, x1, *sorted((yf, yf - sgn * 0.3)), H, H + 0.7, kind="detail")
    for xx in (x0, x1 - 0.3):
        C.box(band, xx, xx + 0.3, y0, y1, H, H + 0.7, kind="detail")
    C.box("roof", x0 + 0.3, x1 - 0.3, y0 + 0.3, y1 - 0.3, H, H + 0.04, kind="detail")
    if col:
        # 옥상(적이 선다): 파라펫·옥상 판 COL (몸이 파라펫을 지나 떨어지지 않게)
        C.col(x0, x1, *sorted((yf, yf - sgn * 0.3)), H, H + 0.7)
        for xx in (x0, x1 - 0.3):
            C.col(xx, xx + 0.3, y0, y1, H, H + 0.7)
        C.col(x0 + 0.3, x1 - 0.3, y0 + 0.3, y1 - 0.3, H, H + 0.04)
    for k in range(roof_units):
        ux = rng.uniform(x0 + 2, x1 - 3)
        uy = (y0 + y1) / 2 + rng.uniform(-2, 2)
        # 옥상 판(H..H+0.04) 위에 올린다: 밑면이 옥상 판 밑면과 같은 평면에 오지 않게
        C.box("steel", ux, ux + 1.4, uy, uy + 1.0, H + 0.04, H + 0.94, kind="detail")
        if col:
            C.col(ux, ux + 1.4, uy, uy + 1.0, H + 0.04, H + 0.94)
    # 1층: 상가 또는 문 + 낱창
    c0 = Vector((cx, yf, 0.0))
    R = Vector((1, 0, 0)) if sgn < 0 else Vector((-1, 0, 0))
    if shop:
        mk.storefront(C, c0, N, R, w - 1.8, 0.0, h0, shop, seed=seed)
    else:
        mk.entrance(C, c0 + R * (L * 0.25), N, R, canopy=False)
        C.rect(gl_d, tuple(c0 + Vector((0, 0, 1.55)) - R * (L * 0.15)), tuple(N), L * 0.4, 1.3, lift=0.02)
    return {"top": H, "front_y": yf}


def far_block(C, x0, x1, y0, y1, h, *, key="far", sides="-y", bands=None, seed=0, col=True):
    """원경 블록 (바닥 없는 상자 + 옥상 판 + 보이는 면의 창 띠 몇 줄, 30~60 삼각형)."""
    mk.lod_box(C, key, x0, x1, y0, y1, -0.3, h, kind="far")
    mk.lod_box(C, "far_d", x0 + 0.8, x1 - 0.8, y0 + 0.8, y1 - 0.8, h, h + 1.0, kind="far")
    if col:
        C.col(x0, x1, y0, y1, -0.3, h)
    nb = bands if bands is not None else max(2, int(h / 7))
    faces = {"-y": ((x0 + x1) / 2, y0, (0, -1, 0), x1 - x0), "+y": ((x0 + x1) / 2, y1, (0, 1, 0), x1 - x0),
             "-x": (x0, (y0 + y1) / 2, (-1, 0, 0), y1 - y0), "+x": (x1, (y0 + y1) / 2, (1, 0, 0), y1 - y0)}
    for sd in (sides[i:i + 2] for i in range(0, len(sides), 2)):
        fx, fy, N, L = faces[sd]
        for k in range(nb):
            zc = h * (k + 0.6) / (nb + 0.4)
            C.rect("glass_d" if k % 2 else "far_d", (fx, fy, zc), N, L * 0.88, min(2.2, h / nb * 0.45), lift=0.08)


def riot_barricade(C, x, y, *, yaw=0.0, z=0.0, w=1.8, h=1.0, col=True):
    """진압반 바리케이드 (mk.barricade와 같은 모양, 글자는 앞면만). 정면 -Y. COL은 회전 상자."""
    Mx = _yaw_m(x, y, z, yaw)
    N = (Mx.to_3x3() @ Vector((0, -1, 0))).normalized()
    R = (Mx.to_3x3() @ Vector((1, 0, 0))).normalized()
    c = Mx @ Vector((0, 0, h * 0.55))
    C.plate("violet", hw.rrect(w, h * 0.62, 0.12, 3), tuple(c), tuple(N), 0.06, kind="main", back=0.03)
    for sgn in (1, -1):
        C.strip("teal", c - R * (w / 2 - 0.08) + N * (0.031 * sgn) - Vector((0, 0, 0.12)),
                c + R * (w / 2 - 0.08) + N * (0.031 * sgn) - Vector((0, 0, 0.12)), 0.1, N * sgn, lift=0.004)
    C.text("white", "진압반 · MONATIUM SUPPRESSION UNIT", 0.075, c + N * 0.031 + Vector((0, 0, 0.08)), N, lift=0.004)
    for s_ in (-1, 1):
        foot = Mx @ Vector((s_ * (w / 2 - 0.15), 0, 0))
        C.beam("steel", foot + Vector((0, 0, 0.02)), foot + Vector((0, 0, h * 0.8)), 0.06, 0.06, kind="detail")
        C.beam("steel", foot - N * 0.3, foot + N * 0.3, 0.07, 0.05, kind="detail")
        C.beam("steel", foot + N * 0.28 + Vector((0, 0, 0.03)), foot + Vector((0, 0, h * 0.45)), 0.04, 0.04,
               kind="detail")
    if col:
        col_obox(C, (x, y, z + h / 2), (w, 0.35, h), yaw)


def avenue_ext(C, x0, x1, *, y=AV, lamp_pitch=24.0, col=True, median_gaps=()):
    """중앙로 연장 (downtown의 road와 같은 단면: 4차로 + 중앙 화단 2 m + 보도 3.2 m) + 성긴 가로등.
    median_gaps = [(xa, xb), ...]: 중앙 화단 연석 COL을 비울 구간 (차량 경로가 화단을 가로지르는 곳)."""
    rd = mk.road(C, "x", y, x0, x1, lanes=4, median=2.0, col=col)
    if col:
        # 중앙 화단 연석 (mk.road는 COL이 없어 0.2 m 묻혔다)
        for (a, b) in _minus([(x0, x1)], list(median_gaps)):
            col_median(C, a, b, y, rd["z_road"], 0.05)
    k = 0
    x = x1 - 6.0
    while x > x0 + 2:
        if k % 2 == 0:
            mk.lamp(C, x, rd["walk_hi"] - 0.6)
        else:
            mk.lamp(C, x, rd["walk_lo"] + 0.6)
        x -= lamp_pitch / 2
        k += 1
    return rd


# ================================================================== 도심 COL 보수 (mk.downtown, mk 파일은 고치지 않는다)

def downtown_cols(C, A, *, x_span=(-96, 96), highway=True):
    """mk.downtown()이 COL을 빠뜨렸거나 모양과 다르게 잡은 곳을 레벨 쪽에서 고친다 (M2·M3 공용).
    - 배경 판석(col=False, 윗면 0): 큰 바닥 COL(-0.32)에 발이 0.32 m 묻히고, 광장(0)으로 다시 오르는 턱이 자동 오르기
      (0.28)보다 높아 점프해야 했다 → 판석 COL
    - 판석이 아예 없는 남쪽 상가 앞 띠·골목·서쪽 끝을 판석으로 메운다
    - 중앙로 가운데 화단 연석(0.2 m), 코어 AI 탑 둥근 기단(r 7), 고속도로 표지 문형 기둥
    (건물 둥근 모서리, 문틀, 분수, 생울타리는 도시 키트가 맞춘다)"""
    rd = A["road"]
    yb1 = rd["walk_lo"] - 0.4
    yb0 = yb1 - 13
    for (x0, x1, y0, y1) in ((-96, -48, -11, 60), (42, 96, -11, 60), (-48, 42, 36, 60), (-96, 96, -60, yb0)):
        C.col(x0, x1, y0, y1, -0.25, 0.0)
    # 판석이 아예 없는 낮은 땅(-0.32): 남쪽 보도와 상가 앞면 사이 0.4 m 띠, 상가 사이 골목(2 m), 상가 줄 서쪽 끝.
    # 보도(0)에서 내려서면 0.32 m 턱을 다시 오르지 못한다 → 판석(+COL)으로 메운다 (레벨의 '빈 땅 메우기'와 같은 방식)
    x, i, row = -80.0, 0, []
    while x < x_span[1] - 34:
        w = mk.SOUTH_ROW[i % len(mk.SOUTH_ROW)][0]
        row.append((x, x + w))
        x += w + (2.0 if i % 3 == 2 else 0.4)
        i += 1
    mk.paving(C, x_span[0], row[0][0], yb0, rd["walk_lo"], grout=None, tile=1.6)
    mk.paving(C, row[0][0], x_span[1] - 30, yb1, rd["walk_lo"], grout=None, tile=1.6)
    for (a, b), (c, _) in zip(row[:-1], row[1:]):
        if c - b > 1.0:
            mk.paving(C, b, c, yb0, yb1, grout=None, tile=1.6)
    col_median(C, x_span[0], x_span[1] - 30 if highway else x_span[1], AV, rd["z_road"], 0.05)
    cx, cy = A["core"].x, A["core"].y
    if drop_col(C, (cx - 5.95, cx + 5.95, cy - 5.95, cy + 5.95, 0, 6.2)):
        col_cyl(C, cx, cy, 7.0, 0.0, 6.2, segs=32, hint="f")
    if highway:
        # 표지 문형 기둥(mk.gantry, 중심선 ±7 m, 반지름 0.18)은 연석(±6.6) 너머 보도 위에 선다: COL은 보도 윗면(z_road + 0.15 = 0)부터.
        # 보이는 기둥은 차도 높이(-0.15)부터 세워 밑동이 보도 판 속에 묻힌다
        for sg in (-1, 1):
            col_cyl(C, x_span[1] - 34, AV + sg * 7.0, 0.18, rd["z_road"] + 0.15, 6.4, segs=10, hint="f")


def bounds(C, boxes, *, z0=-1.0, z1=6.5):
    """맵 경계 COL (COL_bounds_nn). boxes = [(x0, x1, y0, y1), ...]. 높이는 궤도 점검 통로(8.15) 아래까지."""
    n = sum(1 for c in C.cols if c[0].startswith("COL_bounds_"))
    for (x0, x1, y0, y1) in boxes:
        n += 1
        C.col(x0, x1, y0, y1, z0, z1, name=f"COL_bounds_{n:02d}")


def downtown_bounds(C, A, *, west=True):
    """도심 판석 끝(x ±96, y ±60)을 맵 경계로 닫는다. 동쪽은 고속도로 진입로(x 66~, 판석 없는 낮은 땅)를 밖에 둔다.
    west=False면 서쪽 x=-96 벽을 두지 않는다 (M2: 중앙로가 서쪽으로 이어진다, 레벨이 따로 닫는다)."""
    rd = A["road"]
    yb0 = rd["walk_lo"] - 0.4 - 13
    bx = [(-96.3, 96.3, 60.0, 60.3), (-96.3, 96.3, -60.3, -60.0), (96.0, 96.3, rd["walk_hi"], 60.3),
           (96.0, 96.3, -60.3, yb0 + 0.3)]
    # 진입로 쪽: 북쪽 판석 끝(y=walk_hi), 중앙로 끝(x 66), 남쪽 상가 끝에서 남쪽 판석 끝(y=yb0)
    xr = 66.0
    bx += [(xr, 96.3, rd["walk_hi"] - 0.3, rd["walk_hi"]), (xr, xr + 0.3, rd["walk_lo"] - 0.6, rd["walk_hi"]),
           (xr, 96.3, yb0, yb0 + 0.3)]
    if west:
        bx.append((-96.3, -96.0, -60.3, 60.3))
    bounds(C, bx)


# ================================================================== 원경

def far_ring(C, cx, cy, *, radius=280.0, n=28, seed=0, skip=None, h=(30, 70), rx=1.0):
    """안개 속 원경 고층 고리 (far_block). skip(x, y)이 참이면 그 자리를 비운다."""
    rng = random.Random(seed)
    for i in range(n):
        a = 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / n
        rr = radius * rng.uniform(0.9, 1.12)
        sx, sy = cx + math.cos(a) * rr * rx, cy + math.sin(a) * rr
        if skip and skip(sx, sy):
            continue
        w = rng.uniform(16, 28)
        d = rng.uniform(14, 24)
        # 광장 쪽을 보는 면에만 창 띠
        side = ("-x" if math.cos(a) > 0 else "+x") if abs(math.cos(a)) > abs(math.sin(a)) else \
            ("-y" if math.sin(a) > 0 else "+y")
        far_block(C, sx - w / 2, sx + w / 2, sy - d / 2, sy + d / 2, rng.uniform(*h), key=("far", "glass_t")[i % 2],
                  sides=side, seed=seed + i)


def horizon_smoke(C, spots, *, drift=(-0.3, 0.1), seed=0):
    """지평선 연기 기둥들. spots = [(x, y, h, r, dark), ...]."""
    for i, (x, y, h, r, dark) in enumerate(spots):
        smoke_plume(C, x, y, z=0.0, h=h, r=r, drift=drift, seed=seed + i * 7, segs=8, rings=5, dark=dark)


# ================================================================== 마커 도우미

def hold_marks(C, section, center, spots, *, z=0.0, face=None, yaw=None):
    """MARK_hold_<section> + MARK_hold_<section>_<who> (spots = {who: (x, y[, z])})."""
    C.marker(f"MARK_hold_{section}", (center[0], center[1], center[2] if len(center) > 2 else z), face=face, yaw=yaw)
    out = {}
    for who, p in spots.items():
        pz = p[2] if len(p) > 2 else z
        C.marker(f"MARK_hold_{section}_{who}", (p[0], p[1], pz), face=face, yaw=yaw)
        out[who] = (p[0], p[1], pz)
    return out


def trig(C, tid, x0, x1, y0, y1, z0, z1, **props):
    """TRIG_<tid> 상자 (보이지 않는 트리거). 발이 확실히 들어가게 높게 잡는다."""
    o = mk._box_obj(f"TRIG_{tid}", x0, x1, y0, y1, z0, z1)
    for k, v in props.items():
        o[k] = v
    C.add_node(o)
    return o


WEAPON = {"rifleman_a": "r41_carbine", "rifleman_b": "r41_carbine", "rifleman_c": "r41_dmr",
          "assault": "r41_suppressor", "officer": "r41_sidearm", "riot": "r41_sidearm", "hq_guard": "r41_carbine"}


def enemy(C, eid, loc, kind, group, behavior, *, face=None, yaw=None, path=None, **extra):
    """ENEMY_<eid> (spawn=manual). -Y가 쏠 방향."""
    p = {"kind": kind, "group": group, "behavior": behavior, "spawn": "manual"}
    if kind in WEAPON:
        p["weapon"] = WEAPON[kind]
        p["drop"] = WEAPON[kind]
    if path:
        p["path"] = path
    p.update(extra)
    C.marker(f"ENEMY_{eid}", loc, face=face, yaw=yaw, props=p)


def waypoints(C, prefix, pts):
    for i, p in enumerate(pts, start=1):
        C.marker(f"WP_{prefix}_{i:02d}", tuple(p))
