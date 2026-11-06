"""모나티엄 폐허 키트 (monatium_ruins_kit).

2막 「암흑」(둠스데이 정전 이후)의 모나티엄을 도시 키트(monatium_city_kit) 위에 조립한다.
도시 키트는 고치지 않는다. 같은 City 조립기와 프리미티브를 쓰고, 폐허·정전 변형만 이 파일에 더한다.
문서: docs/art/monatium-ruins.md, 노드 규칙: docs/LEVELS.md, 전투 마커: docs/COMBAT.md

사용:
    import monatium_city_kit as mk, monatium_ruins_kit as rk
    C = mk.City("m4_ruins")
    rk.ruined_building(C, 24, 46, 15, 32, floors=4, seed=3)
    rk.rubble(C, 28, 8, r=1.3, h=0.85)
    rk.trig(C, "alley", 19, 23, -1, 14)
    rk.blackout(C)            # finish 직전: 시안 발광·켜진 등을 꺼진 색으로
    C.finish("levels/m4_ruins.glb", root_props={...})

원작: 둠스데이 프로토콜로 모나티엄의 인프라와 데이터가 파괴된다(나무위키 「엘리아스 침공전」).
오리지널: 전 도시 정전, 드론 추락, 차량 정지(1막 종료 시네마틱). 키트는 그 직후의 밤 거리다.
"""
from __future__ import annotations

import math
import random

import bmesh
from mathutils import Matrix, Vector

import home_weapons as hw
import monatium_city_kit as mk

# ================================================================== palette (도시 키트 팔레트에 더한다)
mk.PAL.update({
    "rubble": "#a39d97",     # 콘크리트 잔해 (밝은 면)
    "rubble_d": "#77716f",   # 잔해 (그늘·속살)
    "rebar": "#6b4f45",      # 녹슨 철근
    "burnt": "#3d373b",      # 불탄 차체
    "char": "#262229",       # 숯·검은 구멍 (창 구멍, 갈라진 틈)
    "ash": "#8e8a88",        # 재 덮인 바닥
    "tarp_o": "#5d6a4c",     # 올리브 방수포 (R41 노숙 천막)
    "barrel": "#5a5560",     # 드럼통
    "barrel_r": "#8a4b3b",   # 녹슨 드럼통
})
mk.GLOW.update({
    "ember": "#ff8a3a",      # 잉걸불
    "chem": "#ff4fd8",       # R41 화학 발광봉 (마젠타. 정전에도 켜지는 화학 조명)
})

# 정전 패스: 켜진 발광 키 → 꺼진 키
BLACKOUT = {
    "glow": "glow_off",
    "lamp": "lamp_off",
    "win_lit": "char",
    "cyan_hot": "glow_off",
    "magenta": "char",       # R41 기계 발광도 꺼졌다 (차원문·장비)
    "violet_glow": "char",
    "screen": "char",
}


def blackout(C):
    """finish 직전에 부른다. 도시 키트가 만든 시안 네트워크·켜진 등·화면을 꺼진 색으로 바꾼다."""
    for (g, key, kind) in list(C.acc.keys()):
        if key not in BLACKOUT:
            continue
        nk = BLACKOUT[key]
        nkind = "fine" if mk.is_glow(nk) else kind
        src = C.acc.pop((g, key, kind))
        dst = C.acc.get((g, nk, nkind))
        if dst is None:
            C.acc[(g, nk, nkind)] = src
        else:
            mk._copy_into(dst, src)
            src.free()
    C.objs[:] = [(g, BLACKOUT.get(k, k), ("fine" if mk.is_glow(BLACKOUT.get(k, k)) else kd), o)
                 for (g, k, kd, o) in C.objs]
    for _g, o in C.specials:
        for s in o.material_slots:
            if s.material and s.material.name.startswith("UNLIT_mc_"):
                k = s.material.name[len("UNLIT_mc_"):]
                if k in BLACKOUT:
                    s.material = mk.M(BLACKOUT[k])


# ================================================================== 이동 충돌체 (보이는 모양 그대로의 볼록 COL_)
# 잔해 덩어리·기울어진 판·누운 기둥은 축 정렬 상자로 덮으면 한쪽은 몸이 파고들고 다른 쪽은 보이지 않는 벽이 된다.
# 도시 키트 빌더로 같은 꼭짓점을 만들어 볼록 껍질 COL_(C.ccol)로 넣는다. 로더가 볼록 껍질 충돌체로 만든다.

def _verts(build):
    b = bmesh.new()
    build(b)
    out = [tuple(v.co) for v in b.verts]
    b.free()
    return out


def _rbox_matrix(center, rot):
    """C.rbox와 같은 행렬 (rot = XYZ 도)."""
    return (Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(rot[2]), 4, "Z")
            @ Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))


def _beam_matrix(p0, p1, up=(0, 0, 1)):
    """C.beam과 같은 행렬과 길이."""
    P0, P1 = Vector(p0), Vector(p1)
    d = P1 - P0
    L = d.length
    Y = d.normalized()
    U = Vector(up)
    if abs(Y.dot(U)) > 0.99:
        U = Vector((1, 0, 0))
    X = Y.cross(U).normalized()
    Z = X.cross(Y).normalized()
    Mx = Matrix((X, Y, Z)).transposed().to_4x4()
    Mx.translation = (P0 + P1) / 2
    return Mx, L


def col_blob(C, center, radius, scale=(1, 1, 1), *, segs=10, rings=6, rot_z=0.0):
    """C.blob과 같은 덩어리의 볼록 COL_."""
    C.ccol(_verts(lambda b: mk._bm_blob(b, center, radius, scale, segs=segs, rings=rings, rot_z=rot_z)))


def col_rbox(C, center, size, rot=(0, 0, 0)):
    """C.rbox와 같은 돌린 상자의 COL_ (기울어진 판)."""
    Mx = _rbox_matrix(center, rot)
    sx, sy, sz = (s / 2 for s in size)
    C.ccol([tuple(Mx @ Vector((x, y, z))) for x in (-sx, sx) for y in (-sy, sy) for z in (-sz, sz)])


def col_beam(C, p0, p1, w, h, *, up=(0, 0, 1)):
    """C.beam과 같은 보의 COL_."""
    Mx, L = _beam_matrix(p0, p1, up)
    if L < 1e-6:
        return
    C.ccol([tuple(Mx @ Vector((x, y, z))) for x in (-w / 2, w / 2) for y in (-L / 2, L / 2) for z in (-h / 2, h / 2)])


def col_cyl(C, p0, p1, r, *, segs=12, r2=None):
    """C.cyl과 같은 원기둥(원뿔대)의 COL_."""
    if (Vector(p1) - Vector(p0)).length < 1e-6:
        return
    C.ccol(_verts(lambda b: mk._bm_cyl(b, p0, p1, r, segs=segs, r2=r2, smooth=False)))


def col_prism(C, pts, z0, z1):
    """xy 볼록 다각형을 z0..z1로 세운 COL_ (둥근 모서리 기단 등)."""
    C.ccol([(x, y, z) for (x, y) in pts for z in (z0, z1)])


def swap_col(C, box, tol=0.02):
    """키트가 넣은 축 정렬 COL 상자(x0, x1, y0, y1, z0, z1)를 뺀다 (더 정확한 COL로 바꿀 때). 뺐으면 True."""
    for i, c in enumerate(C.cols):
        if all(abs(a - b) < tol for a, b in zip(c[1:], box)):
            del C.cols[i]
            return True
    return False


def fountain_col(C, x, y, *, r=4.0, z=0.0):
    """도시 키트 분수(mk.fountain)의 네모 COL(반지름 0.8배 상자: 둥근 수반 테 0.8 m를 비우고 대각선 모서리는 0.5 m 넘침)을
    수반 그대로의 둥근 COL로 바꾼다. 테 위 고리(바깥 r+0.03, 위 0.76 m)까지 덮는다(점프로 물 위에 올라서지 않게)."""
    swap_col(C, (x - r * 0.8, x + r * 0.8, y - r * 0.8, y + r * 0.8, z, z + 0.55))
    ro, ri = r + 0.03, r - 0.17
    pts = []
    for i in range(32):
        a = math.tau * i / 32
        ca, sa = math.cos(a), math.sin(a)
        pts += [(x + ca * ro, y + sa * ro, z), (x + ca * ro, y + sa * ro, z + 0.56), (x + ca * ri, y + sa * ri, z + 0.76)]
    C.ccol(pts)


# ================================================================== 트리거·문 (City에는 없는 이름 있는 박스)

def trig(C, tid, x0, x1, y0, y1, z0=-0.5, z1=3.0, **props):
    """TRIG_<tid>: 축 정렬 박스 트리거 (렌더하지 않음, 충돌 없음)."""
    o = mk._box_obj(f"TRIG_{tid}", min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1)
    o["collider"] = 0
    o["noOutline"] = 1
    for k, v in props.items():
        o[k] = v
    C.add_node(o)
    return o


def door(C, did, x0, x1, y0, y1, z0, z1, *, key="metal", move="0,2,0", **props):
    """DOOR_<did>: 미션이 여닫는 문 (키네마틱). move는 three.js 축 (x, 위, -Blender y)."""
    def build(b):
        mk._bm_box(b, x0, x1, y0, y1, z0, z1)
    p = {"move": move}
    p.update(props)
    return C.special(f"DOOR_{did}", build, key, p)


def named_box(C, name, key, x0, x1, y0, y1, z0, z1, **props):
    """이름 있는 박스 메시 (상태 노드, 덮개 등). 충돌 없음."""
    def build(b):
        mk._bm_box(b, x0, x1, y0, y1, z0, z1)
    return C.special(name, build, key, props)


# ================================================================== 잔해

def rubble(C, x, y, *, r=1.2, h=0.85, seed=0, z=0.0, col=True, rebar=True, keys=("rubble", "rubble_d"), sq=1.0):
    """잔해 더미 (엄폐물). 덩어리 몇 개 + 판 조각 + 철근. COL은 덩어리·판마다 같은 모양의 볼록 껍질(철근은 없음).
    예전 COL(가운데 78% 상자)은 덩어리가 빈 쪽에서는 보이지 않는 벽, 덩어리가 나온 쪽에서는 몸이 파고드는 자리였다."""
    rng = random.Random(seed * 7919 + int(x * 13) + int(y * 7))
    n = max(3, int(r * 3.2))
    for i in range(n):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(0, r * 0.6)
        rr = rng.uniform(0.35, 0.6) * r
        hz = h * rng.uniform(0.6, 1.0)
        c = (x + math.cos(a) * d, y + math.sin(a) * d * sq, z + hz * 0.35)
        sc = (1.0, sq * rng.uniform(0.8, 1.1), hz / max(rr, 0.01) * 0.75)
        rz = rng.uniform(0, 3)
        C.blob(keys[i % 2], c, rr, sc, segs=7, rings=4, rot_z=rz)
        if col:
            col_blob(C, c, rr, sc, segs=7, rings=4, rot_z=rz)
    # 깨진 판 조각 (기울어진 슬래브)
    for i in range(max(1, n // 3)):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(0.1, r * 0.7)
        c = (x + math.cos(a) * d, y + math.sin(a) * d * sq, z + h * 0.45)
        sz = (rng.uniform(0.6, 1.3) * r, rng.uniform(0.4, 0.8) * r, 0.14)
        rot = (rng.uniform(-25, 25), rng.uniform(-30, 30), rng.uniform(0, 180))
        C.rbox("concrete" if i % 2 else "rubble", c, sz, rot)
        if col:
            col_rbox(C, c, sz, rot)
    if rebar:
        for i in range(rng.randint(2, 4)):
            a = rng.uniform(0, math.tau)
            p0 = Vector((x + math.cos(a) * r * 0.3, y + math.sin(a) * r * 0.3 * sq, z + h * 0.5))
            p1 = p0 + Vector((math.cos(a) * rng.uniform(0.4, 0.9), math.sin(a) * rng.uniform(0.4, 0.9),
                              rng.uniform(0.3, 0.9)))
            C.beam("rebar", p0, p1, 0.035, 0.035, kind="detail")


def rubble_wall(C, x0, x1, y0, y1, *, h=2.4, seed=0, z=0.0):
    """통행을 막는 큰 잔해 더미 (맵 가장자리). COL은 덩어리·판마다 같은 모양의 볼록 껍질이다.
    덩어리는 x0..x1 × y0..y1보다 약 1 m씩 넓게 퍼진다(예전 COL 상자는 그 1 m를 비워 몸이 잔해 속으로 들어갔다).
    덩어리끼리 겹친 안장도 약 0.93h라 넘어갈 수 없다."""
    rng = random.Random(seed)
    lx, ly = x1 - x0, y1 - y0
    n = max(2, int(max(lx, ly) / 2.2))
    for i in range(n):
        t = (i + 0.5) / n
        cx = x0 + lx * (t if lx >= ly else 0.5)
        cy = y0 + ly * (t if ly > lx else 0.5)
        rr = min(lx, ly) * 0.5 + 0.9
        rz = rng.uniform(0, 3)
        C.blob("rubble" if i % 2 else "rubble_d", (cx, cy, z + h * 0.35), rr, (1.1, 1.1, h / rr * 0.7),
               segs=8, rings=4, rot_z=rz)
        col_blob(C, (cx, cy, z + h * 0.35), rr, (1.1, 1.1, h / rr * 0.7), segs=8, rings=4, rot_z=rz)
        if i % 2 == 0:
            c = (cx + rng.uniform(-0.5, 0.5), cy + rng.uniform(-0.5, 0.5), z + h * 0.75)
            sz = (rng.uniform(1.4, 2.4), rng.uniform(0.6, 1.0), 0.2)
            rot = (rng.uniform(-30, 30), rng.uniform(-35, 35), rng.uniform(0, 180))
            C.rbox("concrete_d", c, sz, rot)
            col_rbox(C, c, sz, rot)
            C.beam("rebar", (cx, cy, z + h * 0.6), (cx + rng.uniform(-1, 1), cy + rng.uniform(-1, 1), z + h + 0.6),
                   0.04, 0.04, kind="detail")


def fallen_column(C, p0, p1, *, r=0.48, key="stone", z=0.0, col=True):
    """쓰러진 둥근 기둥 (포르티코). 바닥에 누운 원기둥 + 금색 띠."""
    a = Vector((p0[0], p0[1], z + r))
    b = Vector((p1[0], p1[1], z + r))
    C.cyl(key, tuple(a), tuple(b), r, segs=14)
    d = (b - a).normalized()
    C.cyl("gold", tuple(b - d * 0.5), tuple(b - d * 0.3), r * 1.12, segs=14, kind="detail")
    C.cyl("stone_d", tuple(a - d * 0.01), tuple(a + d * 0.5), r * 1.25, segs=14, kind="detail")  # 받침 끝면 1 cm 나옴
    if col:
        # 누운 원기둥 그대로 (예전 축 정렬 상자는 비스듬히 누운 기둥 둘레를 몇 m씩 막았다)
        col_cyl(C, tuple(a), tuple(b), r, segs=14)
        col_cyl(C, tuple(b - d * 0.5), tuple(b - d * 0.3), r * 1.12, segs=14)
        col_cyl(C, tuple(a - d * 0.01), tuple(a + d * 0.5), r * 1.25, segs=14)


def fallen_lamp(C, x, y, yaw, *, h=3.6, z=0.0):
    """쓰러진 가로등 (꺼짐). COL은 선 밑동만: 누운 기둥(지름 12 cm, 높이 0.2~0.45 m)과 바닥에 누운 등 머리(0.4 m)는
    COL을 주면 발이 걸리는 턱이 되고 둘레 병사 길에 좁은 틈을 만든다."""
    a = math.radians(yaw)
    d = Vector((math.cos(a), math.sin(a), 0))
    base = Vector((x, y, z + 0.1))
    C.cyl("dark", (x, y, z), (x, y, z + 0.35), 0.16, r2=0.12, segs=8, kind="detail")
    col_cyl(C, (x, y, z), (x, y, z + 0.35), 0.16, r2=0.12, segs=8)
    tip = base + d * h
    C.cyl("dark", tuple(base + Vector((0, 0, 0.3))), tuple(tip + Vector((0, 0, 0.08))), 0.06, segs=6, kind="detail")
    C.cyl("lamp_off", tuple(tip), tuple(tip + d * 0.4), 0.2, r2=0.17, segs=8, kind="detail")


def fallen_tree(C, x, y, yaw, *, h=4.6, seed=0):
    a = math.radians(yaw)
    d = Vector((math.cos(a), math.sin(a), 0))
    p = Vector((x, y, 0.25))
    C.cyl("trunk", tuple(p), tuple(p + d * h * 0.7), 0.16, r2=0.1, segs=7)
    rng = random.Random(seed)
    for k in range(3):
        c = p + d * h * (0.55 + 0.15 * k) + Vector((rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 0.5))
        C.blob("leaf_d" if k % 2 else "leaf", tuple(c), 1.0, (1, 1, 0.7), segs=7, rings=4)
    C.cyl("soil", (x, y, 0.0), (x, y, 0.35), 0.45, segs=8, kind="detail")


def burnt_car(C, x, y, *, yaw=0.0, z=0.0, seed=0, col=True):
    """불탄 엘프 승용차 껍데기 (엄폐물, 높이 약 1.1 m). yaw = 차 앞이 향하는 각(도, +X 기준)."""
    rng = random.Random(seed)
    L, W = 3.4, 1.6
    a = math.radians(yaw)
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(a, 4, "Z")

    def at(px, py, pz):
        return tuple(Mx @ Vector((px, py, pz)))
    C.rbox("burnt", at(0, 0, 0.55), (L, W, 0.55), (0, 0, yaw))
    C.rbox("char", at(-0.15, 0, 0.98), (L * 0.55, W * 0.92, 0.36), (0, 0, yaw))
    C.rbox("rubble_d", at(-0.15, 0, 1.18), (L * 0.5, W * 0.85, 0.05), (rng.uniform(-6, 6), 0, yaw))
    for sx in (-1, 1):
        for sy in (-1, 1):
            C.cyl("char", at(sx * L * 0.32, sy * (W / 2 - 0.05), 0.24), at(sx * L * 0.32, sy * (W / 2 + 0.05), 0.24),
                  0.24, segs=10, kind="detail")
    C.rbox("rubble", at(L * 0.45, 0, 0.45), (0.25, W * 0.9, 0.3), (0, 0, yaw), kind="detail")
    if col:
        # 차체(바퀴 포함)와 좁은 객실을 차와 같이 돌린 상자로 (축 정렬 상자는 비스듬한 차 둘레를 1 m 가까이 막았다)
        C.lcol(x, y, z, yaw, -L / 2, L / 2, -W / 2 - 0.05, W / 2 + 0.05, 0, 0.83)
        C.lcol(x, y, z, yaw, -0.15 - L * 0.275, -0.15 + L * 0.275, -W * 0.46, W * 0.46, 0.83, 1.2)


def fire_barrel(C, fid, x, y, *, z=0.0, rust=False, col=True):
    """불 피운 드럼통 + FX_fire_<fid> (미션이 깜빡이는 점광원·불꽃을 붙인다)."""
    key = "barrel_r" if rust else "barrel"
    C.cyl(key, (x, y, z), (x, y, z + 0.82), 0.3, segs=12)
    C.cyl("char", (x, y, z + 0.82), (x, y, z + 0.86), 0.31, segs=12, kind="detail", cap=False)
    for k, zz in enumerate((0.2, 0.62)):
        C.cyl("dark", (x, y, z + zz), (x, y, z + zz + 0.04), 0.315, segs=12, kind="detail", cap=False)
    C.blob("ember", (x, y, z + 0.84), 0.24, (1, 1, 0.35), segs=8, rings=3)
    C.blob("fire", (x, y, z + 0.95), 0.18, (1, 1, 1.4), segs=7, rings=3)
    C.blob("fire_c", (x, y, z + 0.92), 0.1, (1, 1, 1.5), segs=6, rings=3)
    C.fx(f"fire_{fid}", (x, y, z + 1.0), strength=0.8)
    if col:
        col_cyl(C, (x, y, z), (x, y, z + 0.86), 0.315, segs=12)


def campfire(C, fid, x, y, *, z=0.0):
    """바닥 모닥불 (돌 테 + 장작 + 불꽃) + FX_fire_<fid>."""
    for i in range(8):
        a = i * math.tau / 8
        C.blob("rock", (x + math.cos(a) * 0.45, y + math.sin(a) * 0.45, z + 0.08), 0.12, (1, 1, 0.7), segs=6, rings=3)
    for i in range(3):
        a = i * math.tau / 3
        C.beam("trunk", (x + math.cos(a) * 0.35, y + math.sin(a) * 0.35, z + 0.06), (x, y, z + 0.25), 0.08, 0.08,
               kind="detail")
    C.blob("ember", (x, y, z + 0.08), 0.3, (1, 1, 0.3), segs=8, rings=3)
    C.blob("fire", (x, y, z + 0.3), 0.2, (1, 1, 1.6), segs=7, rings=3)
    C.fx(f"fire_{fid}", (x, y, z + 0.45), strength=0.6)


def chemlight(C, x, y, yaw=0.0, *, z=0.0):
    """R41 화학 발광봉 (바닥에 떨어진 것). 정전에도 빛나는 마젠타 막대."""
    a = math.radians(yaw)
    d = Vector((math.cos(a), math.sin(a), 0)) * 0.08
    C.cyl("chem", (x - d.x, y - d.y, z + 0.02), (x + d.x, y + d.y, z + 0.02), 0.018, segs=6)


def soot(C, center, normal, w, h, *, seed=0, up=(0, 0, 1)):
    """벽 그을음 (위로 번지는 검은 얼룩)."""
    rng = random.Random(seed)
    pts = []
    n = 14
    for i in range(n):
        t = i / n * math.tau
        rr = rng.uniform(0.75, 1.1)
        u = math.cos(t) * w / 2 * rr
        v = math.sin(t) * h / 2 * rr + (h * 0.15 if math.sin(t) > 0 else 0)
        pts.append((u, v))
    C.decal("soot", pts, center, normal, up=up, lift=0.03)


def crack(C, p0, p1, *, w=0.12, z=0.0, seed=0):
    """바닥 갈라짐 (꺾인 검은 띠)."""
    rng = random.Random(seed)
    a, b = Vector((p0[0], p0[1], z)), Vector((p1[0], p1[1], z))
    n = 5
    prev = a
    for i in range(1, n + 1):
        t = i / n
        q = a.lerp(b, t)
        if i < n:
            side = Vector((-(b - a).y, (b - a).x, 0)).normalized()
            q += side * rng.uniform(-0.6, 0.6)
        C.strip("char", tuple(prev), tuple(q), w * rng.uniform(0.6, 1.2), lift=0.02)
        prev = q


# ================================================================== 건물

def ruined_building(C, x0, x1, y0, y1, *, floors=4, style="office", seed=0, front="-y", broken=0.6, sides="-y+y-x+x",
                    shop=None, dark_windows=True, fh=2.7, rubble_front=True, z0=0.0, h0=None, r=1.0, door=True):
    """폐허가 된 도시 블록. 도시 키트 building 위에 들쭉날쭉한 윗면, 검은 창 구멍, 그을음, 잔해를 얹는다.
    COL은 도시 키트가 만든 전체 박스(원래 높이) 그대로다(통짜 블록이라 안으로는 못 들어간다).
    z0·h0: 위층만 얹을 때(아래층은 따로 지은 가게 안: shop_interior) 밑면 높이와 첫 띠 높이. r: 모서리 반지름, door: 정면 문."""
    rng = random.Random(seed)
    info = mk.building(C, x0, x1, y0, y1, floors=floors, style=style, front=front, sides=sides, seed=seed,
                       shop=shop, roof=False, fh=fh, cctv=False, z=z0, h0=h0, r=r, door=door)
    # 창 구멍·그을음 높이의 기준 (예전과 같게: 가게가 있어도 3.0)
    base = z0 + (h0 if h0 is not None else 3.0)
    top = info["top"] if isinstance(info, dict) and "top" in info else (base + floors * fh)
    # 도시 키트 건물 COL은 바닥 사각형 상자인데 몸통은 모서리가 둥글다(반지름 1 m): 모서리마다 0.4 m 보이지 않는 벽.
    # 같은 둥근 사각형의 볼록 COL로 바꾼다
    if swap_col(C, (x0, x1, y0, y1, z0, top)):
        rr = min(1.0, (x1 - x0) / 2 - 0.1, (y1 - y0) / 2 - 0.1)
        col_prism(C, hw.rrect(x1 - x0, y1 - y0, rr, 3, (x0 + x1) / 2, (y0 + y1) / 2), 0.0, top)
        # 둥근 모서리 밖 쐐기에는 포장이 없어 받침 땅(0.2 m 아래)이 드러난다: 발이 빠지지 않게 바닥 높이까지 받친다
        C.col(x0, x1, y0, y1, z0 - 0.6, z0)
    # 들쭉날쭉한 윗면: 남은 벽 조각과 꺾인 슬래브
    nx = max(2, int((x1 - x0) / 3.5))
    ny = max(2, int((y1 - y0) / 3.5))
    body = {"office": "concrete", "apartment": "warm", "brick": "brick", "glass": "glass_t"}.get(style, "concrete")
    for i in range(nx):
        if rng.random() < broken:
            xa = x0 + (x1 - x0) * i / nx
            xb = x0 + (x1 - x0) * (i + 1) / nx
            hh = rng.uniform(0.6, 2.2)
            for yy in (y0, y1 - 0.35):
                C.box(body, xa + 0.1, xb - 0.1, yy, yy + 0.35, top, top + hh * rng.uniform(0.5, 1.0))
    for j in range(ny):
        if rng.random() < broken:
            ya = y0 + (y1 - y0) * j / ny
            yb = y0 + (y1 - y0) * (j + 1) / ny
            hh = rng.uniform(0.6, 2.0)
            for xx in (x0, x1 - 0.35):
                C.box(body, xx, xx + 0.35, ya + 0.1, yb - 0.1, top, top + hh * rng.uniform(0.5, 1.0))
    for k in range(int(2 + broken * 3)):
        cx = rng.uniform(x0 + 1, x1 - 1)
        cy = rng.uniform(y0 + 1, y1 - 1)
        C.rbox("concrete_d", (cx, cy, top + 0.4), (rng.uniform(2, 4), rng.uniform(1.5, 3), 0.25),
               (rng.uniform(-18, 18), rng.uniform(-18, 18), rng.uniform(0, 180)))
        C.beam("rebar", (cx, cy, top + 0.3), (cx + rng.uniform(-1, 1), cy + rng.uniform(-1, 1), top + rng.uniform(1, 2.2)),
               0.05, 0.05, kind="detail")
    # 창 구멍과 그을음 (정면)
    N = mk.FRONT[front]
    if front in ("-y", "+y"):
        fy = y0 if front == "-y" else y1
        span = (x0 + 1.0, x1 - 1.0)
        R = Vector((1, 0, 0))

        def face(u, z):
            return Vector((u, fy, z))
    else:
        fx = x0 if front == "-x" else x1
        span = (y0 + 1.0, y1 - 1.0)
        R = Vector((0, 1, 0))

        def face(u, z):
            return Vector((fx, u, z))
    if dark_windows:
        for f in range(floors):
            z = base + f * fh + fh * 0.55
            n = max(1, int((span[1] - span[0]) / 2.4))
            for k in range(n):
                if rng.random() < 0.45 * broken + 0.15:
                    u = span[0] + (k + 0.5) * (span[1] - span[0]) / n
                    C.rect("char", tuple(face(u, z) + N * 0.04), tuple(N), rng.uniform(1.0, 1.8), rng.uniform(0.8, 1.3),
                           lift=0.03)
    for k in range(int(1 + broken * 3)):
        u = rng.uniform(*span)
        z = rng.uniform(base + 0.5, max(base + 1.0, top - 1.5))
        soot(C, tuple(face(u, z) + N * 0.03), tuple(N), rng.uniform(1.5, 3.5), rng.uniform(2.0, 4.0), seed=seed + k)
    if rubble_front:
        for k in range(int(1 + broken * 2)):
            u = rng.uniform(*span)
            p = face(u, 0) + N * rng.uniform(0.8, 1.6)
            rubble(C, p.x, p.y, r=rng.uniform(0.9, 1.5), h=rng.uniform(0.7, 1.1), seed=seed + 31 * k)
    return {"top": top}


def ruined_city_hall(C, cx=0.0, cy=26.0, *, east_cover=True):
    """폐허가 된 모나티엄 시청 (원작: 흑뉴아가 시청 폐허에서 엘레나·로네를 심문한다).
    도시 키트 city_hall(초상·화면·깃발 없이) + 그을음, 무너진 날개 끝, 찢긴 현수막, 쓰러진 포르티코 기둥,
    계단에 엎어진 엘레나 초상 액자. 가운데 계단 길(x −3..3)과 정문은 비워 둔다."""
    out = mk.city_hall(C, cx, cy, portrait=False, screen=False, flags=False)
    y_front = cy - 7.0
    # 이동 COL: 도시 키트의 기단·날개 상자는 둥근 모서리(반지름 4.2·3.8 m) 밖으로 1 m 넘게 나오고, 포르티코 기둥 상자는
    # 둥근 받침(반지름 0.62)보다 좁다. 보이는 모양 그대로의 볼록 COL로 바꾼다 (city_hall 기본 축척 1).
    WW, WD, WH, PZ = 34.0, 14.0, 11.4, 0.9
    if swap_col(C, (cx - WW / 2 - 1, cx + WW / 2 + 1, cy - WD / 2 - 1, cy + WD / 2 + 1, 0, PZ)):
        col_prism(C, hw.rrect(WW + 2, WD + 2, 4.2, 4, cx, cy), 0, PZ)
    if swap_col(C, (cx - WW / 2, cx + WW / 2, cy - WD / 2, cy + WD / 2, PZ, WH)):
        col_prism(C, hw.rrect(WW, WD, 3.8, 5, cx, cy), PZ, WH)
    TW, PH = 11.0, 8.2
    PY0 = y_front - 5.0
    for k in range(6):
        px = cx - (TW + 4) / 2 + k * (TW + 4) / 5
        if swap_col(C, (px - 0.48, px + 0.48, PY0 + 0.42, PY0 + 1.38, PZ, PH)):
            col_cyl(C, (px, PY0 + 0.9, PZ), (px, PY0 + 0.9, PH), 0.48, segs=16)
            col_cyl(C, (px, PY0 + 0.9, PZ), (px, PY0 + 0.9, PZ + 0.5), 0.62, segs=16)
    C.col(cx - 2.0, cx + 2.0, y_front - 0.25, y_front, PZ, PZ + 4.4)      # 정문 판 (날개 앞면에서 0.25 m 나옴)
    # 그을음 (날개 정면)
    for i, (dx, z, w, h) in enumerate([(-12, 6.5, 4.0, 5.0), (11, 4.5, 3.0, 4.5), (-6.5, 9.5, 3.0, 2.5), (14, 9.0, 3.2, 3.0)]):
        soot(C, (cx + dx, y_front - 0.02, z), (0, -1, 0), w, h, seed=i + 3)
    # 동쪽 날개 끝 일부 붕괴: 지붕 난간 위 잔해, 날개 앞 잔해
    for i in range(4):
        C.rbox("rubble_d", (cx + 13 + i * 1.1, y_front + 1.5 + (i % 2), 11.6 + i * 0.1), (2.2, 1.6, 0.6),
               (10 * i, -12, 25 * i))
    # 찢긴 현수막 (날개 정면)
    for side in (-1, 1):
        fx = cx + side * 9.0
        # 현수막은 날개 앞면 띠(앞면에서 9 cm)보다 1 cm 앞에 건다: 띠 앞면과 같은 평면이면 깜빡인다.
        # 판 y_front-0.10..-0.13, 금색 봉은 판 앞면에서 4 mm
        top = Vector((fx, y_front - 0.10, 10.6))
        C.plate("violet", [(-0.7, 0), (0.7, 0), (0.55, -2.4), (0.1, -1.7), (-0.2, -3.1), (-0.7, -2.0)], tuple(top),
                (0, -1, 0), 0.03, kind="detail")
        C.strip("gold", tuple(top + Vector((-0.7, -0.03, 0))), tuple(top + Vector((0.7, -0.03, 0))), 0.1, (0, -1, 0),
                lift=0.004)
    # 엎어진 초상 액자 (계단 동쪽, 색면이 바닥을 향함). y는 시청 기준(cy − 13.6): 예전에는 y = 12.4로 박혀 있어
    # cy가 다른 레벨(M6, cy 404)에서는 액자가 시청이 아닌 길 한가운데에 놓였다
    C.rbox("gold", (cx + 5.6, cy - 13.6, 0.62), (3.4, 4.8, 0.14), (8, -14, 18))
    C.rbox("char", (cx + 5.6, cy - 13.6, 0.71), (3.0, 4.4, 0.03), (8, -14, 18), kind="fine")
    col_rbox(C, (cx + 5.6, cy - 13.6, 0.62), (3.4, 4.8, 0.14), (8, -14, 18))
    if east_cover:
        # 쓰러진 포르티코 기둥 두 개 (동쪽 끝)
        fallen_column(C, (cx + 12.6, cy - 15.0), (cx + 19.4, cy - 15.0), r=0.36)
        fallen_column(C, (cx + 9.4, cy - 10.8), (cx + 13.6, cy - 13.4), r=0.42)
    return out


# ================================================================== 교통

def monorail_dark(C, x0, x1, y, *, z=7.5, pillars=(), beam_w=1.0, beam_h=1.3, gaps=()):
    """정전된 모노레일 (시안 전력선 없음). gaps=[(xa, xb)]: 보가 없는 구간 (무너진 경간)."""
    segs = [(x0, x1)]
    for (ga, gb) in gaps:
        nxt = []
        for (a, b) in segs:
            if gb <= a or ga >= b:
                nxt.append((a, b))
                continue
            if a < ga:
                nxt.append((a, ga))
            if gb < b:
                nxt.append((gb, b))
        segs = nxt
    for (a, b) in segs:
        C.beam("concrete", (a, y, z), (b, y, z), beam_w, beam_h)
        C.beam("concrete_d", (a, y, z - beam_h / 2 - 0.08), (b, y, z - beam_h / 2 - 0.08), beam_w + 0.2, 0.16,
               kind="detail")
        C.strip("glow_off", (a, y, z + beam_h / 2), (b, y, z + beam_h / 2), 0.08, lift=0.01)
    for px in pillars:
        C.cyl("concrete", (px, y, -0.15), (px, y, z - beam_h / 2 - 1.0), 0.55, segs=14)
        C.beam("concrete", (px, y - 1.3, z - beam_h / 2 - 0.6), (px, y + 1.3, z - beam_h / 2 - 0.6), 1.1, 0.9)
        col_cyl(C, (px, y, -0.15), (px, y, z - beam_h / 2 - 1.0), 0.55, segs=14)


def collapsed_span(C, p_hi, p_lo, *, w=1.0, h=1.3, steps=5, z_floor=-0.15):
    """무너진 모노레일 경간: 위(p_hi)에서 차도(p_lo)로 꺾여 박힌 보. COL은 보와 밑판 그대로의 볼록 껍질.
    (예전 계단식 상자는 보 위·아래로 1 m 넘게 비어 보 밑을 지나갈 자리를 막았다.) 보 윗면은 오를 수 있는 경사라
    아래 끝 가까이에 보 위로만 가로막는 COL을 세운다: 잔해를 밟고 보에 올라 정전된 모노레일 위로 가지 못하게."""
    a, b = Vector(p_hi), Vector(p_lo)
    C.beam("concrete", tuple(a), tuple(b), w, h)
    C.beam("concrete_d", tuple(a - Vector((0, 0, 0.7))), tuple(b - Vector((0, 0, 0.7))), w + 0.2, 0.16, kind="detail")
    for k in range(4):
        t = 0.2 + 0.2 * k
        q = a.lerp(b, t)
        C.beam("rebar", tuple(q), tuple(q + Vector((0.3, 0.6, -0.4))), 0.05, 0.05, kind="detail")
    M0, L = _beam_matrix(tuple(a), tuple(b))
    M1, _ = _beam_matrix(tuple(a - Vector((0, 0, 0.7))), tuple(b - Vector((0, 0, 0.7))))
    C.ccol([tuple(M0 @ Vector((x, y, z))) for x in (-w / 2, w / 2) for y in (-L / 2, L / 2) for z in (-h / 2, h / 2)]
           + [tuple(M1 @ Vector((x, y, z))) for x in (-w / 2 - 0.1, w / 2 + 0.1) for y in (-L / 2, L / 2)
              for z in (-0.08, 0.08)])
    # 보 위 가로막이: 아래 끝에서 보 길이 12~16% 자리, 윗면에서 1.6 m
    q0, q1 = M0 @ Vector((0, L / 2 - L * 0.16, h / 2)), M0 @ Vector((0, L / 2 - L * 0.12, h / 2))
    X = (M0.to_3x3() @ Vector((1, 0, 0))).normalized()
    C.ccol([tuple(q + X * sx + Vector((0, 0, dz))) for q in (q0, q1) for sx in (-w / 2, w / 2) for dz in (0.0, 1.6)])
    rubble(C, b.x, b.y, r=1.6, h=1.2, seed=int(b.x), z=z_floor)


def overpass(C, x0, x1, y0, y1, *, z=6.0, t=0.9, pillars=(), sign=None):
    """고가 상판 한 조각 (위로는 못 올라감). 아래는 어두운 지하도. sign=(ko, en) 표지판."""
    C.box("concrete", x0, x1, y0, y1, z, z + t)
    C.box("concrete_d", x0 - 0.2, x1 + 0.2, y0, y1, z + t, z + t + 0.8, kind="detail")
    C.box("asphalt", x0 + 0.3, x1 - 0.3, y0 + 0.01, y1 - 0.01, z + t + 0.01, z + t + 0.05, kind="detail")  # 끝면은 난간 끝면 안쪽
    C.col(x0, x1, y0, y1, z, z + t + 0.8)
    for (px, py) in pillars:
        C.box("concrete", px - 0.7, px + 0.7, py - 0.7, py + 0.7, -0.15, z)
        C.col(px - 0.7, px + 0.7, py - 0.7, py + 0.7, -0.15, z)
    if sign:
        ko, en = sign
        c = Vector(((x0 + x1) / 2 - 0.2, (y0 + y1) / 2, z - 1.1))
        C.plate("navy", hw.rrect(4.6, 1.5, 0.25, 2), tuple(c - Vector((0.1, 0, 0))), (-1, 0, 0), 0.1, kind="detail")
        C.text("white", ko, 0.42, tuple(c + Vector((-0.25, 0, 0.2))), (-1, 0, 0))
        C.text("stone_d", en, 0.22, tuple(c + Vector((-0.25, 0, -0.35))), (-1, 0, 0))


# ================================================================== 원경

def dark_skyline(C, cx, cy, *, r=150.0, n=36, seed=5, hmin=14, hmax=46, key="far_n", solid_in=None):
    """정전된 원경 고층 (불 꺼진 어두운 실루엣). solid_in=(x0, x1, y0, y1): 이 사각형(걸어 다닐 수 있는 맵)에 걸친
    블록은 COL을 준다. 길쭉한 맵(M6)에서는 원경 고리 일부가 맵 안 땅 위에 서서 몸이 건물을 지나갔다."""
    rng = random.Random(seed)
    for i in range(n):
        a = i / n * math.tau + rng.uniform(-0.05, 0.05)
        rr = r * rng.uniform(0.92, 1.15)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        w, d = rng.uniform(8, 18), rng.uniform(8, 16)
        h = rng.uniform(hmin, hmax)
        mk.lod_box(C, key, x - w / 2, x + w / 2, y - d / 2, y + d / 2, 0, h, kind="far")
        if solid_in and x + w / 2 > solid_in[0] and x - w / 2 < solid_in[1] and y + d / 2 > solid_in[2] \
                and y - d / 2 < solid_in[3]:
            C.col(x - w / 2, x + w / 2, y - d / 2, y + d / 2, -0.5, h)
        if rng.random() < 0.5:
            mk.lod_box(C, key, x - w / 3, x + w / 4, y - d / 3, y + d / 4, h, h + rng.uniform(2, 6), kind="far")


mk.PAL.update({"far_n": "#2c3246", "far_n2": "#232838"})


# ================================================================== 들어가는 폐허 (M4 늘리기, 2026-11-04)
# 통짜 COL 블록이 아니라 안을 걷는 건물·가게. 벽은 구멍(문·창·기는 틈)을 비운 상자 띠, 바닥판은 구멍을 비운 상자, 밑이 빈 비탈은
# 잔해로 꽉 채운다(판 밑 낮은 틈·비탈 천장은 캡슐을 끼우거나 땅으로 눌러 넣는다: docs/DO-NOT-REVIVE.md '들어가면 못 나오는 틈 금지').
# 계획: scratchpad m4plan/plan.md 6장, 마커 표: docs/script/m4.md 6장 '레벨 마커 (늘린 M4)'.

def _cut(a0, a1, ivs):
    """[a0, a1]에서 구간들(ivs)을 뺀 나머지 구간 목록."""
    out = []
    z = a0
    for (h0, h1) in sorted((max(a0, p), min(a1, q)) for (p, q) in ivs if q > a0 and p < a1):
        if h0 > z + 1e-4:
            out.append((z, h0))
        z = max(z, h1)
    if a1 > z + 1e-4:
        out.append((z, a1))
    return out


def wall_run(C, axis, c, a0, a1, z0, z1, *, t=0.3, holes=(), tops=(), key="concrete", col=True, kind="main"):
    """벽 한 줄. axis 'x': x를 따라 a0..a1, 두께 y = c..c+t. axis 'y': y를 따라 a0..a1, 두께 x = c..c+t.
    holes = [(u0, u1, h0, h1)]: 그 구간·높이를 비운다 (문·창·기는 틈). tops = [(u0, u1, z)]: 그 구간 윗면 (무너진 벽 끝).
    세로 띠마다 남는 높이를 상자로 (남는 높이가 같은 이웃 띠는 합친다). col=True면 상자마다 같은 COL."""
    us = {a0, a1}
    for (u0, u1, *_r) in list(holes) + list(tops):
        for u in (u0, u1):
            if a0 < u < a1:
                us.add(u)
    us = sorted(us)
    strips = []
    for ua, ub in zip(us, us[1:]):
        if ub - ua < 1e-4:
            continue
        um = (ua + ub) / 2
        zt = z1
        for (u0, u1, zz) in tops:
            if u0 <= um <= u1:
                zt = zz
        segs = _cut(z0, zt, [(h0, h1) for (u0, u1, h0, h1) in holes if u0 <= um <= u1])
        if strips and strips[-1][2] == segs and abs(strips[-1][1] - ua) < 1e-6:
            strips[-1][1] = ub
        else:
            strips.append([ua, ub, segs])
    for ua, ub, segs in strips:
        for (za, zb) in segs:
            if zb - za < 0.01:
                continue
            if axis == "x":
                C.box(key, ua, ub, c, c + t, za, zb, kind=kind, col=col)
            else:
                C.box(key, c, c + t, ua, ub, za, zb, kind=kind, col=col)


def slab(C, x0, x1, y0, y1, z0, z1, *, holes=(), key="concrete", col=True, kind="main"):
    """바닥판. holes = [(x0, x1, y0, y1)] 비울 사각형. x 띠마다 남는 y 구간을 상자로."""
    xs = {x0, x1}
    for (a, b, _c, _d) in holes:
        for u in (a, b):
            if x0 < u < x1:
                xs.add(u)
    xs = sorted(xs)
    strips = []
    for xa, xb in zip(xs, xs[1:]):
        xm = (xa + xb) / 2
        segs = _cut(y0, y1, [(c, d) for (a, b, c, d) in holes if a <= xm <= b])
        if strips and strips[-1][2] == segs and abs(strips[-1][1] - xa) < 1e-6:
            strips[-1][1] = xb
        else:
            strips.append([xa, xb, segs])
    for xa, xb, segs in strips:
        for (ya, yb) in segs:
            C.box(key, xa, xb, ya, yb, z0, z1, kind=kind, col=col)


def grille(C, axis, c, u0, u1, z0, z1, *, t=0.3, pitch=0.13, key="metal", outer=-1):
    """창 구멍의 방범 창살 (1층 낮은 창). 보이는 살(탄·시야는 살 사이로 지나간다) + 구멍을 덮는 걷기 COL(넘어 들어가지 못하게).
    axis·c·t는 wall_run과 같다. outer = -1이면 바깥면이 c (−x·−y 벽), +1이면 c + t. 살은 바깥면에서 4 cm 안."""
    n = max(2, int((u1 - u0) / pitch))
    o = c + 0.04 if outer < 0 else c + t - 0.04
    for k in range(1, n):
        u = u0 + (u1 - u0) * k / n
        p0, p1 = ((u, o, z0), (u, o, z1)) if axis == "x" else ((o, u, z0), (o, u, z1))
        C.beam(key, p0, p1, 0.022, 0.022, kind="detail")
    for zz in (z0 + 0.06, (z0 + z1) / 2, z1 - 0.06):
        p0, p1 = ((u0, o, zz), (u1, o, zz)) if axis == "x" else ((o, u0, zz), (o, u1, zz))
        C.beam(key, p0, p1, 0.03, 0.04, kind="detail")
    if axis == "x":
        C.col(u0, u1, c, c + t, z0, z1)
    else:
        C.col(c, c + t, u0, u1, z0, z1)


def glass_pane(C, axis, c, u0, u1, z0, z1, *, t=0.3, frame="mullion", mullions=1, cracked=False, seed=0):
    """창 구멍의 유리 (탄·시야는 지나간다: 머티리얼 glass) + 구멍을 덮는 걷기 COL + 틀. 유리는 벽 두께 가운데."""
    m = c + t / 2
    if axis == "x":
        C.box("glass", u0, u1, m - 0.01, m + 0.01, z0, z1, kind="detail")
        C.col(u0, u1, c, c + t, z0, z1)
    else:
        C.box("glass", m - 0.01, m + 0.01, u0, u1, z0, z1, kind="detail")
        C.col(c, c + t, u0, u1, z0, z1)
    for k in range(1, mullions + 1):
        u = u0 + (u1 - u0) * k / (mullions + 1)
        if axis == "x":
            C.box(frame, u - 0.03, u + 0.03, m - 0.03, m + 0.03, z0, z1, kind="detail")
        else:
            C.box(frame, m - 0.03, m + 0.03, u - 0.03, u + 0.03, z0, z1, kind="detail")
    if cracked:
        rng = random.Random(seed)
        for side in (-1, 1):
            for _ in range(3):
                uc = rng.uniform(u0 + 0.2, u1 - 0.2)
                zc = rng.uniform(z0 + 0.2, z1 - 0.2)
                a = rng.uniform(0, math.pi)
                L = rng.uniform(0.25, 0.6)
                du, dz = math.cos(a) * L / 2, math.sin(a) * L / 2
                off = m + side * 0.012
                if axis == "x":
                    p0, p1, nn = (uc - du, off, zc - dz), (uc + du, off, zc + dz), (0, side, 0)
                else:
                    p0, p1, nn = (off, uc - du, zc - dz), (off, uc + du, zc + dz), (side, 0, 0)
                C.strip("white", p0, p1, 0.012, nn, lift=0.002)


def ruined_shell(C, x0, x1, y0, y1, *, floors=3, h0=3.0, fh=2.7, t=0.3, slab_t=0.25, key="concrete", band="concrete_d",
                 holes=None, glass=None, grilles=None, gone=None, slab_holes=None, cols=(), top=(7.5, 10.0), ext=None,
                 bands="-x+x-y+y", walls="-x+x-y+y", seed=0):
    """들어가는 폐허 건물 (통짜 COL이 아니다). 바깥벽 t m, 층 바닥판(구멍), 안 기둥, 지붕 없음(위가 무너짐).
    벽은 바닥판 사이에만 서고(바닥판이 벽 바깥면까지 간다), 바깥 층 띠가 이음매를 덮는다.
      holes / glass / grilles = {side: [(u0, u1, z0, z1)]}: 빈 구멍(문·기는 틈·위층 창) / 유리 창(+COL) / 방범 창살 창(+COL).
          side '-x','+x','-y','+y', u = 그 벽을 따라 (x 벽이면 y, y 벽이면 x), z 절대 높이
      gone = {side: z}: 그 높이 위로 벽이 없다 (쓰러짐)
      slab_holes = {k: [(x0, x1, y0, y1)]}: k층 바닥판(k = 1이 2층 바닥)의 구멍
      cols = [(x, y)]: 안 기둥 0.5 m 각 (1층 바닥부터 맨 위 바닥판 밑까지, 바닥판마다 끊긴다)
      ext = {side: (lo, hi)}: ±x 벽 줄을 발자국 밖 y lo..hi까지 통짜로 늘린다 (옆 건물의 둥근 모서리를 덮을 때)
      top = (lo, hi): 맨 위층 벽 끝 높이 범위 (약 3.2 m 구간마다 무작위)
      walls: 세울 벽 (옆 건물 면이 벽인 쪽은 뺀다), bands: 바깥 층 띠를 두를 면
    반환: dict(levels=[바닥판 윗면 높이 …] (1층 0 포함), top_slab)."""
    rng = random.Random(seed)
    holes, glass, grilles = holes or {}, glass or {}, grilles or {}
    gone, slab_holes, ext = gone or {}, slab_holes or {}, ext or {}
    levels = [0.0] + [h0 + k * fh for k in range(floors - 1)]
    tops_z = levels[1:]                         # 바닥판 윗면 (2층 바닥 …)
    # 바닥판 (2층 바닥 …)
    for k, zt in enumerate(tops_z, start=1):
        slab(C, x0, x1, y0, y1, zt - slab_t, zt, holes=slab_holes.get(k, ()), key=key)
    zmax = top[1]

    def side_run(sd):
        axis = "x" if sd in ("-y", "+y") else "y"
        if axis == "y":
            c = x0 if sd == "-x" else x1 - t
            a0, a1 = y0, y1
        else:
            c = y0 if sd == "-y" else y1 - t
            a0, a1 = x0 + t, x1 - t
        allh = list(holes.get(sd, ())) + list(glass.get(sd, ())) + list(grilles.get(sd, ()))
        # 층마다: 바닥 윗면 ~ 다음 바닥판 밑 (맨 위층은 무너진 끝)
        for k, zlo in enumerate(levels):
            last = k == len(levels) - 1
            zhi = zmax if last else levels[k + 1] - slab_t
            if sd in gone:
                if zlo >= gone[sd] - 1e-4:
                    continue
                zhi = min(zhi, gone[sd])
            tops = []
            if last and sd not in gone:
                u = a0
                while u < a1 - 1e-3:
                    ub = min(a1, u + rng.uniform(2.4, 4.0))
                    if a1 - ub < 1.2:
                        ub = a1
                    tops.append((u, ub, rng.uniform(*top)))
                    u = ub
            wall_run(C, axis, c, a0, a1, zlo, zhi, t=t, holes=allh, tops=tops, key=key)
            if last and tops:
                for (ua, ub, zz) in tops[::2]:
                    um = (ua + ub) / 2
                    p = (um, c + t / 2, zz) if axis == "x" else (c + t / 2, um, zz)
                    C.beam("rebar", p, (p[0] + rng.uniform(-0.3, 0.3), p[1] + rng.uniform(-0.3, 0.3), zz + rng.uniform(0.5, 1.1)),
                           0.04, 0.04, kind="detail")
        for (u0, u1, z0_, z1_) in glass.get(sd, ()):
            glass_pane(C, axis, c, u0, u1, z0_, z1_, t=t, cracked=rng.random() < 0.5, seed=seed + int(u0 * 7 + z0_ * 3))
        for (u0, u1, z0_, z1_) in grilles.get(sd, ()):
            grille(C, axis, c, u0, u1, z0_, z1_, t=t, outer=-1 if sd in ("-x", "-y") else 1)
        if sd in ext and axis == "y":
            lo, hi = ext[sd]
            C.box(key, c, c + t, lo, hi, 0.0, zmax - 0.5, col=True)

    for sd in ("-x", "+x", "-y", "+y"):
        if sd in walls:
            side_run(sd)
    # 바깥 층 띠 (바닥판 끝·벽 이음매 덮개): 벽면에서 6 cm 나온다
    e = 0.06
    for zt in tops_z:
        za, zb = zt - slab_t - 0.06, zt + 0.06
        if "-x" in bands:
            C.box(band, x0 - e, x0, y0 - e, y1 + (0 if "+y" not in bands else e), za, zb, kind="detail")
        if "+x" in bands:
            C.box(band, x1, x1 + e, y0 - e, y1 + (0 if "+y" not in bands else e), za, zb, kind="detail")
        if "-y" in bands:
            C.box(band, x0, x1, y0 - e, y0, za, zb, kind="detail")
        if "+y" in bands:
            C.box(band, x0, x1, y1, y1 + e, za, zb, kind="detail")
    # 안 기둥 (바닥판마다)
    for (cx, cy) in cols:
        for k, zlo in enumerate(levels[:-1]):
            C.box(key, cx - 0.25, cx + 0.25, cy - 0.25, cy + 0.25, zlo, levels[k + 1] - slab_t, col=True)
    # 그을음 (바깥 벽, 위층)
    for k in range(3):
        sd = ("-x", "+x")[k % 2]
        fx = x0 if sd == "-x" else x1
        N = (-1, 0, 0) if sd == "-x" else (1, 0, 0)
        soot(C, (fx + N[0] * 0.03, rng.uniform(y0 + 2, y1 - 2), rng.uniform(h0 + 0.8, top[0] - 1.0)), N,
             rng.uniform(1.4, 2.6), rng.uniform(1.6, 3.0), seed=seed + k)
    return {"levels": levels, "top_slab": tops_z[-1] if tops_z else 0.0}


def wedge_ramp(C, axis, a_lo, a_hi, b0, b1, z_hi, *, t=0.26, key="concrete", fill="rubble_d", z_lo=0.0, seed=0,
               rebar=True):
    """밑이 잔해로 꽉 찬 비탈 판: axis 'y'면 y = a_lo(높이 z_lo)에서 a_hi(z_hi)로 오르고 폭은 x = b0..b1, 'x'면 반대.
    걷는 윗면 = 판 윗면. COL은 판 윗면부터 바닥(z_lo)까지 한 덩이 쐐기 (판 밑 낮은 틈·비탈 천장이 없게).
    보이는 것: 기운 판(두께 t, 아래 끝은 바닥에 묻힘) + 판 밑 잔해 덩이(옆면, COL 안쪽으로 3 cm) + 부러진 끝 철근."""
    rng = random.Random(seed)

    def P(a, b, z):
        return (b, a, z) if axis == "y" else (a, b, z)
    L = abs(a_hi - a_lo)
    rise = z_hi - z_lo
    sl = rise / L
    dz = t * math.sqrt(1 + sl * sl)             # 판 두께의 수직 몫

    def top_z(a):
        return z_lo + rise * (a - a_lo) / (a_hi - a_lo)
    # 판 (윗면 a_lo..a_hi, 아래 끝은 바닥 밑으로)
    a_ext = a_lo - (a_hi - a_lo) / L * 0.25
    b = C.bm(key)
    vs = []
    for a in (a_ext, a_hi):
        for bb in (b0, b1):
            zt = top_z(a)
            vs.append([b.verts.new(P(a, bb, zt)), b.verts.new(P(a, bb, zt - dz))])
    (lo0, lo1), (hi0, hi1) = (vs[0], vs[1]), (vs[2], vs[3])
    quads = [(lo0[0], lo1[0], hi1[0], hi0[0]), (lo0[1], hi0[1], hi1[1], lo1[1]), (lo0[0], hi0[0], hi0[1], lo0[1]),
             (lo1[0], lo1[1], hi1[1], hi1[0]), (lo0[0], lo0[1], lo1[1], lo1[0]), (hi0[0], hi1[0], hi1[1], hi0[1])]
    fs = [b.faces.new(q) for q in quads]
    bmesh.ops.recalc_face_normals(b, faces=fs)
    # 판 밑 잔해 (쐐기, COL보다 3 cm 안)
    i = 0.03
    fz = C.bm(fill)
    w = [fz.verts.new(P(a_lo + (a_hi - a_lo) / L * 0.15, b0 + i, z_lo)), fz.verts.new(P(a_lo + (a_hi - a_lo) / L * 0.15, b1 - i, z_lo)),
         fz.verts.new(P(a_hi, b0 + i, z_lo)), fz.verts.new(P(a_hi, b1 - i, z_lo)),
         fz.verts.new(P(a_hi, b0 + i, z_hi - dz)), fz.verts.new(P(a_hi, b1 - i, z_hi - dz))]
    ffs = [fz.faces.new((w[0], w[2], w[4])), fz.faces.new((w[1], w[5], w[3])), fz.faces.new((w[2], w[3], w[5], w[4])),
           fz.faces.new((w[0], w[4], w[5], w[1]))]
    bmesh.ops.recalc_face_normals(fz, faces=ffs)
    # 옆면 잔해 조각 (기운 판 조각이 옆면에 박힘: 2~4 cm 나온다)
    for k in range(int(L / 1.6)):
        a = a_lo + (a_hi - a_lo) * (k + 0.6) / int(L / 1.6 + 0.4)
        zc = top_z(a) * rng.uniform(0.25, 0.6)
        for bb, sgn in ((b0, -1), (b1, 1)):
            c = P(a, bb - sgn * 0.12, z_lo + max(0.15, zc))
            C.rbox("rubble" if k % 2 else "concrete_d", c, (0.3, 0.9, 0.5) if axis == "y" else (0.9, 0.3, 0.5),
                   (rng.uniform(-12, 12), rng.uniform(-12, 12), rng.uniform(-10, 10)), kind="detail")
    # COL: 쐐기 한 덩이
    C.ccol([P(a_lo, b0, z_lo), P(a_lo, b1, z_lo), P(a_hi, b0, z_lo), P(a_hi, b1, z_lo), P(a_hi, b0, z_hi), P(a_hi, b1, z_hi)])
    if rebar:
        for k in range(4):
            bb = b0 + (b1 - b0) * (k + 0.5) / 4
            p = P(a_hi, bb, z_hi - dz * 0.5)
            q = P(a_hi + (a_hi - a_lo) / L * rng.uniform(0.15, 0.35), bb + rng.uniform(-0.15, 0.15), z_hi - dz * rng.uniform(0.2, 1.2))
            C.beam("rebar", p, q, 0.03, 0.03, kind="detail")
    return {"slope": math.degrees(math.atan(sl))}


def crawl_gap(C, wall_x, y0, y1, *, t=0.3, inn=2.2, clear=0.52, slab_t=0.26, plug=1.25, rise=0.35, seed=0):
    """벽(x = wall_x..wall_x+t, -x 쪽이 바깥)을 지나는 기는 틈: 폭 y0..y1, 바닥 평평, 벽 바깥면에서 높이 clear.
    엎드린 몸(머리·가슴 공 0.44 m + 둘레 0.02)만 지난다: 웅크림(0.82 m)·병사 내비(키 1.2 m)는 못 지난다.
    위층에서 떨어진 바닥판 조각이 벽 구멍에 걸려 안쪽으로 비스듬히 누웠다(안쪽 끝이 rise만큼 높다: 틈은 안으로 갈수록 넓어진다).
    판은 양옆 잔해 턱이 받치고, 판 위 벽 구멍은 잔해로 메웠다. 바깥에는 판이 나오지 않는다(벽 밑동의 낮고 어두운 틈만 보인다).
    벽 구멍 (y0 - 0.3, y1 + 0.3, 0, plug)은 ruined_shell holes에 넣는다. 반환: 그 구멍."""
    rng = random.Random(seed)
    xa, xb = wall_x - 0.04, wall_x + t + inn
    ya, yb = y0 - 0.3, y1 + 0.3
    L = xb - xa
    pitch = math.degrees(math.atan2(rise, L))
    roll = 1.6
    W = (yb - ya) + 0.12
    # 판: 밑면이 벽 바깥 끝에서 clear (+ 기울기 여유 2 cm), 안쪽 끝은 clear + rise
    zc = clear + 0.02 + rise / 2 + (slab_t / 2) / math.cos(math.radians(pitch))
    rot = (roll, -pitch, 0.0)
    c = ((xa + xb) / 2, (y0 + y1) / 2, zc)
    C.rbox("concrete_d", c, (math.hypot(L, rise), W, slab_t), rot)
    col_rbox(C, c, (math.hypot(L, rise), W, slab_t), rot)
    # 양옆 턱 (판 밑면까지, 바닥 밑으로 묻힘): 판과 같이 기운 상자
    for (p, q) in ((ya, y0), (y1, yb)):
        hc = clear + 0.02 + rise / 2 - 0.6
        cc = ((xa + xb) / 2 + 0.05, (p + q) / 2, hc)
        sz = (math.hypot(L, rise) - 0.1, q - p, 1.2 / math.cos(math.radians(pitch)))
        C.rbox("rubble_d", cc, sz, (0.0, -pitch, 0.0))
        col_rbox(C, cc, sz, (0.0, -pitch, 0.0))
    # 부러진 판 끝 (안쪽)과 철근
    for k in range(4):
        yy = ya + (yb - ya) * (k + 0.5) / 4
        C.beam("rebar", (xb - 0.05, yy, clear + rise + slab_t * 0.5),
               (xb + rng.uniform(0.15, 0.35), yy + rng.uniform(-0.15, 0.15), clear + rise + rng.uniform(-0.1, 0.35)),
               0.025, 0.025, kind="detail")
    # 벽 구멍 윗부분: 잔해로 메움 (평평한 COL + 양면에 덩이)
    z_p = clear + 0.02 + slab_t + 0.02
    C.box("rubble_d", wall_x, wall_x + t, ya, yb, z_p, plug, col=True)
    for sgn, xx in ((-1, wall_x), (1, wall_x + t)):
        for k in range(3):
            C.blob("rubble" if k % 2 else "rubble_d", (xx + sgn * 0.03, ya + (yb - ya) * (k + 0.5) / 3, z_p + (plug - z_p) * 0.55),
                   0.24, (0.45, 1.0, 0.9), segs=7, rings=4)
    # 바깥 벽면: 구멍 둘레 깨진 자리 (튀어나온 조각, 철근) + 밑동 양옆 잔해 덩이 (COL, 벽에 묻힘: 틈 0)
    for k in range(5):
        a = math.pi * (0.1 + 0.8 * k / 4)
        py = (ya + yb) / 2 + math.cos(a) * ((yb - ya) / 2 + 0.15)
        pz = plug * 0.55 + math.sin(a) * (plug * 0.55)
        C.rbox("concrete" if k % 2 else "rubble", (wall_x - 0.03, py, pz), (0.12, rng.uniform(0.3, 0.5), rng.uniform(0.25, 0.4)),
               (rng.uniform(-10, 10), 0, rng.uniform(-25, 25)), kind="detail")
    for yy in (ya - 0.42, yb + 0.42):
        cc = (wall_x - 0.22, yy, 0.18)
        rz = rng.uniform(0, 3)
        C.blob("rubble", cc, 0.5, (0.8, 0.8, 0.55), segs=7, rings=4, rot_z=rz)
        col_blob(C, cc, 0.5, (0.8, 0.8, 0.55), segs=7, rings=4, rot_z=rz)
    return (ya, yb, 0.0, plug)


def roll_shutter(C, did, x0, x1, y, *, z_open=1.35, z_top=2.4, raise_by=0.85, out=-1, key="steel", house="metal"):
    """반쯤 올라간 셔터 문 DOOR_<did> (y 벽면 바깥쪽, out = 바깥 방향 -1/+1). 지금 밑면 z_open: 웅크리지 않고 지난다
    (키 1.2 m + 둘레 0.02, 병사 내비도 지난다). 미션이 열면(open) raise_by만큼 올라가 셔터 상자에 들어간다.
    셔터 상자(고정)는 문 구멍 위 z_top부터. 반환: DOOR_ 노드."""
    y_in = y + out * 0.04
    y_out = y + out * 0.12
    ya, yb = sorted((y_in, y_out))

    def build(b):
        mk._bm_box(b, x0, x1, ya, yb, z_open, z_top + 0.05)
        k = z_open + 0.12
        while k < z_top:
            # 바깥면 골 (판 바깥면에서 1 cm 나온 띠)
            if out < 0:
                mk._bm_box(b, x0 + 0.02, x1 - 0.02, ya - 0.01, ya + 0.005, k, k + 0.025)
            else:
                mk._bm_box(b, x0 + 0.02, x1 - 0.02, yb - 0.005, yb + 0.01, k, k + 0.025)
            k += 0.12
        mk._bm_box(b, x0, x1, ya - 0.015, yb + 0.015, z_open, z_open + 0.06)       # 밑 막대
    node = C.special(f"DOOR_{did}", build, key, {"move": f"0,{raise_by},0"})
    # 셔터 상자 (올라간 판이 들어간다) + 옆 레일
    hb = sorted((y, y + out * 0.42))
    C.box(house, x0 - 0.12, x1 + 0.12, hb[0], hb[1], z_top, z_top + raise_by + 0.12, col=True)
    for xx in (x0 - 0.08, x1):
        C.box(house, xx, xx + 0.08, ya - 0.02, yb + 0.02, 0.0, z_top, kind="detail")
    return node


def gondola(C, x0, x1, y0, y1, *, h=1.7, fallen=None, seed=0, key="white", goods=("red", "teal", "hazard", "coral", "mint", "navy_l")):
    """가게 진열대 (서 있으면 높이 h: 서서 엄폐). fallen = '+x'·'-x'·'+y'·'-y': 그쪽으로 넘어져 바닥에 누움(높이 0.6).
    COL은 보이는 상자 그대로. 누운 진열대 옆에 쏟아진 물건(납작, COL 없음)."""
    rng = random.Random(seed)
    if not fallen:
        C.box(key, x0, x1, y0, y1, 0.0, 0.12, col=False)
        C.box("steel", x0 + 0.04, x1 - 0.04, y0 + 0.04, y1 - 0.04, 0.12, h - 0.04, col=False)
        C.col(x0, x1, y0, y1, 0.0, h)
        C.box(key, x0 - 0.01, x1 + 0.01, y0 - 0.01, y1 + 0.01, h - 0.04, h, kind="detail")
        along_x = (x1 - x0) > (y1 - y0)
        for lvl in (0.45, 0.85, 1.25):
            C.box(key, x0 - 0.06, x1 + 0.06, y0 - 0.06, y1 + 0.06, lvl - 0.02, lvl, kind="detail")
            # 상품 (선반 위 작은 상자 띠: 빈 칸이 섞였다)
            a0, a1 = (x0, x1) if along_x else (y0, y1)
            u = a0 + 0.1
            while u < a1 - 0.25:
                w = rng.uniform(0.12, 0.3)
                if rng.random() < 0.7:
                    gk = goods[rng.randrange(len(goods))]
                    hh = rng.uniform(0.12, 0.28)
                    sides = ((y0 - 0.06, y0 + 0.02), (y1 - 0.02, y1 + 0.06)) if along_x else ((x0 - 0.06, x0 + 0.02), (x1 - 0.02, x1 + 0.06))
                    for (s0, s1) in sides:
                        if along_x:
                            C.box(gk, u, u + w, s0, s1, lvl, lvl + hh, kind="detail")
                        else:
                            C.box(gk, s0, s1, u, u + w, lvl, lvl + hh, kind="detail")
                u += w + rng.uniform(0.03, 0.12)
        return
    # 넘어진 진열대: 원래 발자국에서 fallen 쪽으로 높이만큼 누움
    w = (x1 - x0) if fallen in ("+x", "-x") else (y1 - y0)
    if fallen == "+x":
        bx = (x0, x0 + h)
        by = (y0, y1)
    elif fallen == "-x":
        bx = (x1 - h, x1)
        by = (y0, y1)
    elif fallen == "+y":
        bx = (x0, x1)
        by = (y0, y0 + h)
    else:
        bx = (x0, x1)
        by = (y1 - h, y1)
    th = min(0.6, w)
    C.box("steel", bx[0], bx[1], by[0], by[1], 0.0, th, col=True)
    C.box(key, bx[0] - 0.01, bx[1] + 0.01, by[0] - 0.01, by[1] + 0.01, th - 0.04, th, kind="detail")
    for k in range(10):
        gx = rng.uniform(bx[0] - 0.9, bx[1] + 0.9)
        gy = rng.uniform(by[0] - 0.9, by[1] + 0.9)
        if bx[0] - 0.05 < gx < bx[1] + 0.05 and by[0] - 0.05 < gy < by[1] + 0.05:
            continue
        C.rbox(goods[k % len(goods)], (gx, gy, 0.04), (rng.uniform(0.14, 0.3), rng.uniform(0.1, 0.2), 0.08),
               (0, 0, rng.uniform(0, 180)), kind="detail")


def shop_interior(C, x0, x1, y0, y1, *, h=3.2, t=0.3, door=(0.0, 0.0), broken=(), piers=(), back=None, name="", sub="",
                  awning="coral", floor_key="stone", wall_key="warm", ceil_key="concrete_d", seed=0):
    """들어가는 1층 가게 (정면 +y만): 바닥·천장·옆·뒤 벽(COL), 정면 유리창(유리 + 걷기 COL, 탄·시야는 지나간다), 깨진 칸(비움),
    문 구멍(door = (u0, u1) x 구간, 유리 깨짐), 간판·찢긴 차양. 위층은 ruined_building(z0=h)으로 따로 얹는다.
      piers = [x …]: 정면 창살 기둥 자리 (문·깨진 칸 경계는 저절로)
      back = (u0, u1, z1): 뒤 벽 구멍 (셔터 문, roll_shutter로 막는다)
    반환: 안쪽 사각형 (ix0, ix1, iy0, iy1)."""
    rng = random.Random(seed)
    ix0, ix1, iy0, iy1 = x0 + t, x1 - t, y0 + t, y1 - t
    # 바닥 (줄눈 타일, 벽 밑까지: 문턱이 꺼지지 않게) · 천장
    mk.paving(C, x0, x1, y0, y1, key=floor_key, grout="stone_d", tile=0.8)
    C.box(ceil_key, ix0, ix1, iy0, iy1, h - 0.25, h, col=True)
    for k in range(int((ix1 - ix0) / 2.4)):
        xx = ix0 + 1.2 + k * 2.4
        C.box("white", xx - 0.1, xx + 0.1, iy0 + 1.5, iy1 - 1.5, h - 0.29, h - 0.25, kind="detail")   # 꺼진 형광등 줄
    # 옆·뒤 벽 (바깥 면은 이웃 건물·뒷골목)
    wall_run(C, "y", x0, y0, y1, 0.0, h, t=t, key=wall_key)
    wall_run(C, "y", x1 - t, y0, y1, 0.0, h, t=t, key=wall_key)
    bh = [(back[0], back[1], 0.0, back[2])] if back else []
    wall_run(C, "x", y0, x0 + t, x1 - t, 0.0, h, t=t, holes=bh, key=wall_key)
    # 정면: 걸레받이(0.4) · 창 · 상인방(2.4~h) · 기둥
    fy = y1 - t
    du0, du1 = door
    bands = sorted(set([x0, x1, du0, du1] + [p for b in broken for p in b] + list(piers)))
    C.box("warm_d", x0, x1, fy, y1, 2.4, h, col=True)
    for xa, xb in zip(bands, bands[1:]):
        if xb - xa < 0.05:
            continue
        xm = (xa + xb) / 2
        if du0 <= xm <= du1:
            continue                                  # 문 구멍 (위 상인방만)
        C.box("dark", xa, xb, fy, y1, 0.0, 0.4, col=True)
        if any(a <= xm <= b for (a, b) in broken):
            # 깨진 칸: 유리 없음, 틀에 남은 조각만 (COL 없음: 넘어 들어갈 수 있다)
            for k in range(4):
                u = rng.uniform(xa + 0.1, xb - 0.1)
                C.prism("glass", [(u - 0.12, fy + t / 2 - 0.01), (u + 0.12, fy + t / 2 - 0.01), (u + 0.12, fy + t / 2 + 0.01),
                                  (u - 0.12, fy + t / 2 + 0.01)], 2.4 - rng.uniform(0.2, 0.6), 2.4, kind="detail")
            continue
        glass_pane(C, "x", fy, xa, xb, 0.4, 2.4, t=t, mullions=0, cracked=rng.random() < 0.6, seed=seed + int(xa))
    # 기둥 (창살 경계마다 0.16 m)
    for p in bands[1:-1]:
        C.box("dark", p - 0.08, p + 0.08, fy - 0.02, y1 + 0.02, 0.0, 2.4, col=True)
    for p in (x0, x1):
        C.box("warm_d", p - (0 if p == x0 else 0.3), p + (0.3 if p == x0 else 0), fy - 0.02, y1 + 0.02, 0.0, 2.4, col=True)
    # 문틀 + 문 유리 조각
    C.box("dark", du0 - 0.08, du1 + 0.08, fy - 0.02, y1 + 0.02, 2.32, 2.4, kind="detail")
    for k in range(5):
        C.rbox("glass", (rng.uniform(du0, du1), y1 + rng.uniform(0.3, 1.2), 0.012),
               (rng.uniform(0.1, 0.25), rng.uniform(0.08, 0.2), 0.012), (0, 0, rng.uniform(0, 180)), kind="detail")
    # 간판 (정면 상인방)
    W = x1 - x0 - 0.6
    sc = Vector(((x0 + x1) / 2, y1 + 0.02, h - 0.4))
    N = Vector((0, 1, 0))
    C.plate("navy", hw.rrect(min(W, 1.2 + 0.62 * max(len(name), 3)), 0.66, 0.22, 2), tuple(sc), tuple(N), 0.12, kind="detail")
    if name:
        C.text("white", name, 0.38, tuple(sc + N * 0.12 + Vector((0, 0, 0.05))), tuple(N))
    if sub:
        C.text("gold", sub, 0.14, tuple(sc + N * 0.12 - Vector((0, 0, 0.21))), tuple(N))
    # 찢긴 차양 (문 위는 비움, 반쯤 처짐)
    for (xa, xb) in ((x0 + 0.4, du0 - 0.3), (du1 + 0.3, x1 - 0.4)):
        if xb - xa < 0.8:
            continue
        sag = rng.uniform(-8, 14)
        C.rbox(awning, ((xa + xb) / 2, y1 + 0.55, 2.62), (xb - xa, 1.0, 0.06), (-18 + sag, 0, 0), kind="detail")
    return (ix0, ix1, iy0, iy1)


def counter(C, x0, x1, y0, y1, *, h=1.0, key="white", top="warm_d", front="-x"):
    """가게 계산대 (높이 1.0: 웅크려 숨는다). COL은 상자 그대로. 위에 금전등록기·작은 진열대."""
    C.box(key, x0, x1, y0, y1, 0.0, h - 0.05, col=False)
    C.box(top, x0 - 0.04, x1 + 0.04, y0 - 0.04, y1 + 0.04, h - 0.05, h, kind="detail")
    C.col(x0 - 0.04, x1 + 0.04, y0 - 0.04, y1 + 0.04, 0.0, h)
    cx, cy = (x0 + x1) / 2, y0 + (y1 - y0) * 0.3
    C.box("dark", cx - 0.2, cx + 0.2, cy - 0.18, cy + 0.18, h, h + 0.2, kind="detail")
    C.rbox("navy_l", (cx, cy + 0.05, h + 0.32), (0.32, 0.04, 0.2), (-20, 0, 0), kind="detail")


def cooler_bank(C, x0, x1, y0, y1, *, h=2.6, doors=4, face="+y"):
    """꺼진 음료 냉장고 벽 (통짜 덩어리 + 앞면 유리문). face 쪽에 문."""
    C.box("steel", x0, x1, y0, y1, 0.0, h, col=True)
    fy = y1 if face == "+y" else y0
    s = 1 if face == "+y" else -1
    n = doors
    for k in range(n):
        xa = x0 + 0.1 + (x1 - x0 - 0.2) * k / n
        xb = x0 + 0.1 + (x1 - x0 - 0.2) * (k + 1) / n - 0.06
        C.box("dark", xa, xb, fy + (0 if s > 0 else -0.03), fy + (0.03 if s > 0 else 0), 0.25, h - 0.3, kind="detail")
        C.rect("glass_d", ((xa + xb) / 2, fy + s * 0.03, (h - 0.05) / 2 + 0.1), (0, s, 0), xb - xa - 0.12, h - 0.75, lift=0.004)
        for lvl in (0.7, 1.15, 1.6):
            C.rect("red" if k % 2 else "teal", ((xa + xb) / 2, fy + s * 0.03, lvl), (0, s, 0), xb - xa - 0.3, 0.14, lift=0.008)
        C.box("steel", xb - 0.12, xb - 0.08, fy + (0.03 if s > 0 else -0.08), fy + (0.08 if s > 0 else -0.03), 0.9, 1.5, kind="detail")


def dumpster(C, x, y, *, yaw=0.0, key="teal", z=0.0):
    """뒷골목 쓰레기통 (1.6 × 0.9, 높이 1.05: 웅크려 숨는다). COL은 몸통 상자 (돌린 상자)."""
    a = math.radians(yaw)
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(a, 4, "Z")
    b = C.bm(key)
    mk._bm_box(b, -0.8, 0.8, -0.45, 0.45, 0.12, 1.0, matrix=Mx)
    mk._bm_box(C.bm("dark", "detail"), -0.82, 0.82, -0.5, 0.47, 1.0, 1.06, matrix=Mx @ Matrix.Rotation(math.radians(-4), 4, "X"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = Mx @ Vector((sx * 0.65, sy * 0.33, 0.06))
            C.cyl("rubber", tuple(p - Vector((0, 0, 0.0))), tuple(p + Vector((0, 0, 0.06))), 0.06, segs=8, kind="detail")
    mk._bm_box(C.bm("metal", "detail"), -0.84, 0.84, 0.44, 0.48, 0.75, 0.82, matrix=Mx)
    C.lcol(x, y, z, yaw, -0.84, 0.84, -0.5, 0.48, 0.0, 1.06)


def ac_unit(C, x, y, z, *, yaw=0.0):
    """벽 실외기 (뒷골목, 벽에 붙는다: -y 쪽이 앞)."""
    a = math.radians(yaw)
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(a, 4, "Z")
    mk._bm_box(C.bm("steel", "detail"), -0.45, 0.45, -0.32, 0.0, 0.0, 0.7, matrix=Mx)
    C.cyl("dark", tuple(Mx @ Vector((0.08, -0.33, 0.35))), tuple(Mx @ Vector((0.08, -0.34, 0.35))), 0.24, segs=12, kind="detail")
    C.lcol(x, y, z, yaw, -0.45, 0.45, -0.32, 0.0, 0.0, 0.7)


def clothesline(C, p0, p1, *, sag=0.25, items=4, seed=0):
    """골목 위 빨랫줄 (머리 위, COL 없음)."""
    rng = random.Random(seed)
    P0, P1 = Vector(p0), Vector(p1)
    pts = [P0.lerp(P1, k / 8) - Vector((0, 0, sag * math.sin(math.pi * k / 8))) for k in range(9)]
    for a, b in zip(pts, pts[1:]):
        C.beam("dark", tuple(a), tuple(b), 0.012, 0.012, kind="fine")
    for k in range(items):
        tt = rng.uniform(0.15, 0.85)
        q = P0.lerp(P1, tt) - Vector((0, 0, sag * math.sin(math.pi * tt) + 0.02))
        d = (P1 - P0).normalized()
        w = rng.uniform(0.3, 0.55)
        hh = rng.uniform(0.35, 0.6)
        n = Vector((-d.y, d.x, 0))
        C.plate(("canvas", "coral", "mint", "navy_l")[k % 4], [(-w / 2, 0), (w / 2, 0), (w / 2, -hh), (-w / 2, -hh)], tuple(q),
                tuple(n), 0.01, up=(0, 0, 1), kind="detail")
