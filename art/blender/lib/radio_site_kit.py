"""전파 시설 키트 (radio_site_kit): 3막 M7 「통신공사」의 중계탑, 전파국, 송신탑, R41 전파 교란기.

[원작] R41의 전파 교란기가 모나티엄 무선망을 마비시킨다. 코어 AI가 다시 돌고, 엘레나는 교란기가 추적할 때마다
       새 주파수를 만들어 통신망을 되살린다(전파국 장악).
[오리지널] 중계탑·전파국·송신탑의 생김새, 교란기의 생김새(R41 형태 언어), 표지 문구, 배치 모듈.

규약: 레벨 노드 docs/LEVELS.md, 전투 마커 docs/COMBAT.md 2장, 도시 키트 docs/art/monatium-city.md,
R41 형태 언어 docs/art/r41-style.md (45° 모따기 덩어리, 육각 부품, 밝은 회색 + 앰버 + 마젠타 슬릿 발광).
도시 키트(monatium_city_kit)는 읽기만 한다. 팔레트에 키를 더하는 것은 실행 중 딕셔너리만 바꾼다(파일은 그대로).

사용:
    import monatium_city_kit as mk, radio_site_kit as rk
    C = mk.City("m7_relay")
    G = rk.Ground(height_fn)                         # 높이장 지형 (보이는 메시 = 충돌 메시, G.h(x, y) = 실제 바닥 높이)
    G.patch(C, "base", xs, ys, skip=...)
    m = rk.lattice_mast(C, (x, y, z), h=28, lid="site_a", avia="avia_a", sign=("중계탑 서부 1호", "RELAY W-1"))
    j = rk.jammer(C, "a", (x, y, z), yaw=yaw)         # JAMMER_a + 자식 JAMMER_a_glow
    s = rk.radio_station(C, (x, y, z), yaw=-90, lid="site_b", avia="avia_b")
    rk.trig(C, "site_a", x0, x1, y0, y1, z0, z1)

모듈
  지형      Ground(fn).patch(...)  높이장 격자 조각 (삼각형 대각선 고정 → h(x, y)가 메시와 정확히 같다)
            drape(...)              지형 위에 얹는 띠 (공원길·흙길·자갈길)
            street_y(...)           Y축 도로: 아스팔트 띠 + 차선 + 높인 보도(충돌 메시) + 연석
  시설      lattice_mast            격자 철탑 (3·4각, 항공 장애 도장 띠, 패널 안테나, 마이크로파 접시, 사다리,
                                    LIGHT_<lid>_nn 시안 망 표시등, LIGHT_<avia>_nn 적색 항공 장애등)
            dish                    DISH_<id> 접시 안테나 노드 (Z 회전으로 방향 맞춤, alignYaw = 맞출 방향)
            radio_station           전파국: 2층 본관 + 1층 장비실(열린 출입구, 송신 콘솔, 랙) + 옥상 테라스 바깥 계단
                                    + 옥상 안테나, 간판(LIGHT 밑줄), ON AIR 등, 콘솔 화면 LIGHT
            control_box, breaker_cabinet, generator, fuel_tank, dish_control, cable
            chain_fence, fence_gate    철망 울타리(반투명 망 + 가시줄) + 열린 문짝, 축 정렬 COL
  R41       jammer                  전파 교란기 JAMMER_<id> (삼각대 / 손수레), 자식 JAMMER_<id>_glow만 마젠타 UNLIT
            r41_barrier, r41_crate  모따기 차단벽, 보급 상자
  거리      sandbags (싼 모래주머니 벽 + COL), car (폐차 포함), rubble, utility_pole/wires
  원경      core_far (코어 AI 탑 원경 LOD, lit=False면 꺼진 띠), far_block, lod_house
  마커      trig (TRIG_ 상자), beacon (LIGHT_ 발광 렌즈 묶음)

체격: 엘프 기준(키 1.2 m, 눈 0.92 m, 점프 0.6 m, 자동 오르기 0.28 m). 문 2.0 × 1.4 m, 계단 단 0.18 m 이하.
좌표: Blender Z-up, 1 BU = 1 m, 빈 오브젝트와 로컬 틀(Local)의 -Y가 정면. yaw(도)는 Z 회전.
"""
from __future__ import annotations

import bisect
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb
import home_weapons as hw
import monatium_city_kit as mk

# ================================================================== palette (실행 중에만 더한다)
PAL_ADD = {
    "mast_r": "#d8644f",     # 항공 장애 표시 도장 (주황빨강 띠)
    "mast_w": "#ece8e1",     # 흰 띠, 패널 안테나
    "galv": "#a8aab0",       # 아연 도금 강재 (기둥, 난간, 케이블 트레이)
    "galv_d": "#7b7e86",
    "cab": "#8b9daa",        # 전력함·발전기 (청회색 도장)
    "cab_d": "#5c6b78",
    "cable": "#2a272e",
    "dish": "#e8e5df",       # 접시 안테나 면
    "turf": "#8aa476",       # 외곽 잔디 (흐린 날)
    "turf_d": "#71895f",
    "dirt": "#9c8a74",       # 흙길
    "gravel": "#a29d97",     # 자갈길
    "conc": "#c8c3bc",       # 기단 콘크리트
    "conc_d": "#a39d97",
    "floor_in": "#b9b2aa",   # 장비실 바닥
    "wall_in": "#d9d2c6",    # 장비실 안벽
    "rust": "#8a5a44",
    "wreck": "#4e4952",      # 불탄 차체
    "tire": "#2b272d",
    "car_b": "#6d8fb5",
    "car_w": "#e3ded6",
    "fence_p": "#7a7d85",    # 철망 기둥
    "pole": "#7d6550",       # 전봇대 (나무)
    "board": "#2f3644",
}
GLOW_ADD = {
    "magenta_hot": "#ffc4f1",
}
ALPHA_ADD = {
    "mesh_a": ("#5f626b", 0.45),   # 철망
}
for _k, _v in PAL_ADD.items():
    mk.PAL.setdefault(_k, _v)
for _k, _v in GLOW_ADD.items():
    mk.GLOW.setdefault(_k, _v)
for _k, _v in ALPHA_ADD.items():
    mk.ALPHA.setdefault(_k, _v)
mk._DARK.update({"cable", "tire", "wreck", "board", "cab_d"})

CYAN = mk.GLOW["glow"]          # #7ff0ea 모나티엄 네트워크
RED = "#ff4a3a"                 # 항공 장애등
MAGENTA = mk.GLOW["magenta"]    # R41 기계 발광


def S(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def face_yaw(src, dst):
    """src에서 dst를 바라보는 yaw(도). 로컬 -Y가 그쪽을 향한다."""
    return math.degrees(mk.yaw_to(src, dst))


# ================================================================== local frame

class Local:
    """pos + yaw 로컬 틀 (-Y 정면). 도시 키트 누적 버퍼에 월드 좌표로 쓴다."""

    def __init__(self, pos, yaw=0.0):
        self.o = Vector(pos)
        self.yaw = float(yaw)
        self.M = Matrix.Translation(self.o) @ Matrix.Rotation(math.radians(self.yaw), 4, "Z")
        self.R = self.M.to_3x3()

    def p(self, x, y, z=0.0):
        return self.M @ Vector((x, y, z))

    def d(self, x, y, z=0.0):
        return self.R @ Vector((x, y, z))

    def box(self, C, key, x0, x1, y0, y1, z0, z1, kind="main", col=False):
        mk._bm_box(C.bm(key, kind), x0, x1, y0, y1, z0, z1, matrix=self.M)
        if col:
            self.col(C, x0, x1, y0, y1, z0, z1)

    def chbox(self, C, key, c, s, ch, kind="main", rot=None):
        m = self.M if rot is None else self.M @ rot
        chbox_bm(C.bm(key, kind), c, s, ch, matrix=m)

    def cyl(self, C, key, p0, p1, r, **kw):
        C.cyl(key, self.p(*p0), self.p(*p1), r, **kw)

    def beam(self, C, key, p0, p1, w, h, kind="main"):
        C.beam(key, self.p(*p0), self.p(*p1), w, h, kind=kind)

    def rect(self, C, key, c, n, w, h, *, up=(0, 0, 1), lift=None, kind="fine"):
        C.rect(key, self.p(*c), self.d(*n), w, h, up=self.d(*up), lift=lift, kind=kind)

    def decal(self, C, key, pts, c, n, *, up=(0, 0, 1), lift=None, kind="fine"):
        C.decal(key, pts, self.p(*c), self.d(*n), up=self.d(*up), lift=lift, kind=kind)

    def frame_rect(self, C, key, c, n, w, h, t, *, up=(0, 0, 1), lift=None, kind="fine"):
        """폭 t의 사각 테 (w × h 바깥). 테 안쪽을 판으로 덮어 테처럼 보이게 하는 대신 쓴다 (겹친 판 없음)."""
        ow, oh, iw, ih = w / 2, h / 2, w / 2 - t, h / 2 - t
        C.ring(key, [(-ow, -oh), (ow, -oh), (ow, oh), (-ow, oh)], [(-iw, -ih), (iw, -ih), (iw, ih), (-iw, ih)],
               self.p(*c), self.d(*n), up=self.d(*up), lift=lift, kind=kind)

    def plate(self, C, key, pts, c, n, depth, *, kind="detail"):
        C.plate(key, pts, self.p(*c), self.d(*n), depth, kind=kind)

    def text(self, C, key, s, size, c, n, *, lift=None):
        C.text(key, s, size, self.p(*c), self.d(*n), lift=lift)

    def col(self, C, x0, x1, y0, y1, z0, z1):
        """로컬 상자를 그대로 돌린 COL_ (90° 배수면 축 정렬 col). 예전에는 돌린 상자의 축 정렬 경계 상자를 썼다:
        비스듬한 차·모래주머니·상자 둘레에 보이지 않는 벽이 남는다."""
        C.lcol(self.o.x, self.o.y, self.o.z, self.yaw, x0, x1, y0, y1, z0, z1)

    def ccol(self, C, pts):
        """로컬 점들의 볼록 껍질 COL_."""
        C.ccol([tuple(self.p(*q)) for q in pts])


# ================================================================== bmesh helpers

def chbox_bm(bm, c, s, ch, matrix=None):
    """모서리 12개를 45°로 한 단 모따기한 상자 (R41 형태 언어). c = 중심, s = 크기."""
    hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
    ch = min(ch, hx * 0.45, hy * 0.45, hz * 0.45)
    tmp = bmesh.new()
    vs = []
    for X in (-1, 1):
        for Y in (-1, 1):
            for Z in (-1, 1):
                for (a, b, d) in ((hx - ch, hy, hz - ch), (hx, hy - ch, hz - ch), (hx - ch, hy - ch, hz)):
                    vs.append(tmp.verts.new(Vector((c[0] + X * a, c[1] + Y * b, c[2] + Z * d))))
    bmesh.ops.convex_hull(tmp, input=vs)
    bmesh.ops.dissolve_limit(tmp, angle_limit=0.001, verts=list(tmp.verts), edges=list(tmp.edges))
    if matrix is not None:
        bmesh.ops.transform(tmp, matrix=matrix, verts=list(tmp.verts))
    bmesh.ops.recalc_face_normals(tmp, faces=list(tmp.faces))
    mk._copy_into(bm, tmp)
    tmp.free()


def beam_bm(bm, p0, p1, w, h, up=(0, 0, 1)):
    P0, P1 = Vector(p0), Vector(p1)
    d = P1 - P0
    L = d.length
    if L < 1e-6:
        return
    Y = d.normalized()
    U = Vector(up)
    if abs(Y.dot(U)) > 0.99:
        U = Vector((1, 0, 0))
    X = Y.cross(U).normalized()
    Z = X.cross(Y).normalized()
    Mx = Matrix((X, Y, Z)).transposed().to_4x4()
    Mx.translation = (P0 + P1) / 2
    mk._bm_box(bm, -w / 2, w / 2, -L / 2, L / 2, -h / 2, h / 2, matrix=Mx)


def hex_prism_bm(bm, c, r, z0, z1, rot=30.0):
    pts = [(c[0] + r * math.cos(math.radians(rot + 60 * i)), c[1] + r * math.sin(math.radians(rot + 60 * i)))
           for i in range(6)]
    mk._bm_prism(bm, pts, z0, z1)


class Parts:
    """노드 하나에 붙일 머티리얼별 로컬 bmesh 묶음 (교란기, 접시)."""

    def __init__(self):
        self.b: dict[str, bmesh.types.BMesh] = {}

    def __call__(self, key):
        b = self.b.get(key)
        if b is None:
            b = self.b[key] = bmesh.new()
        return b

    def nodes(self, prefix, root, *, glow_key=None, glow_name=None, outline=None):
        out = {}
        for key, b in self.b.items():
            if not b.faces:
                b.free()
                continue
            nm = glow_name if (glow_key and key == glow_key) else f"{prefix}_{key}"
            out[key] = mk._node_obj(nm, b, key, parent=root, outline=outline if not mk.is_glow(key) else None)
        self.b.clear()
        return out


# ================================================================== collision meshes

def col_ramp(C, name, L, x0, x1, ya, za, yb, zb, *, z_floor=-0.3):
    """COL_<name>: 로컬 틀 L에서 y=ya(높이 za) → y=yb(높이 zb)로 오르는 경사 충돌 블록 (계단의 충돌 대역).
    한 단씩 상자를 쌓은 계단은 캐릭터 컨트롤러가 디딤판 모서리에 걸리므로, 보이는 계단 밑에 경사면 하나를 둔다."""
    b = bmesh.new()
    pts = [(x0, ya, z_floor), (x1, ya, z_floor), (x1, yb, z_floor), (x0, yb, z_floor),
           (x0, ya, za), (x1, ya, za), (x1, yb, zb), (x0, yb, zb)]
    v = [b.verts.new(L.p(*q)) for q in pts]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        b.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(b, faces=list(b.faces))
    me = bpy.data.meshes.new(f"COL_{name}")
    b.to_mesh(me)
    b.free()
    o = bpy.data.objects.new(f"COL_{name}", me)
    cb.link(o)
    C.add_node(o)
    return o


# ================================================================== markers · lights

def trig(C, tid, x0, x1, y0, y1, z0, z1, **props):
    """TRIG_<tid> 축 정렬 트리거 상자 (렌더하지 않음)."""
    o = mk._box_obj(f"TRIG_{tid}", min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))
    o["collider"] = 0
    for k, v in props.items():
        o[k] = v
    C.add_node(o)
    return o


def beacon(C, lid, pts, *, color=CYAN, group="site", on=0, blink=None, r=0.2, h=0.34, off_key="glow_off",
           on_key="glow", segs=10, bracket=None, rng=24.0):
    """LIGHT_<lid>: pts마다 받침 + 꺼진 렌즈(늘 보임) + 켜진 렌즈(미션이 켜고 끔, emissiveToggle).
    bracket = [(점, 붙일 곳)] 이면 받침 팔도 그린다."""
    for p in pts:
        P = Vector(p)
        C.cyl("metal", P - Vector((0, 0, 0.07)), P, r * 1.2, segs=segs, kind="detail")
        C.cyl(off_key, P, P + Vector((0, 0, h)), r, r2=r * 0.78, segs=segs, kind="detail")
        C.cyl("metal", P + Vector((0, 0, h)), P + Vector((0, 0, h + 0.05)), r * 0.82, segs=segs, kind="detail")
    for (a, b) in (bracket or []):
        C.beam("galv", a, b, 0.05, 0.05, kind="detail")

    def build(bm):
        for p in pts:
            P = Vector(p)
            mk._bm_cyl(bm, P + Vector((0, 0, 0.004)), P + Vector((0, 0, h - 0.004)), r * 1.05, segs=segs,
                       r2=r * 0.83)
    props = {"emissiveToggle": 1, "group": group, "on": int(on), "color": color, "range": rng}
    if blink:
        props["blink"] = float(blink)
    return C.special(f"LIGHT_{lid}", build, on_key, props, kind="fine")


def light_panel(C, lid, quads, *, color=CYAN, group="site", on=0, on_key="glow", blink=None):
    """LIGHT_<lid>: 평평한 발광판 묶음 (간판 밑줄, 콘솔 화면, ON AIR). quads = [(중심, 법선, 폭, 높이)].
    꺼진 모습은 호출하는 쪽이 아래에 깐다."""
    def build(bm):
        for (c, n, w, hgt) in quads:
            R, U, N = mk.frame(n)
            cc = Vector(c) + N * 0.006
            vs = [bm.verts.new(cc + R * u + U * v) for u, v in ((-w / 2, -hgt / 2), (w / 2, -hgt / 2),
                                                                   (w / 2, hgt / 2), (-w / 2, hgt / 2))]
            f = bm.faces.new(vs)
            f.normal_update()
            if f.normal.dot(N) < 0:
                f.normal_flip()
    props = {"emissiveToggle": 1, "group": group, "on": int(on), "color": color}
    if blink:
        props["blink"] = float(blink)
    return C.special(f"LIGHT_{lid}", build, on_key, props, kind="fine")


# ================================================================== ground

class Ground:
    """높이장 지형. 보이는 메시가 곧 충돌 메시다(collider=1). h(x, y)는 메시 삼각형을 그대로 보간한다.
    조각(patch)은 격자(xs, ys)이고 칸마다 대각선 (i,j)-(i+1,j+1)로 나눈다. 나중에 더한 조각이 먼저 쓰인다.
    skip(xc, yc)가 참인 칸은 비운다(다른 조각이 덮는 자리). 조각 경계에서 높이가 같아야 틈이 없다."""

    def __init__(self, fn):
        self.fn = fn
        self.patches = []

    def patch(self, C, name, xs, ys, *, key="turf", skip=None, collider=True, smooth=True, kind="main"):
        xs = sorted(set(round(x, 4) for x in xs))
        ys = sorted(set(round(y, 4) for y in ys))
        H = [[self.fn(x, y) for y in ys] for x in xs]

        def build(bm):
            V = [[bm.verts.new((x, y, H[i][j])) for j, y in enumerate(ys)] for i, x in enumerate(xs)]
            for i in range(len(xs) - 1):
                for j in range(len(ys) - 1):
                    if skip and skip((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2):
                        continue
                    f1 = bm.faces.new((V[i][j], V[i + 1][j], V[i + 1][j + 1]))
                    f2 = bm.faces.new((V[i][j], V[i + 1][j + 1], V[i][j + 1]))
                    f1.smooth = f2.smooth = smooth
            loose = [v for v in bm.verts if not v.link_faces]
            if loose:
                bmesh.ops.delete(bm, geom=loose, context="VERTS")
        o = C.special(f"ground_{name}", build, key, kind=kind)
        if collider:
            o["collider"] = 1
        self.patches.append((xs, ys, H, skip))
        return o

    def h(self, x, y):
        for xs, ys, H, skip in reversed(self.patches):
            if not (xs[0] <= x <= xs[-1] and ys[0] <= y <= ys[-1]):
                continue
            i = min(max(bisect.bisect_right(xs, x) - 1, 0), len(xs) - 2)
            j = min(max(bisect.bisect_right(ys, y) - 1, 0), len(ys) - 2)
            if skip and skip((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2):
                continue
            u = (x - xs[i]) / (xs[i + 1] - xs[i])
            v = (y - ys[j]) / (ys[j + 1] - ys[j])
            h00, h10, h11, h01 = H[i][j], H[i + 1][j], H[i + 1][j + 1], H[i][j + 1]
            if u >= v:
                return h00 + u * (h10 - h00) + v * (h11 - h10)
            return h00 + v * (h01 - h00) + u * (h11 - h01)
        return self.fn(x, y)

    def hmin(self, x0, x1, y0, y1, n=3):
        return min(self.h(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * j / n) for i in range(n + 1) for j in range(n + 1))

    def hmax(self, x0, x1, y0, y1, n=3):
        return max(self.h(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * j / n) for i in range(n + 1) for j in range(n + 1))


def _resample(pts, step):
    P = [Vector((p[0], p[1], 0.0)) for p in pts]
    out = [P[0]]
    for a, b in zip(P, P[1:]):
        L = (b - a).length
        n = max(1, int(math.ceil(L / step)))
        out += [a.lerp(b, k / n) for k in range(1, n + 1)]
    return out


def drape(C, key, pts, width, ground, *, lift=0.06, step=1.0, kind="fine", fillet=None):
    """지형 위에 얹은 띠(길). pts = [(x, y)] 꺾은선, fillet = 꺾임 반지름. 반환: 다시 뽑은 중심점."""
    if fillet:
        pts = [(p[0], p[1]) for p in mk.fillet_path(pts, fillet, seg=5)]
    P = _resample(pts, step)
    n = len(P)
    b = C.bm(key, kind)
    left, right = [], []
    for i, p in enumerate(P):
        a = P[max(0, i - 1)]
        c = P[min(n - 1, i + 1)]
        t = (c - a)
        t.z = 0
        t = t.normalized() if t.length > 1e-6 else Vector((1, 0, 0))
        s = Vector((-t.y, t.x, 0)) * (width / 2)
        pl, pr = p + s, p - s
        left.append(Vector((pl.x, pl.y, ground.h(pl.x, pl.y) + lift)))
        right.append(Vector((pr.x, pr.y, ground.h(pr.x, pr.y) + lift)))
    vl = [b.verts.new(v) for v in left]
    vr = [b.verts.new(v) for v in right]
    for i in range(n - 1):
        f = b.faces.new((vr[i], vr[i + 1], vl[i + 1], vl[i]))
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    return P


# ================================================================== street

def street_y(C, ground, xc, y0, y1, rows, *, lanes=2, lane_w=2.8, walk=3.2, curb_h=0.15, dash=3.0,
             crossings=(), walk_key="pave", name="street", walk_sides=(-1, 1)):
    """Y축을 따라 뻗은 도로 (중심선 x=xc, y0..y1). 지형(ground) 위에 아스팔트 띠를 얹고 양쪽에 높인 보도
    (충돌 메시 street_<name>_walk_±)를 둔다. rows = 지형 격자 y값(같은 자리에서 꺾어 지형과 평행하게).
    반환: dict(road_lo, road_hi, walk_lo, walk_hi, curb_h)."""
    half = lanes * lane_w / 2
    ys = sorted({y0, y1} | {y for y in rows if y0 < y < y1})
    g = [ground.h(xc, y) for y in ys]
    lift = 0.02
    # 아스팔트
    b = C.bm("asphalt", "fine")
    for i in range(len(ys) - 1):
        q = [(xc - half - 0.05, ys[i], g[i] + lift), (xc + half + 0.05, ys[i], g[i] + lift),
             (xc + half + 0.05, ys[i + 1], g[i + 1] + lift), (xc - half - 0.05, ys[i + 1], g[i + 1] + lift)]
        b.faces.new([b.verts.new(Vector(p)) for p in q])

    def gz(y):
        return ground.h(xc, y) + lift

    def line(x, ya, yb, w, key):
        n = max(1, int(math.ceil((yb - ya) / 4.0)))
        for k in range(n):
            a = ya + (yb - ya) * k / n
            c = ya + (yb - ya) * (k + 1) / n
            C.poly(key, [(x - w / 2, a, gz(a) + 0.012), (x + w / 2, a, gz(a) + 0.012),
                         (x + w / 2, c, gz(c) + 0.012), (x - w / 2, c, gz(c) + 0.012)], normal=(0, 0, 1))
    # 중앙선 (2차로 = 노랑 겹줄) + 가장자리선 + 차선 점선
    if lanes <= 2:
        line(xc - 0.12, y0, y1, 0.1, "line_y")
        line(xc + 0.12, y0, y1, 0.1, "line_y")
    else:
        for k in range(1, lanes):
            if k == lanes // 2:
                line(xc - 0.12, y0, y1, 0.1, "line_y")
                line(xc + 0.12, y0, y1, 0.1, "line_y")
                continue
            x = xc - half + k * lane_w
            a = y0
            while a < y1:
                line(x, a, min(a + dash, y1), 0.12, "line")
                a += dash * 2.2
    for s in (-1, 1):
        line(xc + s * (half - 0.3), y0, y1, 0.12, "line")
    for yc in crossings:
        x = xc - half + 0.4
        while x < xc + half - 0.4:
            C.poly("line", [(x, yc - 1.5, gz(yc - 1.5) + 0.014), (x + 0.5, yc - 1.5, gz(yc - 1.5) + 0.014),
                            (x + 0.5, yc + 1.5, gz(yc + 1.5) + 0.014), (x, yc + 1.5, gz(yc + 1.5) + 0.014)],
                   normal=(0, 0, 1))
            x += 1.0
    # 높인 보도 (충돌 메시)
    for s in walk_sides:
        xa, xb = (xc + s * half, xc + s * (half + walk))
        x_in, x_out = (min(xa, xb), max(xa, xb))

        def build(bm, x_in=x_in, x_out=x_out, s=s):
            top, curb, outer = [], [], []
            for i, y in enumerate(ys):
                gg = g[i]
                top.append((bm.verts.new((x_in, y, gg + curb_h)), bm.verts.new((x_out, y, gg + curb_h))))
                outer.append((bm.verts.new((x_in, y, gg - 0.25)), bm.verts.new((x_out, y, gg - 0.25))))
            for i in range(len(ys) - 1):
                a0, a1 = top[i]
                b0, b1 = top[i + 1]
                bm.faces.new((a0, a1, b1, b0))
                o0, o1 = outer[i]
                p0, p1 = outer[i + 1]
                bm.faces.new((o0, a0, b0, p0))      # x_in 면
                bm.faces.new((a1, o1, p1, b1))      # x_out 면
            for (t, o) in ((top[0], outer[0]), (top[-1], outer[-1])):
                bm.faces.new((o[0], o[1], t[1], t[0]))
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        o = C.special(f"{name}_walk_{'w' if s < 0 else 'e'}", build, walk_key)
        o["collider"] = 1
        # 연석 윗면 띠 + 줄눈
        xcurb = xc + s * (half + 0.15)
        for i in range(len(ys) - 1):
            C.poly("curb", [(xcurb - 0.15, ys[i], g[i] + curb_h + 0.006), (xcurb + 0.15, ys[i], g[i] + curb_h + 0.006),
                            (xcurb + 0.15, ys[i + 1], g[i + 1] + curb_h + 0.006),
                            (xcurb - 0.15, ys[i + 1], g[i + 1] + curb_h + 0.006)], normal=(0, 0, 1))
        y = y0 + 1.6
        while y < y1 - 0.2:
            zz = ground.h(xc, y) + curb_h + 0.008
            C.poly("pave_d", [(x_in + 0.3, y - 0.025, zz), (x_out, y - 0.025, zz), (x_out, y + 0.025, zz),
                              (x_in + 0.3, y + 0.025, zz)], normal=(0, 0, 1))
            y += 1.6
    return {"road_lo": xc - half, "road_hi": xc + half, "walk_lo": xc - half - walk, "walk_hi": xc + half + walk,
            "curb_h": curb_h}


# ================================================================== lattice mast · tower

def lattice_mast(C, base, *, h=28.0, w0=2.4, w1=0.7, legs=3, yaw=0.0, n_sec=None, bands=7, key_a="mast_r",
                 key_b="mast_w", lid=None, group=None, n_cyan=3, avia=None, n_avia=3, panels=True, mw_dish=True,
                 ladder=True, sign=None, pole=3.2, col=True, pier_h=0.35):
    """격자 철탑 (3각 = 중계탑, 4각 = 송신탑). 항공 장애 표시 띠(주황빨강/흰색 bands개), 위쪽 패널 안테나,
    마이크로파 접시, 사다리, 꼭대기 피뢰 기둥.
    lid: LIGHT_<lid>_01..n_cyan 시안 망 표시등 (group=group 또는 lid, on=0) — 높이마다 모든 다리에 렌즈
    avia: LIGHT_<avia>_01(꼭대기), _02.. (중간 높이, 다리마다) 적색 항공 장애등 (group=avia, on=1, blink=1.2)
    sign: (한글, 로마자) 밑동 앞 표지판. yaw = 앞(표지판·사다리) 방향.
    반환: dict(top, base, legs(밑동 다리 위치), front(앞 방향 단위벡터), r0, leg_at(k, z))."""
    B = Vector(base)
    sn = math.sin(math.pi / legs)
    r0 = w0 / (2 * sn)
    r1 = w1 / (2 * sn)
    a0 = 90.0 if legs == 3 else 45.0
    angs = [math.radians(yaw + a0 + k * 360.0 / legs) for k in range(legs)]
    front = Vector((math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)), 0))

    def leg(k, z):
        r = r0 + (r1 - r0) * z / h
        return B + Vector((math.cos(angs[k]) * r, math.sin(angs[k]) * r, z))
    n = n_sec or max(6, round(h / 2.3))
    zs = [h * i / n for i in range(n + 1)]
    band_h = h / bands
    for i in range(n):
        za, zb = zs[i], zs[i + 1]
        key = key_a if int(((za + zb) / 2) / band_h) % 2 == 0 else key_b
        rl = 0.085 - 0.035 * za / h
        for k in range(legs):
            k2 = (k + 1) % legs
            C.cyl(key, leg(k, za), leg(k, zb), rl, segs=6, cap=False)
            C.beam(key, leg(k, zb), leg(k2, zb), 0.06, 0.06, kind="detail")
            if i % 2 == 0:
                C.beam(key, leg(k, za), leg(k2, zb), 0.05, 0.05, kind="detail")
            else:
                C.beam(key, leg(k2, za), leg(k, zb), 0.05, 0.05, kind="detail")
    # 밑동: 기초 콘크리트 + 앵커판
    for k in range(legs):
        p = leg(k, 0)
        C.box("conc", p.x - 0.4, p.x + 0.4, p.y - 0.4, p.y + 0.4, B.z - 0.5, B.z + pier_h)
        C.box("galv_d", p.x - 0.22, p.x + 0.22, p.y - 0.22, p.y + 0.22, B.z + pier_h, B.z + pier_h + 0.05,
              kind="detail")
        if col:
            C.col(p.x - 0.4, p.x + 0.4, p.y - 0.4, p.y + 0.4, B.z - 0.5, B.z + pier_h)
            C.col(p.x - 0.12, p.x + 0.12, p.y - 0.12, p.y + 0.12, B.z + pier_h, B.z + 3.0)
    # 꼭대기 단 + 피뢰 기둥
    top = B + Vector((0, 0, h))
    deck = [(top.x + math.cos(a) * (r1 + 0.3), top.y + math.sin(a) * (r1 + 0.3)) for a in angs]
    C.prism("galv_d", deck, top.z - 0.08, top.z + 0.04, kind="detail")
    C.cyl("galv", top, top + Vector((0, 0, pole)), 0.07, r2=0.045, segs=8, kind="detail")
    # 패널 안테나 (면마다, 위쪽)
    if panels:
        zp = h * 0.84
        for k in range(legs):
            a, b = leg(k, zp), leg((k + 1) % legs, zp)
            mid = (a + b) / 2
            out = (mid - Vector((B.x, B.y, mid.z)))
            out.z = 0
            out.normalize()
            yaw_f = math.degrees(math.atan2(out.x, -out.y))
            L = Local(mid + out * 0.32, yaw_f)
            L.chbox(C, "mast_w", (0, 0, 0.75), (0.42, 0.16, 1.6), 0.05)
            L.beam(C, "galv", (0, 0.08, 0.3), (0, 0.4, 0.3), 0.05, 0.05, kind="detail")
            L.beam(C, "galv", (0, 0.08, 1.2), (0, 0.4, 1.2), 0.05, 0.05, kind="detail")
    # 마이크로파 접시 (앞면)
    if mw_dish:
        zd = h * 0.6
        p = B + front * (r0 + (r1 - r0) * 0.6 + 0.1) + Vector((0, 0, zd))
        L = Local(p + front * 0.25, yaw)
        L.cyl(C, "galv", (0, 0.1, 0), (0, -0.22, 0), 0.48, segs=14)
        L.cyl(C, "dish", (0, -0.22, 0), (0, -0.34, 0), 0.48, r2=0.42, segs=14)
        L.beam(C, "galv", (0, 0.1, 0), (0, 0.45, 0), 0.08, 0.08, kind="detail")
    # 사다리 (앞 다리 안쪽, 가로대는 띠)
    if ladder:
        kf = max(range(legs), key=lambda k: math.cos(angs[k] - math.atan2(front.y, front.x)))
        for s in (-1, 1):
            def rail(z, s=s):
                p = leg(kf, z)
                c = Vector((B.x, B.y, p.z))
                inward = (c - p).normalized()
                side = Vector((-inward.y, inward.x, 0))
                return p + inward * 0.22 + side * 0.18 * s
            C.cyl("galv", rail(0.4), rail(h), 0.022, segs=4, cap=False, kind="detail")
        z = 0.7
        while z < h:
            p = leg(kf, z)
            c = Vector((B.x, B.y, p.z))
            inward = (c - p).normalized()
            side = Vector((-inward.y, inward.x, 0))
            q = p + inward * 0.22
            C.strip("galv", q - side * 0.18, q + side * 0.18, 0.035, -inward, lift=0.0, kind="fine")
            C.strip("galv", q - side * 0.18, q + side * 0.18, 0.035, inward, lift=0.0, kind="fine")
            z += 0.5
    # 표시등
    group = group or lid
    if lid:
        fracs = [0.3, 0.55, 0.8][:n_cyan] if n_cyan <= 3 else [0.15 + 0.7 * i / (n_cyan - 1) for i in range(n_cyan)]
        for i, f in enumerate(fracs):
            z = h * f
            pts, br = [], []
            for k in range(legs):
                p = leg(k, z)
                o = p - Vector((B.x, B.y, p.z))
                o.normalize()
                q = p + o * 0.34 - Vector((0, 0, 0.0))
                pts.append(q)
                br.append((p, q))
            beacon(C, f"{lid}_{i + 1:02d}", pts, color=CYAN, group=group, on=0, r=0.2, h=0.34, bracket=br)
    if avia:
        beacon(C, f"{avia}_01", [top + Vector((0, 0, pole + 0.02))], color=RED, group="avia", on=1, blink=1.2,
               off_key="alert_d", on_key="alert", r=0.2, h=0.32)
        for i in range(1, n_avia):
            z = h * (1 - i / n_avia) * 0.98
            pts, br = [], []
            for k in range(legs):
                p = leg(k, z)
                o = p - Vector((B.x, B.y, p.z))
                o.normalize()
                q = p + o * 0.3 + Vector((0, 0, 0.25))
                pts.append(q)
                br.append((p, q))
            beacon(C, f"{avia}_{i + 1:02d}", pts, color=RED, group="avia", on=1, blink=1.2, off_key="alert_d",
                   on_key="alert", r=0.18, h=0.28, bracket=br)
    # 표지판 (밑동 앞)
    if sign:
        sp = B + front * (r0 + 1.6)
        L = Local(sp, yaw)
        L.cyl(C, "galv", (-0.7, 0, 0), (-0.7, 0, 1.6), 0.04, segs=6, kind="detail")
        L.cyl(C, "galv", (0.7, 0, 0), (0.7, 0, 1.6), 0.04, segs=6, kind="detail")
        L.plate(C, "navy", hw.rrect(1.9, 0.62, 0.1, 2), (0, -0.05, 1.3), (0, -1, 0), 0.04)
        L.text(C, "white", sign[0], 0.2, (0, -0.095, 1.39), (0, -1, 0), lift=0.004)
        L.text(C, "glow", sign[1], 0.12, (0, -0.095, 1.17), (0, -1, 0), lift=0.004)
        # 고압 주의 삼각 표지
        L.plate(C, "white", hw.rrect(0.62, 0.62, 0.05, 1), (0, -0.05, 0.62), (0, -1, 0), 0.03)
        L.decal(C, "hazard", [(-0.22, -0.12), (0.22, -0.12), (0, 0.24)], (0, -0.08, 0.66), (0, -1, 0), lift=0.004)
        L.text(C, "dark", "!", 0.2, (0, -0.08, 0.64), (0, -1, 0), lift=0.012)
        L.text(C, "dark", "고압 주의", 0.075, (0, -0.08, 0.44), (0, -1, 0), lift=0.008)
        if col:
            L.col(C, -0.97, 0.97, -0.11, 0.05, 0.97, 1.63)         # 판
            L.col(C, -0.33, 0.33, -0.11, 0.05, 0.0, 0.97)          # 고압 표지 (기둥과의 틈 0.35 m는 몸보다 좁다)
            for s in (-1, 1):
                L.col(C, s * 0.7 - 0.05, s * 0.7 + 0.05, -0.05, 0.05, 0.0, 0.97)   # 기둥
    return {"top": top, "base": B, "legs": [leg(k, 0) for k in range(legs)], "front": front, "r0": r0,
            "leg_at": leg}


def dish(C, did, mount, *, yaw=0.0, align_yaw=None, diameter=3.0, arm=None):
    """DISH_<did>: 접시 안테나 노드 (원점 = 받침 축, 로컬 -Y가 접시 정면). 미션은 Z 회전으로 방향을 맞춘다.
    arm = 받침 팔이 붙는 월드 점 (탑 다리). align_yaw = 맞출 방향(도, Blender Z 회전 = three.js Y 회전)."""
    root = cb.empty(f"DISH_{did}", loc=tuple(mount), size=0.5)
    root.rotation_euler = (0, 0, math.radians(yaw))
    root["dish"] = 1
    root["yawDeg"] = round(yaw, 2)
    if align_yaw is not None:
        root["alignYaw"] = round(align_yaw, 2)
    P = Parts()
    R = diameter / 2
    depth = R * 0.32
    n, rings = 18, 3
    # 접시 면 (앞 = -Y, 오목): y = depth*(1-(r/R)^2) - depth
    b = P("dish")
    vs = []
    for j in range(rings + 1):
        r = R * j / rings
        y = -0.35 - depth * (r / R) ** 2 + depth * 0.0
        ring = [b.verts.new((math.cos(2 * math.pi * i / n) * r, y, math.sin(2 * math.pi * i / n) * r)) for i in range(n)]
        vs.append(ring)
    for j in range(rings):
        for i in range(n):
            i2 = (i + 1) % n
            if j == 0:
                f = b.faces.new((vs[0][i], vs[1][i], vs[1][i2]))
            else:
                f = b.faces.new((vs[j][i], vs[j + 1][i], vs[j + 1][i2], vs[j][i2]))
            f.smooth = True
    # 테 + 뒤판 + 받침
    g = P("galv")
    mk._bm_cyl(g, (0, -0.35 - depth - 0.02, 0), (0, -0.35 - depth + 0.08, 0), R + 0.04, segs=n, cap=False)
    mk._bm_cyl(g, (0, -0.2, 0), (0, 0.25, 0), 0.32, segs=10)
    mk._bm_box(g, -0.12, 0.12, 0.2, 0.55, -0.5, 0.5)
    m = P("galv_d")
    for i in range(3):
        a = 2 * math.pi * i / 3 + math.pi / 2
        beam_bm(m, (math.cos(a) * R * 0.92, -0.35 - depth, math.sin(a) * R * 0.92), (0, -0.35 - R * 0.9, 0), 0.04, 0.04)
    mk._bm_cyl(m, (0, -0.35 - R * 0.85, 0), (0, -0.35 - R * 1.0, 0), 0.12, segs=8)
    if arm is not None:
        C.beam("galv", Vector(arm), Vector(mount) + Vector((0, 0, -0.1)), 0.14, 0.14, kind="detail")
    P.nodes(f"DISH_{did}", root)
    C.add_node(root)
    return root


# ================================================================== R41 jammer

def jammer(C, jid, pos, *, yaw=0.0, mount="tripod", hidden=False, col=True, cable_to=None):
    """R41 전파 교란기 JAMMER_<jid> (원작: R41 전파 교란기). 45° 모따기 회백 상자 + 어두운 아랫단 + 앰버 띠 +
    앞판 마젠타 슬릿 3줄·옆 슬릿 + 육각 받침의 안테나 기둥(마젠타 끝) + 기울인 패널 안테나.
    mount: 'tripod'(삼각대) | 'cart'(두 바퀴 손수레, 이동식). 모든 부품이 노드 아래에 있어 hidden=1로 통째로 숨는다.
    자식 JAMMER_<jid>_glow = 마젠타 UNLIT 부품만 (미션이 끄면 '연결 끊김').
    cable_to = 케이블이 이어질 월드 점(탑 다리 등). 반환: dict(front=조작 지점(정면 1 m 앞, 바닥), root)."""
    pos = Vector(pos)
    root = cb.empty(f"JAMMER_{jid}", loc=tuple(pos), size=0.5)
    root.rotation_euler = (0, 0, math.radians(yaw))
    root["jammer"] = 1
    root["glow"] = f"JAMMER_{jid}_glow"
    if hidden:
        root["hidden"] = 1
    P = Parts()
    sh, li, me, am, gl = P("r41_shell"), P("r41_light"), P("r41_metal"), P("amber"), P("magenta")
    zb = 0.6                 # 몸체 밑면
    if mount == "cart":
        for s in (-1, 1):
            mk._bm_cyl(P("tire"), (s * 0.44, 0.08, 0.22), (s * 0.56, 0.08, 0.22), 0.22, segs=12)
            mk._bm_cyl(me, (s * 0.38, 0.08, 0.22), (s * 0.58, 0.08, 0.22), 0.07, segs=6)
        beam_bm(me, (-0.5, 0.08, 0.22), (0.5, 0.08, 0.22), 0.05, 0.05)
        chbox_bm(sh, (0, 0, 0.44), (0.82, 0.7, 0.28), 0.05)
        beam_bm(me, (0, -0.32, 0.32), (0, -0.42, 0.0), 0.05, 0.05)
        mk._bm_box(P("rubber"), -0.06, 0.06, -0.48, -0.36, 0.0, 0.03)
        for s in (-1, 1):
            beam_bm(me, (s * 0.3, 0.3, 0.5), (s * 0.3, 0.86, 1.02), 0.045, 0.045)
        beam_bm(me, (-0.34, 0.86, 1.02), (0.34, 0.86, 1.02), 0.05, 0.05)
        chbox_bm(sh, (0, 0.47, 0.75), (0.5, 0.18, 0.3), 0.04)          # 배터리 상자
        mk._bm_box(am, -0.26, 0.26, 0.37, 0.57, 0.8, 0.83)          # 띠는 상자 면보다 1 cm 밖
    else:
        for k in range(3):
            a = math.radians(90 + 120 * k)
            foot = (math.cos(a) * 0.58, math.sin(a) * 0.58, 0.02)
            beam_bm(me, foot, (math.cos(a) * 0.08, math.sin(a) * 0.08, 0.52), 0.05, 0.05)
            mk._bm_box(P("rubber"), foot[0] - 0.06, foot[0] + 0.06, foot[1] - 0.06, foot[1] + 0.06, 0.0, 0.04)
        hex_prism_bm(sh, (0, 0), 0.12, 0.44, zb)
    # 몸체
    chbox_bm(sh, (0, 0, zb + 0.08), (0.9, 0.56, 0.16), 0.05)
    chbox_bm(li, (0, 0, zb + 0.43), (0.86, 0.52, 0.62), 0.07)
    mk._bm_box(am, -0.44, 0.44, -0.27, 0.27, zb + 0.6, zb + 0.635)      # 띠는 몸체 면보다 1 cm 밖 (같은 편향 등급)
    # 앞판 + 슬릿
    mk._bm_box(sh, -0.33, 0.33, -0.285, -0.255, zb + 0.2, zb + 0.56)
    for zz in (0.27, 0.36, 0.45):
        mk._bm_box(gl, -0.26, 0.26, -0.3, -0.284, zb + zz - 0.016, zb + zz + 0.016)
    for s in (-1, 1):
        mk._bm_box(sh, s * 0.425 - 0.012, s * 0.425 + 0.012, -0.16, 0.16, zb + 0.22, zb + 0.5)
        for yy in (-0.08, 0.0, 0.08):
            mk._bm_box(gl, s * 0.44 - 0.006, s * 0.44 + 0.006, yy - 0.012, yy + 0.012, zb + 0.26, zb + 0.46)
        mk._bm_box(am, s * 0.436 - 0.004, s * 0.436 + 0.004, 0.17, 0.23, zb + 0.24, zb + 0.32)   # 막대 부호
    # 손잡이
    for s in (-1, 1):
        beam_bm(me, (s * 0.32, -0.12, zb + 0.74), (s * 0.32, 0.12, zb + 0.74), 0.04, 0.04)
        # 기둥 끝은 손잡이 속(몸체 윗면 zb + 0.74 아래)에서 끝낸다: 윗면과 같은 높이면 손잡이 밖으로 나온 반쪽이 깜빡인다
        beam_bm(me, (s * 0.32, -0.12, zb + 0.66), (s * 0.32, -0.12, zb + 0.73), 0.035, 0.035)
        beam_bm(me, (s * 0.32, 0.12, zb + 0.66), (s * 0.32, 0.12, zb + 0.73), 0.035, 0.035)
    # 안테나 기둥 (육각 받침 + 육각 고리 + 마젠타 끝). 받침 옆면이 손잡이(x 0.30..0.34) 옆면과 1.5 cm 넘게 떨어지게
    ax, ay = 0.22, 0.1
    hex_prism_bm(sh, (ax, ay), 0.11, zb + 0.73, zb + 0.84)
    mk._bm_cyl(me, (ax, ay, zb + 0.84), (ax, ay, zb + 2.05), 0.022, segs=6)
    for zz in (1.2, 1.6):
        hex_prism_bm(sh, (ax, ay), 0.045, zb + zz, zb + zz + 0.05)
    mk._bm_blob(gl, (ax, ay, zb + 2.09), 0.055, segs=8, rings=5)
    hex_prism_bm(gl, (ax, ay), 0.05, zb + 1.86, zb + 1.9)
    # 패널 안테나 (뒤로 기울임)
    rot = Matrix.Translation((-0.2, 0.06, zb + 0.95)) @ Matrix.Rotation(math.radians(25), 4, "X")
    chbox_bm(li, (0, 0, 0.0), (0.36, 0.05, 0.5), 0.03, matrix=rot)
    mk._bm_box(am, -0.19, 0.19, -0.035, -0.024, -0.2, -0.17, matrix=rot)    # 띠·등은 패널 면보다 1 cm 밖
    mk._bm_box(gl, -0.12, 0.12, -0.036, -0.026, 0.05, 0.07, matrix=rot)
    beam_bm(me, (-0.2, 0.06, zb + 0.66), (-0.2, 0.06, zb + 0.78), 0.05, 0.05)
    # 케이블 (몸체 뒤 → 바닥 → cable_to)
    cab = P("cable")
    pts = [Vector((0.0, 0.27, zb + 0.15)), Vector((0.0, 0.42, zb * 0.5)), Vector((0.05, 0.6, 0.03))]
    if cable_to is not None:
        inv = (Matrix.Translation(pos) @ Matrix.Rotation(math.radians(yaw), 4, "Z")).inverted()
        t = inv @ Vector(cable_to)
        mid = pts[-1].lerp(Vector((t.x, t.y, 0.03)), 0.5) + Vector((0.25, 0, 0))
        pts += [mid, Vector((t.x, t.y, max(0.03, t.z)))]
    for a, b in zip(pts, pts[1:]):
        mk._bm_cyl(cab, a, b, 0.028, segs=6, cap=False)
    P.nodes(f"JAMMER_{jid}", root, glow_key="magenta", glow_name=f"JAMMER_{jid}_glow")
    C.add_node(root)
    L = Local(pos, yaw)
    if col and not hidden:
        L.col(C, -0.48, 0.48, -0.3, 0.3, zb - 0.05, zb + 0.8)     # 몸체 + 손잡이 (밑은 몸보다 낮다)
        L.col(C, -0.13, 0.13, -0.13, 0.13, 0.0, zb - 0.05)        # 받침 기둥 (삼각대 다리는 발목 높이)
    return {"front": L.p(0, -1.0, 0), "root": root, "local": L}


# ================================================================== R41 cover

def r41_barrier(C, x, y, z, *, yaw=0.0, w=1.8, h=0.95, col=True):
    """R41 모따기 차단벽 (회백 + 앰버 띠 + 어두운 밑단). 정면 -Y."""
    L = Local((x, y, z), yaw)
    L.chbox(C, "r41_shell", (0, 0, 0.09), (w + 0.06, 0.62, 0.18), 0.05)
    L.chbox(C, "r41_light", (0, 0, 0.18 + (h - 0.18) / 2), (w, 0.42, h - 0.18), 0.09)
    for s in (-1, 1):
        L.rect(C, "amber", (0, s * 0.211, h * 0.72), (0, s, 0), w * 0.9, 0.07, lift=0.006)
        L.rect(C, "r41_shell", (s * w * 0.32, s * 0.211, h * 0.45), (0, s, 0), 0.06, 0.22, lift=0.006)
    if col:
        L.col(C, -w / 2, w / 2, -0.3, 0.3, 0, h)


def r41_crate(C, x, y, z, *, yaw=0.0, s=(0.9, 0.6, 0.5), col=True, stack=1):
    """R41 보급 상자 (제국 흑 몸통 + 회백 뚜껑 + 앰버 띠)."""
    L = Local((x, y, z), yaw)
    for k in range(stack):
        zb = k * s[2]
        L.chbox(C, "r41_shell", (0, 0, zb + s[2] / 2), s, 0.05)
        L.chbox(C, "r41_light", (0, 0, zb + s[2] - 0.035), (s[0] + 0.02, s[1] + 0.02, 0.08), 0.03, kind="detail")
        L.rect(C, "amber", (0, -s[1] / 2, zb + s[2] * 0.45), (0, -1, 0), s[0] * 0.7, 0.05, lift=0.006)
        L.rect(C, "amber", (s[0] / 2, 0, zb + s[2] * 0.45), (1, 0, 0), s[1] * 0.6, 0.05, lift=0.006)
    if col:
        L.col(C, -s[0] / 2, s[0] / 2, -s[1] / 2, s[1] / 2, 0, s[2] * stack)


# ================================================================== site equipment

def breaker_cabinet(C, pos, *, yaw=0.0, label=("전력함", "POWER"), w=0.95, d=0.45, h=1.35, key="cab", col=True):
    """전력 분배함(차단기 함): 받침 + 청회색 함 + 지붕 + 문 두 짝 + 손잡이 + 고압 표지 + 옆 레버. 정면 -Y.
    반환: dict(front=조작 지점(정면 0.65 m 앞, 바닥 높이))."""
    L = Local(pos, yaw)
    L.box(C, "conc", -w / 2 - 0.12, w / 2 + 0.12, -d / 2 - 0.12, d / 2 + 0.12, -0.2, 0.12)
    L.box(C, key, -w / 2, w / 2, -d / 2, d / 2, 0.12, 0.12 + h)
    L.box(C, "cab_d", -w / 2 - 0.05, w / 2 + 0.05, -d / 2 - 0.08, d / 2 + 0.05, 0.12 + h, 0.2 + h, kind="detail")
    zc = 0.12 + h / 2
    L.rect(C, "cab_d", (0, -d / 2, zc), (0, -1, 0), 0.02, h - 0.12, lift=0.004)
    for s in (-1, 1):
        # 문짝 테만 그린다 (문짝은 함과 같은 색: 테 판 위에 문짝 판을 2 mm 띄워 덮으면 먼 거리에서 깜빡인다)
        L.frame_rect(C, "cab_d", (s * w / 4, -d / 2, zc), (0, -1, 0), w / 2 - 0.08, h - 0.14, 0.02, lift=0.002)
        L.beam(C, "steel", (s * 0.06, -d / 2 - 0.03, zc - 0.12), (s * 0.06, -d / 2 - 0.03, zc + 0.12), 0.03, 0.03,
               kind="detail")
        for zz in (zc + h * 0.3, zc - h * 0.3):
            L.rect(C, "dark", (s * (w / 2 - 0.02), -d / 2, zz), (0, -1, 0), 0.03, 0.1, lift=0.006)
    L.decal(C, "hazard", [(-0.12, -0.1), (0.12, -0.1), (0, 0.11)], (-w / 4, -d / 2, zc + 0.3), (0, -1, 0), lift=0.006,
            kind="under")                                   # 표지 판 = under, 그 위 '!' = fine
    L.text(C, "dark", "!", 0.1, (-w / 4, -d / 2, zc + 0.29), (0, -1, 0), lift=0.01)
    L.plate(C, "navy", hw.rrect(0.42, 0.18, 0.04, 1), (w / 4, -d / 2, zc + 0.35), (0, -1, 0), 0.01)
    L.text(C, "white", label[0], 0.07, (w / 4, -d / 2 - 0.012, zc + 0.37), (0, -1, 0), lift=0.002)
    L.text(C, "glow_off", label[1], 0.04, (w / 4, -d / 2 - 0.012, zc + 0.3), (0, -1, 0), lift=0.002)
    # 옆 레버 (빨강) + 배선관
    L.box(C, "dark", w / 2, w / 2 + 0.08, -0.08, 0.08, zc - 0.1, zc + 0.1, kind="detail")
    L.beam(C, "red", (w / 2 + 0.08, 0, zc), (w / 2 + 0.12, -0.05, zc + 0.3), 0.04, 0.04, kind="detail")
    L.cyl(C, "galv_d", (0, d / 2 - 0.1, 0.12), (0, d / 2 - 0.1, -0.2), 0.06, segs=6, kind="detail")
    if col:
        L.col(C, -w / 2 - 0.12, w / 2 + 0.12, -d / 2 - 0.12, d / 2 + 0.12, -0.2, 0.12)      # 받침
        L.col(C, -w / 2 - 0.05, w / 2 + 0.12, -d / 2 - 0.08, d / 2 + 0.05, 0.12, 0.2 + h)   # 함 + 지붕 + 레버
    return {"front": L.p(0, -d / 2 - 0.65, 0.0), "local": L}


def control_box(C, pos, *, yaw=0.0, label=("송신 제어함", "TX CONTROL"), w=1.6, d=0.9, h=1.55, col=True):
    """송신탑 밑동 제어함(작은 함체 + 계량기 창 + 문 + 지붕 차양)."""
    L = Local(pos, yaw)
    L.box(C, "conc", -w / 2 - 0.15, w / 2 + 0.15, -d / 2 - 0.15, d / 2 + 0.15, -0.3, 0.1)
    L.chbox(C, "cab", (0, 0, 0.1 + h / 2), (w, d, h), 0.05)
    L.box(C, "cab_d", -w / 2 - 0.08, w / 2 + 0.08, -d / 2 - 0.15, d / 2 + 0.08, 0.1 + h, 0.18 + h, kind="detail")
    zc = 0.1 + h / 2
    L.frame_rect(C, "cab_d", (-w / 4, -d / 2, zc), (0, -1, 0), w / 2 - 0.08, h - 0.2, 0.02, lift=0.003)   # 문짝 테
    L.beam(C, "steel", (-0.12, -d / 2 - 0.03, zc - 0.1), (-0.12, -d / 2 - 0.03, zc + 0.1), 0.03, 0.03, kind="detail")
    L.rect(C, "screen", (w / 4, -d / 2, zc + 0.25), (0, -1, 0), 0.42, 0.24, lift=0.006)
    L.rect(C, "dark", (w / 4, -d / 2, zc - 0.05), (0, -1, 0), 0.5, 0.18, lift=0.006, kind="under")   # 등 판 (등 = fine)
    for k in range(3):
        L.rect(C, ("glow_off", "alert_d", "glow_off")[k], (w / 4 - 0.15 + 0.15 * k, -d / 2, zc - 0.05), (0, -1, 0),
               0.07, 0.07, lift=0.01)
    L.plate(C, "navy", hw.rrect(0.9, 0.24, 0.05, 1), (0, -d / 2, 0.1 + h - 0.2), (0, -1, 0), 0.01)
    L.text(C, "white", label[0], 0.08, (0, -d / 2 - 0.012, 0.1 + h - 0.17), (0, -1, 0), lift=0.002)
    L.text(C, "glow_off", label[1], 0.045, (0, -d / 2 - 0.012, 0.1 + h - 0.25), (0, -1, 0), lift=0.002)
    L.decal(C, "hazard", [(-0.1, -0.09), (0.1, -0.09), (0, 0.1)], (-w / 4, -d / 2, zc + 0.45), (0, -1, 0), lift=0.008)
    if col:
        L.col(C, -w / 2 - 0.15, w / 2 + 0.15, -d / 2 - 0.15, d / 2 + 0.15, -0.3, 0.1)       # 받침
        L.col(C, -w / 2 - 0.08, w / 2 + 0.08, -d / 2 - 0.15, d / 2 + 0.08, 0.1, 0.18 + h)   # 함 + 차양
    return {"front": L.p(-w / 4, -d / 2 - 0.65, 0.0), "local": L}


def dish_control(C, pos, *, yaw=0.0, col=True):
    """접시 방향 조정반: 기둥 받침 + 기울인 조작판(화면, 핸들 바퀴, 방위 눈금). 정면 -Y."""
    L = Local(pos, yaw)
    L.box(C, "conc", -0.35, 0.35, -0.3, 0.3, -0.2, 0.1)
    L.box(C, "cab_d", -0.14, 0.14, -0.12, 0.12, 0.1, 0.78)
    rot = Matrix.Translation((0, -0.05, 0.88)) @ Matrix.Rotation(math.radians(-35), 4, "X")
    L.chbox(C, "cab", (0, 0, 0), (0.7, 0.42, 0.12), 0.03, rot=rot)
    m = L.M @ rot
    n = (m.to_3x3() @ Vector((0, 0, 1))).normalized()
    up = (m.to_3x3() @ Vector((0, 1, 0))).normalized()
    c = m @ Vector((0, 0, 0.061))
    C.rect("screen", c + (m.to_3x3() @ Vector((-0.14, 0.04, 0))), n, 0.3, 0.2, up=up, lift=0.004)
    C.ring("glow_off", hw.circle(0.11, 16), hw.circle(0.085, 16), c + (m.to_3x3() @ Vector((0.18, 0.02, 0))), n, up=up,
           lift=0.004)
    for k in range(7):
        a = math.radians(-60 + 20 * k)
        p = c + (m.to_3x3() @ Vector((-0.14 + 0.13 * math.sin(a), -0.13 + 0.03 * math.cos(a), 0)))
        C.rect("white", p, n, 0.012, 0.03, up=up, lift=0.004)
    # 핸들 바퀴
    hc = L.p(0.42, -0.02, 0.78)
    C.cyl("dark", hc - L.d(0.04, 0, 0), hc + L.d(0.04, 0, 0), 0.16, segs=10, cap=False, kind="detail")
    C.cyl("steel", hc - L.d(0.06, 0, 0), hc + L.d(0.06, 0, 0), 0.04, segs=6, kind="detail")
    if col:
        L.col(C, -0.35, 0.35, -0.3, 0.3, -0.2, 0.1)           # 받침
        L.col(C, -0.14, 0.14, -0.12, 0.12, 0.1, 0.7)          # 기둥
        L.col(C, -0.37, 0.49, -0.27, 0.17, 0.62, 1.06)        # 기울인 조작판 + 핸들 바퀴
    return {"front": L.p(0, -0.85, 0.0), "local": L}


def generator(C, pos, *, yaw=0.0, w=2.4, d=1.2, h=1.35, col=True, label=("발전기", "GENERATOR")):
    """이동식 디젤 발전기: 강재 받침 + 모따기 함체 + 루버 + 배기관 + 앞 조작반(꺼진 화면, 등) + 표지. 정면 -Y.
    반환: dict(front=조작반 앞 0.7 m 바닥, panel=조작반 중심)."""
    L = Local(pos, yaw)
    L.box(C, "conc", -w / 2 - 0.3, w / 2 + 0.3, -d / 2 - 0.3, d / 2 + 0.3, -0.2, 0.1)
    L.box(C, "metal", -w / 2 - 0.05, w / 2 + 0.05, -d / 2, d / 2, 0.1, 0.28, kind="detail")
    L.chbox(C, "cab", (0, 0, 0.28 + h / 2), (w, d, h), 0.08)
    L.box(C, "hazard", -w / 2 + 0.02, w / 2 - 0.02, -d / 2 - 0.002, d / 2 + 0.002, 0.3, 0.38, kind="detail")
    for s in (-1, 1):
        for k in range(5):
            L.rect(C, "cab_d", (-w / 2 + 0.45 + k * 0.12, s * d / 2, 0.28 + h * 0.62), (0, s, 0), 0.05, h * 0.42,
                   lift=0.006)
    L.cyl(C, "dark", (w / 2 - 0.35, 0.2, 0.28 + h), (w / 2 - 0.35, 0.2, 0.28 + h + 0.5), 0.07, segs=8, kind="detail")
    L.cyl(C, "dark", (w / 2 - 0.35, 0.2, 0.28 + h + 0.5), (w / 2 - 0.15, 0.2, 0.28 + h + 0.58), 0.07, segs=8,
          kind="detail")
    pc = (-w / 4, -d / 2, 0.28 + h * 0.55)
    L.plate(C, "navy", hw.rrect(0.8, 0.6, 0.06, 2), pc, (0, -1, 0), 0.03)
    L.rect(C, "screen", (pc[0] - 0.12, -d / 2 - 0.03, pc[2] + 0.1), (0, -1, 0), 0.32, 0.18, lift=0.004)
    for k, key in enumerate(("alert_d", "glow_off", "glow_off")):
        L.rect(C, key, (pc[0] + 0.2, -d / 2 - 0.03, pc[2] + 0.16 - 0.1 * k), (0, -1, 0), 0.06, 0.06, lift=0.006)
    L.beam(C, "red", (pc[0] - 0.12, -d / 2 - 0.05, pc[2] - 0.15), (pc[0] - 0.12, -d / 2 - 0.12, pc[2] - 0.15), 0.06,
           0.06, kind="detail")
    L.text(C, "white", label[0], 0.12, (w / 5, -d / 2, 0.28 + h * 0.72), (0, -1, 0), lift=0.008)
    L.text(C, "dark", label[1], 0.07, (w / 5, -d / 2, 0.28 + h * 0.6), (0, -1, 0), lift=0.008)
    if col:
        L.col(C, -w / 2 - 0.3, w / 2 + 0.3, -d / 2 - 0.3, d / 2 + 0.3, -0.2, 0.1)           # 받침
        L.col(C, -w / 2 - 0.05, w / 2 + 0.05, -d / 2 - 0.12, d / 2, 0.1, 0.28 + h)          # 함체 + 앞 조작반
    return {"front": L.p(pc[0], -d / 2 - 0.7, 0.0), "panel": L.p(*pc), "local": L}


def fuel_tank(C, pos, *, yaw=0.0, length=2.2, r=0.55, col=True):
    """누운 원통 연료 탱크 + 받침 두 개."""
    L = Local(pos, yaw)
    for s in (-1, 1):
        L.box(C, "conc", s * length * 0.3 - 0.15, s * length * 0.3 + 0.15, -r * 0.8, r * 0.8, -0.1, r * 0.6)
    L.cyl(C, "white", (-length / 2, 0, r + 0.25), (length / 2, 0, r + 0.25), r, segs=14)
    L.rect(C, "red", (0, -r, r + 0.25), (0, -1, 0), length * 0.5, 0.1, lift=0.01)
    L.text(C, "red", "경유 · DIESEL", 0.14, (0, -r - 0.01, r + 0.45), (0, -1, 0), lift=0.01)
    L.cyl(C, "dark", (length * 0.3, 0, 2 * r + 0.2), (length * 0.3, 0, 2 * r + 0.42), 0.08, segs=8, kind="detail")
    if col:
        pts = [(s * length / 2, r * math.cos(2 * math.pi * k / 12), r + 0.25 + r * math.sin(2 * math.pi * k / 12))
               for s in (-1, 1) for k in range(12)]
        pts += [(s * (length * 0.3 + 0.15), t * r * 0.8, -0.1) for s in (-1, 1) for t in (-1, 1)]
        L.ccol(C, pts)                                       # 누운 원통 + 받침 (볼록 껍질)


def cable(C, pts, *, r=0.03, key="cable"):
    """바닥·벽을 따라가는 케이블 (꺾은선)."""
    for a, b in zip(pts, pts[1:]):
        C.cyl(key, Vector(a), Vector(b), r, segs=6, cap=False, kind="detail")


# ================================================================== fences

def chain_fence(C, p0, p1, *, z0, z1=None, h=2.0, pitch=2.6, gaps=(), col=True, wire=True, mid=True, key="fence_p",
                mesh="mesh_a", ground=None):
    """철망 울타리 (4각 기둥 + 위(·가운데) 가로대 + 반투명 망 + 가시줄). 축 정렬 구간에서 COL 박스를 만든다.
    gaps = [(t0, t1)] p0에서 잰 거리 구간(문·부서진 틈). ground가 있으면 바닥 높이를 따라간다.
    한 칸 삼각형: 가시줄·가운데 가로대 있음 약 40, 없음 약 18."""
    P0 = Vector((p0[0], p0[1], 0))
    P1 = Vector((p1[0], p1[1], 0))
    d = P1 - P0
    L = d.length
    t = d.normalized()
    z1 = z0 if z1 is None else z1

    def zf(s):
        q = P0 + t * s
        return ground.h(q.x, q.y) if ground else z0 + (z1 - z0) * s / L

    segs, a = [], 0.0
    for (g0, g1) in sorted(gaps):
        if g0 > a:
            segs.append((a, g0))
        a = max(a, g1)
    if a < L:
        segs.append((a, L))
    nrm = Vector((-t.y, t.x, 0))
    for (a, b) in segs:
        n = max(1, int(math.ceil((b - a) / pitch)))
        ss = [a + (b - a) * k / n for k in range(n + 1)]
        for k, sk in enumerate(ss):
            q = P0 + t * sk
            zz = zf(sk)
            C.cyl(key, (q.x, q.y, zz - 0.2), (q.x, q.y, zz + h + 0.05), 0.05, segs=4, cap=False, kind="detail")
            if wire:
                C.cyl(key, Vector((q.x, q.y, zz + h)), Vector((q.x, q.y, zz + h)) + nrm * 0.35 + Vector((0, 0, 0.25)),
                      0.02, segs=3, cap=False, kind="detail")
        for k in range(n):
            qa, qb = P0 + t * ss[k], P0 + t * ss[k + 1]
            za, zb = zf(ss[k]), zf(ss[k + 1])
            for hh in ((h, h * 0.5) if mid else (h,)):
                C.cyl(key, (qa.x, qa.y, za + hh), (qb.x, qb.y, zb + hh), 0.025, segs=4, cap=False, kind="detail")
            C.poly(mesh, [(qa.x, qa.y, za + 0.05), (qb.x, qb.y, zb + 0.05), (qb.x, qb.y, zb + h),
                          (qa.x, qa.y, za + h)])
            if wire:
                for (u, v) in ((0.18, 0.13), (0.35, 0.25)):
                    A = Vector((qa.x, qa.y, za + h + v)) + nrm * u
                    B = Vector((qb.x, qb.y, zb + h + v)) + nrm * u
                    C.cyl("dark", A, B, 0.008, segs=3, cap=False, kind="fine")
        if col:
            qa, qb = P0 + t * a, P0 + t * b
            zl = min(zf(a), zf(b))
            zh = max(zf(a), zf(b))
            C.col(min(qa.x, qb.x) - 0.08, max(qa.x, qb.x) + 0.08, min(qa.y, qb.y) - 0.08, max(qa.y, qb.y) + 0.08,
                  zl - 0.5, zh + h + 0.3)
    return segs


def fence_gate(C, hinge, *, yaw=0.0, w=3.0, h=1.9, swing=70.0, key="fence_p", mesh="mesh_a", col=True):
    """문짝 하나 (관 테 + 대각 + 망). hinge = 경첩 바닥 점, 닫히면 로컬 +X로 뻗는다. swing(도)만큼 열어 둔다."""
    L = Local(hinge, yaw + swing)
    for (a, b) in (((0, 0, 0.1), (w, 0, 0.1)), ((0, 0, h), (w, 0, h)), ((0, 0, 0.1), (0, 0, h)),
                   ((w, 0, 0.1), (w, 0, h)), ((0, 0, 0.1), (w, 0, h))):
        L.cyl(C, key, a, b, 0.035, segs=6, kind="detail")
    C.poly(mesh, [L.p(0, 0, 0.12), L.p(w, 0, 0.12), L.p(w, 0, h), L.p(0, 0, h)])
    if col:
        L.col(C, -0.04, w + 0.04, -0.06, 0.06, 0.0, h + 0.04)      # 열어 둔 문짝


# ================================================================== street props

def sandbags(C, x, y, z, *, yaw=0.0, n=4, rows=3, col=True, key="sand"):
    """싼 모래주머니 벽 (주머니 하나 24 삼각형 + 묶음 끈). 정면 -Y. 높이 rows*0.21+0.06 m."""
    L = Local((x, y, z), yaw)
    for row in range(rows):
        cnt = n - (row % 2)
        for k in range(cnt):
            off = -0.29 * (cnt - 1) + k * 0.58
            p = L.p(off, 0, 0.12 + row * 0.21)
            C.blob(key, tuple(p), 0.31, (1.0, 0.58, 0.4), segs=6, rings=3, rot_z=math.radians(yaw + (k * 7 % 5) - 2))
            C.strip("sand_d", p + L.d(-0.1, -0.175, 0.0), p + L.d(0.1, -0.175, 0.0), 0.025, L.d(0, -1, 0), lift=0.0)
    if col:
        L.col(C, -0.29 * n - 0.05, 0.29 * n + 0.05, -0.2, 0.2, 0, rows * 0.21 + 0.06)
    return L.p(0, -0.7, 0)


def car(C, x, y, z, *, yaw=0.0, key="car_b", wreck=False, col=True, seed=0):
    """엘프 소형차 (길이 3.2 m, 폭 1.5 m). wreck=True면 불탄 차체·빠진 바퀴·검은 창. 정면(-Y)이 앞."""
    rng = random.Random(seed)
    L = Local((x, y, z), yaw)
    body = "wreck" if wreck else key
    tilt = Matrix.Rotation(math.radians(rng.uniform(-4, 4) if wreck else 0), 4, "Y")
    L.chbox(C, body, (0, 0, 0.52), (1.5, 3.2, 0.62), 0.14, rot=tilt)
    L.chbox(C, body if wreck else "car_w", (0, 0.25, 1.05), (1.32, 1.75, 0.5), 0.16, rot=tilt)
    win = "dark" if wreck else "glass_d"
    L.rect(C, win, (0, -0.63, 1.06), (0, -1, 0.55), 1.1, 0.34, lift=0.02)
    L.rect(C, win, (0, 1.13, 1.06), (0, 1, 0.5), 1.1, 0.32, lift=0.02)
    for s in (-1, 1):
        L.rect(C, win, (s * 0.665, 0.25, 1.08), (s, 0, 0), 1.45, 0.3, lift=0.02)
        for (yy, gone) in ((-1.0, wreck and s > 0), (1.05, False)):
            if gone:
                L.box(C, "dark", s * 0.75 - 0.05, s * 0.75 + 0.05, yy - 0.2, yy + 0.2, 0.0, 0.25, kind="detail")
                continue
            L.cyl(C, "tire", (s * 0.66, yy, 0.3), (s * 0.8, yy, 0.3), 0.3, segs=10)
            L.cyl(C, "rust" if wreck else "steel", (s * 0.8, yy, 0.3), (s * 0.81, yy, 0.3), 0.17, segs=8,
                  kind="detail")
    L.rect(C, "alert_d" if wreck else "red", (0, 1.6, 0.62), (0, 1, 0), 1.2, 0.1, lift=0.015)
    L.rect(C, "dark" if wreck else "lamp_off", (0, -1.6, 0.6), (0, -1, 0), 1.2, 0.12, lift=0.015)
    if wreck:
        C.decal("soot", hw.circle(1.6, 10), L.p(0, 0, 0), (0, 0, 1), lift=0.03)
        C.decal("soot", hw.circle(0.6, 8), L.p(0.2, 0.3, 1.31), (0, 0, 1), lift=0.01)
    if col:
        L.col(C, -0.8, 0.8, -1.6, 1.6, 0, 0.83)             # 차체 + 바퀴
        L.col(C, -0.66, 0.66, -0.63, 1.13, 0.83, 1.3)       # 객실


def rubble(C, x, y, z, *, r=1.6, seed=0, n=7, key="concrete_d", col=True):
    """무너진 잔해 더미 (덩어리 + 철근)."""
    rng = random.Random(seed)
    chunks = []
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, r * 0.7)
        s = rng.uniform(0.35, 0.75) * r * 0.6
        c = (x + math.cos(a) * d, y + math.sin(a) * d, z + s * 0.25)
        size = (s, s * rng.uniform(0.6, 1.2), s * 0.6)
        rot = (rng.uniform(-20, 20), rng.uniform(-20, 20), rng.uniform(0, 90))
        C.rbox(key if i % 3 else "concrete", c, size, rot)
        chunks.append((c, size, rot))
    for i in range(3):
        a = rng.uniform(0, 2 * math.pi)
        p0 = Vector((x + math.cos(a) * 0.3, y + math.sin(a) * 0.3, z + 0.3))
        p1 = p0 + Vector((math.cos(a + 0.6) * r * 0.8, math.sin(a + 0.6) * r * 0.8, rng.uniform(0.2, 0.8)))
        C.cyl("rust", p0, p1, 0.02, segs=4, cap=False, kind="detail")
    if col:
        # 덩어리마다 볼록 껍질 (예전 축 정렬 상자는 덩어리 사이 빈 곳을 막고 바깥 덩어리는 놓쳤다).
        # 발목 높이(0.12 m 아래)만 남는 덩어리는 넘어가게 둔다
        for (c, size, rot) in chunks:
            Mx = (Matrix.Translation(Vector(c)) @ Matrix.Rotation(math.radians(rot[2]), 4, "Z")
                  @ Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
            hx, hy, hz = (v / 2 for v in size)
            pts = [Mx @ Vector((u * hx, v * hy, w * hz)) for u in (-1, 1) for v in (-1, 1) for w in (-1, 1)]
            if max(p.z for p in pts) - z < 0.12:
                continue
            C.ccol([tuple(p) for p in pts])


def utility_pole(C, x, y, z, *, h=7.5, yaw=0.0):
    """나무 전봇대 + 가로 완목 + 애자. 반환: 전선이 걸리는 점 3개."""
    L = Local((x, y, z), yaw)
    L.cyl(C, "pole", (0, 0, -0.3), (0, 0, h), 0.13, r2=0.1, segs=8, kind="detail")
    L.beam(C, "pole", (-1.0, 0, h - 0.5), (1.0, 0, h - 0.5), 0.12, 0.12, kind="detail")
    pts = []
    for u in (-0.85, 0.0, 0.85):
        L.cyl(C, "white", (u, 0, h - 0.44), (u, 0, h - 0.3), 0.05, segs=6, kind="detail")
        pts.append(L.p(u, 0, h - 0.3))
    L.box(C, "dark", -0.25, 0.25, 0.12, 0.42, h - 2.2, h - 1.5, kind="detail")   # 변압기
    C.col(x - 0.13, x + 0.13, y - 0.13, y + 0.13, z - 0.3, z + h)                 # 기둥 (밑동 반지름 0.13)
    return pts


def wires(C, a_pts, b_pts, *, sag=0.6, n=4):
    for a, b in zip(a_pts, b_pts):
        P = []
        for k in range(n + 1):
            t = k / n
            q = Vector(a).lerp(Vector(b), t) - Vector((0, 0, sag * 4 * t * (1 - t)))
            P.append(q)
        for p, q in zip(P, P[1:]):
            C.cyl("cable", p, q, 0.012, segs=3, cap=False, kind="fine")


# ================================================================== far LOD

def core_far(C, x, y, z, *, h=60.0, lit=False, r0=9.0):
    """코어 AI 탑 원경 LOD (도시 키트 core_ai의 형태를 크게·단순하게): 둥근 기단, 가늘어지는 탑, 띠 6개,
    꼭대기 관 + 후광 고리 + 등. lit=False면 띠가 꺼진 시안(glow_off)."""
    gk = "glow" if lit else "glow_off"
    C.cyl("stone", (x, y, z - 2), (x, y, z + 8), r0, segs=20, kind="far")
    C.cyl("navy", (x, y, z + 8), (x, y, z + 8.8), r0 + 0.4, segs=20, kind="far")
    C.cyl("concrete", (x, y, z + 8.8), (x, y, z + h), r0 * 0.5, r2=r0 * 0.36, segs=16, kind="far")
    for i in range(6):
        zz = z + 14 + i * (h - 20) / 6
        rr = r0 * 0.5 - (r0 * 0.14) * (zz - z - 8.8) / (h - 8.8) + 0.3
        C.cyl("navy", (x, y, zz - 0.7), (x, y, zz + 0.7), rr, segs=16, kind="far")
        C.cyl(gk, (x, y, zz - 0.25), (x, y, zz + 0.25), rr + 0.06, segs=16, cap=False)
    C.cyl("navy", (x, y, z + h), (x, y, z + h + 2), r0 * 0.42, r2=r0 * 0.2, segs=16, kind="far")
    C.cyl("gold", (x, y, z + h + 2), (x, y, z + h + 11), 0.3, segs=6, kind="far")
    mk._bm_torus(C.bm("gold", "far"), (x, y, z + h + 5.5), r0 * 0.55, 0.3, seg=20, rseg=4)
    C.blob(gk, (x, y, z + h + 11.6), 0.9, segs=8, rings=5)


def far_block(C, x0, x1, y0, y1, z0, z1, *, key="far", win_key="far_d", faces=("-x",), bands=True, kind="far"):
    """원경 건물 상자 (바닥면 없음) + 보는 쪽 면의 창 띠."""
    mk.lod_box(C, key, x0, x1, y0, y1, z0, z1, kind=kind)
    if not bands:
        return
    H = z1 - z0
    nb = max(1, int(H / 6.0))
    for f in faces:
        N = mk.FRONT[f]
        if f in ("-x", "+x"):
            c = Vector((x0 if f == "-x" else x1, (y0 + y1) / 2, 0))
            L = y1 - y0
        else:
            c = Vector(((x0 + x1) / 2, y0 if f == "-y" else y1, 0))
            L = x1 - x0
        for i in range(nb):
            zc = z0 + 3.0 + i * (H - 4.0) / nb
            C.rect(win_key, c + Vector((0, 0, zc)), N, L * 0.85, 1.2, lift=0.08)


def building_col(C, x0, x1, y0, y1, z0, z1, *, r=1.0):
    """도시 키트 building()의 둥근 모서리 평면(rrect)을 그대로 세운 볼록 COL_. building(col=False)와 함께 쓴다
    (키트의 축 정렬 상자는 둥근 모서리 밖으로 0.3 m쯤 남는다)."""
    r = min(r, (x1 - x0) / 2 - 0.1, (y1 - y0) / 2 - 0.1)
    fp = hw.rrect(x1 - x0, y1 - y0, r, 3, (x0 + x1) / 2, (y0 + y1) / 2)
    C.ccol([(x, y, z0) for x, y in fp] + [(x, y, z1) for x, y in fp])


def lod_house(C, x, y, z, *, w=8.0, d=7.0, h=5.6, axis="x", wall="warm", roof="roof", kind="main"):
    """원경·경계 밖 박공집 (삼각형 14개)."""
    mk.lod_gable(C, wall, roof, x - w / 2, x + w / 2, y - d / 2, y + d / 2, z - 0.5, z + h, z + h + 2.2, axis=axis,
                 kind=kind)


# ================================================================== radio station (전파국)

def radio_station(C, origin, *, yaw=-90.0, name=("모나티엄 전파국", "MONATIUM RADIO"), lid="site_b", group=None,
                  avia=None, seed=5):
    """전파국: 2층 본관(로컬 x -7..7, y 0..12) + 앞쪽 1층 장비실(x -6..6, y -8..0, 열린 출입구 1.4×2.0 m)
    + 장비실 옥상 테라스(바깥 계단, 로컬 +X 옆) + 본관 옥상 안테나.
    origin = 장비실 뒷벽 가운데 바닥(마당 높이), yaw = Z 회전(로컬 -Y = 정면 = 출입구 쪽). 90° 배수만 COL이 정확하다.
    장비실: 바닥 0.15, 천장 2.85, 지붕 3.1(테라스 바닥), 파라펫 0.6.
    LIGHT_<lid>_01·02 안테나 시안 표시등, _03 ON AIR 등, _04 간판 밑줄, _05 콘솔 화면 (group=group or lid, on=0)
    LIGHT_<avia>_01 안테나 꼭대기 항공 장애등. 반환: 미션 지점 dict."""
    group = group or lid
    L = Local(origin, yaw)
    O = Vector(origin)
    FL = 0.15            # 장비실 바닥
    CE = 2.85            # 천장
    RF = 3.1             # 지붕(테라스) 윗면
    T = 0.25             # 벽 두께
    # ---------------------------------------------------------- 본관 (도시 키트 건물)
    corners = [L.p(x, y) for x in (-7, 7) for y in (0, 12)]
    wx0, wx1 = min(p.x for p in corners), max(p.x for p in corners)
    wy0, wy1 = min(p.y for p in corners), max(p.y for p in corners)
    fd = L.d(0, -1)
    front = "-x" if fd.x < -0.5 else "+x" if fd.x > 0.5 else "-y" if fd.y < -0.5 else "+y"
    bld = mk.building(C, wx0, wx1, wy0, wy1, floors=1, style="office", front=front, sides="-y+y-x+x", seed=seed,
                      door=False, h0=3.1, fh=2.8, z=O.z, r=0.6, cctv=False, col=False)
    building_col(C, wx0, wx1, wy0, wy1, O.z, bld["top"], r=0.6)
    H = bld["top"] - O.z
    # ---------------------------------------------------------- 장비실 바닥·벽·지붕
    L.box(C, "floor_in", -6, 6, -8, 0, -0.35, FL, col=True)
    L.box(C, "concrete", -6, -0.7, -8, -8 + T, FL, CE, col=True)              # 앞벽 (출입구 왼쪽)
    L.box(C, "concrete", 0.7, 6, -8, -8 + T, FL, CE, col=True)                # 앞벽 (오른쪽)
    L.box(C, "concrete", -0.7, 0.7, -8, -8 + T, 2.15, CE, col=True)           # 상인방
    for s in (-1, 1):
        L.box(C, "concrete", s * 6 - (T if s > 0 else 0), s * 6 + (0 if s > 0 else T), -8 + T, 0, FL, CE, col=True)
    L.box(C, "concrete", -6.1, 6.1, -8.1, 0, CE, RF - 0.02, col=True)        # 지붕 슬래브
    L.box(C, "roof", -5.9, 5.9, -7.9, -0.05, RF - 0.02, RF)
    L.box(C, "concrete_d", -6.14, 6.14, -8.14, 0, CE - 0.1, CE + 0.08, kind="detail")
    # 파라펫 (오른쪽 옆에 계단 쪽 틈)
    gap = (-4.0, -1.3)
    L.box(C, "concrete_d", -6.1, 6.1, -8.1, -7.9, RF, RF + 0.6, col=True)
    L.box(C, "concrete_d", -6.1, -5.9, -7.9, 0, RF, RF + 0.6, col=True)
    L.box(C, "concrete_d", 5.9, 6.1, -7.9, gap[0], RF, RF + 0.6, col=True)
    L.box(C, "concrete_d", 5.9, 6.1, gap[1], 0, RF, RF + 0.6, col=True)
    # 바깥 마감: 걸레받이 띠, 출입구 테, 창
    for s in (-1, 1):
        L.rect(C, "concrete_d", (s * 6, -4, 0.35), (s, 0, 0), 7.9, 0.4, lift=0.01)
        for yy in (-6.0, -2.6):
            L.decal(C, "glass_d", hw.rrect(1.3, 0.9, 0.12, 2), (s * 6, yy, 1.75), (s, 0, 0), lift=0.012)
            L.rect(C, "concrete_d", (s * 6, yy, 1.22), (s, 0, 0), 1.5, 0.1, lift=0.016)
            L.decal(C, "dark", hw.rrect(1.3, 0.9, 0.12, 2), (s * (6 - T), yy, 1.75), (-s, 0, 0), lift=0.008)
    L.rect(C, "concrete_d", (0, -8, 0.35), (0, -1, 0), 11.8, 0.4, lift=0.01)
    # 출입구 테: 벽의 문설주·상인방 밑면을 8 mm 덮는다 (벽 면과 한 평면이면 깜빡인다)
    for (x0, x1, z0, z1) in ((-0.85, -0.692, FL, 2.3), (0.692, 0.85, FL, 2.3), (-0.85, 0.85, 2.142, 2.3)):
        L.box(C, "navy", x0, x1, -8.06, -8 + T + 0.03, z0, z1, kind="detail")
    for xx in (-3.6, 3.6):
        L.decal(C, "glass_d", hw.rrect(1.6, 0.9, 0.12, 2), (xx, -8, 1.75), (0, -1, 0), lift=0.012)
        L.decal(C, "dark", hw.rrect(1.6, 0.9, 0.12, 2), (xx, -8 + T, 1.75), (0, 1, 0), lift=0.008)
    # ON AIR 등 (LIGHT_<lid>_03)
    L.box(C, "navy", -0.55, 0.55, -8.16, -8.0, 2.38, 2.7, kind="detail")
    L.rect(C, "glow_off", (0, -8.16, 2.54), (0, -1, 0), 0.95, 0.24, lift=0.004)
    L.text(C, "navy", "ON AIR · 송출 중", 0.11, (0, -8.16, 2.54), (0, -1, 0), lift=0.022)
    light_panel(C, f"{lid}_03", [(L.p(0, -8.166, 2.54), L.d(0, -1, 0), 0.95, 0.24)], group=group)
    # 출입구 앞 디딤 (0.15 → 마당)
    L.box(C, "conc", -1.2, 1.2, -8.9, -8, -0.3, 0.08, col=True)
    # ---------------------------------------------------------- 실내
    L.rect(C, "wall_in", (0, 0.0, 1.5), (0, -1, 0), 11.5, 2.7, lift=0.035)                  # 본관 쪽 벽
    for s in (-1, 1):
        L.rect(C, "navy_l", (s * (6 - T), -4, 0.55), (-s, 0, 0), 7.7, 0.8, lift=0.006)
    L.rect(C, "navy_l", (0, -8 + T, 0.55), (0, 1, 0), 11.4, 0.8, lift=0.006)
    L.rect(C, "concrete_d", (0, -4, CE), (0, 0, -1), 11.4, 7.6, up=(0, 1, 0), lift=0.004)
    L.box(C, "galv", -0.25, 0.25, -7.6, -0.3, CE - 0.3, CE - 0.24, kind="detail")          # 케이블 트레이
    for yy in (-6.5, -4.0, -1.5):
        L.box(C, "galv_d", -0.03, 0.03, yy - 0.03, yy + 0.03, CE - 0.24, CE, kind="detail")
    # 송신 콘솔 (본관 벽 앞, 출입구를 마주봄)
    L.box(C, "navy_l", -1.8, 1.8, -0.85, -0.02, FL, FL + 0.62, col=True)
    L.box(C, "steel", -1.85, 1.85, -0.9, -0.02, FL + 0.62, FL + 0.67, kind="detail")
    L.rect(C, "dark", (0, -0.9, FL + 0.3), (0, -1, 0), 3.4, 0.4, lift=0.004)
    scr = []
    for k, xx in enumerate((-1.1, 0.0, 1.1)):
        L.box(C, "dark", xx - 0.45, xx + 0.45, -0.32, -0.18, FL + 0.7, FL + 1.28, kind="detail")
        L.rect(C, "screen", (xx, -0.32, FL + 0.99), (0, -1, 0), 0.8, 0.5, lift=0.004)
        scr.append((L.p(xx, -0.326, FL + 0.99), L.d(0, -1, 0), 0.8, 0.5))
    for k in range(9):
        L.rect(C, ("glow_off", "alert_d", "steel")[k % 3], (-1.4 + k * 0.35, -0.8, FL + 0.675), (0, 0, 1), 0.12, 0.08,
               up=(0, 1, 0), lift=0.004)
    light_panel(C, f"{lid}_05", scr, group=group)
    # 송신기 함 (콘솔 오른쪽 구석) + 랙 (양옆 벽)
    L.box(C, "cab", 3.6, 5.7, -1.1, -0.02, FL, FL + 2.3, col=True)
    L.rect(C, "cab_d", (4.65, -1.1, FL + 1.2), (0, -1, 0), 1.9, 2.1, lift=0.004, kind="under")   # 판 = under
    for k in range(3):
        L.decal(C, "white", hw.circle(0.13, 12), (4.0 + k * 0.33, -1.1, FL + 1.75), (0, -1, 0), lift=0.008)
        u = 4.0 + k * 0.33                                   # 바늘은 계기판 위 1 cm 두께 막대 (판 위 판이 아니게)
        L.box(C, "dark", u - 0.01, u + 0.01, -1.118, -1.108, FL + 1.7, FL + 1.8, kind="fine")
    L.text(C, "white", "송신기 TX-1", 0.1, (4.65, -1.1, FL + 2.1), (0, -1, 0), lift=0.01)
    L.beam(C, "red", (5.4, -1.15, FL + 1.0), (5.4, -1.35, FL + 1.25), 0.05, 0.05, kind="detail")
    for s in (-1, 1):
        for (y0, y1) in ((-6.9, -5.7), (-5.5, -4.3)):
            x_in = s * (6 - T) - s * 0.65
            xa, xb = sorted((x_in, s * (6 - T)))
            L.box(C, "dark", xa, xb, y0, y1, FL, FL + 2.0, col=True)
            for r in range(5):
                L.rect(C, ("glow_off", "steel", "alert_d", "steel", "glow_off")[r], (x_in, (y0 + y1) / 2, FL + 0.4 + r * 0.32),
                       (-s, 0, 0), 0.9, 0.05, lift=0.006)
    L.box(C, "wood_d", -3.6, -2.2, -3.2, -2.4, FL, FL + 0.55, col=True)        # 작업대
    L.box(C, "paper" if "paper" in mk.PAL else "white", -3.3, -2.8, -3.0, -2.6, FL + 0.55, FL + 0.57, kind="detail")
    # ---------------------------------------------------------- 바깥 계단 (로컬 +X 옆, 앞 → 뒤로 오름)
    n_r = 17
    rise = RF / n_r                  # 0.18 m
    tread = 0.3
    ys0 = -9.2
    for i in range(n_r - 1):
        ya, yb = ys0 + i * tread, ys0 + (i + 1) * tread
        L.box(C, "conc" if i % 2 else "conc_d", 6.0, 7.3, ya, yb, -0.3, (i + 1) * rise)
        L.rect(C, "hazard", (6.65, ya + 0.03, (i + 1) * rise), (0, 0, 1), 1.3, 0.05, up=(0, 1, 0), lift=0.005)
    yl = ys0 + (n_r - 1) * tread
    L.box(C, "conc", 6.0, 7.3, yl, -1.0, -0.3, RF, col=True)
    # 충돌은 디딤판 가운데를 잇는 경사면 하나 (약 31°)
    col_ramp(C, f"stair_{lid}", L, 6.0, 7.3, ys0 - tread / 2, 0.0, yl, RF - rise / 2)
    # 바깥 난간 (계단 + 층계참)
    for (y_a, z_a, y_b, z_b) in ((ys0, rise, yl, RF), (yl, RF, -1.0, RF)):
        L.beam(C, "galv", (7.2, y_a, z_a + 0.85), (7.2, y_b, z_b + 0.85), 0.05, 0.05, kind="detail")
    for (yy, zz) in ((ys0 + 0.1, rise), (yl - 2.0, RF - 2.0 / tread * rise), (yl, RF), (-1.1, RF)):
        L.beam(C, "galv", (7.2, yy, zz), (7.2, yy, zz + 0.85), 0.05, 0.05, kind="detail")
    L.col(C, 7.15, 7.3, yl, -1.0, RF, RF + 0.9)
    L.col(C, 7.2, 7.35, ys0, yl, 0.0, RF + 0.9)            # 계단 바깥 난간
    # ---------------------------------------------------------- 간판 (본관 앞면, 테라스 위) + LIGHT 밑줄
    sc = (0, -0.02, RF + 1.75)
    L.plate(C, "navy", hw.rrect(7.4, 1.25, 0.25, 2), sc, (0, -1, 0), 0.16)
    L.text(C, "white", name[0], 0.5, (0, -0.19, RF + 1.9), (0, -1, 0), lift=0.004)
    L.text(C, "gold", name[1], 0.22, (0, -0.19, RF + 1.42), (0, -1, 0), lift=0.004)
    C.logo(L.p(-3.1, -0.19, RF + 1.75), 0.8, L.d(0, -1, 0), key="gold", disc="navy_l", lift=0.006)
    L.rect(C, "glow_off", (0, -0.19, RF + 1.04), (0, -1, 0), 6.6, 0.1, lift=0.004)
    light_panel(C, f"{lid}_04", [(L.p(0, -0.196, RF + 1.04), L.d(0, -1, 0), 6.6, 0.1)], group=group)
    # 테라스 위: 실외기 + 접시
    L.box(C, "steel", -4.8, -3.6, -7.2, -6.4, RF, RF + 0.75, col=True)
    L.cyl(C, "metal", (-4.2, -6.8, RF + 0.75), (-4.2, -6.8, RF + 0.8), 0.32, segs=10, kind="detail")
    # ---------------------------------------------------------- 옥상 안테나 (본관)
    ab = L.p(2.5, 7.0, H)
    ah = 8.5
    C.box("conc", ab.x - 0.6, ab.x + 0.6, ab.y - 0.6, ab.y + 0.6, ab.z, ab.z + 0.25)
    C.cyl("galv", ab + Vector((0, 0, 0.25)), ab + Vector((0, 0, ah)), 0.1, r2=0.06, segs=8)
    for (zz, half) in ((ah * 0.62, 1.1), (ah * 0.85, 0.8)):
        q = ab + Vector((0, 0, zz))
        C.beam("galv", q - L.d(half, 0), q + L.d(half, 0), 0.06, 0.06, kind="detail")
        for s in (-1, 1):
            C.cyl("galv", q + L.d(s * half, 0), q + L.d(s * half, 0) + Vector((0, 0, 1.1)), 0.02, segs=4,
                  kind="detail")
    for k in range(4):
        a = math.radians(45 + 90 * k)
        C.cyl("cable", ab + Vector((0, 0, ah * 0.55)), ab + Vector((math.cos(a) * 4.2, math.sin(a) * 3.8, 0.05)), 0.01,
              segs=3, cap=False, kind="fine")
    dp = ab + Vector((0, 0, ah * 0.4)) + L.d(0, -0.3)
    C.cyl("dish", dp, dp + L.d(0, -0.25), 0.55, r2=0.45, segs=12, kind="detail")
    beacon(C, f"{lid}_01", [ab + Vector((0, 0, ah * 0.85)) + L.d(s * 0.3, 0) for s in (-1, 1)], group=group,
           r=0.18, h=0.3)
    beacon(C, f"{lid}_02", [ab + Vector((0, 0, ah * 0.5)) + L.d(s * 0.3, 0) for s in (-1, 1)], group=group,
           r=0.18, h=0.3)
    if avia:
        beacon(C, f"{avia}_01", [ab + Vector((0, 0, ah + 0.02))], color=RED, group="avia", on=1, blink=1.2,
               off_key="alert_d", on_key="alert", r=0.18, h=0.3)
    return {
        "console_front": L.p(0, -1.35, FL),
        "spawn_in": L.p(1.6, -3.2, FL),
        "door_out": L.p(0, -9.4, 0.0),
        "door_in": L.p(0, -7.0, FL),
        "terrace": L.p(-2.0, -4.0, RF),
        "terrace_edge": L.p(-1.5, -7.2, RF),
        "stair_bottom": L.p(6.65, -9.8, 0.0),
        "roof_z": O.z + RF,
        "top_z": O.z + H,
        "antenna_top": ab + Vector((0, 0, ah)),
        "local": L,
    }
