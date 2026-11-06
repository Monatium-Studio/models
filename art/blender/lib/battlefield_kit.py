"""전장 키트 (battlefield_kit): 3막 M9 「종막」 에르피엔 외곽 총공격의 들판·참호·마을 외곽·R41 야전 지휘소·성전군·원경.

[원작] 성전군의 총공격. 마카샤와 실라의 지휘로 요정들이 돌격하고, 에르피엔 결전에서 R41 돌격 편대가 동요해 대거 이탈한다.
       에르피엔은 요정 왕국(왕도), 엘리아스 한가운데에 세계수가 있다.
[오리지널] 에르피엔 외곽 들판의 참호선(요정 출발 참호 / R41 참호선), 요정 마을 외곽 폐허(돌집·풍차), R41 침공군 야전 지휘소
       (울타리·문·지휘 컨테이너와 콘솔·안테나 탑·발전기·작전 탁자),
       에르피엔 원경 실루엣의 생김새와 배치.
[원작] 성전군 깃발·천막 깃발 = 에르피엔 군기, 보급 상자 스텐실 = 그 군기의 나비 (lib/erpien_flag.py, 사용자 결정 2026-11-02).

규약: 레벨 노드 docs/LEVELS.md, 전투 마커 docs/COMBAT.md 2장, 도시 키트 docs/art/monatium-city.md,
요정 진영 docs/art/fairy-faction.md (초록 #2f6a4f · 금 #e8c178 · 흰색, 나비 문장), R41 형태 언어 docs/art/r41-style.md
(45° 모따기 덩어리, 육각 부품, 밝은 회색 + 앰버 + 마젠타 슬릿 발광). 도시 키트(monatium_city_kit)는 읽기만 한다.
팔레트에 키를 더하는 것은 실행 중 딕셔너리만 바꾼다(파일은 그대로).

사용:
    import monatium_city_kit as mk, battlefield_kit as bk
    C = mk.City("m9_assault")
    G = bk.Ground(H)                                   # 높이장 지형 (보이는 메시 = 충돌 메시, G.h(x, y) = 실제 바닥 높이)
    T = bk.Trenches("start", style="fairy")           # 축 정렬 사각형을 합친 참호망
    T.rect(-46, 46, -1.1, 1.1); T.steps(-7.5, -4.5, 1.1, 3.0, "+y")
    G.patch(C, "band0", xs + T.xlines(), ys + T.ylines(), skip=T.skip)
    T.build(C)
    solid = bk.Solid("crater")                         # 걸을 수 있는 둔덕(분화구 테, 흙둑)의 트라이메시 충돌
    bk.crater(C, G, solid, 12, 30, 3.0); solid.flush(C)

모듈
  지형      Ground(fn).patch / h / far_lin            높이장 격자 조각 (삼각형 대각선 고정 → h(x, y)가 메시와 같다)
            axis_lines, drape, ground_disc              격자 줄, 지형 위 띠(길), 지형 위 원판 데칼
            Solid                                       걸을 수 있는 둔덕 메시를 모아 collider=1 노드로
  참호      Trenches (rect/steps/fire_step/build)       얕은 참호: 흙 바닥 + 널빤지(요정)/회색 패널(R41) 벽 + 발판 + 계단,
                                                        구멍 난 지형과 정확히 맞는 COL
            bag_row, berm                               모래주머니 줄(COL) / 흙둑(트라이메시)
  들판      crater, wire_coil, hedgerow, stone_wall,    포탄 구덩이 테, 철조망 코일(낮음, COL), 생울타리, 돌담,
            hay_bale, stump, hedgehog                   건초 더미, 그루터기, R41 육각 대전차 장애물
  부서짐    Breakable, breakable=True                 bag_row·wire_coil·stone_wall·picket·hq_fence: 전차가 밀거나 주포로 쏘면 무너지는
                                                        BRK_ 소품 (무너진 모습 BRKD_, 충돌체 COL_BRK_). 런타임 src/game/level/destructibles.ts
  R41       r41_bunker, r41_container, command_post,    야전 벙커(모따기, 마젠타 슬릿), 조립식 컨테이너, 지휘 컨테이너(콘솔),
            antenna_mast, generator, map_table,         안테나 탑, 발전기, 작전 탁자, 철망 울타리·문, 투광등,
            hq_fence, hq_gate, floodlight, r41_barrier, 차단벽, 보급 상자, 연료통, 불탄 R41 기동차량
            r41_crate, drum_r41, wreck_raider
  성전군    butterfly, fairy_banner, fairy_crate,       에르피엔 나비 스텐실, 에르피엔 군기(erpien_flag), 보급 상자, 천막, 머스킷 거치대, 보급 수레, 북
            fairy_tent, musket_rack, supply_cart, war_drum
  마을      wall_run, cottage, windmill, well,          구멍 난 벽, 부서진 돌집, 풍차, 우물, 나무 울타리(mk.fence)
            picket
  숲        tree_round, conifer, scatter                둥근 활엽수, 침엽수, 영역 흩뿌리기
  원경      erpien, far_trees, far_mountains, cloud      에르피엔 왕도 실루엣(성벽·탑·성), 원경 숲, 원경 산, 저녁 구름

체격: 엘프 기준(키 1.2 m, 눈 0.92 m, 점프 0.6 m, 자동 오르기 0.28 m). 문 1.9 × 1.0 m, 참호 깊이 0.65~0.75 m,
계단 단 0.17 m 이하, 사격 발판 0.18 m.
좌표: Blender Z-up, 1 BU = 1 m, 빈 오브젝트와 로컬 틀(Local)의 -Y가 정면. yaw(도)는 Z 회전.
"""
from __future__ import annotations

import bisect
import contextlib
import math
import random

import bmesh
from mathutils import Matrix, Vector

import erpien_flag as ef
import home_weapons as hw
import monatium_city_kit as mk

# ================================================================== palette (실행 중에만 더한다)
PAL_ADD = {
    # 들판 (해 질 녘 초원)
    "meadow": "#a8bf6c",
    "meadow_d": "#8fa95c",
    "dry": "#cbb878",        # 마른 풀 자국
    "mud": "#7d6650",        # 참호 바닥, 파헤친 흙
    "mud_d": "#5d4a3b",
    "scorch_e": "#6e5a4b",   # 그을린 흙 (포격 자국)
    "earth": "#977c5e",      # 흙둑, 구덩이 테
    "plank": "#b48c5c",      # 발판, 널빤지 벽
    "plank_d": "#7f6043",
    "sandbag": "#c6b086",
    "sandbag_d": "#a99168",
    "wire": "#4b4651",
    "stake": "#6a5646",
    "sand_spill": "#d6c396",  # 터진 모래주머니에서 쏟아진 모래 (부서지는 소품)
    # 요정 마을
    "stone_v": "#dccfbc",    # 돌집 벽 (밝은 석회석)
    "stone_vd": "#b5a791",
    "plaster": "#f1e7d4",    # 회칠 (풍차)
    "roof_r": "#b9634a",     # 붉은 기와
    "roof_rd": "#8e4937",
    "roof_g": "#4f8064",     # 초록 슬레이트 (요정 왕국 색)
    "timber": "#6f5039",
    "thatch": "#c9a665",
    "hay": "#d9bf6e",
    "flower_r": "#e0675c",
    # 성전군 (fairy.GUARD와 같은 값)
    "fy_green": "#2f6a4f",
    "fy_green_d": "#21483a",
    "fy_gold": "#e8c178",
    "fy_gold_d": "#c49448",
    "fy_white": "#f5f2f3",
    # R41 야전
    "r41_panel": "#8f8a99",  # 참호 벽 패널
    "r41_tarp": "#77717f",   # R41 천막·차양
    "r41_dark": "#34303d",   # 문틀 안, 슬릿 안
    "paper": "#ece2c8",      # 작전 지도
    # 숲
    "foliage": "#6c9b5a",
    "foliage_l": "#8db66b",
    "foliage_d": "#557f4c",
    "foliage_au": "#b7a454", # 가을빛 섞인 잎
    "pine": "#4b7a56",
    "pine_d": "#3b6248",
    "bark_d": "#5e4637",
    # 원경
    "far_grass": "#93a76a",
    "far_forest": "#5c7d5b",
    "far_forest_d": "#4b6a50",
    "far_hill": "#8e9d72",
    "erp_wall": "#ecdfc8",
    "erp_wall_d": "#cbbca1",
    "erp_roof": "#4c876a",   # 에르피엔 초록 지붕
    "erp_roof_b": "#5d7fac", # 푸른 슬레이트
    "erp_roof_r": "#bb6a4f", # 붉은 기와
    "erp_gold": "#e6c172",
    "mount_d": "#9aa6b6",
    "cloud_p": "#f2c6ad",    # 해 질 녘 구름 (복숭아빛)
    "cloud_s": "#d7a7a8",    # 구름 그늘 (장밋빛)
}
GLOW_ADD = {
    "ember": "#ff8a3a",
    "screen_r41": "#b98cff",     # R41 콘솔 화면 (보라)
    "lamp_warm": "#ffe2a8",      # 따뜻한 창불
}
ALPHA_ADD = {
    "wire_mesh": ("#5a5662", 0.5),   # 철망
}
for _k, _v in PAL_ADD.items():
    mk.PAL.setdefault(_k, _v)
for _k, _v in GLOW_ADD.items():
    mk.GLOW.setdefault(_k, _v)
for _k, _v in ALPHA_ADD.items():
    mk.ALPHA.setdefault(_k, _v)
mk._DARK.update({"mud_d", "wire", "timber", "plank_d", "bark_d", "r41_dark", "fy_green_d", "stake"})
mk._R41.update({"r41_panel", "r41_tarp", "r41_dark"})

MAGENTA = mk.GLOW["magenta"]


def S(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def face_yaw(src, dst):
    """src에서 dst를 바라보는 yaw(도). 로컬 -Y가 그쪽을 향한다."""
    return math.degrees(mk.yaw_to(src, dst))


# ================================================================== local frame · bmesh helpers

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

    def blob(self, C, key, c, r, scale=(1, 1, 1), **kw):
        C.blob(key, self.p(*c), r, scale, rot_z=math.radians(self.yaw), **kw)

    def rect(self, C, key, c, n, w, h, *, up=(0, 0, 1), lift=None, kind="fine"):
        C.rect(key, self.p(*c), self.d(*n), w, h, up=self.d(*up), lift=lift, kind=kind)

    def decal(self, C, key, pts, c, n, *, up=(0, 0, 1), lift=None):
        C.decal(key, pts, self.p(*c), self.d(*n), up=self.d(*up), lift=lift)

    def plate(self, C, key, pts, c, n, depth, *, kind="detail", up=(0, 0, 1)):
        C.plate(key, pts, self.p(*c), self.d(*n), depth, kind=kind, up=self.d(*up))

    def text(self, C, key, s, size, c, n, *, lift=None):
        C.text(key, s, size, self.p(*c), self.d(*n), lift=lift)

    def col(self, C, x0, x1, y0, y1, z0, z1, shrink=0.0):
        """로컬 상자 COL을 이 틀의 yaw만큼 돌려 넣는다 (90°의 배수면 축 정렬). 예전에는 돌린 상자의 축 정렬 경계
        상자를 넣어 비스듬한 수레·천막·차단벽 둘레에 보이지 않는 벽이 남았다."""
        C.lcol(self.o.x, self.o.y, self.o.z, self.yaw, x0 + shrink, x1 - shrink, y0 + shrink, y1 - shrink, z0, z1)

    def hull(self, C, pts):
        """로컬 점들의 볼록 껍질 COL."""
        C.ccol([tuple(self.p(*q)) for q in pts])


def bm_col(C, build):
    """build(bm)이 만든 임시 메시 꼭짓점의 볼록 껍질 COL (보이는 원뿔·원통·절두체 그대로)."""
    b = bmesh.new()
    build(b)
    C.ccol([tuple(v.co) for v in b.verts])
    b.free()


def beam_col(C, p0, p1, w, *, z_min=None):
    """얇은 보 p0 → p1 둘레 w 폭의 볼록 COL (z_min이면 그 높이 아래 부분은 잘라 버린다)."""
    P0, P1 = Vector(p0), Vector(p1)
    if z_min is not None:
        if P0.z < z_min and P1.z < z_min:
            return
        if P0.z < z_min or P1.z < z_min:
            lo, hi = (P0, P1) if P0.z < P1.z else (P1, P0)
            lo = lo.lerp(hi, (z_min - lo.z) / (hi.z - lo.z))
            P0, P1 = lo, hi
    d = P1 - P0
    n = Vector((-d.y, d.x, 0))
    n = n.normalized() * (w / 2) if n.length > 1e-6 else Vector((w / 2, 0, 0))
    C.ccol([tuple(q + n * a + Vector((0, 0, w / 2 * c))) for q in (P0, P1) for a in (-1, 1) for c in (-1, 1)])


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


def ngon(r, n, rot=0.0, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(math.radians(rot) + 2 * math.pi * i / n),
             cy + r * math.sin(math.radians(rot) + 2 * math.pi * i / n)) for i in range(n)]


def frustum_bm(bm, c, r0, r1, z0, z1, n, rot=0.0, top=True):
    """다각 절두체 (풍차 탑, 원경 성탑)."""
    lo = [bm.verts.new((c[0] + x, c[1] + y, z0)) for x, y in ngon(r0, n, rot)]
    hi = [bm.verts.new((c[0] + x, c[1] + y, z1)) for x, y in ngon(r1, n, rot)]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    if top:
        bm.faces.new(hi)


def quad_slab(bm, corners, thick):
    """네 꼭짓점(윗면, 반시계)에서 법선 반대쪽으로 thick만큼 내린 판 (지붕면)."""
    P = [Vector(c) for c in corners]
    n = (P[1] - P[0]).cross(P[3] - P[0]).normalized()
    if n.z < 0:
        n = -n
    top = [bm.verts.new(p) for p in P]
    bot = [bm.verts.new(p - n * thick) for p in P]
    fs = [bm.faces.new(top), bm.faces.new(list(reversed(bot)))]
    for i in range(4):
        j = (i + 1) % 4
        fs.append(bm.faces.new((bot[i], bot[j], top[j], top[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)


def hull2d(pts):
    """2D 볼록 껍질 (반시계)."""
    P = sorted(set((round(x, 5), round(y, 5)) for x, y in pts))
    if len(P) <= 2:
        return P

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def ccw(pts):
    """다각형을 반시계로 (부호 넓이가 음수면 뒤집는다)."""
    a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return list(pts) if a >= 0 else list(reversed(pts))


# ================================================================== walkable mounds (trimesh)

class Solid:
    """걸을 수 있는 둔덕(분화구 테, 흙둑) 메시를 머티리얼별로 모아 collider=1 노드로 내보낸다.
    COL_ 박스로 막기 어려운 비탈을 엔진이 트라이메시로 받는다."""

    def __init__(self, name):
        self.name = name
        self.b: dict[str, bmesh.types.BMesh] = {}

    def __call__(self, key):
        b = self.b.get(key)
        if b is None:
            b = self.b[key] = bmesh.new()
        return b

    def flush(self, C, outline=None):
        out = []
        for key, b in list(self.b.items()):
            if not b.faces:
                b.free()
                continue

            def build(bm, src=b):
                mk._copy_into(bm, src)
            o = C.special(f"solid_{self.name}_{key}", build, key)
            o["collider"] = 1
            if outline is not None:
                o["outline"] = outline
            b.free()
            out.append(o)
        self.b.clear()
        return out


# ================================================================== ground

def axis_lines(a0, a1, step, *, fine=(), extra=(), min_gap=0.08):
    """a0..a1을 step 간격으로 (fine = [(lo, hi, 간격)] 촘촘한 구간, extra = 꼭 넣을 줄). 너무 가까운 줄은 extra를 남긴다."""
    vals = {}
    n = max(1, int(math.ceil((a1 - a0) / step)))
    for i in range(n + 1):
        vals[round(min(a1, a0 + (a1 - a0) * i / n), 4)] = False
    for lo, hi, fs in fine:
        k = max(lo, a0)
        while k < min(hi, a1) - 1e-6:
            vals.setdefault(round(k, 4), False)
            k += fs
        vals.setdefault(round(min(hi, a1), 4), False)
    for e in extra:
        if a0 - 1e-6 <= e <= a1 + 1e-6:
            vals[round(e, 4)] = True
    out = []
    for v in sorted(vals):
        if out and v - out[-1][0] < min_gap:
            if vals[v] and not out[-1][1]:
                out[-1] = (v, True)
            continue
        out.append((v, vals[v]))
    return [v for v, _ in out]


class Ground:
    """높이장 지형. 보이는 메시가 곧 충돌 메시다(collider=1). h(x, y)는 메시 삼각형을 그대로 보간한다.
    조각(patch)은 격자(xs, ys)이고 칸마다 대각선 (i,j)-(i+1,j+1)로 나눈다. 나중에 더한 조각이 먼저 쓰인다.
    skip(xc, yc)가 참인 칸은 비운다(참호 구멍, 다른 조각이 덮는 자리). 조각 경계에서 높이가 같아야 틈이 없다."""

    def __init__(self, fn):
        self.fn = fn
        self.patches = []

    def patch(self, C, name, xs, ys, *, fn=None, key="meadow", skip=None, collider=True, smooth=True, kind="main"):
        f = fn or self.fn
        xs = sorted(set(round(x, 4) for x in xs))
        ys = sorted(set(round(y, 4) for y in ys))
        H = [[f(x, y) for y in ys] for x in xs]

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
        o["collider"] = 1 if collider else 0
        self.patches.append((xs, ys, H, skip))
        return o

    @staticmethod
    def _interp(P, x, y):
        xs, ys, H, _ = P
        i = min(max(bisect.bisect_right(xs, x) - 1, 0), len(xs) - 2)
        j = min(max(bisect.bisect_right(ys, y) - 1, 0), len(ys) - 2)
        u = (x - xs[i]) / (xs[i + 1] - xs[i])
        v = (y - ys[j]) / (ys[j + 1] - ys[j])
        h00, h10, h11, h01 = H[i][j], H[i + 1][j], H[i + 1][j + 1], H[i][j + 1]
        if u >= v:
            return h00 + u * (h10 - h00) + v * (h11 - h10)
        return h00 + v * (h01 - h00) + u * (h11 - h01)

    def h(self, x, y):
        for P in reversed(self.patches):
            xs, ys, H, skip = P
            if not (xs[0] <= x <= xs[-1] and ys[0] <= y <= ys[-1]):
                continue
            i = min(max(bisect.bisect_right(xs, x) - 1, 0), len(xs) - 2)
            j = min(max(bisect.bisect_right(ys, y) - 1, 0), len(ys) - 2)
            if skip and skip((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2):
                continue
            return self._interp(P, x, y)
        return self.fn(x, y)

    def far_lin(self, index, x, y):
        """조각 index의 보간값 (skip 무시). 가까운 조각을 먼 조각에 이어 붙일 때 쓴다."""
        return self._interp(self.patches[index], x, y)

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


def drape(C, key, pts, width, ground, *, lift=0.05, step=1.5, kind="fine", fillet=None):
    """지형 위에 얹은 띠(길, 바퀴 자국). pts = [(x, y)] 꺾은선, fillet = 꺾임 반지름. 반환: 다시 뽑은 중심점."""
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


def ground_disc(C, key, cx, cy, r, ground, *, n=12, rings=2, lift=0.04, seed=0, jitter=0.18, kind="fine"):
    """지형을 따라 휘는 원판 데칼 (그을음, 진흙, 마른 풀 자국). 고리 rings개로 나눠 지형에 붙는다."""
    rng = random.Random(seed)
    rad = [r * rng.uniform(1 - jitter, 1 + jitter) for _ in range(n)]
    b = C.bm(key, kind)
    c = b.verts.new((cx, cy, ground.h(cx, cy) + lift))
    prev = None
    for k in range(1, rings + 1):
        f = k / rings
        ring = []
        for i in range(n):
            a = 2 * math.pi * i / n
            x, y = cx + math.cos(a) * rad[i] * f, cy + math.sin(a) * rad[i] * f
            ring.append(b.verts.new((x, y, ground.h(x, y) + lift)))
        for i in range(n):
            j = (i + 1) % n
            if prev is None:
                b.faces.new((c, ring[i], ring[j]))
            else:
                b.faces.new((prev[i], ring[i], ring[j], prev[j]))
        prev = ring


# ================================================================== trenches

class Trenches:
    """얕은 참호망. 축 정렬 사각형(겹치지 않고 맞닿게)을 합친 구멍 + 흙 바닥 + 벽 + 발판 + 계단·사격 발판.
    지형은 이 사각형의 모서리를 격자 줄로 넣고(xlines/ylines) skip으로 구멍을 낸다. 벽 COL은 구멍 바깥으로 0.5 m,
    바닥 COL은 윗면 = 바닥. 계단과 사격 발판은 단 높이 0.17 m 이하 (자동 오르기 0.28 m 안에서 확실히 오른다).
    style: 'fairy'(널빤지 + 말뚝 + 가로대) | 'r41'(회색 패널 + 금속 기둥 + 앰버 표지)."""

    def __init__(self, name, *, z_top=0.0, depth=0.75, style="fairy"):
        self.name = name
        self.zt = z_top
        self.d = depth
        self.zf = z_top - depth
        self.style = style
        self.rects: list[tuple] = []
        self.blocks: list[tuple] = []      # (x0, x1, y0, y1, z_top, kind)

    def rect(self, x0, x1, y0, y1):
        self.rects.append((min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)))
        return len(self.rects) - 1

    def steps(self, x0, x1, y0, y1, up, n=None):
        """구멍 안의 계단 (up = 올라가는 쪽 '+x' '-x' '+y' '-y'). 마지막 단 윗면 = 지면.
        단 높이는 0.17 m 이하로 나눈다 (Rapier 자동 오르기 0.28 m는 캐릭터 오프셋 때문에 0.25 m 단에서 걸린다)."""
        n = n or max(2, int(math.ceil(self.d / 0.17 - 1e-6)))
        rise = self.d / n
        for k in range(n):
            f = k / n
            if up == "+y":
                box = (x0, x1, y0 + (y1 - y0) * f, y1)
            elif up == "-y":
                box = (x0, x1, y0, y1 - (y1 - y0) * f)
            elif up == "+x":
                box = (x0 + (x1 - x0) * f, x1, y0, y1)
            else:
                box = (x0, x1 - (x1 - x0) * f, y0, y1)
            self.blocks.append((*box, self.zf + rise * (k + 1), "step"))

    def fire_step(self, x0, x1, y0, y1, h=0.18):
        self.blocks.append((x0, x1, y0, y1, self.zf + h, "fire"))

    def inside(self, x, y, eps=1e-4):
        return any(x0 + eps < x < x1 - eps and y0 + eps < y < y1 - eps for (x0, x1, y0, y1) in self.rects)

    def skip(self, xc, yc):
        return self.inside(xc, yc)

    def xlines(self):
        return sorted({r[0] for r in self.rects} | {r[1] for r in self.rects})

    def ylines(self):
        return sorted({r[2] for r in self.rects} | {r[3] for r in self.rects})

    def floor_z(self, x, y):
        """참호 안이면 그 자리 바닥(계단·사격 발판 포함), 밖이면 None."""
        if not self.inside(x, y, eps=-1e-4):
            return None
        z = self.zf
        for (x0, x1, y0, y1, zt, _) in self.blocks:
            if x0 - 1e-4 <= x <= x1 + 1e-4 and y0 - 1e-4 <= y <= y1 + 1e-4:
                z = max(z, zt)
        return z

    def boundary(self):
        """합집합의 바깥 테두리 조각 [(side, c, a0, a1)]. side = 바깥 법선 방향."""
        out = []
        R = self.rects
        e = 1e-3
        for i, (x0, x1, y0, y1) in enumerate(R):
            for side, c, a0, a1 in (("-y", y0, x0, x1), ("+y", y1, x0, x1), ("-x", x0, y0, y1), ("+x", x1, y0, y1)):
                cuts = []
                for j, (u0, u1, v0, v1) in enumerate(R):
                    if j == i:
                        continue
                    if side in ("-y", "+y"):
                        yy = c - e if side == "-y" else c + e
                        if v0 < yy < v1:
                            lo, hi = max(a0, u0), min(a1, u1)
                            if hi > lo:
                                cuts.append((lo, hi))
                    else:
                        xx = c - e if side == "-x" else c + e
                        if u0 < xx < u1:
                            lo, hi = max(a0, v0), min(a1, v1)
                            if hi > lo:
                                cuts.append((lo, hi))
                cur = a0
                for lo, hi in sorted(cuts):
                    if lo > cur + 1e-3:
                        out.append((side, c, cur, lo))
                    cur = max(cur, hi)
                if a1 > cur + 1e-3:
                    out.append((side, c, cur, a1))
        return out

    def build(self, C, *, posts=None, duck=True):
        zf, zt = self.zf, self.zt
        fairy = self.style == "fairy"
        posts = posts or (2.6 if fairy else 2.6)
        wall_k = "plank" if fairy else "r41_panel"
        post_k = "timber" if fairy else "r41_metal"
        # 바닥
        for (x0, x1, y0, y1) in self.rects:
            C.box("mud", x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, zf - 0.3, zf)
            C.col(x0, x1, y0, y1, zf - 0.3, zf)
            if duck:
                L = max(x1 - x0, y1 - y0)
                if L >= 2.5:
                    along_x = (x1 - x0) >= (y1 - y0)
                    if along_x:
                        cy = (y0 + y1) / 2
                        C.box("plank", x0 + 0.15, x1 - 0.15, cy - 0.36, cy + 0.36, zf, zf + 0.04, kind="detail")
                        k = x0 + 0.4
                        while k < x1 - 0.3:
                            C.strip("plank_d", (k, cy - 0.36, zf + 0.04), (k, cy + 0.36, zf + 0.04), 0.04, lift=0.004)
                            k += 0.6
                    else:
                        cx = (x0 + x1) / 2
                        C.box("plank", cx - 0.36, cx + 0.36, y0 + 0.15, y1 - 0.15, zf, zf + 0.04, kind="detail")
                        k = y0 + 0.4
                        while k < y1 - 0.3:
                            C.strip("plank_d", (cx - 0.36, k, zf + 0.04), (cx + 0.36, k, zf + 0.04), 0.04, lift=0.004)
                            k += 0.6
        # 벽 (바깥 테두리)
        for side, c, a0, a1 in self.boundary():
            o = -1 if side in ("-y", "-x") else 1        # 바깥 방향 부호
            if side in ("-y", "+y"):
                C.box(wall_k, a0, a1, min(c, c + o * 0.1), max(c, c + o * 0.1), zf - 0.02, zt - 0.015)
                C.col(a0, a1, min(c, c + o * 0.5), max(c, c + o * 0.5), zf - 0.3, zt)
            else:
                C.box(wall_k, min(c, c + o * 0.1), max(c, c + o * 0.1), a0, a1, zf - 0.02, zt - 0.015)
                C.col(min(c, c + o * 0.5), max(c, c + o * 0.5), a0, a1, zf - 0.3, zt)
            L = a1 - a0
            n = max(1, int(round(L / posts)))
            N = Vector((0, o, 0)) if side in ("-y", "+y") else Vector((o, 0, 0))
            for k in range(n + 1):
                a = a0 + L * k / n
                a = min(max(a, a0 + 0.06), a1 - 0.06)
                if side in ("-y", "+y"):
                    p = (a, c - o * 0.03)
                else:
                    p = (c - o * 0.03, a)
                C.box(post_k, p[0] - 0.05, p[0] + 0.05, p[1] - 0.05, p[1] + 0.05, zf - 0.02, zt + (0.1 if fairy else 0.05),
                      kind="detail")
                if not fairy and k % 4 == 0:
                    C.box("amber", p[0] - 0.055, p[0] + 0.055, p[1] - 0.055, p[1] + 0.055, zt - 0.12, zt - 0.04,
                          kind="fine")      # 5 mm 띠: 기둥(detail)보다 강한 편향 등급이라 거리와 상관없이 이긴다
            # 가로대 / 패널 이음매
            for zz in ((zf + 0.25, zf + 0.55) if fairy else (zf + 0.4,)):
                if side in ("-y", "+y"):
                    C.strip("plank_d" if fairy else "r41_metal", (a0, c - o * 0.004, zz), (a1, c - o * 0.004, zz), 0.035,
                            normal=-N, lift=0.0)
                else:
                    C.strip("plank_d" if fairy else "r41_metal", (c - o * 0.004, a0, zz), (c - o * 0.004, a1, zz), 0.035,
                            normal=-N, lift=0.0)
            if not fairy:
                k = a0 + 1.2
                while k < a1 - 0.2:
                    if side in ("-y", "+y"):
                        C.strip("r41_metal", (k, c - o * 0.004, zf + 0.05), (k, c - o * 0.004, zt - 0.05), 0.03,
                                normal=-N, lift=0.0)
                    else:
                        C.strip("r41_metal", (c - o * 0.004, k, zf + 0.05), (c - o * 0.004, k, zt - 0.05), 0.03,
                                normal=-N, lift=0.0)
                    k += 1.2
        # 계단·사격 발판
        for (x0, x1, y0, y1, ztop, kind) in self.blocks:
            C.box(wall_k if kind == "step" else ("plank" if fairy else "r41_metal"), x0, x1, y0, y1, zf - 0.02, ztop,
                  kind="detail")
            C.box("mud", x0 + 0.03, x1 - 0.03, y0 + 0.03, y1 - 0.03, ztop - 0.02, ztop + 0.012, kind="detail")
            C.col(x0, x1, y0, y1, zf - 0.3, ztop)


# ================================================================== 부서지는 소품 (breakable=True)

_BRK_COUNT: dict = {}


class Breakable:
    """부서지는 소품 묶음 (런타임 src/game/level/destructibles.ts, 규약 docs/LEVELS.md '부서지는 소품').

        with bk.Breakable(C, "wall") as b:     # 안에서 만든 메시 → BRK_wall_<n> 노드(머티리얼별로 합침),
            ...서 있는 모습...                  # C.col·ocol·ccol → COL_BRK_wall_<n>_* (그 소품의 충돌체)
            with b.broken():                   # 안의 메시 → BRKD_wall_<n> (hidden=1, 부서지면 보인다). 충돌체는 만들지 않는다
                ...무너진 모습 (낮아서 넘어 다닌다)...

    kind: wire(철조망) | sandbag(모래주머니) | wall(돌·벽돌 담) | fence(나무·철망 울타리). 전차(M1A1)는 모두, R41 장갑차는
    철조망·울타리만 밀고 지나가며 부순다. 주포는 모두, 로켓·차량 잔해 폭발은 철조망·울타리만. 보병·소화기·수류탄으로는 부서지지 않는다.
    소품 하나가 정적 묶음(zone_*)과 따로 남아 그리기 호출이 머티리얼 수(외곽선 포함 2~6)만큼 는다: 담은 조각(2.6 m)마다, 울타리는
    3 m 안팎마다 하나. 이름은 name을 주면 <kind>_<name>, 아니면 레벨 안에서 차례 번호."""

    KINDS = ("wire", "sandbag", "wall", "fence")

    def __init__(self, C, kind, name=None):
        if kind not in self.KINDS:
            raise ValueError(f"breakable kind {kind!r} (wire | sandbag | wall | fence)")
        key = (id(C), kind)
        _BRK_COUNT[key] = _BRK_COUNT.get(key, 0) + 1
        self.C = C
        self.kind = kind
        self.name = f"{kind}_{name}" if name else f"{kind}_{_BRK_COUNT[key]:02d}"
        self.node = f"BRK_{self.name}"
        self.rubble = f"BRKD_{self.name}"
        self._prev = None

    def __enter__(self):
        self._prev = self.C.grp
        self.C.group(self.node, kind=self.kind)
        return self

    def __exit__(self, *exc):
        self.C.grp = self._prev
        return False

    @contextlib.contextmanager
    def broken(self):
        prev = self.C.grp
        self.C.group(self.rubble, hidden=1, kind=self.kind)
        try:
            yield self
        finally:
            self.C.grp = prev


def _bags_slumped(C, P0, t, Lt, base, rows, keys, rng, L, W, H, kind):
    """터진 모래주머니 더미: 내려앉아 옆으로 퍼진 주머니(일부는 찢겨 짧다) + 쏟아진 모래. 높이 0.2 m 안팎 (넘어 다닌다)."""
    s_ = Vector((-t.y, t.x, 0))
    yaw0 = math.atan2(t.y, t.x)
    n = max(1, int(Lt / (L * 0.9)))
    for k in range(n):
        for r in range(max(1, rows)):
            if rng.random() < 0.3:
                continue  # 터져 모래가 된 주머니
            s = (k + 0.5) / n * Lt + rng.uniform(-0.12, 0.12)
            side = rng.uniform(-1.0, 1.0) * W * (0.5 + 0.6 * r)
            q = P0 + t * s + s_ * side
            zb = base + (0.0 if r == 0 else H * 0.4 * rng.random())
            bag_mesh(C.bm(keys[rng.randrange(len(keys))], kind), (q.x, q.y, zb), yaw0 + rng.uniform(-0.6, 0.6),
                     L=L * rng.uniform(0.55, 1.0), W=W * rng.uniform(1.0, 1.3), H=H * rng.uniform(0.45, 0.7))
    m = max(1, int(Lt / 0.6))
    for k in range(m):
        q = P0 + t * (Lt * (k + rng.uniform(0.2, 0.8)) / m) + s_ * rng.uniform(-W * 1.2, W * 1.2)
        C.blob("sand_spill", (q.x, q.y, base + 0.01), rng.uniform(0.22, 0.38), (1.6, 1.0, 0.24), segs=7, rings=3,
               kind="detail", rot_z=yaw0 + rng.uniform(-0.8, 0.8))


def _wire_crushed(C, P0, d, L, t, s_, hf, r, pitch, rng):
    """깔려 납작해진 철조망: 짓눌려 옆으로 퍼진 고리(일부 끊김) + 땅에 늘어진 위 가닥 토막 + 쓰러진 말뚝. 높이 0.15 m 안팎."""
    b = C.bm("wire", "fine")
    n = max(2, int(L / pitch))
    for k in range(n + 1):
        if rng.random() < 0.25:
            continue
        q = P0 + d * (k / n) + s_ * rng.uniform(-0.3, 0.3)
        z0 = hf(q.x, q.y)
        ring = []
        for i in range(5):
            a = 2 * math.pi * i / 5 + rng.uniform(-0.3, 0.3)
            u, v = math.cos(a) * r * 1.4, math.sin(a) * r
            ring.append(q + s_ * u + t * (v * rng.uniform(-0.7, 0.7)) + Vector((0, 0, z0 + 0.03 + (v + r) * 0.1)))
        for i in range(5):
            if rng.random() < 0.18:
                continue  # 끊어진 가닥
            a, c = ring[i], ring[(i + 1) % 5]
            w = t * 0.012
            b.faces.new([b.verts.new(a - w), b.verts.new(c - w), b.verts.new(c + w), b.verts.new(a + w)])
    for off in (-0.25, 0.25):
        for k in range(n):
            if rng.random() < 0.35:
                continue
            qa = P0 + d * (k / n) + s_ * (off + rng.uniform(-0.25, 0.25))
            qb = P0 + d * ((k + 1) / n) + s_ * (off + rng.uniform(-0.25, 0.25))
            C.strip("wire", (qa.x, qa.y, hf(qa.x, qa.y) + 0.05), (qb.x, qb.y, hf(qb.x, qb.y) + 0.07), 0.014,
                    normal=(0, 0, 1), lift=0.0)
    m = max(1, int(L / 2.6))
    for k in range(m + 1):
        q = P0 + d * (k / m) + s_ * rng.uniform(-0.2, 0.2)
        z0 = hf(q.x, q.y)
        a = rng.uniform(0, 2 * math.pi)
        C.beam("stake", (q.x, q.y, z0 + 0.04), (q.x + math.cos(a) * 0.8, q.y + math.sin(a) * 0.8, z0 + 0.06), 0.05, 0.05,
               kind="detail")


def _wall_rubble(C, G, a, c, t, h, key, cap, rng):
    """무너진 담 조각: 담 자리를 따라 쌓인 깨진 돌·벽돌 덩어리(가운데 0.45 m 안팎, 끝으로 낮게) + 갓돌 + 흙먼지 둔덕. 넘어 다닌다."""
    A, Cc = Vector((a[0], a[1], 0)), Vector((c[0], c[1], 0))
    d = Cc - A
    L = d.length
    if L < 0.1:
        return
    u = d.normalized()
    n_ = Vector((-u.y, u.x, 0))
    yaw = math.degrees(math.atan2(u.y, u.x))
    # 둔덕 (덩어리 사이 틈을 메움)
    for k in range(max(1, int(L / 0.9))):
        q = A + d * ((k + 0.5) / max(1, int(L / 0.9))) + n_ * rng.uniform(-0.15, 0.15)
        C.blob(key, (q.x, q.y, G.h(q.x, q.y) - 0.02), rng.uniform(0.42, 0.55), (1.5, 1.2, 0.42), segs=8, rings=3,
               kind="detail", rot_z=math.radians(yaw) + rng.uniform(-0.3, 0.3))
    m = max(4, int(L / 0.22))
    for k in range(m):
        f = (k + rng.uniform(0.1, 0.9)) / m
        q = A + d * f + n_ * rng.gauss(0.0, t * 0.8)
        mid = 1.0 - abs(f - 0.5) * 1.3
        sz = rng.uniform(0.16, 0.34)
        z = G.h(q.x, q.y) + sz * 0.3 + max(0.0, mid) * rng.uniform(0.0, min(0.3, h * 0.3))
        C.rbox(key if rng.random() < 0.8 else cap, (q.x, q.y, z), (sz * rng.uniform(1.0, 1.8), sz * rng.uniform(0.7, 1.1), sz * 0.7),
               (rng.uniform(-30, 30), rng.uniform(-30, 30), yaw + rng.uniform(-60, 60)), kind="detail")
    for k in range(max(1, int(L / 1.1))):
        q = A + d * rng.uniform(0.1, 0.9) + n_ * rng.uniform(-t * 1.6, t * 1.6)
        C.rbox(cap, (q.x, q.y, G.h(q.x, q.y) + 0.06), (rng.uniform(0.35, 0.6), t * 0.5 + 0.08, 0.1),
               (rng.uniform(-12, 12), rng.uniform(-12, 12), yaw + rng.uniform(-40, 40)), kind="detail")


def _fence_wrecked(C, G, P0, d, L, h, pitch, key, rng, *, w=0.06, th=0.03):
    """밀려 쓰러진 나무 울타리: 부러진 말뚝 그루터기 + 땅에 누운 널·가로대 토막."""
    t = d.normalized()
    s_ = Vector((-t.y, t.x, 0))
    n = max(1, int(L / pitch))
    for k in range(n + 1):
        q = P0 + d * (k / n)
        z = G.h(q.x, q.y)
        if rng.random() < 0.55:
            C.beam(key, (q.x, q.y, z - 0.1), (q.x + rng.uniform(-0.04, 0.04), q.y, z + rng.uniform(0.08, 0.22)), w, th, kind="detail")
        if rng.random() < 0.8:
            a = math.atan2(t.y, t.x) + math.pi / 2 + rng.uniform(-0.9, 0.9)
            off = s_ * rng.uniform(-0.6, 0.6)
            ln = h * rng.uniform(0.45, 0.9)
            p0 = q + off
            p1 = p0 + Vector((math.cos(a), math.sin(a), 0)) * ln
            C.beam(key, (p0.x, p0.y, z + 0.035), (p1.x, p1.y, G.h(p1.x, p1.y) + 0.04), w, th, kind="detail",
                   up=(0, 0, 1))
    for k in range(max(1, int(L / 1.4))):
        q0 = P0 + d * rng.uniform(0.0, 0.8) + s_ * rng.uniform(-0.5, 0.5)
        a = math.atan2(t.y, t.x) + rng.uniform(-0.5, 0.5)
        q1 = q0 + Vector((math.cos(a), math.sin(a), 0)) * rng.uniform(0.6, 1.2)
        C.beam(key, (q0.x, q0.y, G.h(q0.x, q0.y) + 0.05), (q1.x, q1.y, G.h(q1.x, q1.y) + 0.06), 0.05, 0.06, kind="detail")


def bag_mesh(bm, c, yaw, L=0.62, W=0.34, H=0.15):
    """모래주머니 하나 (육각 단면, 양끝을 조금 줄인 베개 모양, 삼각형 20개)."""
    sec = [(-W / 2, H * 0.5), (-W * 0.34, 0.0), (W * 0.34, 0.0), (W / 2, H * 0.5), (W * 0.34, H), (-W * 0.34, H)]
    Mx = Matrix.Translation(Vector(c)) @ Matrix.Rotation(yaw, 4, "Z")
    ends = []
    for s, k in ((-1, 0.82), (1, 0.82)):
        ends.append([bm.verts.new(Mx @ Vector((s * L / 2, u * k, H * 0.5 + (v - H * 0.5) * k))) for u, v in sec])
    a, b = ends
    fs = [bm.faces.new(list(reversed(a))), bm.faces.new(b)]
    n = len(sec)
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)


def bag_row(C, p0, p1, z, *, rows=2, keys=("sandbag", "sandbag_d"), col=True, seed=0, L=0.62, W=0.34, H=0.15,
            zfn=None, kind="main", breakable=False, brk_name=None):
    """모래주머니 줄 (p0 → p1, 바닥 z 또는 zfn(x, y)). 줄마다 반 개씩 엇갈려 쌓는다. 높이 rows × H.
    breakable=True: 줄 하나가 부서지는 소품 BRK_sandbag_<n> (전차가 밀거나 주포로 쏘면 터져 낮은 더미가 된다). 이름을 돌려준다."""
    if breakable:
        with Breakable(C, "sandbag", brk_name) as b:
            bag_row(C, p0, p1, z, rows=rows, keys=keys, col=col, seed=seed, L=L, W=W, H=H, zfn=zfn, kind=kind)
            P0, P1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
            Lt = (P1 - P0).length
            if Lt >= 0.2:
                base = min(zfn(q.x, q.y) for q in (P0, (P0 + P1) / 2, P1)) if zfn else z
                with b.broken():
                    _bags_slumped(C, P0, (P1 - P0).normalized(), Lt, base, rows, keys, random.Random(seed + 7919), L, W, H, kind)
        return [b.node]
    rng = random.Random(seed)
    P0, P1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
    d = P1 - P0
    Lt = d.length
    if Lt < 0.2:
        return
    t = d.normalized()
    yaw = math.atan2(t.y, t.x)
    slots = []
    for r in range(rows):
        off = (L / 2) * (r % 2)
        n = max(1, int((Lt - off) / (L * 0.96)))
        for k in range(n):
            s = off + L * 0.48 + k * L * 0.96
            if s > Lt - L * 0.3:
                break
            slots.append((r, k, P0 + t * s))
    # 이웃 주머니는 끝이 4 % 겹친다. 겹친 곳에서 면이 한 평면에서 다투지 않게:
    #  - 줄 전체를 한 바닥 높이에 놓는다 (지형을 따르면 이웃 높이 차가 우연히 윗면을 맞춘다. zfn이면 가장 낮은 점)
    #  - 하나 걸러 단면을 같은 중심에서 10 % 줄인다 (윗면이 이웃보다 6 mm 낮다)
    #  - 하나 걸러 2.6° 돌린다 (흔들림 ±0.6°): 이웃 옆면·끝면의 방향이 늘 1.4° 넘게 달라 같은 평면이 되지 않는다
    base = min(zfn(q.x, q.y) for _, _, q in slots) if (zfn and slots) else z
    for r, k, q in slots:
        zb = base + r * H * 0.92
        sk = 0.9 if k % 2 else 1.0
        turn = (0.045 if (k // 2) % 2 else -0.045) if k % 2 else 0.0
        bag_mesh(C.bm(keys[rng.randrange(len(keys))], kind), (q.x, q.y, zb + H * (1 - sk) / 2),
                 yaw + turn + rng.uniform(-0.05, 0.05) * 0.2, L=L * rng.uniform(0.95, 1.03), W=W * sk, H=H * sk)
    if col:
        hgt = rows * H * 0.92 + H * 0.08
        nseg = max(1, int(Lt / 1.5)) if abs(t.x) > 0.02 and abs(t.y) > 0.02 else 1
        for k in range(nseg):
            a = P0 + d * (k / nseg)
            b = P0 + d * ((k + 1) / nseg)
            zb = min(zfn(a.x, a.y), zfn(b.x, b.y)) if zfn else z
            C.col(min(a.x, b.x) - W / 2 + 0.04, max(a.x, b.x) + W / 2 - 0.04, min(a.y, b.y) - W / 2 + 0.04,
                  max(a.y, b.y) + W / 2 - 0.04, zb - 0.1, zb + hgt)


def berm(solid, p0, p1, z, out, *, w=1.5, h=0.3, crest=0.45, key="earth"):
    """흙둑 (참호 테두리의 흉벽·배벽). p0→p1 선(참호 가장자리)에서 out(2D 단위 벡터) 쪽으로 w만큼, 꼭대기 h.
    안쪽 면은 거의 수직이고 바깥은 완만한 비탈. Solid에 넣어 트라이메시 충돌이 된다."""
    P0, P1 = Vector((p0[0], p0[1], z)), Vector((p1[0], p1[1], z))
    # 양 끝을 2 cm 안으로: 끝면이 참호 벽 끝(0)·벙커 옆면(0)·참호 끝 기둥 옆면(1 cm)과 1 cm 넘게 어긋나게
    t = (P1 - P0).normalized() * 0.02
    P0, P1 = P0 + t, P1 - t
    O = Vector((out[0], out[1], 0)).normalized()
    sec = [(0.0, -0.05), (0.03, h * 0.85), (crest, h), (w, -0.05)]
    b = solid(key)
    rows = []
    for P in (P0, P1):
        rows.append([b.verts.new(P + O * u + Vector((0, 0, v))) for u, v in sec])
    a, c = rows
    fs = []
    for i in range(len(sec) - 1):
        fs.append(b.faces.new((a[i], a[i + 1], c[i + 1], c[i])))
    fs.append(b.faces.new(list(reversed(a))))
    fs.append(b.faces.new(c))
    bmesh.ops.recalc_face_normals(b, faces=fs)


# ================================================================== field

def crater(C, G, solid, x, y, r, *, seed=0, h=0.32, n=12):
    """포탄 구덩이: 흙 테(트라이메시, 걸을 수 있는 비탈) + 짙은 흙 바닥 + 그을음 데칼."""
    rng = random.Random(seed)
    rad = [rng.uniform(0.85, 1.12) for _ in range(n)]
    hs = [h * rng.uniform(0.7, 1.15) for _ in range(n)]
    b = solid("earth")
    rings = []
    for (f, dz) in ((0.5, -0.04), (0.74, None), (1.08, -0.06)):
        ring = []
        for i in range(n):
            a = 2 * math.pi * i / n + seed
            xx, yy = x + math.cos(a) * r * f * rad[i], y + math.sin(a) * r * f * rad[i]
            zz = G.h(xx, yy) + (hs[i] if dz is None else dz)
            ring.append(b.verts.new((xx, yy, zz)))
        rings.append(ring)
    fs = []
    for k in range(2):
        for i in range(n):
            j = (i + 1) % n
            fs.append(b.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i])))
    for f in fs:
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    ground_disc(C, "mud_d", x, y, r * 0.58, G, n=n, rings=1, lift=0.03, seed=seed)
    ground_disc(C, "mud", x, y, r * 0.34, G, n=8, rings=1, lift=0.045, seed=seed + 1)


def wire_coil(C, G, p0, p1, *, r=0.34, pitch=0.55, col=True, seed=0, stakes=2.6, zfn=None, breakable=False, brk_name=None,
              section=6.0):
    """철조망 코일(낮음): 기울어진 육각 고리를 줄지어 + 위 가닥 + 말뚝. COL은 높이 0.75 (뛰어넘지 못한다).
    breakable=True: section m(기본 6) 안팎 토막마다 부서지는 소품 BRK_wire_<n> (전차·장갑차가 밀면 납작하게 깔려 지나갈 수 있다).
    이름 목록을 돌려준다."""
    if breakable:
        hf = zfn or G.h
        P0, P1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
        L = (P1 - P0).length
        m = max(1, int(round(L / section)))
        names = []
        for k in range(m):
            a = P0.lerp(P1, k / m)
            c = P0.lerp(P1, (k + 1) / m)
            nm = f"{brk_name}_{k + 1}" if (brk_name and m > 1) else brk_name
            with Breakable(C, "wire", nm) as b:
                wire_coil(C, G, (a.x, a.y), (c.x, c.y), r=r, pitch=pitch, col=col, seed=seed + k, stakes=stakes, zfn=zfn)
                d = c - a
                with b.broken():
                    _wire_crushed(C, a, d, d.length, d.normalized(), Vector((-d.normalized().y, d.normalized().x, 0)), hf, r,
                                  pitch, random.Random(seed + 104729 + k))
            names.append(b.node)
        return names
    rng = random.Random(seed)
    hf = zfn or G.h
    P0, P1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
    d = P1 - P0
    L = d.length
    t = d.normalized()
    s_ = Vector((-t.y, t.x, 0))
    b = C.bm("wire", "fine")
    n = max(2, int(L / pitch))
    for k in range(n + 1):
        q = P0 + d * (k / n)
        z0 = hf(q.x, q.y)
        tilt = 0.35 if k % 2 else -0.35
        ring = []
        for i in range(5):
            a = 2 * math.pi * i / 5 + rng.uniform(-0.15, 0.15)
            u, v = math.cos(a) * r, math.sin(a) * r
            ring.append(q + s_ * u + t * (v * tilt) + Vector((0, 0, z0 + r + 0.02 + v)))
        for i in range(5):
            a, c = ring[i], ring[(i + 1) % 5]
            w = t * 0.012
            vs = [b.verts.new(a - w), b.verts.new(c - w), b.verts.new(c + w), b.verts.new(a + w)]
            b.faces.new(vs)
    # 위 가닥 두 줄
    for off in (-0.12, 0.12):
        for k in range(n):
            qa = P0 + d * (k / n) + s_ * off
            qb = P0 + d * ((k + 1) / n) + s_ * off
            za, zb = hf(qa.x, qa.y) + 2 * r + 0.02, hf(qb.x, qb.y) + 2 * r + 0.02
            C.strip("wire", (qa.x, qa.y, za), (qb.x, qb.y, zb), 0.014, normal=s_, lift=0.0)
    m = max(1, int(L / stakes))
    for k in range(m + 1):
        q = P0 + d * (k / m)
        z0 = hf(q.x, q.y)
        C.beam("stake", (q.x, q.y, z0 - 0.1), (q.x, q.y, z0 + 2 * r + 0.15), 0.05, 0.05, kind="detail")
    if col:
        nseg = max(1, int(L / 1.5)) if abs(t.x) > 0.02 and abs(t.y) > 0.02 else 1
        for k in range(nseg):
            a = P0 + d * (k / nseg)
            c = P0 + d * ((k + 1) / nseg)
            zb = min(hf(a.x, a.y), hf(c.x, c.y))
            C.col(min(a.x, c.x) - r * 0.8, max(a.x, c.x) + r * 0.8, min(a.y, c.y) - r * 0.8, max(a.y, c.y) + r * 0.8,
                  zb - 0.2, zb + 0.75)


def hedgerow(C, G, pts, *, h=1.6, w=1.3, col=True, seed=0, seg=4.0, blobs=True, keys=("foliage_d", "foliage", "foliage_l")):
    """생울타리: 둥근 윗면 육각 단면 띠 + 위에 덩어리. 지형을 따라 휘고, COL은 조각마다 (높은 엄폐)."""
    rng = random.Random(seed)
    P = _resample(pts, seg)
    sec = [(-w / 2, -0.25), (w / 2, -0.25), (w * 0.48, h * 0.62), (w * 0.22, h), (-w * 0.22, h), (-w * 0.48, h * 0.62)]
    b = C.bm(keys[0], "main")
    prev = None
    n = len(P)
    for i, p in enumerate(P):
        a = P[max(0, i - 1)]
        c = P[min(n - 1, i + 1)]
        t = (c - a)
        t.z = 0
        t = t.normalized()
        s_ = Vector((-t.y, t.x, 0))
        z0 = G.h(p.x, p.y)
        ring = [b.verts.new(Vector((p.x, p.y, z0)) + s_ * u + Vector((0, 0, v * rng.uniform(0.93, 1.06) if v > 0 else v)))
                for u, v in sec]
        if prev is not None:
            for k in range(len(sec)):
                j = (k + 1) % len(sec)
                if k == 0:
                    continue
                f = b.faces.new((prev[k], prev[j], ring[j], ring[k]))
                f.smooth = True
        else:
            b.faces.new(list(reversed(ring)))
        prev = ring
    b.faces.new(prev)
    if blobs:
        for i in range(0, n, 1):
            p = P[i]
            if rng.random() < 0.5:
                z0 = G.h(p.x, p.y)
                C.blob(keys[1 + (i % 2)], (p.x + rng.uniform(-0.3, 0.3), p.y + rng.uniform(-0.3, 0.3), z0 + h * 0.86),
                       w * rng.uniform(0.5, 0.62), (1.3, 1.3, 0.7), segs=6, rings=3, rot_z=rng.uniform(0, 3))
    if col:
        # 조각마다 돌린 상자 (길이 = 조각, 폭 0.8w). 예전 축 정렬 상자는 끝에서 0.4w(0.5 m)씩 넘어 나갔다
        for a, c in zip(P, P[1:]):
            za, zc = G.h(a.x, a.y), G.h(c.x, c.y)
            m = (a + c) / 2
            yaw = math.degrees(math.atan2(c.y - a.y, c.x - a.x))
            C.ocol((m.x, m.y, min(za, zc) - 0.3), ((c - a).length, w * 0.8, max(za, zc) + h * 0.95 - min(za, zc) + 0.3),
                   yaw)


def stone_wall(C, G, pts, *, h=0.85, t=0.55, col=True, seed=0, seg=2.6, broken=(), key="stone_v", cap="stone_vd",
               breakable=False, brk_name=None):
    """마른 돌담 (낮은 엄폐, 높이 h). 조각마다 상자 + 갓돌, broken = [(s0, s1)] 무너진 구간(누적 거리, m).
    key·cap으로 벽돌 담도 된다 (도시: key="brick", cap="concrete_d").
    breakable=True: 조각(seg m)마다 부서지는 소품 BRK_wall_<n> (전차가 밀거나 주포로 쏘면 깨진 덩어리 더미가 되어 넘어 다닌다).
    broken 구간은 처음부터 무너진 정적 조각. 이름 목록을 돌려준다."""
    if breakable:
        P = _resample(pts, seg)
        names = []
        s = 0.0
        for k, (a, c) in enumerate(zip(P, P[1:])):
            L = (c - a).length
            s_mid = s + L / 2
            s += L
            if any(b0 <= s_mid <= b1 for b0, b1 in broken):
                stone_wall(C, G, [a, c], h=h, t=t, col=col, seed=seed + k, seg=L + 1, broken=[(0, L)], key=key, cap=cap)
                continue
            nm = f"{brk_name}_{k + 1}" if brk_name else None
            with Breakable(C, "wall", nm) as b:
                stone_wall(C, G, [a, c], h=h, t=t, col=col, seed=seed + k, seg=L + 1, key=key, cap=cap)
                with b.broken():
                    _wall_rubble(C, G, a, c, t, h, key, cap, random.Random(seed + 7877 + k))
            names.append(b.node)
        return names
    rng = random.Random(seed)
    P = _resample(pts, seg)
    s = 0.0
    for a, c in zip(P, P[1:]):
        L = (c - a).length
        mid = (a + c) / 2
        s_mid = s + L / 2
        s += L
        if any(b0 <= s_mid <= b1 for b0, b1 in broken):
            for k in range(2):
                q = a.lerp(c, rng.uniform(0.1, 0.9)) + Vector((rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0))
                C.blob(key if k else cap, (q.x, q.y, G.h(q.x, q.y) + 0.08), rng.uniform(0.18, 0.3), (1.2, 1, 0.6), segs=6,
                       rings=3, kind="detail")
            hh = h * rng.uniform(0.25, 0.4)
        else:
            hh = h * rng.uniform(0.92, 1.06)
        za, zc = G.h(a.x, a.y), G.h(c.x, c.y)
        zb = min(za, zc) - 0.35
        zt = (za + zc) / 2 + hh
        t_ = (c - a).normalized()
        yaw = math.degrees(math.atan2(t_.y, t_.x))
        C.rbox(key, (mid.x, mid.y, (zb + zt) / 2), (L + 0.04, t, zt - zb), (0, 0, yaw))
        C.rbox(cap, (mid.x, mid.y, zt + 0.05), (L + 0.02, t + 0.08, 0.12), (0, 0, yaw + rng.uniform(-1.5, 1.5)),
               kind="detail")
        if hh > h * 0.5:
            # 쌓은 돌 줄눈 (가로 한 줄 + 엇갈린 세로 줄눈, 양면)
            nrm = Vector((-t_.y, t_.x, 0))
            zm = (za + zc) / 2 + hh * 0.48
            for sg in (-1, 1):
                off = nrm * (sg * (t / 2 + 0.004))
                C.strip(cap, Vector((a.x, a.y, zm)) + off, Vector((c.x, c.y, zm)) + off, 0.035, normal=nrm * sg, lift=0.0)
                for u, z_a, z_b in ((0.35 if sg > 0 else 0.6, zm, zt), (0.7 if sg > 0 else 0.25, zb + 0.35, zm)):
                    q = a.lerp(c, u) + off
                    C.strip(cap, Vector((q.x, q.y, z_a)), Vector((q.x, q.y, z_b)), 0.03, normal=nrm * sg, lift=0.0)
        if col:
            C.ocol((mid.x, mid.y, zb), (L + 0.04, t + 0.08, zt + 0.11 - zb), yaw)   # 비스듬한 담도 담 모양 그대로


def hay_bale(C, x, y, z, *, yaw=0.0, r=0.62, L=1.0, col=True):
    """둥근 건초 더미 (눕힌 원통)."""
    Lc = Local((x, y, z), yaw)
    Lc.cyl(C, "hay", (-L / 2, 0, r), (L / 2, 0, r), r, segs=10)
    for s in (-0.25, 0.25):
        Lc.cyl(C, "thatch", (s * L - 0.02, 0, r), (s * L + 0.02, 0, r), r + 0.012, segs=10, kind="detail")
    if col:
        bm_col(C, lambda b: mk._bm_cyl(b, Lc.p(-L / 2 - 0.02, 0, r), Lc.p(L / 2 + 0.02, 0, r), r + 0.012, segs=10))


def stump(C, x, y, z, *, r=0.28, h=0.7, seed=0, col=True):
    """포격에 부러진 나무 그루터기 (뾰족한 끝)."""
    rng = random.Random(seed)
    C.cyl("bark_d", (x, y, z - 0.1), (x, y, z + h), r, r2=r * 0.8, segs=7)
    for k in range(3):
        a = rng.uniform(0, 6.28)
        C.cyl("plank", (x + math.cos(a) * r * 0.4, y + math.sin(a) * r * 0.4, z + h - 0.02),
              (x + math.cos(a) * r * 0.3, y + math.sin(a) * r * 0.3, z + h + rng.uniform(0.25, 0.5)), r * 0.35, r2=0.01,
              segs=4, kind="detail", smooth=False)
    if col:
        C.col(x - r, x + r, y - r, y + r, z - 0.1, z + h)


def hedgehog(C, x, y, z, *, yaw=0.0, s=1.1, col=True):
    """R41 육각 장애물 (강철 들보 세 개를 엇갈려 묶은 '고슴도치'). R41 회색 + 앰버 띠."""
    Lc = Local((x, y, z + s * 0.42), yaw)
    for k in range(3):
        a = math.radians(60 * k)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        e = Matrix.Rotation(math.radians(35), 3, Vector((-d.y, d.x, 0))) @ d
        p0, p1 = -e * s * 0.62, e * s * 0.62
        C.beam("r41_light", Lc.p(*p0), Lc.p(*p1), 0.1, 0.1, kind="detail")
        C.beam("amber", Lc.p(*(p1 * 0.82)), Lc.p(*(p1 * 0.92)), 0.106, 0.106, kind="fine")   # 3 mm 띠: 강한 편향
    if col:
        # 들보 여섯 끝의 볼록 껍질 (예전 상자는 들보 사이 모서리가 0.6 m 비었다)
        pts = []
        for k in range(3):
            a = math.radians(60 * k)
            d = Vector((math.cos(a), math.sin(a), 0.0))
            e = Matrix.Rotation(math.radians(35), 3, Vector((-d.y, d.x, 0))) @ d
            for q in (-e * s * 0.62, e * s * 0.62):
                pts += [tuple(Lc.p(*(q + Vector((dx, dy, dz))))) for dx in (-0.05, 0.05) for dy in (-0.05, 0.05)
                        for dz in (-0.05, 0.05)]
        C.ccol([(px, py, max(pz, z - 0.05)) for (px, py, pz) in pts])


# ================================================================== R41 field works

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


def drum_r41(C, x, y, z, *, r=0.26, h=0.78, lie=False, yaw=0.0, col=True):
    """R41 연료통 (제국 흑 + 앰버 띠 두 줄)."""
    if lie:
        Lc = Local((x, y, z), yaw)
        Lc.cyl(C, "r41_shell", (-h / 2, 0, r), (h / 2, 0, r), r, segs=10)
        for u in (-0.22, 0.22):
            Lc.cyl(C, "amber", (u * h - 0.025, 0, r), (u * h + 0.025, 0, r), r + 0.008, segs=10, kind="detail")
        if col:
            Lc.col(C, -h / 2, h / 2, -r, r, 0, 2 * r)
        return
    C.cyl("r41_shell", (x, y, z), (x, y, z + h), r, segs=10)
    for zz in (0.22, 0.6):
        C.cyl("amber", (x, y, z + zz * h - 0.025), (x, y, z + zz * h + 0.025), r + 0.008, segs=10, kind="detail")
    if col:
        C.col(x - r, x + r, y - r, y + r, z, z + h)


def r41_bunker(C, x0, x1, y0, y1, zf, zt, *, front="-y", door=None, top=1.3, seed=0, logo=True):
    """R41 야전 벙커: 모따기 회백 몸체(바닥 zf부터 지면 위 top까지) + 어두운 밑단 + 앰버 띠 + 앞면 마젠타 사격 슬릿과 덮개 +
    문(앞면, 참호 바닥 높이) + 지붕 모래주머니 + 육각 환기 덮개 + 엘프 로고. 앞면이 참호 벽을 덮는다. COL = 몸체 상자."""
    rng = random.Random(seed)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, d = x1 - x0, y1 - y0
    zh = zt + top
    yaw = {"-y": 0.0, "+y": 180.0, "-x": -90.0, "+x": 90.0}[front]
    W, D = (w, d) if front in ("-y", "+y") else (d, w)
    L = Local((cx, cy, 0), yaw)
    L.chbox(C, "r41_light", (0, 0, (zf + zh) / 2), (W, D, zh - zf), 0.22)
    L.chbox(C, "r41_shell", (0, 0, zt + 0.12), (W + 0.08, D + 0.08, 0.26), 0.06, kind="detail")
    L.chbox(C, "r41_shell", (0, 0, zh + 0.06), (W - 0.3, D - 0.3, 0.14), 0.05, kind="detail")
    for s in (-1, 1):
        L.rect(C, "amber", (s * W / 2, 0, zt + top * 0.7), (s, 0, 0), D * 0.7, 0.07, lift=0.008)
    L.rect(C, "amber", (0, D / 2, zt + top * 0.7), (0, 1, 0), W * 0.7, 0.07, lift=0.008)
    # 앞면 사격 슬릿 (어두운 홈 + 마젠타 줄 + 덮개)
    sw = W - 1.6
    zs = zt + top * 0.48
    L.box(C, "r41_dark", -sw / 2, sw / 2, -D / 2 - 0.03, -D / 2 + 0.02, zs - 0.11, zs + 0.11, kind="fine")
    L.box(C, "magenta", -sw / 2 + 0.1, sw / 2 - 0.1, -D / 2 - 0.055, -D / 2 - 0.03, zs - 0.02, zs + 0.02)  # 문보다 1.2 cm 앞
    L.chbox(C, "r41_shell", (0, -D / 2 - 0.12, zs + 0.2), (sw + 0.3, 0.3, 0.1), 0.04, kind="detail")
    # 문 (참호 바닥에서)
    if door is not None:
        du, dw = door
        # 문 안 어둠: 밑단 띠(-D/2 - 0.04, detail)보다 3 mm 앞, 마젠타 슬릿(-0.055)보다 뒤
        L.box(C, "r41_dark", du - dw / 2, du + dw / 2, -D / 2 - 0.043, -D / 2 + 0.025, zf, zf + 1.75, kind="fine")
        L.box(C, "r41_shell", du - dw / 2 - 0.1, du - dw / 2, -D / 2 - 0.08, -D / 2, zf, zf + 1.85, kind="detail")
        L.box(C, "r41_shell", du + dw / 2, du + dw / 2 + 0.1, -D / 2 - 0.08, -D / 2, zf, zf + 1.85, kind="detail")
        L.box(C, "r41_shell", du - dw / 2 - 0.1, du + dw / 2 + 0.1, -D / 2 - 0.08, -D / 2, zf + 1.75, zf + 1.86,
              kind="detail")
        L.box(C, "magenta", du + dw / 2 + 0.02, du + dw / 2 + 0.08, -D / 2 - 0.1, -D / 2 - 0.08, zf + 1.55, zf + 1.7)
        L.col(C, du - dw / 2 - 0.1, du + dw / 2 + 0.1, -D / 2 - 0.1, -D / 2 + 0.01, zf, zf + 1.86)   # 문틀 (앞 8 cm)
    if logo:
        C.logo(L.p(-W / 2 + 0.6, -D / 2 - 0.02, zt + top * 0.3), 0.32, L.d(0, -1, 0), key="amber", disc="r41_shell",
               disc_scale=0.72)
    # 지붕 모래주머니 + 육각 환기 덮개
    for s in (-1, 1):
        bag_row(C, L.p(-W / 2 + 0.4, s * (D / 2 - 0.35), 0), L.p(W / 2 - 0.4, s * (D / 2 - 0.35), 0), zh + 0.12, rows=1,
                col=False, seed=seed + s)
    for k, u in enumerate((-W * 0.22, W * 0.22)):
        c = L.p(u, D * 0.15, 0)
        mk._bm_prism(C.bm("r41_shell", "detail"), ngon(0.22, 6, 30, c.x, c.y), zh + 0.1, zh + 0.42)
        mk._bm_prism(C.bm("r41_metal", "detail"), ngon(0.27, 6, 30, c.x, c.y), zh + 0.42, zh + 0.48)
    C.col(x0, x1, y0, y1, zf - 0.3, zh + 0.2)


def r41_container(C, cx, cy, z, *, axis="x", L=5.6, W=2.3, H=2.4, door="+y", seed=0, col=True, label="R41-07",
                  burnt=False):
    """R41 조립식 컨테이너 (회백 모따기 몸체 + 제국 흑 골조·밑틀 + 앰버 띠·스텐실 + 마젠타 상태등 + 문 데칼)."""
    yaw = 0.0 if axis == "x" else 90.0
    Lc = Local((cx, cy, z), yaw)
    body = "r41_shell" if burnt else "r41_light"
    Lc.chbox(C, body, (0, 0, 0.12 + H / 2), (L, W, H), 0.14)
    Lc.box(C, "r41_shell", -L / 2 + 0.1, L / 2 - 0.1, -W / 2 + 0.1, W / 2 - 0.1, -0.15, 0.14)
    # 벽에 겹쳐 붙는 판은 편향 등급을 나눈다(표준 깊이 버퍼는 같은 등급 몇 mm를 먼 거리에서 못 가른다):
    # 골조·끝판·그을음 = under(약한 편향), 앰버 띠·글자·문 = fine(강한 편향). 같은 등급끼리는 겹치지 않게
    # 그을음 자리의 골조는 끊고, 앰버 띠는 문 자리에서 끊는다
    soot = (-L * 0.3, L * 0.3, 0.12 + H * 0.3, 0.12 + H * 0.9) if burnt else None     # -Y 면 (u0, u1, z0, z1)
    door_side = {"+y": 1, "-y": -1}.get(door)
    for s in (-1, 1):
        k = -L / 2 + 0.55
        while k < L / 2 - 0.3:
            runs = [(0.27, H - 0.03)]
            if soot and s < 0 and soot[0] - 0.04 < k < soot[1] + 0.04:
                runs = [(0.27, soot[2]), (soot[3], H - 0.03)]
            for za, zb in runs:
                if zb - za > 0.05:
                    Lc.rect(C, "r41_shell", (k, s * W / 2, (za + zb) / 2), (0, s, 0), 0.08, zb - za, lift=0.006,
                            kind="under")
            k += 0.9
        if not burnt:
            runs = [(-L * 0.46, L * 0.46)]
            if s == door_side:
                runs = [(-L * 0.46, L * 0.25 - 0.5), (L * 0.25 + 0.5, L * 0.46)]
            for u0, u1 in runs:
                if u1 - u0 > 0.05:
                    Lc.rect(C, "amber", ((u0 + u1) / 2, s * W / 2, 0.12 + H * 0.78), (0, s, 0), u1 - u0, 0.08, lift=0.01)
            if label and s < 0:
                Lc.text(C, "amber", label, 0.22, (-L * 0.3, s * W / 2, 0.12 + H * 0.55), (0, s, 0), lift=0.012)
    for s in (-1, 1):
        Lc.rect(C, "r41_shell", (s * L / 2, 0, 0.12 + H / 2), (s, 0, 0), W * 0.8, H * 0.8, lift=0.006, kind="under")
    if door:
        n = {"+y": (0, 1, 0), "-y": (0, -1, 0), "+x": (1, 0, 0), "-x": (-1, 0, 0)}[door]
        if door in ("+y", "-y"):
            pos = (L * 0.25, n[1] * W / 2, 0.14 + 0.95)
            Lc.rect(C, "r41_dark", pos, n, 0.95, 1.85, lift=0.012)
            if not burnt:
                Lc.box(C, "magenta", L * 0.25 + 0.55, L * 0.25 + 0.62, n[1] * (W / 2 + 0.005) - 0.01,
                       n[1] * (W / 2 + 0.005) + 0.01, 1.8, 1.95)
        else:
            Lc.rect(C, "r41_dark", (n[0] * L / 2, 0, 0.14 + 0.95), n, 1.0, 1.85, lift=0.012)
    if burnt:
        Lc.rect(C, "soot", (0, -W / 2, (soot[2] + soot[3]) / 2), (0, -1, 0), soot[1] - soot[0], soot[3] - soot[2],
                lift=0.009, kind="under")
    if col:
        Lc.col(C, -L / 2, L / 2, -W / 2, W / 2, -0.15, H + 0.2)


def wreck_raider(C, x, y, z, *, yaw=0.0, col=True, embers=True):
    """불탄 R41 기동차량(레이더): 그을린 모따기 차체 + 지붕 틀 + 바퀴 넷(하나 빠짐) + 남은 앰버 띠 + 불씨. 정면 -Y."""
    L = Local((x, y, z), yaw)
    L.chbox(C, "r41_shell", (0, 0, 0.75), (1.9, 3.6, 0.7), 0.16)
    L.chbox(C, "soot", (0, 0.35, 1.3), (1.7, 1.8, 0.45), 0.12)
    for s in (-1, 1):
        L.beam(C, "r41_metal", (s * 0.8, -0.7, 1.1), (s * 0.75, -0.1, 1.75), 0.06, 0.06, kind="detail")
        L.rect(C, "amber", (s * 0.951, -0.9, 0.85), (s, 0, 0), 1.0, 0.05, lift=0.006)
    L.beam(C, "r41_metal", (-0.75, -0.1, 1.75), (0.75, -0.1, 1.75), 0.06, 0.06, kind="detail")
    for i, (sx, sy) in enumerate(((-1, -1.15), (1, -1.15), (-1, 1.15), (1, 1.15))):
        if i == 1:
            L.cyl(C, "rubber", (sx * 1.6, sy - 0.9, 0.12), (sx * 1.6, sy - 0.9, 0.42), 0.38, segs=10)
            continue
        L.cyl(C, "rubber", (sx * 0.85, sy, 0.4), (sx * 1.1, sy, 0.4), 0.4, segs=10)
    L.rect(C, "soot", (0, -1.8, 0.75), (0, -1, 0), 1.5, 0.5, lift=0.01)
    if embers:
        L.blob(C, "ember", (0.2, 0.6, 1.5), 0.18, segs=6, rings=4)
        L.blob(C, "fire", (-0.3, 0.2, 1.48), 0.12, segs=6, rings=4)
    if col:
        L.col(C, -1.0, 1.0, -1.85, 1.85, 0, 1.6)


def generator(C, x, y, z, *, yaw=0.0, col=True):
    """R41 야전 발전기: 모따기 흑 몸체 + 회백 덮개판 + 앰버 띠 + 배기관 + 육각 환기 + 마젠타 상태등. 정면 -Y."""
    L = Local((x, y, z), yaw)
    L.box(C, "r41_metal", -1.05, 1.05, -0.55, 0.55, 0.0, 0.12)
    L.chbox(C, "r41_shell", (0, 0, 0.12 + 0.55), (2.0, 1.0, 1.1), 0.12)
    for s in (-1, 1):
        L.chbox(C, "r41_light", (s * 0.55, -0.5, 0.75), (0.75, 0.06, 0.7), 0.03, kind="detail")
    L.rect(C, "amber", (0, -0.505, 1.12), (0, -1, 0), 1.8, 0.06, lift=0.006)
    L.rect(C, "magenta", (-0.15, -0.505, 1.02), (0, -1, 0), 0.08, 0.05, lift=0.008)
    L.text(C, "amber", "R41 · 발전기", 0.09, (0.35, -0.505, 1.0), (0, -1, 0), lift=0.008)
    L.cyl(C, "r41_metal", (0.7, 0.25, 1.22), (0.7, 0.25, 1.85), 0.07, segs=8)
    L.cyl(C, "soot", (0.7, 0.25, 1.85), (0.7, 0.25, 1.9), 0.08, segs=8, kind="detail")
    c = L.p(-0.4, 0.2, 0)
    mk._bm_prism(C.bm("r41_metal", "detail"), ngon(0.2, 6, 30, c.x, c.y), z + 1.22, z + 1.36)
    if col:
        L.col(C, -1.05, 1.05, -0.55, 0.55, 0, 1.3)


def cable(C, pts, *, r=0.03, key="r41_shell"):
    for a, b in zip(pts, pts[1:]):
        C.cyl(key, a, b, r, segs=5, cap=False, kind="detail")


def antenna_mast(C, x, y, z, *, h=14.0, yaw=0.0, guy=7.0):
    """R41 야전 안테나 탑: 육각 받침 + 세 다리 격자 탑(가새) + 패널 안테나 + 마젠타 꼭대기 등 + 당김줄."""
    L = Local((x, y, z), yaw)
    mk._bm_prism(C.bm("r41_shell", "main"), ngon(0.95, 6, 30, x, y), z - 0.3, z + 0.35)
    mk._bm_prism(C.bm("amber", "detail"), ngon(0.97, 6, 30, x, y), z + 0.24, z + 0.3)
    w0, w1 = 0.62, 0.22
    legs = []
    for k in range(3):
        a = math.radians(90 + 120 * k)
        legs.append((math.cos(a), math.sin(a)))
    nsec = 6

    def leg(k, zz):
        f = zz / h
        r = w0 + (w1 - w0) * f
        return L.p(legs[k][0] * r, legs[k][1] * r, 0.35 + zz)
    for k in range(3):
        C.beam("r41_light", leg(k, 0), leg(k, h), 0.07, 0.07, kind="detail")
    for s in range(nsec):
        za, zb = h * s / nsec, h * (s + 1) / nsec
        for k in range(3):
            j = (k + 1) % 3
            C.beam("r41_metal", leg(k, za), leg(j, zb), 0.035, 0.035, kind="detail")
            C.beam("r41_metal", leg(k, zb), leg(j, zb), 0.035, 0.035, kind="detail")
        if s % 2 == 0:
            for k in range(3):
                p = leg(k, (za + zb) / 2)
                C.box("amber", p.x - 0.045, p.x + 0.045, p.y - 0.045, p.y + 0.045, p.z - 0.15, p.z + 0.15, kind="detail")
    top = L.p(0, 0, 0.35 + h)
    C.cyl("r41_metal", top, top + Vector((0, 0, 2.2)), 0.03, segs=6)
    C.blob("magenta", top + Vector((0, 0, 2.25)), 0.1, segs=8, rings=5)
    C.blob("magenta", L.p(0.25, 0, 0.35 + h * 0.62), 0.07, segs=6, rings=4)
    for k in range(3):
        a = math.radians(30 + 120 * k)
        c = L.p(math.cos(a) * 0.38, math.sin(a) * 0.38, 0.35 + h * 0.84)
        rot = Matrix.Translation(c) @ Matrix.Rotation(a + math.pi / 2, 4, "Z")
        chbox_bm(C.bm("r41_light", "detail"), (0, 0, 0), (0.36, 0.08, 0.9), 0.03, matrix=rot)
        C.box("amber", c.x - 0.02, c.x + 0.02, c.y - 0.02, c.y + 0.02, c.z - 0.47, c.z - 0.4, kind="detail")
    for k in range(3):
        a = math.radians(90 + 120 * k + 60)
        anc = Vector((x + math.cos(a) * guy, y + math.sin(a) * guy, z))
        C.beam("wire", L.p(0, 0, 0.35 + h * 0.75), anc + Vector((0, 0, 0.1)), 0.016, 0.016, kind="fine")
        C.box("r41_shell", anc.x - 0.15, anc.x + 0.15, anc.y - 0.15, anc.y + 0.15, z - 0.2, z + 0.15, kind="detail")
    C.ccol([(x + px, y + py, zz) for (px, py) in ngon(0.97, 6, 30) for zz in (z - 0.3, z + 0.35)])   # 육각 받침
    C.ccol([tuple(leg(k, zz)) for k in range(3) for zz in (0.0, h)])     # 세 다리 격자 탑 (예전 상자는 위로 갈수록 4 m 비었다)


def map_table(C, x, y, z, *, yaw=0.0, col=True):
    """작전 탁자 (엘프 높이 0.68 m): 회백 상판 + 지도(종이 + 선 + 앰버·마젠타 핀) + 태블릿 + 의자 둘."""
    L = Local((x, y, z), yaw)
    for sx in (-1, 1):
        for sy in (-1, 1):
            L.box(C, "r41_metal", sx * 0.85 - 0.04, sx * 0.85 + 0.04, sy * 0.45 - 0.04, sy * 0.45 + 0.04, 0, 0.64,
                  kind="detail")
    L.chbox(C, "r41_light", (0, 0, 0.66), (1.9, 1.05, 0.05), 0.02)
    L.rect(C, "paper", (0, 0, 0.687), (0, 0, 1), 1.5, 0.82, up=(0, 1, 0), lift=0.003)
    rng = random.Random(int(x * 10 + y))
    for k in range(6):
        a = (rng.uniform(-0.7, 0.7), rng.uniform(-0.38, 0.38))
        b = (a[0] + rng.uniform(-0.4, 0.4), a[1] + rng.uniform(-0.2, 0.2))
        zl = 0.694 if k < 2 else 0.692                       # 선끼리 겹치는 곳: 초록이 위
        C.strip("fy_green" if k < 2 else "r41_shell", L.p(a[0], a[1], zl), L.p(b[0], b[1], zl), 0.012, lift=0.0)
    for k in range(5):
        p = L.p(rng.uniform(-0.65, 0.65), rng.uniform(-0.34, 0.34), 0.69)
        C.cyl("magenta" if k % 2 else "amber", p, p + Vector((0, 0, 0.05)), 0.012, segs=5, kind="fine")
    L.chbox(C, "r41_shell", (0.6, -0.3, 0.705), (0.32, 0.22, 0.03), 0.01, kind="detail")
    L.rect(C, "screen_r41", (0.6, -0.3, 0.721), (0, 0, 1), 0.26, 0.16, up=(0, 1, 0), lift=0.002)
    for s in (-1, 1):
        L.chbox(C, "r41_shell", (s * 0.4, -0.85, 0.36), (0.42, 0.4, 0.06), 0.02, kind="detail")
        for u in (-0.15, 0.15):
            L.box(C, "r41_metal", s * 0.4 + u - 0.025, s * 0.4 + u + 0.025, -0.85 - 0.025, -0.85 + 0.025, 0, 0.34,
                  kind="detail")
        if col:
            L.col(C, s * 0.4 - 0.22, s * 0.4 + 0.22, -1.06, -0.64, 0, 0.4)    # 의자
    if col:
        L.col(C, -0.95, 0.95, -0.53, 0.53, 0, 0.7)


def floodlight(C, x, y, z, *, yaw=0.0, h=3.4, lit=False):
    """R41 투광등 기둥 (육각 받침 + 기둥 + 모따기 등 머리 두 개, 렌즈)."""
    L = Local((x, y, z), yaw)
    mk._bm_prism(C.bm("r41_shell", "detail"), ngon(0.32, 6, 30, x, y), z - 0.1, z + 0.18)
    C.cyl("r41_metal", (x, y, z), (x, y, z + h), 0.06, segs=6)
    for s in (-1, 1):
        L.chbox(C, "r41_shell", (s * 0.22, -0.06, h + 0.05), (0.3, 0.22, 0.22), 0.04, kind="detail")
        L.rect(C, "lamp" if lit else "lamp_off", (s * 0.22, -0.172, h + 0.05), (0, -1, 0), 0.22, 0.16, lift=0.004)
    C.col(x - 0.3, x + 0.3, y - 0.3, y + 0.3, z, z + 0.18)        # 육각 받침
    C.col(x - 0.08, x + 0.08, y - 0.08, y + 0.08, z, z + h)       # 기둥


def _mesh_fence_flat(C, G, a, c, h, rng):
    """깔려 누운 철망 울타리 토막: 밀린 쪽으로 누운 철망 판(가운데가 꺾임) + 쓰러진 기둥 + 늘어진 가시줄."""
    d = c - a
    L = d.length
    if L < 0.1:
        return
    t = d.normalized()
    n_ = Vector((-t.y, t.x, 0)) * (1 if rng.random() < 0.5 else -1)
    b = C.bm("wire_mesh", "fine")
    z = lambda q: G.h(q.x, q.y)
    reach = min(h, 1.8)
    q0, q1 = a, c
    m0, m1 = a + n_ * reach * 0.5, c + n_ * reach * 0.5
    e0, e1 = a + n_ * reach, c + n_ * reach
    for (u0, u1, v0, v1, lift0, lift1) in ((q0, q1, m1, m0, 0.08, 0.16), (m0, m1, e1, e0, 0.16, 0.05)):
        b.faces.new([b.verts.new((u0.x, u0.y, z(u0) + lift0)), b.verts.new((u1.x, u1.y, z(u1) + lift0)),
                     b.verts.new((v0.x, v0.y, z(v0) + lift1)), b.verts.new((v1.x, v1.y, z(v1) + lift1))])
    for q in (a, c):
        tip = q + n_ * reach + t * rng.uniform(-0.3, 0.3)
        C.beam("r41_metal", (q.x, q.y, z(q) + 0.06), (tip.x, tip.y, z(tip) + 0.07), 0.12, 0.12, kind="detail")
    for off in (0.0, 0.08):
        p0 = a + n_ * (reach + off)
        p1 = c + n_ * (reach + off + rng.uniform(-0.1, 0.1))
        C.strip("wire", (p0.x, p0.y, z(p0) + 0.04), (p1.x, p1.y, z(p1) + 0.04), 0.015, normal=(0, 0, 1), lift=0.0)


def hq_fence(C, G, p0, p1, *, h=2.0, pitch=3.2, gaps=(), col=True, breakable=False, brk_name=None, cluster=2):
    """R41 철망 울타리 (축 정렬 직선 p0 → p1): 육각 기둥 + 반투명 철망 + 위 가시줄 두 가닥 + 앰버 반사표.
    gaps = [(s0, s1)] 비울 구간(시작점에서 잰 거리).
    breakable=True: 기둥 칸 cluster개(기본 2, 약 6.4 m)마다 부서지는 소품 BRK_fence_<n> (전차·장갑차가 밀면 철망째 눕는다).
    이름 목록을 돌려준다."""
    if breakable:
        P0, P1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
        d = P1 - P0
        Lt = d.length
        t = d.normalized()
        runs, cur = [], 0.0
        for a, b_ in sorted(gaps):
            if a > cur:
                runs.append((cur, a))
            cur = max(cur, b_)
        if cur < Lt:
            runs.append((cur, Lt))
        names = []
        rng = random.Random(len(runs) * 31 + int(Lt * 10))
        for (s0, s1) in runs:
            span = pitch * max(1, cluster)
            m = max(1, int(round((s1 - s0) / span)))
            for k in range(m):
                a = P0 + t * (s0 + (s1 - s0) * k / m)
                c = P0 + t * (s0 + (s1 - s0) * (k + 1) / m)
                nm = f"{brk_name}_{len(names) + 1}" if brk_name else None
                with Breakable(C, "fence", nm) as b:
                    hq_fence(C, G, (a.x, a.y), (c.x, c.y), h=h, pitch=pitch, col=col)
                    with b.broken():
                        _mesh_fence_flat(C, G, a, c, h, rng)
                names.append(b.node)
        return names
    P0, P1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
    d = P1 - P0
    Lt = d.length
    t = d.normalized()
    nrm = Vector((-t.y, t.x, 0))
    cuts = sorted(gaps)
    runs = []
    cur = 0.0
    for a, b in cuts:
        if a > cur:
            runs.append((cur, a))
        cur = max(cur, b)
    if cur < Lt:
        runs.append((cur, Lt))
    for (s0, s1) in runs:
        n = max(1, int(math.ceil((s1 - s0) / pitch)))
        for k in range(n + 1):
            q = P0 + t * (s0 + (s1 - s0) * k / n)
            zq = G.h(q.x, q.y)
            C.box("r41_metal", q.x - 0.06, q.x + 0.06, q.y - 0.06, q.y + 0.06, zq - 0.2, zq + h + 0.1, kind="detail")
            if k % 2 == 0:
                C.box("amber", q.x - 0.07, q.x + 0.07, q.y - 0.07, q.y + 0.07, zq + 1.25, zq + 1.33, kind="detail")
            if k < n:
                q2 = P0 + t * (s0 + (s1 - s0) * (k + 1) / n)
                z2 = G.h(q2.x, q2.y)
                b = C.bm("wire_mesh", "fine")
                vs = [b.verts.new((q.x, q.y, zq + 0.05)), b.verts.new((q2.x, q2.y, z2 + 0.05)),
                      b.verts.new((q2.x, q2.y, z2 + h - 0.05)), b.verts.new((q.x, q.y, zq + h - 0.05))]
                b.faces.new(vs)
                for zz in (0.05, h - 0.05):
                    C.strip("r41_metal", (q.x, q.y, zq + zz), (q2.x, q2.y, z2 + zz), 0.04, normal=nrm, lift=0.0)
                for zz in (h + 0.02, h + 0.1):
                    C.strip("wire", (q.x, q.y, zq + zz), (q2.x, q2.y, z2 + zz), 0.015, normal=nrm, lift=0.0)
        if col:
            a = P0 + t * s0
            b = P0 + t * s1
            za, zb = G.h(a.x, a.y), G.h(b.x, b.y)
            C.col(min(a.x, b.x) - 0.12, max(a.x, b.x) + 0.12, min(a.y, b.y) - 0.12, max(a.y, b.y) + 0.12,
                  min(za, zb) - 0.3, max(za, zb) + h + 0.15)


def hq_gate(C, x, y, z, *, yaw=0.0, w=6.0, h=2.2, sign=("R41 · 전방 지휘소", "FIELD HQ"), swing=65.0):
    """울타리 문: 모따기 문기둥 두 개(마젠타 등) + 위 가로 간판 + 바깥(-Y)으로 열린 철망 문짝 두 짝.
    (x, y)는 문 가운데 바닥. 정면 -Y = 바깥."""
    L = Local((x, y, z), yaw)
    for s in (-1, 1):
        L.chbox(C, "r41_light", (s * (w / 2 + 0.25), 0, h / 2 + 0.2), (0.45, 0.45, h + 0.4), 0.08)
        L.chbox(C, "r41_shell", (s * (w / 2 + 0.25), 0, 0.1), (0.55, 0.55, 0.3), 0.06, kind="detail")
        L.rect(C, "amber", (s * (w / 2 + 0.25), -0.226, h * 0.6), (0, -1, 0), 0.3, 0.06, lift=0.006)
        L.blob(C, "magenta", (s * (w / 2 + 0.25), 0, h + 0.5), 0.12, segs=8, rings=5)
        L.col(C, s * (w / 2 + 0.25) - 0.23, s * (w / 2 + 0.25) + 0.23, -0.23, 0.23, -0.2, h + 0.4)
        # 문짝 (경첩 = 문기둥 안쪽, 바깥으로 열림)
        hx = s * w / 2
        a = math.radians(swing) * s
        dirv = Vector((-s * math.cos(a), -abs(math.sin(a)), 0))
        p0 = L.p(hx, 0, 0.1)
        p1 = p0 + L.d(*dirv) * (w / 2 - 0.1)
        b = C.bm("wire_mesh", "fine")
        vs = [b.verts.new(p0), b.verts.new(p1), b.verts.new(p1 + Vector((0, 0, h - 0.2))),
              b.verts.new(p0 + Vector((0, 0, h - 0.2)))]
        b.faces.new(vs)
        for zz in (0.0, h - 0.2):
            C.beam("r41_metal", p0 + Vector((0, 0, zz)), p1 + Vector((0, 0, zz)), 0.05, 0.05, kind="detail")
        C.beam("r41_metal", p1, p1 + Vector((0, 0, h - 0.2)), 0.05, 0.05, kind="detail")
        C.beam("amber", p1 + Vector((0, 0, h * 0.45)), p1 + Vector((0, 0, h * 0.55)), 0.06, 0.06, kind="fine")
        # 열린 문짝 COL (철망 판 + 테, 두께 0.08)
        nn = Vector((-(p1 - p0).y, (p1 - p0).x, 0)).normalized() * 0.04
        C.ccol([tuple(q + nn * a + Vector((0, 0, zz))) for q in (p0, p1) for a in (-1, 1) for zz in (-0.1, h - 0.15)])
    # 간판
    L.chbox(C, "r41_shell", (0, 0, h + 0.62), (w + 0.9, 0.18, 0.5), 0.05)
    L.rect(C, "amber", (0, -0.092, h + 0.4), (0, -1, 0), w + 0.6, 0.04, lift=0.004)
    if sign:
        L.text(C, "amber", sign[0], 0.2, (0, -0.092, h + 0.7), (0, -1, 0), lift=0.006)
        L.text(C, "r41_light", sign[1], 0.11, (0, -0.092, h + 0.52), (0, -1, 0), lift=0.006)
    C.logo(L.p(-w / 2 + 0.1, -0.095, h + 0.62), 0.3, L.d(0, -1, 0), key="amber")


def command_post(C, cx, cy, z, *, L=6.6, W=2.7, H=2.5, door_u=-1.3, seed=0):
    """R41 지휘 컨테이너 (x축으로 긴 상자, 문은 -Y 긴 면). 안: 바닥(+0.2) + 북쪽 벽 통신 콘솔(화면 셋, 무전기 단, 의자)
    + 동쪽 벽 상황판 + 천장 등. 벽·지붕·콘솔 COL, 문 1.0 × 1.9 m. 반환: dict(console=콘솔 앞 바닥점, door=문 밖 바닥점,
    floor=바닥 z)."""
    x0, x1 = cx - L / 2, cx + L / 2
    y0, y1 = cy - W / 2, cy + W / 2
    t = 0.12
    zf = z + 0.2
    zr = z + H
    # 바닥·밑틀
    C.box("r41_shell", x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, z - 0.25, zf)
    C.col(x0, x1, y0, y1, z - 0.25, zf)
    C.box("r41_metal", x0 + t, x1 - t, y0 + t, y1 - t, zf, zf + 0.01, kind="detail")
    # 벽 (문 자리 비움)
    du0, du1 = cx + door_u - 0.5, cx + door_u + 0.5
    zd = zf + 1.9
    walls = [
        (x0, du0, y0, y0 + t, zf, zr), (du1, x1, y0, y0 + t, zf, zr), (du0, du1, y0, y0 + t, zd, zr),
        (x0, x1, y1 - t, y1, zf, zr), (x0, x0 + t, y0, y1, zf, zr), (x1 - t, x1, y0, y1, zf, zr),
    ]
    for (a0, a1, b0, b1, c0, c1) in walls:
        C.box("r41_light", a0, a1, b0, b1, c0, c1)
        C.col(a0, a1, b0, b1, c0, c1)
    # 지붕 (모따기 판) + 테
    chbox_bm(C.bm("r41_light", "main"), (cx, cy, zr + 0.08), (L + 0.1, W + 0.1, 0.18), 0.07)
    C.col(x0, x1, y0, y1, zr, zr + 0.17)
    chbox_bm(C.bm("r41_shell", "detail"), (cx, cy, zr + 0.2), (L - 0.6, W - 0.6, 0.08), 0.03)
    # 바깥 골조·띠
    for s, yy in ((-1, y0), (1, y1)):
        k = x0 + 0.45
        while k < x1 - 0.3:
            if not (du0 - 0.15 < k < du1 + 0.15):     # 골조 = under: 그 위 띠·글자(fine)가 늘 이긴다
                C.rect("r41_shell", (k, yy, (zf + zr) / 2), (0, s, 0), 0.08, H - 0.4, lift=0.006, kind="under")
            k += 0.9
        C.rect("amber", (cx + (1.6 if s < 0 else 0), yy, zf + 2.05), (0, s, 0), L * (0.45 if s < 0 else 0.9), 0.07,
               lift=0.01)
    C.text("amber", "R41 · 지휘", 0.24, (cx + 1.6, y0, zf + 1.45), (0, -1, 0), lift=0.012)
    C.text("r41_light", "COMMAND", 0.12, (cx + 1.6, y0, zf + 1.2), (0, -1, 0), lift=0.012)
    C.logo((cx + 1.6, y0 - 0.01, zf + 0.75), 0.4, (0, -1, 0), key="amber", disc="r41_shell")
    # 문틀 + 상태등 + 문턱 발판. 틀은 벽의 문설주·상인방 밑면·안쪽 면을 8 mm 덮는다 (벽 면과 한 평면이면 깜빡인다)
    fe = 0.008
    C.box("r41_shell", du0 - 0.1, du0 + fe, y0 - 0.06, y0 + t + fe, zf, zd + 0.1, kind="detail")
    C.box("r41_shell", du1 - fe, du1 + 0.1, y0 - 0.06, y0 + t + fe, zf, zd + 0.1, kind="detail")
    C.box("r41_shell", du0 - 0.1, du1 + 0.1, y0 - 0.06, y0 + t + fe, zd - fe, zd + 0.1, kind="detail")
    C.box("magenta", du1 + 0.14, du1 + 0.22, y0 - 0.02, y0, zd - 0.1, zd + 0.05)
    # 문턱 경사판: 땅(z)에서 0.55 m 앞 바닥(zf)까지 오르는 쐐기. 예전 발판(땅 +0.1 평판)은 땅 → 발판 → 바닥의
    # 0.1 m 턱 둘이 문설주 끝과 만나 비스듬히(±25°) 들어가면 섰다. 보이는 판도 같은 기울기 (윗면 1 cm 위)
    quad_slab(C.bm("r41_metal", "detail"), [(du0, y0 - 0.55, z + 0.01), (du1, y0 - 0.55, z + 0.01),
                                             (du1, y0 + 0.01, zf + 0.01), (du0, y0 + 0.01, zf + 0.01)], 0.12)
    C.ccol([(u, v, zz) for u in (du0, du1) for (v, zz) in ((y0 - 0.55, z - 0.1), (y0, z - 0.1), (y0 - 0.55, z),
                                                           (y0, zf))])
    # 안: 콘솔 (북쪽 벽)
    yb = y1 - t
    c0, c1 = cx - 0.6, cx + 2.4
    chbox_bm(C.bm("r41_shell", "main"), ((c0 + c1) / 2, yb - 0.3, zf + 0.36), (c1 - c0, 0.6, 0.72), 0.04)
    chbox_bm(C.bm("r41_light", "detail"), ((c0 + c1) / 2, yb - 0.32, zf + 0.735), (c1 - c0 + 0.04, 0.66, 0.04), 0.015)
    C.col(c0, c1, yb - 0.62, yb, zf, zf + 0.76)
    C.rect("amber", ((c0 + c1) / 2, yb - 0.6, zf + 0.6), (0, -1, 0), c1 - c0 - 0.1, 0.04, lift=0.006)
    for k, u in enumerate((c0 + 0.5, (c0 + c1) / 2, c1 - 0.5)):
        rot = Matrix.Translation((u, yb - 0.16, zf + 1.12)) @ Matrix.Rotation(math.radians(-14), 4, "X")
        chbox_bm(C.bm("r41_shell", "detail"), (0, 0, 0), (0.86, 0.06, 0.56), 0.03, matrix=rot)
        b = C.bm("screen_r41", "under")          # 화면 = under, 그 위 마젠타 줄 = fine
        q = [rot @ Vector(p) for p in ((-0.38, -0.035, -0.24), (0.38, -0.035, -0.24), (0.38, -0.035, 0.24),
                                        (-0.38, -0.035, 0.24))]
        b.faces.new([b.verts.new(p) for p in q])
        for j in range(4):
            zz = -0.16 + j * 0.1
            w = 0.5 if (j + k) % 2 else 0.3
            ln = [rot @ Vector(p) for p in ((-0.32, -0.04, zz), (-0.32 + w, -0.04, zz), (-0.32 + w, -0.04, zz + 0.025),
                                            (-0.32, -0.04, zz + 0.025))]
            bm2 = C.bm("magenta", "fine")
            bm2.faces.new([bm2.verts.new(p) for p in ln])
        C.box("r41_metal", u - 0.05, u + 0.05, yb - 0.1, yb - 0.04, zf + 0.75, zf + 0.86, kind="detail")
        C.box("r41_metal", u - 0.3, u + 0.3, yb - 0.5, yb - 0.32, zf + 0.755, zf + 0.78, kind="detail")
    # 무전기 단 (콘솔 동쪽)
    rx = c1 + 0.35
    chbox_bm(C.bm("r41_shell", "main"), (rx, yb - 0.25, zf + 0.75), (0.55, 0.5, 1.5), 0.04)
    C.col(rx - 0.28, rx + 0.28, yb - 0.5, yb, zf, zf + 1.5)
    for j in range(4):
        zz = zf + 0.3 + j * 0.32
        C.rect("r41_metal", (rx, yb - 0.505, zz), (0, -1, 0), 0.46, 0.22, lift=0.004, kind="under")
        C.rect("magenta" if j % 2 else "amber", (rx + 0.16, yb - 0.505, zz + 0.06), (0, -1, 0), 0.05, 0.03, lift=0.008)
        C.rect("screen_r41", (rx - 0.08, yb - 0.505, zz), (0, -1, 0), 0.2, 0.08, lift=0.008)
    # 의자 둘
    for u in (cx + 0.2, cx + 1.6):
        chbox_bm(C.bm("r41_shell", "detail"), (u, yb - 0.95, zf + 0.38), (0.42, 0.42, 0.06), 0.02)
        chbox_bm(C.bm("r41_shell", "detail"), (u, yb - 0.75, zf + 0.62), (0.42, 0.05, 0.42), 0.02)
        C.cyl("r41_metal", (u, yb - 0.95, zf), (u, yb - 0.95, zf + 0.36), 0.03, segs=6, kind="detail")
        C.col(u - 0.22, u + 0.22, yb - 1.17, yb - 0.73, zf, zf + 0.42)   # 의자 좌판
        C.col(u - 0.22, u + 0.22, yb - 0.79, yb - 0.72, zf + 0.42, zf + 0.84)   # 등판
    # 동쪽 벽 상황판 + 서쪽 벽 지도
    C.rect("r41_shell", (x1 - t, cy, zf + 1.3), (-1, 0, 0), 1.6, 0.9, up=(0, 0, 1), lift=0.006, kind="under")
    C.rect("screen_r41", (x1 - t, cy, zf + 1.3), (-1, 0, 0), 1.45, 0.75, lift=0.012)
    C.rect("paper", (x0 + t, cy, zf + 1.3), (1, 0, 0), 1.4, 0.85, lift=0.006, kind="under")
    for k in range(4):
        C.rect("fy_green" if k < 2 else "magenta", (x0 + t, cy - 0.4 + k * 0.26, zf + 1.2 + (k % 2) * 0.2), (1, 0, 0),
               0.08, 0.08, lift=0.01)
    # 천장 등
    C.box("lamp_warm", cx - 1.2, cx + 1.2, cy - 0.08, cy + 0.08, zr - 0.04, zr - 0.01)
    return {"console": (cx + 0.9, yb - 1.05, zf), "door": (cx + door_u, y0 - 0.9, z), "floor": zf,
            "inside": (cx - 1.8, cy, zf)}


# ================================================================== fairy holy army

def butterfly(C, center, normal, size, *, up=(0, 0, 1), lift=0.009, kind="fine"):
    """성전군 나비 문장 = 에르피엔 군기의 나비 (lib/erpien_flag.emblem: 원작 도안, 노란 바탕 + 금 윤곽선 + 말린 선.
    사용자 결정 2026-11-02, docs/art/erpien.md 5장). 면에 그린 스텐실. size = 나비 폭, center = 면 위 점, normal = 바깥.
    kind = 바탕·윤곽선의 깊이 편향 등급 (보급 상자 면이 detail이라 fine). 말린 선은 lift × 2.2로 1 cm쯤 더 띄운다."""
    R, U, N = mk.frame(normal, up)
    M = Matrix((R, -N, U)).transposed().to_4x4()
    M.translation = Vector(center)
    ef.emblem(ef.city(C), M, size, res=1, lift=lift, layers={"under": kind})


def fairy_banner(C, x, y, z, *, yaw=0.0, h=4.2, w=1.1, L=None, fly=1, col=True):
    """성전군 깃발 = 에르피엔 군기 (lib/erpien_flag.standard): 나무 깃대 + 창끝 + 깃대 옆에 매단 물결 초록 천(노란 나비,
    금 술, 깃대 쪽 금 줄). 깃대 z -0.2 → h. 천 폭 = 1.6 w (예전 세로 깃발과 같은 무게), 세로 = 폭 / 1.71(원작 비율).
    천 면은 로컬 X-Z (정면 -Y), 깃대 옆 +X로 날린다 (fly=-1이면 -X). L은 예전 세로 깃발 길이 (쓰지 않음)."""
    Lc = Local((x, y, z), yaw)
    ef.standard(ef.city(C), Lc.M @ Matrix.Translation((0.0, 0.0, -0.2)), pole=h + 0.2, W=1.6 * w, r=0.045,
                cols=6, res=1, fly=fly, phase=0.4 + 0.37 * ((x * 7.0 + y * 3.0) % 5.0))
    if col:
        Lc.col(C, -0.08, 0.08, -0.08, 0.08, -0.2, h)


def fairy_crate(C, x, y, z, *, s=0.7, yaw=0.0, emblem=False, stack=1, col=True):
    """성전군 보급 상자 (나무 + 초록 띠 + 에르피엔 나비 스텐실)."""
    Lc = Local((x, y, z), yaw)
    for k in range(stack):
        zb = k * s * 0.72
        Lc.box(C, "plank", -s / 2, s / 2, -s * 0.36, s * 0.36, zb, zb + s * 0.72, kind="detail")
        for u in (-s * 0.32, s * 0.32):
            Lc.box(C, "fy_green", u - 0.04, u + 0.04, -s * 0.36 - 0.01, s * 0.36 + 0.01, zb - 0.01, zb + s * 0.72 + 0.01,
                   kind="detail")   # 띠는 상자 면보다 1 cm 밖 (같은 detail 등급)
        if emblem and k == stack - 1:
            butterfly(C, Lc.p(0, -s * 0.36, zb + s * 0.36), Lc.d(0, -1, 0), s * 0.42, up=Lc.d(0, 0, 1))
    if col:
        Lc.col(C, -s / 2, s / 2, -s * 0.36, s * 0.36, 0, s * 0.72 * stack)


def fairy_tent(C, x, y, z, *, yaw=0.0, w=2.8, d=3.4, h=2.0, pennant=True):
    """성전군 야전 천막 (흰 천 + 초록 용마루 띠 + 앞 용마루 끝 작은 에르피엔 군기)."""
    mk.tent(C, x, y, yaw=yaw, w=w, d=d, h=h, key="fy_white", z=z)
    Lc = Local((x, y, z), yaw)
    C.beam("fy_green", Lc.p(0, -d / 2 - 0.02, h + 0.01), Lc.p(0, d / 2 + 0.02, h + 0.01), 0.16, 0.05, kind="detail")
    for s in (-1, 1):
        C.beam("fy_green", Lc.p(s * w * 0.5, -d / 2 - 0.01, 0.08), Lc.p(s * w * 0.5, d / 2 + 0.01, 0.08), 0.06, 0.18,
               kind="detail")
    if pennant:
        # 앞 용마루 끝의 작은 에르피엔 군기 (깃대 0.45 m, 천은 앞(-Y)으로 날림)
        ef.far_flag(ef.city(C), Lc.M @ Matrix.Translation((0.0, -d / 2 - 0.02, h - 0.1))
                    @ Matrix.Rotation(-math.pi / 2, 4, "Z"), W=0.62, pole=0.45, r=0.02,
                    layers={"pole": "detail", "cloth": "detail"})
    # COL은 도시 키트 천막의 삼각 기둥 껍질이 맡는다 (여기 상자를 더하면 비스듬한 천막 둘레에 벽이 생겼다)


def musket_rack(C, x, y, z, *, yaw=0.0, n=6):
    """머스킷 거치대 (A자 받침 + 기대 세운 머스킷)."""
    Lc = Local((x, y, z), yaw)
    W = 0.24 * n
    for s in (-1, 1):
        Lc.beam(C, "timber", (s * W / 2, -0.3, 0), (s * W / 2, 0, 0.9), 0.05, 0.05, kind="detail")
        Lc.beam(C, "timber", (s * W / 2, 0.3, 0), (s * W / 2, 0, 0.9), 0.05, 0.05, kind="detail")
    Lc.beam(C, "timber", (-W / 2 - 0.05, 0, 0.88), (W / 2 + 0.05, 0, 0.88), 0.05, 0.05, kind="detail")
    for k in range(n):
        u = -W / 2 + 0.12 + k * 0.24
        sgn = 1 if k % 2 else -1
        Lc.beam(C, "plank_d", (u, sgn * 0.32, 0.0), (u, sgn * 0.02, 0.62), 0.05, 0.035, kind="detail")
        Lc.beam(C, "r41_metal", (u, sgn * 0.02, 0.62), (u, -sgn * 0.12, 1.05), 0.025, 0.025, kind="detail")
        Lc.beam(C, "fy_gold", (u, sgn * 0.1, 0.42), (u, sgn * 0.07, 0.48), 0.055, 0.04, kind="fine")   # 개머리(detail) 위
    Lc.col(C, -W / 2 - 0.05, W / 2 + 0.05, -0.32, 0.32, 0, 1.0)


def supply_cart(C, x, y, z, *, yaw=0.0, load=True, seed=0):
    """성전군 보급 수레 (짐칸 + 두 바퀴 + 끌채 + 통·자루)."""
    rng = random.Random(seed)
    Lc = Local((x, y, z), yaw)
    Lc.box(C, "plank", -0.75, 0.75, -1.1, 1.1, 0.55, 0.68)
    for s in (-1, 1):
        Lc.box(C, "plank_d", s * 0.75 - 0.04, s * 0.75 + 0.04, -1.1, 1.1, 0.68, 1.0, kind="detail")
        Lc.cyl(C, "timber", (s * 0.86, 0.1, 0.48), (s * 0.94, 0.1, 0.48), 0.48, segs=12)
        Lc.cyl(C, "fy_gold", (s * 0.95, 0.1, 0.48), (s * 0.98, 0.1, 0.48), 0.08, segs=6, kind="detail")
        Lc.beam(C, "timber", (s * 0.45, -1.1, 0.6), (s * 0.4, -2.4, 0.15), 0.06, 0.06, kind="detail")
        beam_col(C, Lc.p(s * 0.45, -1.1, 0.6), Lc.p(s * 0.4, -2.4, 0.15), 0.1, z_min=z + 0.3)   # 끌채 (발목 위)
    Lc.beam(C, "timber", (-0.95, 0.1, 0.48), (0.95, 0.1, 0.48), 0.07, 0.07, kind="detail")
    Lc.rect(C, "fy_green", (0.75, 0, 0.84), (1, 0, 0), 1.9, 0.12, lift=0.05)
    if load:
        for k in range(3):
            u = -0.38 + k * 0.38
            Lc.cyl(C, "plank_d", (u, 0.55, 0.68), (u, 0.55, 1.18), 0.17, segs=8)
            Lc.cyl(C, "r41_metal", (u, 0.55, 0.9), (u, 0.55, 0.94), 0.175, segs=8, kind="detail")
        for k in range(3):
            Lc.blob(C, "canvas", (rng.uniform(-0.4, 0.4), -0.45 + k * 0.05, 0.85), 0.22, (1.3, 0.9, 0.7), segs=6,
                    rings=4, kind="detail")
    Lc.col(C, -0.8, 0.8, -1.12, 1.12, 0, 1.05 if load else 1.0)              # 짐칸 + 옆판 (+ 짐)
    for s in (-1, 1):
        Lc.col(C, min(s * 0.82, s * 0.99), max(s * 0.82, s * 0.99), -0.38, 0.58, 0, 0.96)   # 바퀴


def war_drum(C, x, y, z, *, r=0.3, h=0.42):
    """요정 군악대 북 (초록 몸통 + 금 테 + 흰 가죽 + 북채)."""
    C.cyl("fy_green", (x, y, z + 0.05), (x, y, z + h), r, segs=12)
    for zz in (0.045, h - 0.04):     # 테 끝면이 몸통 끝면보다 5 mm 밖
        C.cyl("fy_gold", (x, y, z + zz), (x, y, z + zz + 0.045), r + 0.012, segs=12, kind="detail")
    C.cyl("fy_white", (x, y, z + h), (x, y, z + h + 0.01), r * 0.96, segs=12, kind="detail")
    for s in (-1, 1):
        C.beam("timber", (x + s * 0.08, y - 0.05, z + h + 0.02), (x + s * 0.2, y - 0.25, z + h + 0.05), 0.025, 0.025,
               kind="detail")
    bm_col(C, lambda b: mk._bm_cyl(b, (x, y, z - 0.05), (x, y, z + h + 0.01), r + 0.012, segs=12))


# ================================================================== village

def wall_run(C, axis, c, a0, a1, z0, z1, t, out, *, openings=(), key="stone_v", col=True, tops=None, frame="timber"):
    """축 정렬 벽 한 줄. axis='x'면 x로 뻗고 바깥 면이 y=c (out=+1이면 바깥이 +y, 두께는 안쪽으로).
    openings = [(중심 a, 폭, 아래 z, 위 z)]. tops(a) → 그 자리 벽 윗면(부서진 벽)."""
    w0, w1 = (c - t, c) if out > 0 else (c, c + t)
    top = (lambda a: z1) if tops is None else tops

    def bx(lo, hi, zb, zt):
        if hi - lo < 0.02 or zt - zb < 0.02:
            return
        if axis == "x":
            C.box(key, lo, hi, w0, w1, zb, zt)
            if col:
                C.col(lo, hi, w0, w1, zb, zt)
        else:
            C.box(key, w0, w1, lo, hi, zb, zt)
            if col:
                C.col(w0, w1, lo, hi, zb, zt)

    def solid(lo, hi, zb):
        n = max(1, int(math.ceil((hi - lo) / 1.1))) if tops is not None else 1
        for k in range(n):
            u0 = lo + (hi - lo) * k / n
            u1 = lo + (hi - lo) * (k + 1) / n
            bx(u0, u1, zb, top((u0 + u1) / 2))
    cur = a0
    for (m, w, zb, zt) in sorted(openings):
        lo, hi = m - w / 2, m + w / 2
        if lo > cur:
            solid(cur, lo, z0)
        if zb > z0 + 0.01:
            bx(lo, hi, z0, min(zb, top(m)))
        tm = top(m)
        if tm > zt + 0.15:
            bx(lo, hi, zt, tm)
        # 문·창틀 (바깥 면)
        if frame:
            o = out * 0.05
            if axis == "x":
                for xx in (lo - 0.06, hi + 0.06):
                    C.box(frame, xx - 0.06, xx + 0.06, min(c, c + o), max(c, c + o), zb, min(zt, tm), kind="detail")
                if tm > zt:
                    C.box(frame, lo - 0.12, hi + 0.12, min(c, c + o), max(c, c + o), zt, zt + 0.1, kind="detail")
            else:
                for yy in (lo - 0.06, hi + 0.06):
                    C.box(frame, min(c, c + o), max(c, c + o), yy - 0.06, yy + 0.06, zb, min(zt, tm), kind="detail")
                if tm > zt:
                    C.box(frame, min(c, c + o), max(c, c + o), lo - 0.12, hi + 0.12, zt, zt + 0.1, kind="detail")
        cur = hi
    if cur < a1:
        solid(cur, a1, z0)


def cottage(C, G, cx, cy, *, w=7.0, d=5.0, axis="x", door="-y", roof="roof_r", broken=0.5, seed=0, h=2.5,
            chimney=True, col=True, flowers=True):
    """요정 마을 돌집 (폐허). 석회석 벽(문 1.0 × 1.9, 창) + 박공 + 지붕(broken: 0 멀쩡 / 0.4~ 한쪽 지붕이 무너져 서까래 /
    0.75~ 거의 다 무너짐, 벽 윗면이 들쭉날쭉) + 굴뚝 + 창틀·덧문·꽃상자 + 안쪽 잔해. 바닥은 지면 + 0.12 (자동 오르기).
    axis = 용마루 방향, door = 문이 난 쪽. 반환: dict(floor, door=문 밖 바닥점, x0..y1)."""
    rng = random.Random(seed)
    z0 = G.h(cx, cy)
    zf = z0 + 0.12
    hx, hy = (w / 2, d / 2) if axis == "x" else (d / 2, w / 2)
    x0, x1, y0, y1 = cx - hx, cx + hx, cy - hy, cy + hy
    C.box("stone_vd", x0 - 0.1, x1 + 0.1, y0 - 0.1, y1 + 0.1, z0 - 0.9, zf)
    if col:
        C.col(x0 - 0.1, x1 + 0.1, y0 - 0.1, y1 + 0.1, z0 - 0.9, zf)
    C.box("plank_d", x0 + 0.4, x1 - 0.4, y0 + 0.4, y1 - 0.4, zf, zf + 0.01, kind="fine")
    t = 0.34
    zt = zf + h
    span = (y1 - y0) if axis == "x" else (x1 - x0)
    rh = span * 0.42
    zr = zt + rh
    side_broken = rng.choice(["+y", "-y", "+x", "-x"]) if broken > 0.3 else None

    def tops_for(side):
        if broken <= 0.3 or side != side_broken:
            return None
        amp = 0.6 + broken * 1.4
        ph = rng.uniform(0, 6)
        return lambda a: zt - amp * (0.5 + 0.5 * math.sin(a * 1.7 + ph)) * S(1.2 * broken)
    sides = {"-y": ("x", y0, x0, x1, -1), "+y": ("x", y1, x0, x1, 1), "-x": ("y", x0, y0 + t, y1 - t, -1),
             "+x": ("y", x1, y0 + t, y1 - t, 1)}
    door_pt = None
    for s, (ax, c, a0, a1, out) in sides.items():
        L = a1 - a0
        ops = []
        mid = (a0 + a1) / 2
        if s == door:
            dm = mid + rng.uniform(-0.25, 0.25) * L * 0.3
            ops.append((dm, 1.0, zf, zf + 1.9))
            door_pt = (dm, c + out * 0.8) if ax == "x" else (c + out * 0.8, dm)
            nwin = 1 if L > 5 else 0
            wins = [a0 + L * (0.18 if dm > mid else 0.82)] if nwin else []
        else:
            nwin = 2 if L > 6 else 1
            wins = [a0 + L * (k + 1) / (nwin + 1) for k in range(nwin)]
        for wm in wins:
            ops.append((wm, 0.7, zf + 0.85, zf + 1.65))
        wall_run(C, ax, c, a0, a1, zf, zt, t, out, openings=ops, col=col, tops=tops_for(s))
        # 창 안쪽 어둠 + 덧문 + 꽃상자
        Nv = (0, out, 0) if ax == "x" else (out, 0, 0)
        tf = tops_for(s)
        for k, wm in enumerate(wins):
            if tf is not None and tf(wm) < zf + 1.75:
                continue
            pc = (wm, c - out * t * 0.5, zf + 1.25) if ax == "x" else (c - out * t * 0.5, wm, zf + 1.25)
            C.rect("r41_dark", pc, Nv, 0.7, 0.8, lift=0.0)
            if flowers and k == 0 and tops_for(s) is None and s == door:
                fb = (wm, c + out * 0.14, zf + 0.78) if ax == "x" else (c + out * 0.14, wm, zf + 0.78)
                if ax == "x":
                    C.box("timber", fb[0] - 0.4, fb[0] + 0.4, fb[1] - 0.1, fb[1] + 0.1, fb[2] - 0.1, fb[2] + 0.06,
                          kind="detail")
                    if col:
                        C.col(fb[0] - 0.4, fb[0] + 0.4, fb[1] - 0.1, fb[1] + 0.1, fb[2] - 0.1, fb[2] + 0.16)   # 꽃상자
                else:
                    C.box("timber", fb[0] - 0.1, fb[0] + 0.1, fb[1] - 0.4, fb[1] + 0.4, fb[2] - 0.1, fb[2] + 0.06,
                          kind="detail")
                    if col:
                        C.col(fb[0] - 0.1, fb[0] + 0.1, fb[1] - 0.4, fb[1] + 0.4, fb[2] - 0.1, fb[2] + 0.16)
                for j in range(4):
                    u = -0.3 + j * 0.2
                    pp = (fb[0] + u, fb[1], fb[2] + 0.1) if ax == "x" else (fb[0], fb[1] + u, fb[2] + 0.1)
                    C.blob("flower_r" if j % 2 else "flower_y", pp, 0.08, segs=4, rings=2, kind="fine")
            if rng.random() < 0.6:
                # 덧문 한 짝 (열려 비스듬히)
                if ax == "x":
                    C.rbox("fy_green", (wm + 0.62, c + out * 0.08, zf + 1.25), (0.42, 0.04, 0.78), (0, 0, out * 25))
                    if col:
                        C.ocol((wm + 0.62, c + out * 0.08, zf + 0.86), (0.42, 0.06, 0.78), out * 25)
                else:
                    C.rbox("fy_green", (c + out * 0.08, wm + 0.62, zf + 1.25), (0.04, 0.42, 0.78), (0, 0, out * 25))
                    if col:
                        C.ocol((c + out * 0.08, wm + 0.62, zf + 0.86), (0.06, 0.42, 0.78), out * 25)
    # 박공 (용마루와 수직인 두 벽 위)
    gable_sides = ("-x", "+x") if axis == "x" else ("-y", "+y")
    for s in gable_sides:
        if broken > 0.75 and s == gable_sides[seed % 2]:
            continue
        if axis == "x":
            xx = x0 if s == "-x" else x1
            xi = xx + t if s == "-x" else xx - t
            pts = [(y0, zt), (y1, zt), ((y0 + y1) / 2, zr)]
            b = C.bm("stone_v", "main")
            fa = [b.verts.new((xx, u, v)) for u, v in pts]
            fb_ = [b.verts.new((xi, u, v)) for u, v in pts]
            fs = [b.faces.new(fa), b.faces.new(list(reversed(fb_)))]
            for i in range(3):
                j = (i + 1) % 3
                fs.append(b.faces.new((fa[i], fa[j], fb_[j], fb_[i])))
            bmesh.ops.recalc_face_normals(b, faces=fs)
        else:
            yy = y0 if s == "-y" else y1
            yi = yy + t if s == "-y" else yy - t
            pts = [(x0, zt), (x1, zt), ((x0 + x1) / 2, zr)]
            b = C.bm("stone_v", "main")
            fa = [b.verts.new((u, yy, v)) for u, v in pts]
            fb_ = [b.verts.new((u, yi, v)) for u, v in pts]
            fs = [b.faces.new(fa), b.faces.new(list(reversed(fb_)))]
            for i in range(3):
                j = (i + 1) % 3
                fs.append(b.faces.new((fa[i], fa[j], fb_[j], fb_[i])))
            bmesh.ops.recalc_face_normals(b, faces=fs)
    # 지붕
    ov = 0.35
    if axis == "x":
        ridge = [(x0 - ov, (y0 + y1) / 2, zr + 0.08), (x1 + ov, (y0 + y1) / 2, zr + 0.08)]
        eaves = {-1: [(x0 - ov, y0 - ov, zt - 0.2), (x1 + ov, y0 - ov, zt - 0.2)],
                 1: [(x0 - ov, y1 + ov, zt - 0.2), (x1 + ov, y1 + ov, zt - 0.2)]}
    else:
        ridge = [((x0 + x1) / 2, y0 - ov, zr + 0.08), ((x0 + x1) / 2, y1 + ov, zr + 0.08)]
        eaves = {-1: [(x0 - ov, y0 - ov, zt - 0.2), (x0 - ov, y1 + ov, zt - 0.2)],
                 1: [(x1 + ov, y0 - ov, zt - 0.2), (x1 + ov, y1 + ov, zt - 0.2)]}
    gone = seed % 2 * 2 - 1           # 무너지는 쪽
    for sgn in (-1, 1):
        e0, e1 = Vector(eaves[sgn][0]), Vector(eaves[sgn][1])
        r0, r1 = Vector(ridge[0]), Vector(ridge[1])
        if broken > 0.35 and sgn == gone:
            keep = 0.0 if broken > 0.75 else 0.38
            if keep > 0:
                m0, m1 = e0.lerp(r0, keep), e1.lerp(r1, keep)
                quad_slab(C.bm(roof, "main"), [e0, e1, m1, m0], 0.12)
            # 서까래
            n = int((r1 - r0).length / 0.7)
            for k in range(n + 1):
                f = k / n
                a = e0.lerp(e1, f)
                b_ = r0.lerp(r1, f)
                if k % 3 == 2 and broken > 0.6:
                    b_ = a.lerp(b_, 0.55) + Vector((0, 0, -0.6))
                C.beam("timber", a + Vector((0, 0, -0.1)), b_ + Vector((0, 0, -0.1)), 0.1, 0.12, kind="detail")
        elif broken > 0.75:
            m0, m1 = e0.lerp(e1, 0.0), e0.lerp(e1, 0.55)
            quad_slab(C.bm(roof, "main"), [m0, m1, r0.lerp(r1, 0.55), r0], 0.12)
            n = int((r1 - r0).length / 0.7)
            for k in range(n + 1):
                f = k / n
                if f < 0.55:
                    continue
                C.beam("timber", e0.lerp(e1, f) + Vector((0, 0, -0.1)), r0.lerp(r1, f) + Vector((0, 0, -0.1)), 0.1,
                       0.12, kind="detail")
        else:
            quad_slab(C.bm(roof, "main"), [e0, e1, r1, r0], 0.12)
    rd = (Vector(ridge[1]) - Vector(ridge[0])).normalized() * 0.02       # 지붕 끝면과 겹치지 않게 2 cm 더
    C.beam("timber", Vector(ridge[0]) - rd + Vector((0, 0, -0.08)), Vector(ridge[1]) + rd + Vector((0, 0, -0.08)), 0.16,
           0.16, kind="detail")
    if chimney:
        if axis == "x":
            chx, chy = x1 - 0.8, (y0 + y1) / 2 + 0.6
        else:
            chx, chy = (x0 + x1) / 2 + 0.6, y1 - 0.8
        C.box("stone_vd", chx - 0.32, chx + 0.32, chy - 0.32, chy + 0.32, zt - 0.4, zr + 0.65)
        C.box("stone_v", chx - 0.38, chx + 0.38, chy - 0.38, chy + 0.38, zr + 0.55, zr + 0.7, kind="detail")
    # 안쪽 잔해
    if broken > 0.35:
        for k in range(3 + int(broken * 3)):
            px, py = rng.uniform(x0 + 0.8, x1 - 0.8), rng.uniform(y0 + 0.8, y1 - 0.8)
            C.blob(roof if k % 2 else "stone_vd", (px, py, zf + 0.08), rng.uniform(0.25, 0.5), (1.3, 1, 0.45), segs=6,
                   rings=3, rot_z=rng.uniform(0, 3), kind="detail")
        # 바깥 무너진 돌
        for k in range(3):
            if axis == "x":
                px = rng.uniform(x0, x1)
                py = (y0 - 0.8) if gone < 0 else (y1 + 0.8)
            else:
                px = (x0 - 0.8) if gone < 0 else (x1 + 0.8)
                py = rng.uniform(y0, y1)
            C.blob("stone_v", (px, py, G.h(px, py) + 0.1), rng.uniform(0.2, 0.4), (1.2, 1, 0.6), segs=6, rings=3,
                   kind="detail")
    return {"floor": zf, "door": door_pt, "box": (x0, x1, y0, y1), "eave": zt, "ridge": zr}


def windmill(C, G, x, y, *, sail_yaw=200.0, broken=True, seed=0, h=8.4, r0=2.4, r1=1.6):
    """요정 마을 풍차: 회칠한 팔각 탑(돌 밑단, 문·창) + 나무 모자 지붕 + 축 + 날개 넷(격자 + 일부 돛천), broken이면 한 날개가
    부러져 아래에 떨어져 있다. 날개는 sail_yaw(도) 쪽을 본다. COL = 탑 밑동 상자. 반환: dict(door=문 앞 바닥점)."""
    rng = random.Random(seed)
    zb = G.hmin(x - r0, x + r0, y - r0, y + r0) - 0.4
    zg = G.h(x, y - r0)
    b = C.bm("plaster", "main")
    frustum_bm(b, (x, y), r0 + 0.08, r1, zb, zb + h, 8, rot=22.5)
    frustum_bm(C.bm("stone_vd", "main"), (x, y), r0 + 0.16, r0 + 0.06, zb - 0.2, zg + 0.75, 8, rot=22.5)
    # 문 (남쪽, 지면 높이) + 창: 기울어진 팔각 면 위에 붙인다
    tan_t = (r0 + 0.08 - r1) * math.cos(math.radians(22.5)) / h

    def face(adeg, zz):
        rr = (r0 + 0.08 + (r1 - r0 - 0.08) * (zz - zb) / h) * math.cos(math.radians(22.5))
        a = math.radians(adeg)
        n = Vector((math.cos(a), math.sin(a), tan_t)).normalized()
        return Vector((x + math.cos(a) * rr, y + math.sin(a) * rr, zz)), n
    p, n = face(-90, zg + 1.0)
    C.rect("timber", p, n, 1.15, 2.05, lift=0.03)
    C.rect("r41_dark", p - Vector((0, 0, 0.04)), n, 0.95, 1.9, lift=0.05)
    for zz, a in ((zb + 3.6, -90), (zb + 5.8, 0), (zb + 5.2, 180), (zb + 4.4, 135)):
        p, n = face(a, zz)
        C.rect("timber", p, n, 0.58, 0.72, lift=0.03)
        C.rect("r41_dark", p, n, 0.46, 0.6, lift=0.05)
    # 모자 지붕 (돌아가는 나무 덮개)
    zc = zb + h
    yaw = math.radians(sail_yaw)
    D = Vector((math.sin(yaw), -math.cos(yaw), 0))       # 날개가 보는 쪽 (yaw 규칙: -Y 정면)
    Lc = Local((x, y, zc), sail_yaw)
    Lc.box(C, "timber", -r1 - 0.15, r1 + 0.15, -r1 - 0.45, r1 + 0.35, 0.0, 0.5)
    b = C.bm("roof_g", "main")
    pts = [(-r1 - 0.3, 0.5), (r1 + 0.3, 0.5), (0, 2.1)]
    fa = [b.verts.new(Lc.p(u, -r1 - 0.6, v)) for u, v in pts]
    fb_ = [b.verts.new(Lc.p(u, r1 + 0.5, v)) for u, v in pts]
    fs = [b.faces.new(fa), b.faces.new(list(reversed(fb_)))]
    for i in range(3):
        j = (i + 1) % 3
        fs.append(b.faces.new((fa[i], fa[j], fb_[j], fb_[i])))
    bmesh.ops.recalc_face_normals(b, faces=fs)
    Lc.blob(C, "fy_gold", (0, r1 + 0.5, 2.15), 0.12, segs=6, rings=4, kind="detail")
    hub = Lc.p(0, -r1 - 0.9, 1.0)
    C.cyl("timber", Lc.p(0, 0, 1.0), hub, 0.16, segs=8)
    C.blob("fy_gold", hub, 0.24, segs=8, rings=5, kind="detail")
    # 날개
    R = Vector((math.cos(yaw), math.sin(yaw), 0))         # 날개 면의 가로
    U = Vector((0, 0, 1))
    Ls = 6.2
    for k in range(4):
        a = math.radians(18 + 90 * k)
        sd = R * math.cos(a) + U * math.sin(a)
        sw = R * math.cos(a + math.pi / 2) + U * math.sin(a + math.pi / 2)
        snap = broken and k == 3
        Lk = Ls * (0.45 if snap else 1.0)
        tip = hub + sd * Lk
        C.beam("timber", hub, tip, 0.13, 0.13, kind="detail")
        for off in (0.18, 0.95):
            C.beam("timber", hub + sd * 1.1 + sw * off, hub + sd * Lk + sw * off, 0.06, 0.06, kind="detail")
        nb = int((Lk - 1.1) / 0.62)
        for j in range(nb + 1):
            q = hub + sd * (1.1 + j * 0.62)
            C.beam("timber", q, q + sw * 0.95, 0.045, 0.045, kind="detail")
        if k in (0, 2):
            q0 = hub + sd * 1.15 + sw * 0.2
            pts = [q0 - D * 0.03, q0 + sd * (Lk - 1.3) - D * 0.03, q0 + sd * (Lk - 1.3) + sw * 0.72 - D * 0.03,
                   q0 + sw * 0.72 - D * 0.03]
            bb = C.bm("canvas", "main")
            bb.faces.new([bb.verts.new(p) for p in pts])
    if broken:
        # 부러진 날개 조각이 탑 앞 땅에
        px, py = x + 3.4, y - 3.0
        pz = G.h(px, py)
        C.beam("timber", (px - 2.2, py - 0.6, pz + 0.1), (px + 1.0, py + 0.5, pz + 0.25), 0.13, 0.13, kind="detail")
        for j in range(4):
            q = Vector((px - 1.8 + j * 0.8, py - 0.45 + j * 0.27, pz + 0.12))
            C.beam("timber", q, q + Vector((0.25, -0.85, 0.05)), 0.05, 0.05, kind="detail")
    # 팔각 탑 그대로 (예전 상자는 모서리에서 0.9 m 넘게 비었다)
    bm_col(C, lambda b: frustum_bm(b, (x, y), r0 + 0.16, r1, zb - 0.2, zb + h, 8, rot=22.5))
    return {"door": (x, y - r0 - 0.9, zg), "top": zc}


def well(C, x, y, z):
    """마을 우물 (돌 고리 + 나무 지붕 + 도르래)."""
    ro = [(x + px, y + py) for px, py in ngon(0.85, 10)]
    ri = [(x + px, y + py) for px, py in ngon(0.62, 10)]
    mk._bm_ring_prism(C.bm("stone_v", "main"), ro, ri, z - 0.2, z + 0.62)
    C.decal("r41_dark", ngon(0.62, 10), (x, y, z + 0.5), (0, 0, 1), up=(0, 1, 0), lift=0.0)
    for s in (-1, 1):
        C.beam("timber", (x + s * 0.72, y, z + 0.5), (x + s * 0.72, y, z + 1.9), 0.09, 0.09, kind="detail")
    C.beam("timber", (x - 0.8, y, z + 1.7), (x + 0.8, y, z + 1.7), 0.07, 0.07, kind="detail")
    for s in (-1, 1):
        quad_slab(C.bm("roof_g", "main"), [(x - 1.0, y + s * 0.7, z + 1.85), (x + 1.0, y + s * 0.7, z + 1.85),
                                           (x + 1.0, y, z + 2.3), (x - 1.0, y, z + 2.3)], 0.06)
    C.cyl("plank_d", (x, y, z + 1.0), (x, y, z + 1.3), 0.14, segs=8, kind="detail")
    C.ccol([(px, py, zz) for (px, py) in ro for zz in (z - 0.2, z + 0.62)])   # 십각 돌 고리 그대로


def picket(C, G, p0, p1, *, h=0.8, pitch=0.32, key="fy_white", broken=(), seed=0, breakable=False, brk_name=None,
           section=3.2):
    """하얀 나무 울타리 (요정 마을 정원). broken = [(s0, s1)] 쓰러진 구간(지나갈 수 있다).
    COL은 서 있는 구간마다 얇은 판 (높이 0.8 m는 엘프 허리 위라 넘어가지 못한다).
    breakable=True: section m(기본 3.2) 안팎 토막마다 부서지는 소품 BRK_fence_<n> (전차·장갑차가 밀거나 주포·로켓에 쓰러진다).
    broken 구간과 겹치는 토막은 처음부터 쓰러진 정적 토막. 이름 목록을 돌려준다."""
    if breakable:
        P0, P1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
        d = P1 - P0
        L = d.length
        m = max(1, int(round(L / section)))
        names = []
        for k in range(m):
            s0, s1 = L * k / m, L * (k + 1) / m
            a, c = P0.lerp(P1, k / m), P0.lerp(P1, (k + 1) / m)
            local = [(max(0.0, b0 - s0), min(s1, b1) - s0) for b0, b1 in broken if b1 > s0 and b0 < s1]
            if local:
                picket(C, G, (a.x, a.y), (c.x, c.y), h=h, pitch=pitch, key=key, broken=local, seed=seed + k)
                continue
            nm = f"{brk_name}_{k + 1}" if (brk_name and m > 1) else brk_name
            with Breakable(C, "fence", nm) as b:
                picket(C, G, (a.x, a.y), (c.x, c.y), h=h, pitch=pitch, key=key, seed=seed + k)
                with b.broken():
                    _fence_wrecked(C, G, a, c - a, (c - a).length, h, pitch, key, random.Random(seed + 6007 + k))
            names.append(b.node)
        return names
    rng = random.Random(seed)
    P0, P1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
    d = P1 - P0
    L = d.length
    t = d.normalized()
    n = int(L / pitch)
    for k in range(n + 1):
        s = L * k / n
        if any(a <= s <= b for a, b in broken):
            continue
        q = P0 + t * s
        z = G.h(q.x, q.y)
        lean = rng.uniform(-0.03, 0.03)
        C.beam(key, (q.x, q.y, z - 0.1), (q.x + lean, q.y, z + h), 0.06, 0.03, kind="detail")
    for zz in (0.25, 0.6):
        a = P0
        for k in range(1, 5):
            b = P0 + d * (k / 4)
            sa, sb = (a - P0).length, (b - P0).length
            if not any(x0 < (sa + sb) / 2 < x1 for x0, x1 in broken):
                C.beam(key, (a.x, a.y, G.h(a.x, a.y) + zz), (b.x, b.y, G.h(b.x, b.y) + zz), 0.05, 0.06, kind="detail")
            a = b
    runs, cur = [], 0.0
    for b0, b1 in sorted(broken):
        if b0 > cur:
            runs.append((cur, b0))
        cur = max(cur, b1)
    if cur < L:
        runs.append((cur, L))
    yaw = math.degrees(math.atan2(t.y, t.x))
    for s0, s1 in runs:
        if s1 - s0 < 0.1:
            continue
        m = P0 + t * ((s0 + s1) / 2)
        zs = [G.h(q.x, q.y) for q in (P0 + t * s0, m, P0 + t * s1)]
        C.ocol((m.x, m.y, min(zs) - 0.1), (s1 - s0 + 0.06, 0.1, max(zs) + h + 0.02 - min(zs) + 0.1), yaw)


# ================================================================== trees

def tree_round(C, x, y, z, *, h=7.0, seed=0, keys=("foliage", "foliage_l", "foliage_d"), kind="main", n=2):
    """둥근 활엽수 (줄기 + 낮은 분할 덩어리 n개, 약 100~140 삼각형)."""
    rng = random.Random(seed)
    C.cyl("bark_d", (x, y, z - 0.3), (x, y, z + h * 0.55), h * 0.035, r2=h * 0.022, segs=5, kind=kind, cap=False)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(0.2, 0.6) * h * 0.1
        cz = z + h * rng.uniform(0.6, 0.78) + i * h * 0.08
        C.blob(keys[i % len(keys)], (x + math.cos(a) * rr, y + math.sin(a) * rr, cz), h * rng.uniform(0.26, 0.32),
               (1, 1, 0.82), segs=7, rings=4, kind=kind, rot_z=rng.uniform(0, 3))


CANOPY_CLEAR = 1.9    # 사람이 다니는 자리의 잎 밑면 ≥ 그 아래 땅 + 이만큼 (엘프 키 1.2 m + 점프 0.6 m + 여유)


def conifer(C, x, y, z, *, h=9.0, seed=0, keys=("pine", "pine_d"), kind="main", ground=None):
    """침엽수 (줄기 + 겹친 원뿔 셋, 약 60 삼각형).
    ground(x, y) → 땅 높이를 주면 사람이 다니는 자리의 나무다: 원뿔마다 밑면(가지 끝)을 그 원뿔이 덮는 땅 가장 높은 곳
    + CANOPY_CLEAR 위로 올린다. 비탈 위쪽에서도 머리와 점프가 잎에 닿지 않아 잎에 충돌체가 필요 없다(잎은 엄폐가 아니다.
    줄기 COL은 레벨이 단다). 예전(col=True)에는 아래 원뿔의 볼록 껍질 COL을 달았는데, 비탈 위쪽에서 머리 높이까지 내려온
    껍질 밑면이 낮은 천장이 되어 그 아래에서 점프가 안 됐고 캡슐이 껍질과 겹치면 바닥 붙이기에 눌려 땅 밑으로 빠졌다
    (2026-11-04 M9 길 밖, scripts/groundcheck.mjs)."""
    rng = random.Random(seed)
    cones = []
    for i, (f0, f1, rf) in enumerate(((0.18, 0.62, 0.3), (0.4, 0.84, 0.23), (0.62, 1.0, 0.15))):
        r = h * rf * rng.uniform(0.9, 1.1)
        zb, zt = z + h * f0, z + h * f1
        if ground is not None:
            top = max(ground(x + math.cos(a) * rr, y + math.sin(a) * rr)
                      for rr in (0.0, r * 0.5, r) for a in [k * math.pi / 6 for k in range(12)])
            zb = max(zb, top + CANOPY_CLEAR)
            if zb > zt - 1.2:
                print(f"[bk] 경고: 침엽수 ({x:.1f}, {y:.1f}) 원뿔 {i}: 비탈이 가팔라 잎 밑면을 땅 + {CANOPY_CLEAR} m로 올리면 원뿔이 "
                      f"{zt - zb:.2f} m만 남는다 (나무를 옮길 것)")
                zb = zt - 1.2
        cones.append((zb, zt, r))
    # 줄기는 가장 낮은 원뿔 속까지 (밑면을 올린 나무에서 줄기와 잎 사이가 뜨지 않게)
    C.cyl("bark_d", (x, y, z - 0.3), (x, y, max(z + h * 0.3, cones[0][0] + 0.5)), h * 0.03, segs=5, kind=kind, cap=False)
    for i, (zb, zt, r) in enumerate(cones):
        C.cyl(keys[i % len(keys)], (x, y, zb), (x, y, zt), r, r2=0.0, segs=6, kind=kind, smooth=False)


def scatter(region, n, *, seed=0, avoid=None, min_d=3.0, tries=40):
    """region = (x0, x1, y0, y1) 또는 함수(rng) → (x, y). avoid(x, y)가 참이면 버린다. 서로 min_d 떨어진 점 n개."""
    rng = random.Random(seed)
    pts = []
    for _ in range(n):
        for _t in range(tries):
            if callable(region):
                x, y = region(rng)
            else:
                x, y = rng.uniform(region[0], region[1]), rng.uniform(region[2], region[3])
            if avoid and avoid(x, y):
                continue
            if any((x - px) ** 2 + (y - py) ** 2 < min_d * min_d for px, py in pts):
                continue
            pts.append((x, y))
            break
    return pts


# ================================================================== smoke

def smoke(C, x, y, z, *, h=40.0, r=3.0, drift=(0.3, 0.08), seed=0, dark=0.45, fire=True, segs=6, rings=4,
          keys=("smoke_l", "smoke_d"), kind="main"):
    """연기 기둥: 덩어리를 반지름보다 좁게 겹치고 옆으로 흩어 끊기지 않게 피어오르는 기둥 (도시 키트 smoke_column은
    낮은 기둥에서 덩어리가 떨어져 보인다). 아래 dark 비율은 검은 연기, 위로 갈수록 커지며 둘로 퍼지고 drift 쪽으로 기운다."""
    rng = random.Random(seed)
    if fire:
        C.blob("fire", (x, y, z + r * 0.2), r * 0.4, (1, 1, 0.5), segs=6, rings=3)
    zz = z + r * 0.3
    k = 0
    while zz < z + h:
        t = (zz - z) / h
        base = r * (0.5 + 1.4 * t)
        for j in range(1 if t < 0.45 else 2):
            rr = base * rng.uniform(0.72, 1.12)
            ox, oy = rng.uniform(-0.42, 0.42) * base, rng.uniform(-0.42, 0.42) * base
            cx = x + drift[0] * (zz - z) + ox
            cy = y + drift[1] * (zz - z) + oy
            C.blob(keys[1] if t < dark * rng.uniform(0.8, 1.2) else keys[0],
                   (cx, cy, zz + rng.uniform(-0.15, 0.15) * base), rr, (1.0, 1.0, 0.8 - 0.15 * t), segs=segs,
                   rings=rings, rot_z=rng.uniform(0, 3), kind=kind)
            k += 1
        zz += base * rng.uniform(0.8, 1.0)
    return k


def cone_bm(bm, x, y, z0, z1, r, n=6, rot=0.0, smooth=True):
    """밑면 없는 다각뿔 (삼각형 n개). 원경 나무·산."""
    ring = [bm.verts.new((x + math.cos(rot + 2 * math.pi * i / n) * r, y + math.sin(rot + 2 * math.pi * i / n) * r, z0))
            for i in range(n)]
    top = bm.verts.new((x, y, z1))
    for i in range(n):
        f = bm.faces.new((ring[i], ring[(i + 1) % n], top))
        f.smooth = smooth


# ================================================================== far: Erpien, forests, mountains, clouds

def far_trees(C, G, pts, *, seed=0, h=(10, 18), keys=("far_forest", "far_forest_d", "pine_d"), kind="far", n=5):
    """원경 숲: 땅에 박힌 다각뿔 (나무당 삼각형 n개). 쌍뿔과 달리 아래가 떠 보이지 않는다."""
    rng = random.Random(seed)
    for (x, y) in pts:
        hh = rng.uniform(*h)
        cone_bm(C.bm(keys[rng.randrange(len(keys))], kind), x, y, G.h(x, y) - 0.8, G.h(x, y) + hh,
                hh * rng.uniform(0.26, 0.34), n=n, rot=rng.uniform(0, 1))


def far_mountains(C, ranges, hfun, *, keys=("mount", "mount_d"), snow="mount_l", kind="far", seed=0):
    """원경 산맥: ranges = [((x0, y0), (x1, y1), 봉우리 수, (최저, 최고 높이))]. 넓고 부드러운 다각뿔 봉우리를 줄지어
    겹치고 높은 봉우리에 눈 모자. 밑동은 그 자리 지형 hfun 아래에서 시작한다(떠 보이지 않게)."""
    rng = random.Random(seed)
    for ri, ((x0, y0), (x1, y1), n, (hmin, hmax)) in enumerate(ranges):
        for k in range(n):
            t = (k + rng.uniform(-0.25, 0.25)) / max(1, n - 1)
            px, py = x0 + (x1 - x0) * t + rng.uniform(-60, 60), y0 + (y1 - y0) * t + rng.uniform(-60, 60)
            hh = rng.uniform(hmin, hmax) * (0.7 + 0.3 * math.sin(math.pi * min(1, max(0, t))))
            z0 = hfun(px, py) - 15
            rb = hh * rng.uniform(1.9, 2.5)
            rot = rng.uniform(0, 1)
            cone_bm(C.bm(keys[(ri + k) % 2], kind), px, py, z0, z0 + hh, rb, n=12, rot=rot)
            if hh > 170:
                f = 0.72
                cone_bm(C.bm(snow, kind), px, py, z0 + hh * f + 1.5, z0 + hh + 1.5, rb * (1 - f) * 1.04, n=12, rot=rot)


def cloud(C, x, y, z, *, size=60.0, seed=0, keys=("cloud_p", "cloud_s")):
    """해 질 녘 구름 (아래가 평평한 낮은 분할 덩어리 6개)."""
    rng = random.Random(seed)
    for i in range(6):
        u = (i - 2.5) / 2.5
        r = size * (0.36 - 0.14 * abs(u)) * rng.uniform(0.85, 1.15)
        C.blob(keys[0] if i % 3 else keys[1], (x + u * size * 0.8, y + rng.uniform(-0.2, 0.2) * size * 0.3, z + r * 0.3),
               r, (1.3, 1.0, 0.55), segs=7, rings=3, kind="far")


def erpien(C, cx, cy, z, *, seed=11, r_city=240.0, kind="far", face=(0.0, -1.0), tall=1.35):
    """에르피엔 왕도 원경 실루엣 (요정 왕국): 성벽 고리 + 둥근 성탑(초록 원뿔 지붕, 금 꼭지) + 남문 + 박공 지붕 집들(초록·푸른·
    붉은 지붕) + 가운데 언덕 위의 성(본채·대전·가는 탑들·가장 높은 첨탑) + 남쪽(보는 쪽)을 향한 따뜻한 창불 + 탑 꼭대기 깃발.
    face = 보는 사람 쪽 방향(창불·문). 반환: dict(center, spire_top, castle_z)."""
    rng = random.Random(seed)
    F = Vector((face[0], face[1], 0)).normalized()
    # 언덕과 성 터
    C.cyl("far_hill", (cx, cy, z - 8), (cx, cy, z + 20), 130, r2=92, segs=18, kind=kind)
    C.cyl("erp_wall_d", (cx, cy, z + 18), (cx, cy, z + 31), 74, r2=70, segs=18, kind=kind)
    C.cyl("erp_wall", (cx, cy, z + 31), (cx, cy, z + 33), 71, segs=18, kind=kind)
    zc = z + 33
    # 성벽 고리 + 탑
    n = 20
    outer = [(cx + math.cos(2 * math.pi * i / n) * r_city, cy + math.sin(2 * math.pi * i / n) * r_city) for i in range(n)]
    inner = [(cx + math.cos(2 * math.pi * i / n) * (r_city - 4), cy + math.sin(2 * math.pi * i / n) * (r_city - 4))
             for i in range(n)]
    mk._bm_ring_prism(C.bm("erp_wall", kind), outer, inner, z - 4, z + 11)
    for i in range(0, n, 2):
        a = 2 * math.pi * i / n
        px, py = cx + math.cos(a) * r_city, cy + math.sin(a) * r_city
        C.cyl("erp_wall", (px, py, z - 4), (px, py, z + 18), 6.5, segs=10, kind=kind)
        C.cyl("erp_roof", (px, py, z + 18), (px, py, z + 29), 7.6, r2=0.0, segs=10, kind=kind, smooth=False)
    # 남문 (보는 쪽)
    g = Vector((cx, cy, 0)) + F * r_city
    sd = Vector((-F.y, F.x, 0))
    for s in (-1, 1):
        q = g + sd * (s * 11)
        C.cyl("erp_wall", (q.x, q.y, z - 4), (q.x, q.y, z + 24), 7.5, segs=10, kind=kind)
        C.cyl("erp_roof", (q.x, q.y, z + 24), (q.x, q.y, z + 38), 8.6, r2=0.0, segs=10, kind=kind, smooth=False)
        C.blob("erp_gold", (q.x, q.y, z + 38.5), 1.0, segs=6, rings=4, kind=kind)
    C.beam("erp_wall_d", g - sd * 10 + Vector((0, 0, z + 15)), g + sd * 10 + Vector((0, 0, z + 15)), 8, 8, kind=kind)
    C.rect("r41_dark", g + F * 4.2 + Vector((0, 0, z + 4)), F, 9, 12, kind="fine", lift=0.0)
    # 집들 (고리 모양 거리)
    roofs = ("erp_roof", "erp_roof_r", "erp_roof_b", "erp_roof_r", "erp_roof")
    houses = []
    for ring_r, cnt in ((104, 24), (140, 32), (176, 40), (210, 46)):
        for i in range(cnt):
            a = 2 * math.pi * (i + rng.uniform(-0.25, 0.25)) / cnt + ring_r * 0.01
            rr = ring_r + rng.uniform(-6, 6)
            px, py = cx + math.cos(a) * rr, cy + math.sin(a) * rr
            if (Vector((px - cx, py - cy, 0)).normalized().dot(F) > 0.985 and rr > 150):
                continue                                   # 남문 큰길
            if rng.random() < 0.12:
                continue
            houses.append((px, py, a))
    for (px, py, a) in houses:
        w, d = rng.uniform(8, 13), rng.uniform(6, 9)
        hh = rng.uniform(6, 10)
        ta = Vector((-math.sin(a), math.cos(a), 0))        # 접선 = 용마루
        axis = "x" if abs(ta.x) > abs(ta.y) else "y"
        if axis == "x":
            x0, x1, y0, y1 = px - w / 2, px + w / 2, py - d / 2, py + d / 2
        else:
            x0, x1, y0, y1 = px - d / 2, px + d / 2, py - w / 2, py + w / 2
        mk.lod_gable(C, "erp_wall", roofs[rng.randrange(len(roofs))], x0, x1, y0, y1, z - 2, z + hh, z + hh + d * 0.45,
                     axis=axis, kind=kind)
    # 성: 본채 + 대전 + 탑
    Fx, Sx = F, sd
    keep = Vector((cx, cy, 0)) - F * 6
    corners = [keep + Sx * u + Fx * v for u, v in ((-22, -16), (22, -16), (22, 16), (-22, 16))]
    mk._bm_prism(C.bm("erp_wall", kind), ccw([(p.x, p.y) for p in corners]), zc - 2, zc + 26, top=True, bottom=False)
    # 대전 박공 지붕 (용마루 = 옆 방향)
    b = C.bm("erp_roof", kind)
    e = [keep + Sx * u + Fx * v + Vector((0, 0, zc + 26)) for u, v in ((-23, -17), (23, -17), (23, 17), (-23, 17))]
    rr0 = keep + Sx * -23 + Vector((0, 0, zc + 40))
    rr1 = keep + Sx * 23 + Vector((0, 0, zc + 40))
    vs = [b.verts.new(p) for p in (e[0], e[1], rr1, rr0, e[3], e[2])]
    fs = [b.faces.new((vs[0], vs[1], vs[2], vs[3])), b.faces.new((vs[3], vs[2], vs[5], vs[4])),
          b.faces.new((vs[0], vs[3], vs[4])), b.faces.new((vs[1], vs[5], vs[2]))]
    bmesh.ops.recalc_face_normals(b, faces=fs)
    towers = [(-26, -18, 6.5, 44 * tall), (26, -18, 6.5, 44 * tall), (-26, 18, 6, 38 * tall), (26, 18, 6, 38 * tall),
              (-12, -24, 4.5, 52 * tall), (12, -24, 4.5, 52 * tall), (0, 26, 5.5, 46 * tall), (-44, 4, 5, 32 * tall),
              (44, 4, 5, 32 * tall)]
    tops = []
    for (u, v, r, hh) in towers:
        q = keep + Sx * u + Fx * v
        C.cyl("erp_wall", (q.x, q.y, zc - 2), (q.x, q.y, zc + hh), r, segs=10, kind=kind)
        C.cyl("erp_gold", (q.x, q.y, zc + hh), (q.x, q.y, zc + hh + 1.2), r + 0.6, segs=10, kind=kind)
        C.cyl("erp_roof", (q.x, q.y, zc + hh + 1.2), (q.x, q.y, zc + hh + 1.2 + r * 2.8), r + 1.2, r2=0.0, segs=10,
              kind=kind, smooth=False)
        tops.append(Vector((q.x, q.y, zc + hh + 1.2 + r * 2.8)))
    # 가장 높은 첨탑
    sp = keep + Fx * 4
    z1 = zc + 72 * tall
    C.cyl("erp_wall", (sp.x, sp.y, zc + 20), (sp.x, sp.y, z1), 7.5, r2=6.2, segs=12, kind=kind)
    C.cyl("erp_gold", (sp.x, sp.y, z1), (sp.x, sp.y, z1 + 2), 7.2, segs=12, kind=kind)
    C.cyl("erp_roof", (sp.x, sp.y, z1 + 2), (sp.x, sp.y, z1 + 36), 8.2, r2=0.0, segs=12, kind=kind, smooth=False)
    C.cyl("erp_gold", (sp.x, sp.y, z1 + 36), (sp.x, sp.y, z1 + 45), 0.6, r2=0.0, segs=6, kind=kind)
    C.blob("erp_gold", (sp.x, sp.y, z1 + 36.5), 1.8, segs=8, rings=5, kind=kind)
    spire_top = Vector((sp.x, sp.y, z1 + 45))
    tops.append(spire_top)
    # 따뜻한 창불 (보는 쪽 면)
    for (u, v, r, hh) in towers + [(0, 4, 7.0, 70 * tall)]:
        q = keep + Sx * u + Fx * v
        for k in range(2):
            zz = zc + hh * (0.45 + 0.25 * k)
            p = q + F * (r + 0.15) + Vector((0, 0, zz))
            C.rect("lamp_warm", p, F, 1.4, 2.2, lift=0.0)
    for k in range(10):
        p = keep + Sx * (-18 + k * 4) + F * 16.2 + Vector((0, 0, zc + 9 + (k % 2) * 7))
        C.rect("lamp_warm", p, F, 1.6, 2.6, lift=0.0)
    # 탑 꼭대기 깃발 (초록·금)
    for tp in tops:
        C.cyl("timber", tp, tp + Vector((0, 0, 7)), 0.25, segs=4, kind=kind)
        C.decal("fy_green", [(0, 0), (5.5, -1.0), (0, -2.2)], tp + Vector((0, 0, 7)), F, up=(0, 0, 1), lift=0.0)
        C.decal("fy_gold", [(0, -0.6), (3.0, -1.0), (0, -1.5)], tp + Vector((0, 0, 7)), F, up=(0, 0, 1), lift=0.1)
    return {"center": Vector((cx, cy, zc)), "spire_top": spire_top, "castle_z": zc}
