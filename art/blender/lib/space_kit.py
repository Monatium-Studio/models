"""엘피니아 함대와 우주 장면 공용 키트 (space_kit).

프롤로그 오프닝(docs/scenario.md 4장 '프롤로그' 1~2)의 함선, 지구, 별하늘을 만든다. 규약: docs/art/space.md

사용:
    import os, sys
    sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
    import cb, space_kit as sk
    cb.reset()
    S = sk.Ship("elfinia_cruiser")
    hull = sk.Hull([sk.st(-15, 0, 0, 0), sk.st(-9, 4, 3.5, 2.8), ...], ring=32)
    S.s(hull.mesh("hull", "hull"))              # 정지 파츠 (아웃라인 O)
    S.f(hull.decal("emb", pts, s=-6, t=0, ...))  # 세부 (아웃라인 X)
    S.g(...)                                     # UNLIT 발광 (창, 추진기 심지)
    S.p(...)                                     # 반투명 UNLIT (추진 화염)
    S.finish("space/elfinia_cruiser.glb", outline=0.08, budget=6000)

형태 문법 (교주 차원 병기와 같은 계보, docs/art/weapons-home.md 2장)
  - 둥근 판: 초타원 단면(n=2.5~4)으로 로프트한 통통한 선체. R41의 45° 모따기와 반대
  - 금색 고리: 추진기 노즐 테, 함수 광자포 테, 포신 끝, 엠블럼 원판 테. 가는 줄에는 쓰지 않는다
  - 시안 발광: 둥근 창 줄, 스타디움 창, 추진기 심지 (UNLIT)
  - 남색 원판 + 금테 + 원작 엘프 로고 엠블럼, 남색 띠
  - [오리지널] 엘프 귀 지느러미: 옆으로 뻗고 살짝 올라간 잎 모양 날개. 함대 공통 서명

좌표: 1 BU = 1 m, Z-up, **함수(앞) = -Y**, 오른쪽(우현) = -X... 가 아니라 캐릭터 규약처럼 '함선의 왼쪽(좌현) = +X'.
     함선 원점 = 선체 중심. 내보내면 three.js에서 함수가 +Z를 향한다.

출력 노드 (Ship.finish)
  <이름> (루트 empty, outline·collider=0·shipClass 등 속성)
    <이름>_body   불투명 파츠. 머티리얼 색을 정점색으로 구워 툰 머티리얼 1개 (아웃라인 O)
    <이름>_fine   데칼·패널선·글자. 정점색 툰 머티리얼 1개, noOutline
    <이름>_glow   UNLIT 정점색 1개 (창, 심지, 항해등)
    <이름>_plume  UNLIT 정점색 반투명 1개 (추진 화염, 단면 컬링)
  → 함선 1척 = 그리기 호출 4개 + 아웃라인 1개
"""
from __future__ import annotations

import math
import os
import struct
import zlib

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb
import home_weapons as hw  # 읽기 전용: 2D 외곽선, 관, 고리, 데칼, 글자, 엘프 로고

# ------------------------------------------------------------------ palette
# 엘피니아 정규군 = home_weapons.PAL의 회녹·남색·금색·시안 계열 (docs/art/weapons-home.md 3장)
PAL = {
    "hull": "#8d988c",      # 회녹 선체 (엘피니아 화기 olive와 같음)
    "hull_l": "#a7b1a4",    # 밝은 회녹: 윗면 장갑, 지느러미
    "hull_d": "#6f7a70",    # 회녹 그림자: 아랫배, 덮개, 패널
    "seam": "#5b655d",      # 패널선 (회녹보다 한 단 어두움)
    "metal": "#5d555d",     # 자줏빛 건메탈: 노즐, 포탑, 기계부
    "gear": "#7b737a",      # 밝은 장비 회색: 안테나, 레일
    "dark": "#3a333b",      # 노즐 안, 틈, 포신
    "navy": "#2f3644",      # 엘피니아 남색: 띠, 엠블럼 원판, 창 띠
    "navy_l": "#3e4a5e",    # 밝은 남색: 지느러미 끝, 판
    "gold": "#d6b25e",      # 금색 고리, 엠블럼 테, 로고
    "paper": "#e9e0c8",     # 흰 스텐실 글자
    "steel": "#cfcac4",     # 은색 금속: 접시 안테나, 핀
    "hazard": "#e8c34a",    # 경고 노랑 (도킹부)
    "lens": "#26303a",      # 꺼진 렌즈
    # 발광 (UNLIT)
    "glow": "#7ff0ea",      # 시안 창·발광 (엘피니아 장비 발광)
    "core": "#eafffd",      # 추진기 심지 (거의 흰 시안)
    "warm": "#ffe7a6",      # 따뜻한 조명 (함교 실내)
    "nav_r": "#ff7a7a",     # 항해등 빨강 (좌현 = +X)
    "nav_g": "#8dffb0",     # 항해등 초록 (우현 = -X)
    # 반투명 화염 (UNLIT, alpha)
    "plume": "#7ff0ea",
    "plume_hot": "#d8fffb",
    # 지구(인간) 미사일: 엘프 팔레트와 일부러 다르게 (흰 동체, 회색·검정 띠, 주황 화염)
    "m_white": "#e6e3dc",
    "m_gray": "#9b98a0",
    "m_black": "#2c2b31",
    "m_yellow": "#e3c04a",
    "flame": "#ffb054",
    "flame_core": "#fff4d6",
    "flame_haze": "#ff9a3c",
}
GLOW_KEYS = {"glow", "core", "warm", "nav_r", "nav_g", "flame", "flame_core"}
PLUME_KEYS = {"plume", "plume_hot", "flame_haze"}
PLUME_ALPHA = 0.5
LINE = "#4a2229"            # 원작 먹선 (붉은 갈색). 정점색으로 합치므로 함선 전체 한 색

_mat_key: dict[str, str] = {}


def M(key: str):
    """팔레트 작업용 머티리얼 (sk_<key>). finish()에서 정점색으로 구워 합쳐진다."""
    if key in GLOW_KEYS:
        m = cb.mat(f"sk_{key}", PAL[key], emission=PAL[key], unlit=True)
    elif key in PLUME_KEYS:
        m = cb.mat(f"sk_{key}", PAL[key], emission=PAL[key], unlit=True, alpha=PLUME_ALPHA, double_sided=False)
    else:
        m = cb.mat(f"sk_{key}", PAL[key], line=LINE)
    _mat_key[m.name] = key
    return m


def _m(mat):
    if mat is None:
        return None
    return M(mat) if isinstance(mat, str) else mat


def srgb(hexstr: str) -> tuple[float, float, float]:
    h = hexstr.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ------------------------------------------------------------------ interpolation

def pchip(xs, ys):
    """단조 3차 보간 (Fritsch-Carlson). 넘침 없이 매끈하게 정거장 사이를 잇는다."""
    n = len(xs)
    if n == 1:
        return lambda x: ys[0]
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    if n == 2:
        m = [d[0], d[0]]
    else:
        m[0], m[-1] = d[0], d[-1]
        for i in range(1, n - 1):
            if d[i - 1] * d[i] <= 0:
                m[i] = 0.0
            else:
                w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
                m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(x):
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            return ys[-1]
        lo, hi = 0, n - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        i = lo
        t = (x - xs[i]) / h[i]
        t2, t3 = t * t, t * t * t
        return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i]
                + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * m[i + 1])
    return f


def st(s, w, ht, hb=None, vc=0.0, n=2.6, nb=None, uc=0.0):
    """로프트 정거장. s = 축 위치, w = 반폭, ht/hb = 위/아래 반높이, vc = 단면 중심 높이, n/nb = 위/아래 초타원 지수."""
    return dict(s=s, w=w, ht=ht, hb=ht if hb is None else hb, vc=vc, n=n, nb=n if nb is None else nb, uc=uc)


def nose(s_tip, s_full, full: dict, k=5, *, vc_tip=None, power=0.5):
    """둥근 코 정거장 k개 (s_tip은 뾰족 끝, s_full에서 full 단면). 타원 옆모습 (power=0.5)."""
    out = []
    for i in range(k):
        a = i / (k - 1)                         # 0 = 끝, 1 = 전단면
        x = 1 - (1 - a) ** 2 if power == 0.5 else a
        r = math.sqrt(max(0.0, 1 - (1 - a) ** 2)) if power == 0.5 else a ** power
        s = s_tip + (s_full - s_tip) * a
        vc0 = full["vc"] if vc_tip is None else vc_tip
        out.append(dict(s=s, w=full["w"] * r, ht=full["ht"] * r, hb=full["hb"] * r,
                        vc=vc0 + (full["vc"] - vc0) * x, n=full["n"], nb=full["nb"], uc=full["uc"]))
    return out


# ------------------------------------------------------------------ hull loft

_AX = {
    # axis: (축 단위, u 단위, v 단위)  단면 (u, v), 축 s
    "Y": (Vector((0, 1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1))),
    "X": (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))),
    "Z": (Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0))),
}


def _se(c, e):
    """초타원 성분: sgn(c)·|c|^(2/e)."""
    return math.copysign(abs(c) ** (2.0 / e), c) if c != 0 else 0.0


class Hull:
    """초타원 단면 로프트. 정거장(st/nose) 사이는 PCHIP으로 잇고, 표면 점·법선·틀을 돌려준다.

    t (라디안): 0 = +u 쪽, π/2 = +v 쪽(위), π = -u, 3π/2 = 아래.
    axis='Y'면 u = X(좌현 +X), v = Z. 표면 위에 데칼·띠·창 줄을 붙일 때 같은 매개변수를 쓴다.
    """

    def __init__(self, stations, *, axis="Y", ring=32, sub=2, origin=(0, 0, 0)):
        self.st = sorted(stations, key=lambda d: d["s"])
        self.axis = axis
        self.A, self.U, self.V = _AX[axis]
        self.O = Vector(origin)
        self.ring = ring
        xs = [d["s"] for d in self.st]
        # 같은 s가 겹치면 아주 조금 민다
        for i in range(1, len(xs)):
            if xs[i] <= xs[i - 1]:
                xs[i] = xs[i - 1] + 1e-4
                self.st[i]["s"] = xs[i]
        self.s0, self.s1 = xs[0], xs[-1]
        self.f = {k: pchip(xs, [d[k] for d in self.st]) for k in ("w", "ht", "hb", "vc", "n", "nb", "uc")}
        samples = []
        for i in range(len(xs) - 1):
            for j in range(sub):
                samples.append(xs[i] + (xs[i + 1] - xs[i]) * j / sub)
        samples.append(xs[-1])
        self.samples = samples

    def sec(self, s):
        return {k: f(s) for k, f in self.f.items()}

    def local(self, s, t, grow=0.0):
        p = self.sec(s)
        c, sn = math.cos(t), math.sin(t)
        w = max(p["w"] + grow, 0.0)
        u = p["uc"] + w * _se(c, p["n"] if sn >= 0 else p["nb"])
        h = (p["ht"] if sn >= 0 else p["hb"]) + grow
        v = p["vc"] + max(h, 0.0) * _se(sn, p["n"] if sn >= 0 else p["nb"])
        return u, v

    def point(self, s, t, grow=0.0):
        u, v = self.local(s, t, grow)
        return self.O + self.A * s + self.U * u + self.V * v

    def frame(self, s, t, eps=1e-3):
        """(점, 축 방향 접선, 둘레 접선, 바깥 법선)."""
        s = min(max(s, self.s0 + eps), self.s1 - eps)
        P = self.point(s, t)
        Ts = (self.point(s + eps, t) - self.point(s - eps, t)).normalized()
        Tt = (self.point(s, t + eps) - self.point(s, t - eps))
        Tt = Tt.normalized() if Tt.length > 1e-9 else self.V.copy()
        N = Ts.cross(Tt).normalized()
        c = self.O + self.A * s + self.U * self.sec(s)["uc"] + self.V * self.sec(s)["vc"]
        if N.dot(P - c) < 0:
            N = -N
        return P, Ts, Tt, N

    def t_at(self, s, v_target, side=1):
        """단면 s에서 높이 v_target이 되는 t (side=1 → +u 쪽, -1 → -u 쪽)."""
        p = self.sec(s)
        h = p["ht"] if v_target >= p["vc"] else p["hb"]
        e = p["n"] if v_target >= p["vc"] else p["nb"]
        q = max(-0.999, min(0.999, (v_target - p["vc"]) / max(h, 1e-6)))
        sn = math.copysign(abs(q) ** (e / 2.0), q)
        t = math.asin(max(-1.0, min(1.0, sn)))
        return t if side > 0 else math.pi - t

    # ---------------------------------------------------------------- meshes

    def mesh(self, name, mat=None, *, grow=0.0, s_range=None, caps=True, ring=None, sub_samples=None):
        """로프트 메시. 끝 단면 반폭이 0이면 뾰족 끝(부채), 아니면 납작 뚜껑."""
        M_ = ring or self.ring
        ss = sub_samples or self.samples
        if s_range:
            a, b = s_range
            ss = [a] + [s for s in ss if a < s < b] + [b]
        bm = bmesh.new()
        rings = []
        for s in ss:
            p = self.sec(s)
            if p["w"] + grow < 1e-4 and p["ht"] + grow < 1e-4:
                rings.append([bm.verts.new(self.point(s, 0.0, grow))])
            else:
                rings.append([bm.verts.new(self.point(s, 2 * math.pi * j / M_, grow)) for j in range(M_)])
        for i in range(len(rings) - 1):
            r0, r1 = rings[i], rings[i + 1]
            if len(r0) == 1 and len(r1) == 1:
                continue
            if len(r0) == 1:
                for j in range(M_):
                    bm.faces.new((r0[0], r1[(j + 1) % M_], r1[j]))
            elif len(r1) == 1:
                for j in range(M_):
                    bm.faces.new((r0[j], r0[(j + 1) % M_], r1[0]))
            else:
                for j in range(M_):
                    j2 = (j + 1) % M_
                    bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
        if caps:
            for r in (rings[0], rings[-1]):
                if len(r) > 2:
                    bm.faces.new(r)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        o = cb._new_mesh_obj(name, bm)
        cb.smooth(o, angle=60)
        if mat:
            cb.assign(o, _m(mat))
        return o

    def patch(self, name, s0, s1, t0, t1, mat, *, lift=0.02, ns=None, nt=None):
        """표면을 따라가는 띠·판 데칼 (s0..s1 × t0..t1), 법선 방향으로 lift만큼 띄움."""
        if ns:
            svals = [s0 + (s1 - s0) * i / ns for i in range(ns + 1)]
        else:
            # 선체 표본(곡률이 큰 코·꼬리에 촘촘함)을 두 배로 쪼개 따라간다
            base = [s0] + [x for x in self.samples if s0 < x < s1] + [s1]
            svals = []
            for a, b in zip(base, base[1:]):
                svals += [a, (a + b) / 2]
            svals.append(s1)
            ns = len(svals) - 1
        nt = nt or max(1, int(abs(t1 - t0) / (2 * math.pi) * self.ring * 1.5))
        verts, faces = [], []
        for i in range(ns + 1):
            s = svals[i]
            for j in range(nt + 1):
                t = t0 + (t1 - t0) * j / nt
                P, _, _, N = self.frame(s, t)
                verts.append(P + N * lift)
        for i in range(ns):
            for j in range(nt):
                a = i * (nt + 1) + j
                faces.append((a, a + 1, a + nt + 2, a + nt + 1))
        o = cb.from_pydata("decal_" + name, verts, faces, material=_m(mat))
        _orient_out(o, self)
        return o

    def ring_line(self, name, s, width, mat, *, lift=0.02, t0=0.0, t1=2 * math.pi):
        return self.patch(name, s - width / 2, s + width / 2, t0, t1, mat, lift=lift, ns=1)

    def long_line(self, name, s0, s1, t, width_rad, mat, *, lift=0.02):
        return self.patch(name, s0, s1, t - width_rad / 2, t + width_rad / 2, mat, lift=lift, nt=1)

    def decal(self, name, pts, s, t, mat, *, lift=0.03, up=(0, 0, 1)):
        """평평한 데칼을 표면 점 (s, t)에 붙인다. pts (u, v): u = 오른쪽(바깥에서 볼 때), v = up 투영."""
        P, R, U, N = self.oriented(s, t, up)
        return hw.decal(name, pts, P, right=R, up=U, lift=lift, mat=_m(mat))

    def conform(self, name, pts, s0, t0, mat, *, lift=0.05, rings=3, flip_u=True):
        """2D 외곽선 (u, v)을 표면을 따라 휘어 붙인 데칼 (부채꼴 + 동심 고리로 쪼갬).
        v = 축(s) 방향, u = 둘레 방향 (flip_u=True면 바깥에서 볼 때 오른쪽 = +u)."""
        rho = max(abs(self.local(s0, t0)[0] - self.sec(s0)["uc"]),
                  abs(self.local(s0, t0)[1] - self.sec(s0)["vc"]), 1e-3)
        verts = []
        P, _, _, N = self.frame(s0, t0)
        verts.append(P + N * lift)
        n = len(pts)
        for k in range(1, rings + 1):
            f = k / rings
            for (u, v) in pts:
                s = s0 + v * f
                t = t0 + (-u if flip_u else u) * f / rho
                P, _, _, N = self.frame(s, t)
                verts.append(P + N * lift)
        faces = []
        for i in range(n):
            faces.append((0, 1 + i, 1 + (i + 1) % n))
        for k in range(rings - 1):
            a0, a1 = 1 + k * n, 1 + (k + 1) * n
            for i in range(n):
                j = (i + 1) % n
                faces.append((a0 + i, a1 + i, a1 + j, a0 + j))
        o = cb.from_pydata("decal_" + name, verts, faces, material=_m(mat))
        _orient_out(o, self)
        return o

    def oriented(self, s, t, up=(0, 0, 1)):
        P, Ts, Tt, N = self.frame(s, t)
        Uh = Vector(up)
        U = (Uh - N * Uh.dot(N))
        if U.length < 1e-4:
            U = Ts.copy()
        U.normalize()
        R = U.cross(N).normalized()
        return P, R, U, N


def _orient_out(o, hull: Hull):
    """패치 면이 선체 바깥을 보게."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.normal_update()
    flip = []
    for f in bm.faces:
        c = f.calc_center_median()
        s = (c - hull.O).dot(hull.A)
        p = hull.sec(min(max(s, hull.s0), hull.s1))
        axis_pt = hull.O + hull.A * s + hull.U * p["uc"] + hull.V * p["vc"]
        if f.normal.dot(c - axis_pt) < 0:
            flip.append(f)
    if flip:
        bmesh.ops.reverse_faces(bm, faces=flip)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = True


# ------------------------------------------------------------------ transforms

def basis_from(N, U):
    """로컬 Z = N, 로컬 Y = U 인 회전 행렬 (4x4)."""
    Z = Vector(N).normalized()
    Y = (Vector(U) - Z * Vector(U).dot(Z)).normalized()
    X = Y.cross(Z).normalized()
    return Matrix((X, Y, Z)).transposed().to_4x4()


def place(obj, loc, *, rot=None, basis=None):
    """메시를 회전(도, XYZ) 또는 기저 행렬로 돌리고 loc로 옮겨 굽는다."""
    cb.apply_modifiers(obj)
    M4 = Matrix.Identity(4)
    if basis is not None:
        M4 = basis
    elif rot:
        M4 = (Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y")
              @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
    obj.matrix_world = Matrix.Translation(Vector(loc)) @ M4 @ obj.matrix_world
    return obj


def mirror(obj, name=None):
    return hw.mirror_x(obj, name)


# ------------------------------------------------------------------ parts

def disc(name, r, center, normal, mat, *, n=24, up=(0, 0, 1)):
    """한 면 원판 (법선 방향을 봄)."""
    N = Vector(normal).normalized()
    U = Vector(up)
    if abs(U.dot(N)) > 0.99:
        U = Vector((0, 1, 0)) if abs(N.y) < 0.99 else Vector((1, 0, 0))
    B = basis_from(N, U)
    R, Uv = B.col[0].to_3d(), B.col[1].to_3d()
    return hw.decal(name, hw.circle(r, n), Vector(center), right=R, up=Uv, lift=0.0, mat=_m(mat))


def annulus(name, r_out, r_in, center, normal, mat, *, n=24, up=(0, 0, 1)):
    N = Vector(normal).normalized()
    U = Vector(up)
    if abs(U.dot(N)) > 0.99:
        U = Vector((0, 1, 0)) if abs(N.y) < 0.99 else Vector((1, 0, 0))
    B = basis_from(N, U)
    R, Uv = B.col[0].to_3d(), B.col[1].to_3d()
    return hw.ring_decal(name, Vector(center), r_out, r_in, right=R, up=Uv, lift=0.0, mat=_m(mat), seg=n)


def ring_y(name, R, r, y, x=0.0, z=0.0, mat="gold", seg=28, rseg=8):
    """Y축을 감는 금색 고리 (노즐 테, 포구 테)."""
    o = hw.torus(name, R, r, seg=seg, rseg=rseg, mat=_m(mat))
    return place(o, (x, y, z), rot=(90, 0, 0))


def engine(S, name, x, z, y0, r, *, length=None, flare=0.12, plume=2.2, seg=24, housing="metal",
           gold="ring", core=True):
    """함미 추진기 하나 (+Y로 분사). y0 = 노즐 뿌리, 노즐 끝은 y0 + length.

    노즐 관(건메탈) + 금색 테(gold='ring' 둥근 고리, 'lip' 얇은 관, None) + 어두운 목
    + 심지(시안 원판 + 흰 심 + 흰 불꽃 원뿔) + 반투명 시안 화염 원뿔.
    """
    L = length or r * 1.1
    y1 = y0 + L
    ro0, ro1 = r * 1.12, r * (1.12 + flare)
    S.s(hw.tube(f"{name}_nozzle", ro0, r * 0.92, y0, y1, c=(x, z), verts=seg, r_out2=ro1, r_in2=r * (0.98 + flare),
                mat=_m(housing)))
    if gold == "ring":
        S.s(ring_y(f"{name}_ring", ro1, r * 0.1, y1, x, z, seg=seg, rseg=6))
    elif gold == "lip":
        S.s(hw.tube(f"{name}_lip", ro1 + r * 0.06, r * (0.95 + flare), y1 - r * 0.18, y1 + r * 0.04, c=(x, z),
                    verts=seg, mat=_m("gold")))
    S.s(hw.ycyl(f"{name}_throat", r * 0.95, y0 + L * 0.25, y0 + L * 0.3, x=x, z=z, verts=seg, mat=_m("dark"),
                cap=True))
    if core:
        S.g(disc(f"{name}_glow", r * 0.93, (x, y0 + L * 0.31, z), (0, 1, 0), "glow", n=seg))
        S.g(disc(f"{name}_core", r * 0.58, (x, y0 + L * 0.33, z), (0, 1, 0), "core", n=max(8, seg // 2)))
        S.g(hw.ycyl(f"{name}_hot", r * 0.5, y0 + L * 0.33, y1 + plume * r * 0.55, x=x, z=z, r2=0.0, verts=12,
                    mat=_m("core"), cap=False))
        S.p(hw.ycyl(f"{name}_plume", r * 0.9, y0 + L * 0.5, y1 + plume * r, x=x, z=z, r2=r * 0.05,
                    verts=max(12, seg * 2 // 3), mat=_m("plume"), cap=False))
    return y1


def turret(S, name, x, y, z, *, k=1.0, up=1, barrels=2, yaw=0.0):
    """둥근 포탑 (밝은 회녹 포탑 집 + 건메탈 받침 + 포신 끝 금색 고리). 포신은 -Y(함수 쪽)."""
    parts = []
    parts.append(hw.zcyl(f"{name}_base", 1.55 * k, 0.0, 0.55 * k, verts=16, mat=_m("metal")))
    hs = Hull([st(-1.6 * k, 0.0, 0.0, 0.0, vc=0.95 * k, n=2.4),
               st(-1.2 * k, 1.1 * k, 0.62 * k, 0.45 * k, vc=0.95 * k, n=3.0),
               st(0.0, 1.35 * k, 0.72 * k, 0.5 * k, vc=1.0 * k, n=3.4),
               st(1.5 * k, 1.1 * k, 0.5 * k, 0.45 * k, vc=0.95 * k, n=3.0)], ring=16, sub=1)
    parts.append(hs.mesh(f"{name}_house", "hull_l"))
    gap = 0.42 * k
    xs = [0.0] if barrels == 1 else [-gap, gap]
    for i, bx in enumerate(xs):
        parts.append(hw.ycyl(f"{name}_barrel{i}", 0.18 * k, -4.2 * k, -1.2 * k, x=bx, z=1.0 * k, verts=8,
                             mat=_m("dark")))
        parts.append(hw.ycyl(f"{name}_muzzle{i}", 0.27 * k, -4.45 * k, -4.0 * k, x=bx, z=1.0 * k, verts=10,
                             r2=0.23 * k, mat=_m("gold")))
    fine = [hs.decal(f"{name}_slit", hw.stadium(1.1 * k, 0.22 * k, 3), -0.6 * k, 0.6, "navy", lift=0.02 * k),
            hs.decal(f"{name}_slit_m", hw.stadium(1.1 * k, 0.22 * k, 3), -0.6 * k, math.pi - 0.6, "navy",
                     lift=0.02 * k)]
    sensor = disc(f"{name}_eye", 0.15 * k, (0.75 * k, -1.25 * k, 1.28 * k), (0, -1, 0.3), "glow", n=8)
    for o in parts + fine + [sensor]:
        if up < 0:
            place(o, (0, 0, 0), rot=(0, 180, 0))
        if yaw:
            place(o, (0, 0, 0), rot=(0, 0, yaw))
        place(o, (x, y, z))
    S.s(*parts)
    S.f(*fine)
    S.g(sensor)


def emblem_plate(S, name, P, N, r, *, up=(0, 0, 1), depth=0.5, logo=True, n=20, tolerance=0.0035):
    """남색 원판 + 금테 + 원작 엘프 로고 (P = 선체 표면 점, N = 바깥 법선). 원판은 선체에 반쯤 묻힌다."""
    N = Vector(N).normalized()
    B = basis_from(N, up)
    R, U = B.col[0].to_3d(), B.col[1].to_3d()
    face = Vector(P) + N * (depth * 0.45)
    plate = cb.cylinder(f"{name}_plate", radius=r, depth=depth * 2.0, verts=n, material=_m("navy"))
    plate.matrix_world = Matrix.Translation(face - N * depth) @ B
    rim = hw.torus(f"{name}_rim", r * 0.98, r * 0.07, seg=n, rseg=6, mat=_m("gold"))
    rim.matrix_world = Matrix.Translation(face) @ B
    S.s(plate, rim)
    if logo:
        lg = hw.elf_logo(f"{name}_logo", face, r * 1.25, right=R, up=U, mat=_m("gold"), lift=0.04 + r * 0.01,
                         tolerance=tolerance)
        if lg is not None:
            S.f(lg)
        else:
            S.slots.append((tuple(face), r * 1.25))
    return face


def window_row(S, hull: Hull, name, s0, s1, v, *, side=1, r=0.4, pitch=1.6, band=True, band_mat="navy",
               win="glow", n=8, lift=0.1, skip=()):
    """선체 옆 둥근 창 줄 (원작 엘프 화기의 '둥근 구멍 줄' 문법). band=True면 남색 창 띠를 깐다."""
    count = max(1, int(abs(s1 - s0) / pitch) + 1)
    ys = [s0 + (s1 - s0) * i / max(count - 1, 1) for i in range(count)]
    if band:
        tA = hull.t_at((s0 + s1) / 2, v, side)
        # 띠는 각 위치마다 같은 높이를 따라가도록 짧은 조각으로
        segs = []
        for i in range(len(ys) - 1):
            a, b = ys[i], ys[i + 1]
            ta, tb = hull.t_at(a, v, side), hull.t_at(b, v, side)
            dt = r * 1.7 / max(hull.sec((a + b) / 2)["ht"], 1e-3)
            tm = (ta + tb) / 2
            segs.append(hull.patch(f"{name}_band{i}", a - pitch * 0.5 if i == 0 else a,
                                   b + pitch * 0.5 if i == len(ys) - 2 else b, tm - dt / 2, tm + dt / 2,
                                   band_mat, lift=lift * 0.5, ns=2, nt=1))
        S.f(*segs)
        del tA
    for i, y in enumerate(ys):
        if i in skip:
            continue
        t = hull.t_at(y, v, side)
        S.g(hull.decal(f"{name}_w{i}", hw.circle(r, n), y, t, win, lift=lift))


def fin(name, y_mid, chord, span, *, sweep=6.0, rise=2.0, thick=0.8, ring=16, sub=2, K=9, lean=1.3):
    """엘프 귀 지느러미 (+X로 뻗는 잎 모양). y_mid = 뿌리 시위 중심 y, chord = 최대 시위.

    잎 모양: 뿌리 시위 ≈ 0.76 × 최대, 폭이 가장 넓은 곳은 span의 1/3, 두 가장자리가 볼록하고 끝이 뾰족하다.
    끝은 뒤로 sweep, 위로 rise만큼 휘어 올라간다(엘프 귀처럼 옆으로 뻗고 살짝 위로).
    반환 Hull (axis X): s = 0..span, 단면 (u = Y 시위, v = Z 두께). 거울상은 Hull.A를 (-1,0,0)으로.
    """
    stations = []
    for i in range(K):
        a = i / (K - 1)
        f = max(math.sin(math.pi * (0.25 + 0.75 * a)), 0.0) ** 0.8
        w = chord / 2 * f
        th = thick * (1 - 0.7 * a)
        if i == K - 1:
            w, th = 0.0, 0.0
        stations.append(dict(s=span * a, w=w, ht=th, hb=th * 0.8, vc=rise * a ** 1.4, n=2.2, nb=2.2,
                             uc=y_mid + sweep * a ** lean))
    return Hull(stations, axis="X", ring=ring, sub=sub)


# ------------------------------------------------------------------ assembly

def _join(objs, name):
    objs = [o for o in objs if o is not None]
    if not objs:
        return None
    for o in objs:
        cb.apply_modifiers(o)
    if len(objs) == 1:
        o = objs[0]
        o.name = name
        o.data.name = name
        return o
    return cb.join(objs, name)


def _parent_keep(child, parent):
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = Matrix.Identity(4)
    child.matrix_world = mw


def vc_material(name, *, unlit=False, alpha=None, line=LINE, double_sided=True):
    """정점색('Col')을 바탕색으로 쓰는 머티리얼. unlit이면 UNLIT_ 접두사(조명 없음)."""
    full = f"UNLIT_{name}" if unlit else name
    if full in bpy.data.materials:
        return bpy.data.materials[full]
    m = bpy.data.materials.new(full)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    node = nt.nodes.new("ShaderNodeVertexColor")
    node.layer_name = "Col"
    nt.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6
    if alpha is not None:
        bsdf.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except AttributeError:
            pass
    m.use_backface_culling = not double_sided
    if not unlit:
        m["lineColor"] = line
    return m


def bake_vcol(obj, fallback="#ffffff"):
    """면마다 머티리얼 팔레트 색을 'Col' 정점색(sRGB)으로 굽는다."""
    me = obj.data
    ca = me.color_attributes.get("Col") or me.color_attributes.new(name="Col", type="BYTE_COLOR", domain="CORNER")
    cols = []
    for m in me.materials:
        key = _mat_key.get(m.name) if m else None
        hexv = PAL.get(key, fallback) if key else fallback
        cols.append((*srgb(hexv), 1.0))
    if not cols:
        cols = [(*srgb(fallback), 1.0)]
    for poly in me.polygons:
        c = cols[min(poly.material_index, len(cols) - 1)]
        for li in poly.loop_indices:
            ca.data[li].color_srgb = c
        poly.material_index = 0
    me.color_attributes.active_color = ca
    me.materials.clear()


def _tris(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def vc_join(objs, name, kind="body", *, line=LINE, parent=None):
    """파츠 목록을 합쳐 정점색을 굽고 kind별 머티리얼을 붙인다 (Ship 없이 노드를 직접 짤 때).

    kind: 'body'(툰, 아웃라인 O) | 'fine'(툰, noOutline) | 'glow'(UNLIT) | 'plume'(UNLIT 반투명)
    """
    o = _join(list(objs), name)
    if o is None:
        return None
    bake_vcol(o)
    vc_name = "sk_vc" if line == LINE else "sk_vc_" + line.lstrip("#")
    m = {"body": lambda: vc_material(vc_name, line=line), "fine": lambda: vc_material(vc_name, line=line),
         "glow": lambda: vc_material("sk_glow_vc", unlit=True),
         "plume": lambda: vc_material("sk_plume_vc", unlit=True, alpha=PLUME_ALPHA, double_sided=False)}[kind]()
    o.data.materials.append(m)
    o["collider"] = 0
    if kind != "body":
        o["noOutline"] = 1
    if parent is not None:
        _parent_keep(o, parent)
    return o


def set_origin(obj, world_pt):
    hw._set_origin(obj, world_pt)


def purge_materials():
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)


class Ship:
    """함선 한 척 조립기.

    s(obj)  정지 파츠 (아웃라인 O)      → <이름>_body
    f(obj)  데칼·패널선·글자 (아웃라인 X) → <이름>_fine
    g(obj)  UNLIT 발광                  → <이름>_glow
    p(obj)  반투명 UNLIT 화염            → <이름>_plume
    anchor(name, pt)  빈 오브젝트 (함교, 엔진 중심 등)
    """

    def __init__(self, name, line=LINE):
        self.name = name
        self.line = line
        self.groups = {"body": [], "fine": [], "glow": [], "plume": []}
        self.anchors = []
        self.slots = []

    def s(self, *objs):
        self.groups["body"].extend(o for o in objs if o is not None)
        return objs[0] if objs else None

    def f(self, *objs):
        self.groups["fine"].extend(o for o in objs if o is not None)
        return objs[0] if objs else None

    def g(self, *objs):
        self.groups["glow"].extend(o for o in objs if o is not None)
        return objs[0] if objs else None

    def p(self, *objs):
        self.groups["plume"].extend(o for o in objs if o is not None)
        return objs[0] if objs else None

    def anchor(self, name, pt):
        self.anchors.append((name, tuple(pt)))

    def part(self, name, **props):
        """따로 움직이거나 바꿔 끼울 블록 (예: 함교). <name> 빈 오브젝트 아래 같은 그룹 구조로 나간다.
        props는 그 노드의 커스텀 속성 (예: hidden=1)."""
        sub = Ship(name, line=self.line)
        sub.props = props
        self.parts = getattr(self, "parts", [])
        self.parts.append(sub)
        return sub

    def build(self):
        """그룹별로 합치고 정점색을 구워 루트 아래에 붙인다. (루트, {그룹: tris})"""
        root = cb.empty(self.name, size=1.0)
        report = {}
        vc_name = "sk_vc" if self.line == LINE else "sk_vc_" + self.line.lstrip("#")
        mats = {
            "body": vc_material(vc_name, line=self.line),
            "fine": vc_material(vc_name, line=self.line),
            "glow": vc_material("sk_glow_vc", unlit=True),
            "plume": vc_material("sk_plume_vc", unlit=True, alpha=PLUME_ALPHA, double_sided=False),
        }
        if os.environ.get("SK_DEBUG"):
            deps = bpy.context.evaluated_depsgraph_get()
            rows = []
            for g, objs in self.groups.items():
                for o in objs:
                    ev = o.evaluated_get(deps)
                    me = ev.to_mesh()
                    me.calc_loop_triangles()
                    rows.append((len(me.loop_triangles), g, o.name))
                    ev.to_mesh_clear()
            agg = {}
            for n, g, nm in rows:
                key = g + ":" + nm.rstrip("0123456789-+_").split("_")[0]
                agg[key] = agg.get(key, 0) + n
            for k, v in sorted(agg.items(), key=lambda kv: -kv[1])[:30]:
                print(f"[sk]   {v:6d}  {k}")
        for g, objs in self.groups.items():
            o = _join(objs, f"{self.name}_{g}")
            if o is None:
                continue
            bake_vcol(o)
            o.data.materials.append(mats[g])
            o["collider"] = 0
            if g != "body":
                o["noOutline"] = 1
            _parent_keep(o, root)
            report[g] = _tris(o)
        for sub in getattr(self, "parts", []):
            node = cb.empty(sub.name, size=0.5)
            _parent_keep(node, root)
            for k, v in sub.props.items():
                node[k] = v
            for g, objs in sub.groups.items():
                o = _join(objs, f"{sub.name}_{g}")
                if o is None:
                    continue
                bake_vcol(o)
                o.data.materials.append(mats[g])
                o["collider"] = 0
                if g != "body":
                    o["noOutline"] = 1
                _parent_keep(o, node)
                report[f"{sub.name}.{g}"] = _tris(o)
            for name, pt in sub.anchors:
                e = cb.empty(name, loc=pt, size=0.5)
                _parent_keep(e, node)
        for name, pt in self.anchors:
            e = cb.empty(name, loc=pt, size=0.5)
            _parent_keep(e, root)
        for i, (c, size) in enumerate(self.slots):
            e = cb.empty("emblem_slot" if i == 0 else f"emblem_slot_{i}", loc=c, size=size / 2)
            e["emblemSize"] = size
            _parent_keep(e, root)
        for m in list(bpy.data.materials):
            if m.users == 0:
                bpy.data.materials.remove(m)
        return root, report

    def finish(self, rel_path, *, outline, budget, extra=None):
        root, report = self.build()
        hidden = {p.name for p in getattr(self, "parts", []) if p.props.get("hidden")}
        alt = sum(v for k, v in report.items() if k.split(".")[0] in hidden)
        total = sum(report.values()) - alt
        print("[sk] group tris:", ", ".join(f"{k}={v}" for k, v in report.items()))
        print(f"[sk] total tris {total} / {budget}" + (f"  (+ hidden variants {alt})" if alt else ""))
        preview = os.environ.get("SK_PREVIEW")      # 숨김 변형 미리보기: 그 변형만 보이게 따로 내보냄
        if preview:
            for p in getattr(self, "parts", []):
                node = bpy.data.objects.get(p.name)
                if node is None:
                    continue
                show = (p.name == preview) or (not p.props.get("hidden") and
                                                 not any(q.name == preview and q.name.startswith(p.name)
                                                         for q in self.parts))
                for o in [node] + list(node.children_recursive):
                    o.hide_set(not show)
                    o.hide_render = not show
            rel_path = rel_path.replace(".glb", f"__{preview}.glb")
        if total > budget and not os.environ.get("SK_NOBUDGET"):
            raise RuntimeError(f"[sk] 예산 초과: tris {total}/{budget}")
        props = {"outline": outline, "collider": 0}
        if extra:
            props.update(extra)
        return cb.export(rel_path, props=props, root=root)


# ------------------------------------------------------------------ textures (지구, 달, 하늘)

def save_png(path, rgb, *, palette=None):
    """numpy uint8 (H, W, 3|4) → PNG (zlib, 필터 없음/위 필터). palette가 있으면 rgb 대신 인덱스(H, W) + 팔레트."""
    import numpy as np
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def chunk(t, data):
        c = struct.pack(">I", len(data)) + t + data
        return c + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)

    if palette is not None:
        idx = np.asarray(rgb, dtype=np.uint8)
        h, w = idx.shape
        ihdr = struct.pack(">IIBBBBB", w, h, 8, 3, 0, 0, 0)
        plte = b"".join(bytes(c[:3]) for c in palette)
        raw = b"".join(b"\x00" + idx[y].tobytes() for y in range(h))
        body = chunk(b"IHDR", ihdr) + chunk(b"PLTE", plte)
        if any(len(c) == 4 for c in palette):
            body += chunk(b"tRNS", bytes(c[3] if len(c) == 4 else 255 for c in palette))
        body += chunk(b"IDAT", zlib.compress(raw, 9))
    else:
        a = np.asarray(rgb, dtype=np.uint8)
        h, w, ch = a.shape
        ihdr = struct.pack(">IIBBBBB", w, h, 8, 6 if ch == 4 else 2, 0, 0, 0)
        # 위 필터(2): 평탄한 색 면이 잘 압축된다
        up = a.astype(np.int16)
        diff = np.empty_like(a)
        diff[0] = a[0]
        diff[1:] = ((up[1:] - up[:-1]) % 256).astype(np.uint8)
        raw = b"".join(b"\x02" + diff[y].tobytes() for y in range(h))
        body = chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9))
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + body + chunk(b"IEND", b""))
    return path


def quantize(rgb, palette):
    """(H, W, 3) uint8 → 가장 가까운 팔레트 인덱스 (H, W). 팔레트 색만 쓰는 툰 텍스처용."""
    import numpy as np
    pal = np.array([c[:3] for c in palette], dtype=np.int32)
    a = rgb.reshape(-1, 3).astype(np.int32)
    best = np.zeros(a.shape[0], dtype=np.uint8)
    bestd = np.full(a.shape[0], 1 << 30, dtype=np.int64)
    for i, c in enumerate(pal):
        d = ((a - c) ** 2).sum(1)
        m = d < bestd
        best[m] = i
        bestd[m] = d[m]
    return best.reshape(rgb.shape[:2])


def image_material(name, png_path, *, unlit=True, alpha=False, double_sided=False, interpolation="Linear"):
    """PNG 텍스처를 바탕색으로 쓰는 머티리얼 (glTF baseColorTexture). unlit이면 UNLIT_."""
    full = f"UNLIT_{name}" if unlit else name
    m = bpy.data.materials.new(full)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    img = bpy.data.images.load(png_path, check_existing=False)
    img.name = name + "_tex"
    img.colorspace_settings.name = "sRGB"
    img.pack()
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = interpolation
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if alpha:
        nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        try:
            m.surface_render_method = "BLENDED"
        except AttributeError:
            pass
    m.use_backface_culling = not double_sided
    return m


def uv_sphere(name, radius, segs, rings, *, inward=False, loc=(0, 0, 0)):
    """경위도 UV 구. u = (경도 + 180°) / 360°, v = (위도 + 90°) / 180°. 이음매는 경도 ±180°.

    로컬 좌표: +Z = 북극, 경도 0°(그리니치) = -Y, 동경 90° = +X. 점 = (cosφ·sinλ, -cosφ·cosλ, sinφ).
    텍스처 PNG는 첫 줄 = 북위 90°, 첫 열 = 서경 180° (일반 정거원통 지도와 같음).
    """
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    grid = []
    for j in range(rings + 1):
        lat = -math.pi / 2 + math.pi * j / rings
        row = []
        for i in range(segs + 1):
            lon = -math.pi + 2 * math.pi * i / segs
            p = Vector((math.cos(lat) * math.sin(lon), -math.cos(lat) * math.cos(lon), math.sin(lat))) * radius
            row.append(bm.verts.new(p))
        grid.append(row)
    for j in range(rings):
        for i in range(segs):
            ids = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if j == 0:
                ids = [(i, j), (i + 1, j + 1), (i, j + 1)]
            elif j == rings - 1:
                ids = [(i, j), (i + 1, j), (i + 1, j + 1)]
            f = bm.faces.new([grid[jj][ii] for ii, jj in ids])
            for lp, (ii, jj) in zip(f.loops, ids):
                u = ii / segs
                if jj in (0, rings):
                    u = (i + 0.5) / segs
                lp[uvl].uv = (u, jj / rings)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=radius * 1e-6)
    bm.normal_update()
    out = [f for f in bm.faces if f.normal.dot(f.calc_center_median()) < 0]
    if out:
        bmesh.ops.reverse_faces(bm, faces=out)
    if inward:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    o = cb._new_mesh_obj(name, bm)
    o.location = loc
    cb.smooth(o, angle=180)
    return o


def export_glb(rel_path, *, props=None, root=None, image_format="AUTO"):
    """cb.export와 같지만 이미지 형식을 고를 수 있다 (텍스처가 있는 지구·하늘용)."""
    path = os.path.join(cb.MODELS_DIR, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if props:
        targets = [root] if root else [o for o in bpy.context.scene.objects if o.parent is None]
        for t in targets:
            for k, v in props.items():
                t[k] = v
    bpy.context.view_layer.update()
    tris = cb.tri_count()
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=False, use_visible=True, export_apply=True,
        export_yup=True, export_extras=True, export_cameras=False, export_lights=False,
        export_animations=False, export_skins=False, export_materials="EXPORT",
        export_image_format=image_format,
    )
    print(f"[sk] exported {rel_path}  tris={tris}  size={os.path.getsize(path) / 1024:.0f} KB")
    return path
