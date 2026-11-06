"""에르피엔 깃발 (요정 왕국 군기) 공용 키트. 깃발이 나오는 모든 장면이 이 모듈 하나로 같은 깃발을 쓴다.

[원작] 2026-11-02 조회, 나무위키. 사용자 결정(2026-11-02)으로 원작 문양을 그대로 쓴다 (ART_GUIDE 1장 '베끼지 않기' 예외).
  「요정(트릭컬 리바이브)」 2.4 '요정 왕국 에르피엔' 정보 상자 그림 '에르피엔 군기'
      ("찬탈과 일탈 사이에서 공개된 군기로 추측되는 깃발", 500×292 px): 짙은 초록 바탕 #385f52 한가운데 노란 나비 #ffdd76.
      나비는 짙은 금색 윤곽선을 두르고, 하트꼴로 맞붙은 큰 위 날개 둘 + 옆으로 뻗은 아래 날개 둘 + 맨 아래 둥근 꼬리 둘이다.
      안쪽 선: 꼬리마다 위쪽이 말려 들어가는 선, 위·아래 날개 사이 홈에서 안으로 들어가는 짧은 선.
      나비 폭 = 깃발 폭의 0.257, 높이 = 깃발 높이의 0.43.
  「폴랑」 어사이드 3성 효과 '에르피엔 진군깃발' 아이콘: 같은 초록 천과 크림빛 금 나비, 끝·아래 가장자리의 금 술,
      깃대 쪽 세로 금 줄 둘, 창끝 달린 깃대.
  「폴랑」 애장품 '요정 장교 깃발': "요정 왕국 심볼이 새겨져 있는" 접힌 초록 깃발(말린 꼬리 나비).
[오리지널] 3D 형태: 천의 물결과 처짐·두께, 깃대·창끝·금 띠 모양, 세로 현수막·손깃발·원경 깃발로 바꾼 비율.

변형 (모두 같은 나비 도안 outline()/STROKES를 쓴다)
  standard()   큰 군기: 깃대 + 옆으로 매단 물결 천 + 금 술 + 깃대 쪽 금 줄 + 창끝 (성전군 기수 소품, M9 진지 깃발)
  banner()     세로 현수막: 금 봉에 매단 천 + 위 금 줄 + 아래 금 술 (대관식 왕성·회랑·대로·개선문)
  hand_flag()  군중 손깃발: 막대 + 작은 물결 천 (crowd_*.glb)
  far_flag()   원경·작은 깃발: 평판 천 + 저분할 나비 (탑 꼭대기, 가로등, 천막, 원경 본대, 망루)
  emblem()     나비 문장만 (평면 위: 보급 상자 스텐실, 대관식 바닥·아치·성문 문장)
  badge()      두께 있는 나비 문장 (배지·부조·조형: 경비대 샤코·부츠 원판, 퍼레이드 차 메달, 대관식 지붕 조형)
  BUNTING      깃발 줄 삼각기 색 (초록·노랑)
  outline() / edge_outline() / STROKES   도안 자체 (곡면 부조처럼 자기 빌더로 그리는 곳: 경비대 머스킷)
  grid_tris()  오목 외곽선의 고른 격자 분할, warp_sink() 곡면에 감싸 붙이기 (경비대 샤코)

출력은 sink.mesh(key, layer, verts, faces, smooth) 하나로 모든 빌더에 쓴다.
  city(C)               도시·레벨 키트 mk.City: layer 그대로 kind (main, detail, under, fine, far)
  bm_sink(get, remap)   get(key, kind) → bmesh 를 주는 빌더 (parade_car 등). remap으로 layer → kind를 바꾼다
  buf_sink(buf, mats)   엘프 키트 Buf (군중 손깃발: 소켓 소품으로 정점 색에 합쳐진다)
색 키: erf_green, erf_yellow, erf_gold, erf_pole (PAL). 소품 머티리얼 4개 안에 들어가도록 나비 윤곽선·말린 선과 금 술·창끝을
같은 금색 하나로 쓴다.

겹친 면 금지: 천(main) → 나비 바탕·윤곽 고리·금 줄(under, 천 위로 lift) → 말린 선(fine, 그 위로 lift). 윤곽선은 바탕 둘레의
고리 띠라 바탕과 겹치지 않는다. 금 술은 천 가장자리 밖으로 이어 붙인다. 물결 천은 열(column)마다 평면이고, 문장은 열 경계에서
잘라 각 열 평면 위에 놓으므로 천을 뚫지 않는다.
"""
from __future__ import annotations

import math

from mathutils import Matrix, Vector
from mathutils.geometry import delaunay_2d_cdt, tessellate_polygon

# ---------------------------------------------------------------- 색 [원작 군기 그림에서 뽑음]
GREEN = "#385f52"
YELLOW = "#ffdd76"
GOLD = "#c49b34"
POLE = "#6b4f3c"
PAL = {"erf_green": GREEN, "erf_yellow": YELLOW, "erf_gold": GOLD, "erf_pole": POLE}
BUNTING = ("erf_green", "erf_yellow")
ASPECT = 500.0 / 292.0          # 가로 / 세로
EMBLEM_W = 0.257                # 나비 폭 / 깃발 폭

# ---------------------------------------------------------------- 나비 도안 [원작 군기 그림의 윤곽을 따라 그림]
# 오른쪽 반 외곽선. 나비 반폭 = 1, 가운데 원점, 위 +y. 셋째 값 1 = 꺾이는 점(홈). 위 가운데 홈 → 오른쪽 → 꼬리 사이 홈.
_HALF = [
    (0.000, 0.553, 1), (0.191, 0.785, 0), (0.385, 0.936, 0), (0.536, 0.971, 0), (0.724, 0.971, 0),
    (0.828, 0.946, 0), (0.906, 0.893, 0), (0.993, 0.690, 0), (0.992, 0.414, 0), (0.905, 0.215, 0),
    (0.673, -0.021, 1), (0.823, -0.013, 0), (0.907, -0.041, 0), (0.961, -0.107, 0), (0.957, -0.211, 0),
    (0.907, -0.307, 0), (0.745, -0.451, 0), (0.440, -0.615, 1), (0.458, -0.706, 0), (0.446, -0.789, 0),
    (0.359, -0.924, 0), (0.208, -0.971, 0), (0.120, -0.952, 0), (0.044, -0.857, 0), (0.000, -0.728, 1),
]
_LOW = (0, 2, 4, 6, 7, 8, 10, 12, 14, 16, 17, 19, 21, 23, 24)      # 원경용으로 남기는 점
# 안쪽 선 (오른쪽 반, 왼쪽은 거울): 꼬리 위가 말려 들어가는 선, 위·아래 날개 사이 홈에서 들어가는 선
STROKES = [
    [(0.440, -0.615), (0.386, -0.585), (0.305, -0.577), (0.232, -0.603), (0.183, -0.657), (0.160, -0.735)],
    [(0.673, -0.021), (0.622, -0.064), (0.569, -0.111)],
]
EDGE = 0.032                    # 윤곽선 굵기 (나비 반폭 기준)
STROKE_W = 0.034                # 안쪽 선 굵기


def _cr(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return tuple(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3)
                 for a, b, c, d in zip(p0, p1, p2, p3))


def outline(res=2, low=False):
    """나비 외곽선 (반폭 1, 반시계). res = 조절점 사이 나눔 수, low = 원경용 성긴 점."""
    half = [p for i, p in enumerate(_HALF) if not low or i in _LOW]
    loop = half + [(-x, y, c) for (x, y, c) in reversed(half[1:-1])]
    n = len(loop)
    corners = [i for i, p in enumerate(loop) if p[2]]
    out = []
    for a, b in zip(corners, corners[1:] + [corners[0] + n]):
        ch = [loop[i % n][:2] for i in range(a, b + 1)]
        for j in range(len(ch) - 1):
            p1, p2 = ch[j], ch[j + 1]
            p0 = ch[j - 1] if j > 0 else (2 * p1[0] - p2[0], 2 * p1[1] - p2[1])
            p3 = ch[j + 2] if j + 2 < len(ch) else (2 * p2[0] - p1[0], 2 * p2[1] - p1[1])
            for k in range(res):
                out.append(_cr(p0, p1, p2, p3, k / res))
    out.reverse()
    return out


def _offset(poly, d):
    """반시계 다각형을 바깥으로 d만큼 (꺾인 곳은 길이 제한)."""
    n = len(poly)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e0, e1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0, n1 = Vector((e0.y, -e0.x)), Vector((e1.y, -e1.x))
        m = n0 + n1
        m = n1 if m.length < 1e-6 else m.normalized()
        out.append(tuple(p1 + m * (d / max(m.dot(n1), 0.4))))
    return out


def edge_outline(res=2, low=False):
    """나비 윤곽선(금 테)의 바깥 둘레 (outline()을 EDGE만큼 밖으로). 반폭 1 기준, 반시계."""
    return _offset(outline(res, low), EDGE)


def _strip(pts, w0, w1):
    """폴리라인 → 굵기가 w0에서 w1로 줄어드는 사각형 띠 조각들."""
    P = [Vector(p) for p in pts]
    n = len(P)
    L, R = [], []
    for i in range(n):
        t = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        nv = Vector((-t.y, t.x))
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        L.append(P[i] + nv * w)
        R.append(P[i] - nv * w)
    return [[tuple(R[i]), tuple(R[i + 1]), tuple(L[i + 1]), tuple(L[i])] for i in range(n - 1)]


def emblem_parts(size, *, res=2, low=False, edge=True, strokes=True, center=(0.0, 0.0)):
    """나비 문장의 2D 조각 [(key, layer, polygon)]. size = 나비 폭. layer: 'under' 바탕·윤곽, 'fine' 안쪽 선."""
    s = size / 2
    cx, cy = center
    T = (lambda p: (cx + p[0] * s, cy + p[1] * s))
    fill = outline(res, low)
    parts = [("erf_yellow", "under", [T(p) for p in fill])]
    if edge:
        outer = _offset(fill, EDGE)
        n = len(fill)
        for i in range(n):
            j = (i + 1) % n
            parts.append(("erf_gold", "under", [T(fill[i]), T(fill[j]), T(outer[j]), T(outer[i])]))
    if strokes:
        for st in STROKES:
            for sx in (1, -1):
                q = [(sx * x, y) for x, y in st]
                for quad in _strip(q, STROKE_W, STROKE_W * 0.45):
                    parts.append(("erf_gold", "fine", [T(p) for p in quad]))
    return parts


# ---------------------------------------------------------------- 출력 (sink)
class _BMSink:
    def __init__(self, get, remap=None):
        self.get, self.remap = get, remap or {}

    def mesh(self, key, layer, verts, faces, smooth=False):
        bm = self.get(key, self.remap.get(layer, layer))
        vs = [bm.verts.new(v) for v in verts]
        for f in faces:
            try:
                face = bm.faces.new([vs[i] for i in f])
            except ValueError:
                continue
            face.smooth = smooth


class _BufSink:
    def __init__(self, buf, mats, w=None):
        self.buf, self.mats, self.w = buf, mats, w

    def mesh(self, key, layer, verts, faces, smooth=False):
        idx = [self.buf.vert(v, self.w) for v in verts]
        for f in faces:
            self.buf.face(tuple(idx[i] for i in f), self.mats[key])


class _WarpSink:
    def __init__(self, sink, fn):
        self.sink, self.fn = sink, fn

    def mesh(self, key, layer, verts, faces, smooth=False):
        self.sink.mesh(key, layer, [self.fn(Vector(v)) for v in verts], faces, smooth)


def warp_sink(sink, fn):
    """점을 fn(Vector) → 점으로 옮겨 sink에 넘긴다. 문장을 곡면에 감싸 붙일 때(경비대 샤코 앞면): 문장 로컬 (x, y, z)를
    곡면 위 (가로 x, 세로 z) 자리 + 바깥 법선 × (-y)로 옮기는 fn을 주고 M은 단위 행렬로 둔다."""
    return _WarpSink(sink, fn)


def city(C):
    """mk.City (레벨·소품 키트). 색 키를 키트 팔레트에 넣는다 (이미 있으면 두므로 레벨이 미리 물들일 수 있다)."""
    import monatium_city_kit as mk
    for k, v in PAL.items():
        mk.PAL.setdefault(k, v)
    return _BMSink(C.bm)


def bm_sink(get, remap=None):
    return _BMSink(get, remap)


def buf_sink(buf, mats, w=None):
    return _BufSink(buf, mats, w)


class _Out:
    """조각을 모아 변환(M)을 걸어 sink로 보낸다. 면은 원하는 법선 쪽을 보게 감김을 맞춘다."""

    def __init__(self, sink, M):
        self.sink, self.M = sink, M
        self.R = M.to_3x3()

    def poly(self, key, layer, pts, normal):
        pts = [Vector(p) for p in pts]
        if len(pts) < 3:
            return
        nrm = Vector((0, 0, 0))
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            nrm += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
        if nrm.length < 1e-12:
            return
        if nrm.dot(Vector(normal)) < 0:
            pts.reverse()
        self.sink.mesh(key, layer, [self.M @ p for p in pts], [list(range(len(pts)))])

    def mesh(self, key, layer, verts, faces, smooth=False):
        self.sink.mesh(key, layer, [self.M @ Vector(v) for v in verts], faces, smooth)

    def lathe(self, key, layer, prof, *, segs=8, sx=1.0, sy=1.0, smooth=True):
        """Z축 회전체. prof = [(r, z)] 아래에서 위로. r = 0인 끝은 한 점으로 모은다."""
        verts, faces, rings = [], [], []
        for r, z in prof:
            if r <= 1e-6:
                verts.append((0.0, 0.0, z))
                rings.append([len(verts) - 1])
                continue
            ring = []
            for i in range(segs):
                a = 2 * math.pi * i / segs
                verts.append((math.cos(a) * r * sx, math.sin(a) * r * sy, z))
                ring.append(len(verts) - 1)
            rings.append(ring)
        for r0, r1 in zip(rings, rings[1:]):
            if len(r0) == 1 and len(r1) == 1:
                continue
            for i in range(segs):
                j = (i + 1) % segs
                if len(r0) == 1:
                    faces.append([r0[0], r1[j], r1[i]])
                elif len(r1) == 1:
                    faces.append([r0[i], r0[j], r1[0]])
                else:
                    faces.append([r0[i], r0[j], r1[j], r1[i]])
        if len(rings[0]) > 1:
            faces.append(list(reversed(rings[0])))
        if len(rings[-1]) > 1:
            faces.append(list(rings[-1]))
        self.mesh(key, layer, verts, faces, smooth)

    def cyl(self, key, layer, z0, z1, r, *, segs=8, r2=None, x=0.0, y=0.0, smooth=True):
        prof = [(r, z0), (r if r2 is None else r2, z1)]
        verts, faces = [], []
        rings = []
        for rr, z in prof:
            ring = []
            for i in range(segs):
                a = 2 * math.pi * i / segs
                verts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, z))
                ring.append(len(verts) - 1)
            rings.append(ring)
        for i in range(segs):
            j = (i + 1) % segs
            faces.append([rings[0][i], rings[0][j], rings[1][j], rings[1][i]])
        faces.append(list(reversed(rings[0])))
        faces.append(list(rings[1]))
        self.mesh(key, layer, verts, faces, smooth)


# ---------------------------------------------------------------- 천 표면 (물결)
class _Cloth:
    """천 2D 좌표 (s: 매단 쪽 0 → 끝 W, t: 위 0 → 아래 -H) → 로컬 3D. 매단 쪽 위 모서리 = 원점, 끝 = +X, 위 = +Z, 앞면 = -Y.
    물결·처짐이 s에만 달려 있어 열(column)마다 평면이다."""

    def __init__(self, W, H, *, cols=1, amp=0.0, waves=1.2, droop=0.0, phase=0.0):
        self.W, self.H = W, H
        self.us = [W * i / cols for i in range(cols + 1)]
        A = []
        for u in self.us:
            f = u / W
            A.append(Vector((u, amp * W * math.sin(2 * math.pi * waves * f + phase) * f ** 0.7 if amp else 0.0,
                             -droop * H * f ** 1.6)))
        self.A = A
        cn = []
        for a, b in zip(A, A[1:]):
            d = b - a
            cn.append(Vector((d.y, -d.x, 0.0)).normalized())
        self.N = [cn[0]] + [(cn[i - 1] + cn[i]).normalized() for i in range(1, len(cn))] + [cn[-1]]

    def col(self, s):
        for i in range(len(self.us) - 2, -1, -1):
            if s >= self.us[i] - 1e-9:
                return i
        return 0

    def at(self, s, t, off, c=None):
        c = self.col(s) if c is None else c
        u0, u1 = self.us[c], self.us[c + 1]
        f = (s - u0) / (u1 - u0)
        return (self.A[c].lerp(self.A[c + 1], f) + Vector((0, 0, t)) + self.N[c].lerp(self.N[c + 1], f) * off)

    def normal(self, c):
        return (self.N[c] + self.N[c + 1]).normalized()


def _clip(poly, a, b):
    """다각형을 a <= x <= b 띠로 자른다 (볼록한 띠라 Sutherland-Hodgman)."""
    def clip(poly, keep, x0):
        out = []
        for i in range(len(poly)):
            P, Q = poly[i - 1], poly[i]
            kp, kq = keep(P), keep(Q)
            if kq != kp:
                t = (x0 - P[0]) / (Q[0] - P[0])
                out.append((x0, P[1] + (Q[1] - P[1]) * t))
            if kq:
                out.append(Q)
        return out
    poly = clip(poly, lambda p: p[0] >= a - 1e-9, a)
    if len(poly) < 3:
        return []
    poly = clip(poly, lambda p: p[0] <= b + 1e-9, b)
    return poly if len(poly) >= 3 else []


def _tris(poly):
    if len(poly) == 3:
        return [poly]
    idx = tessellate_polygon([[Vector((x, y, 0.0)) for x, y in poly]])
    return [[poly[i] for i in tri] for tri in idx]


def _on_cloth(out, cl, key, layer, poly, off, front=True):
    """천 2D 다각형을 열마다 잘라 천 표면(앞 또는 뒤) 위에 놓는다."""
    sgn = 1 if front else -1
    xs = [p[0] for p in poly]
    c0, c1 = cl.col(min(xs)), cl.col(max(xs))
    if c0 == c1 and len(poly) <= 4 and _convex(poly):
        pieces = [(c0, poly)]
    else:
        pieces = []
        for tri in _tris(poly):
            xs = [p[0] for p in tri]
            a, b = cl.col(min(xs)), cl.col(max(xs))
            if a == b:
                pieces.append((a, tri))
                continue
            for c in range(a, b + 1):
                lo = cl.us[c] if c > 0 else -1e9
                hi = cl.us[c + 1] if c < len(cl.us) - 2 else 1e9
                q = _clip(tri, lo, hi)
                if q:
                    pieces.append((c, q))
    for c, q in pieces:
        out.poly(key, layer, [cl.at(s, t, sgn * off, c) for s, t in q], cl.normal(c) * sgn)


def _convex(poly):
    n = len(poly)
    sg = 0
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        cx, cy = poly[(i + 2) % n]
        z = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if abs(z) < 1e-12:
            continue
        s = 1 if z > 0 else -1
        if sg and s != sg:
            return False
        sg = s
    return True


def _cloth_body(out, cl, key, layer, th):
    """천 판: 앞·뒤 면 + 가장자리 (열마다 평면 사각형)."""
    n = len(cl.us)
    verts = []
    for i in range(n):
        for t in (0.0, -cl.H):
            for off in (th / 2, -th / 2):
                verts.append(cl.at(cl.us[i], t, off, min(i, n - 2)))
    # 정점 순서: i*4 + (위앞, 위뒤, 아래앞, 아래뒤)
    faces = []
    for i in range(n - 1):
        a, b = i * 4, (i + 1) * 4
        faces.append([a + 0, a + 2, b + 2, b + 0])      # 앞 (-Y 쪽)
        faces.append([a + 1, b + 1, b + 3, a + 3])      # 뒤
        faces.append([a + 0, b + 0, b + 1, a + 1])      # 위
        faces.append([a + 2, a + 3, b + 3, b + 2])      # 아래
    e = (n - 1) * 4
    faces.append([0, 1, 3, 2])                          # 매단 쪽
    faces.append([e + 0, e + 2, e + 3, e + 1])          # 끝
    # 감김 맞춤: 앞 면 법선이 -Y 쪽이 되도록 확인
    v0, v1, v2 = verts[faces[0][0]], verts[faces[0][1]], verts[faces[0][2]]
    if (v1 - v0).cross(v2 - v0).dot(cl.normal(0)) < 0:
        faces = [list(reversed(f)) for f in faces]
    out.mesh(key, layer, verts, faces, smooth=False)


def _fringe_polys(W, H, f, *, bottom=True, fly=True, teeth=None):
    """천 가장자리 밖으로 이어 붙이는 금 술: 띠(사각형) + 톱니(삼각형 하나씩). 2D (s, t). 조각이 볼록이라 싸다."""
    polys = []
    b = f * 0.45
    if bottom:
        n = teeth or max(4, round(W / (f * 1.4)))
        polys.append([(0.0, -H), (W, -H), (W, -H - b), (0.0, -H - b)])
        for i in range(n):
            s0, s1 = W * i / n, W * (i + 1) / n
            polys.append([(s0, -H - b), (s1, -H - b), ((s0 + s1) / 2, -H - f)])
    if fly:
        n = max(3, round(H / (f * 1.4)))
        polys.append([(W, 0.0), (W + b, 0.0), (W + b, -H), (W, -H)])
        for i in range(n):
            t0, t1 = -H * i / n, -H * (i + 1) / n
            polys.append([(W + b, t0), (W + f, (t0 + t1) / 2), (W + b, t1)])
    return polys


def flag_cloth(out, W, H, *, cols=1, amp=0.0, waves=1.2, droop=0.0, phase=0.0, th=0.01, lift=0.004, res=2,
               low=False, edge=True, strokes=True, both=True, fringe=0.0, stripes=False, emblem_w=EMBLEM_W,
               emblem_c=None, cloth_layer="main", emblem_layer=None, trim_layer="detail"):
    """천 + 나비 (+ 금 술, 깃대 쪽 금 줄). 로컬: 매단 쪽 위 모서리 = 원점, 끝 = +X, 위 = +Z, 앞면 = -Y."""
    cl = _Cloth(W, H, cols=cols, amp=amp, waves=waves, droop=droop, phase=phase)
    _cloth_body(out, cl, "erf_green", cloth_layer, th)
    sides = (True, False) if both else (True,)
    ec = emblem_c or (W / 2, -H / 2)
    parts = emblem_parts(emblem_w * W, res=res, low=low, edge=edge, strokes=strokes, center=ec)
    if stripes:
        for a, b in ((0.030, 0.048), (0.064, 0.082)):
            parts.append(("erf_gold", "under", [(a * W, -0.0), (b * W, -0.0), (b * W, -H), (a * W, -H)]))
    for front in sides:
        for key, layer, poly in parts:
            lf = th / 2 + (lift if layer == "under" else lift * 2.2)
            _on_cloth(out, cl, key, emblem_layer or layer, poly, lf, front)
    if fringe > 0:
        for poly in _fringe_polys(W, H, fringe):
            for front in (True, False):
                _on_cloth(out, cl, "erf_gold", trim_layer, poly, th * 0.35, front)
    return cl


# ---------------------------------------------------------------- 변형
def standard(sink, M, *, pole=2.5, W=1.1, H=None, top=None, r=None, wave=0.06, droop=0.05, cols=10, res=2,
             low=False, strokes=True, fly=1, fringe=True, stripes=True, finial=True, butt=True, th=None, lift=None,
             phase=0.4, pole_key="erf_pole", layers=None):
    """큰 군기. 로컬: 깃대 = +Z (z 0 → pole), 천은 깃대 옆 +X(fly=-1이면 -X)로 매달려 물결친다. 앞면 = -Y.
    M = 로컬 → 세계(또는 소품) 행렬. top = 천 위 가장자리 높이(기본: 창끝 아래). 반환: 천 위 가장자리 높이."""
    H = W / ASPECT if H is None else H
    r = max(0.018, W * 0.022) if r is None else r
    th = max(0.008, H * 0.016) if th is None else th
    lift = max(0.002, H * 0.004) if lift is None else lift
    L = {"pole": "main", "gold": "detail", "cloth": "main"}
    L.update(layers or {})
    top = pole - r * 2.5 if top is None else top
    base = M @ Matrix.Rotation(math.pi, 4, "Z") if fly < 0 else M
    o = _Out(sink, base)
    o.cyl(pole_key, L["pole"], 0.0, pole, r, segs=8)
    if butt:
        o.cyl("erf_gold", L["gold"], -0.01, 0.045, r * 1.3, segs=8)
    # 천을 매단 금 고리 (천 위·아래)
    for z in (top + r * 0.9, top - H - r * 0.3):
        o.cyl("erf_gold", L["gold"], z - r * 0.6, z + r * 0.6, r * 1.35, segs=8)
    if finial:
        k = r
        o.lathe("erf_gold", L["gold"], [(k * 1.5, pole - 0.01), (k * 1.6, pole + k * 0.8), (k * 1.1, pole + k * 1.2),
                                         (k * 1.9, pole + k * 2.4), (k * 1.1, pole + k * 3.6), (k * 0.7, pole + k * 4.0)],
                segs=8)
        # 창끝: 납작한 마름모 날 (진군깃발 아이콘의 창끝)
        z0 = pole + k * 3.9
        o.lathe("erf_gold", L["gold"], [(k * 0.75, z0), (k * 2.3, z0 + k * 2.2), (k * 1.6, z0 + k * 5.0),
                                         (0.0, z0 + k * 8.5)], segs=4, sx=1.0, sy=0.38, smooth=False)
    co = _Out(sink, base @ Matrix.Translation((r * 0.5, 0.0, top)))
    flag_cloth(co, W, H, cols=cols, amp=wave, droop=droop, phase=phase, th=th, lift=lift, res=res, low=low,
               strokes=strokes, fringe=(H * 0.07 if fringe else 0.0), stripes=stripes, cloth_layer=L["cloth"],
               trim_layer=L["gold"])
    return top


def carried(sink, *, grip=0.55, pole=2.6, W=1.12, M=None, **kw):
    """기수가 드는 큰 군기 (소품 규약: 원점 = 오른손 파지점, 깃대 +Y, 천은 X-Y 면, 위 +Z).
    NPC 자세의 _holdRrot [-90, 0, 0]으로 깃대가 위로 선다. 천은 +X 쪽으로 날린다."""
    base = Matrix.Rotation(math.radians(-90.0), 4, "X") @ Matrix.Translation((0.0, 0.0, -grip))
    return standard(sink, (M or Matrix.Identity(4)) @ base, pole=pole, W=W, **kw)


def banner(sink, M, *, W=1.2, H=3.6, res=1, low=False, strokes=True, fringe=True, rod=True, both=False,
           emblem_w=0.6, th=None, lift=None, layers=None):
    """세로 현수막 (벽·기둥에 거는 천). 로컬: 위 가운데 = 원점, 천은 -Z로 늘어지고 앞면 = -Y, 봉은 X축.
    원작 군기의 초록 바탕 + 나비를 세로 천에 옮겼다 (나비 폭 = 천 폭 × emblem_w, 위에서 0.4 H). 위 금 줄 둘, 아래 금 술.
    low = 멀리 보는 자리(성긴 나비 외곽선)."""
    th = max(0.012, W * 0.02) if th is None else th
    lift = max(0.003, W * 0.004) if lift is None else lift
    L = {"gold": "detail", "cloth": "main"}
    L.update(layers or {})
    if rod:
        rr = max(0.03, W * 0.035)
        R = Matrix.Rotation(math.pi / 2, 4, "Y")
        ro = _Out(sink, M @ R)
        ro.cyl("erf_gold", L["gold"], -W / 2 - rr * 3, W / 2 + rr * 3, rr, segs=6)
        for sx in (-1, 1):
            _Out(sink, M @ Matrix.Translation((sx * (W / 2 + rr * 3.6), 0, 0))).lathe(
                "erf_gold", L["gold"], [(0.0, -rr * 1.7), (rr * 1.6, -rr * 0.5), (rr * 1.6, rr * 0.5),
                                        (0.0, rr * 1.7)], segs=6)
    co = _Out(sink, M @ Matrix.Translation((-W / 2, 0.0, -0.02)))
    cl = _Cloth(W, H, cols=1)
    _cloth_body(co, cl, "erf_green", L["cloth"], th)
    parts = emblem_parts(emblem_w * W, res=res, low=low, strokes=strokes, center=(W / 2, -0.4 * H))
    for a, b in ((0.045, 0.06), (0.08, 0.095)):
        parts.append(("erf_gold", "under", [(0.0, -a * H), (W, -a * H), (W, -b * H), (0.0, -b * H)]))
    for front in ((True, False) if both else (True,)):
        for key, layer, poly in parts:
            _on_cloth(co, cl, key, layer, poly, th / 2 + (lift if layer == "under" else lift * 2.2), front)
    if fringe:
        for poly in _fringe_polys(W, H, H * 0.045, fly=False, teeth=max(6, round(W / 0.12))):
            for front in (True, False):
                _on_cloth(co, cl, "erf_gold", L["gold"], poly, th * 0.35, front)


def hand_flag(sink, M, *, W=0.16, stick=0.34, r=None, wave=0.07, cols=3, res=1, low=True, edge=True, th=None,
              lift=None, layers=None):
    """군중 손깃발. 로컬: 원점 = 파지점, 막대 = +Z (z -0.05 → stick), 천은 막대 끝에서 +X로. 앞면 = -Y."""
    H = W / ASPECT
    r = max(0.0035, W * 0.026) if r is None else r
    th = max(0.002, H * 0.03) if th is None else th
    lift = max(0.0012, H * 0.012) if lift is None else lift
    L = {"pole": "main", "cloth": "main"}
    L.update(layers or {})
    o = _Out(sink, M)
    o.lathe("erf_pole", L["pole"], [(r, -0.05), (r, stick), (r * 1.6, stick + r * 0.8), (0.0, stick + r * 2.6)], segs=6)
    co = _Out(sink, M @ Matrix.Translation((r * 0.6, 0.0, stick - r)))
    flag_cloth(co, W, H, cols=cols, amp=wave, waves=1.0, droop=0.04, th=th, lift=lift, res=res, low=low, edge=edge,
               strokes=False, cloth_layer=L["cloth"])


def far_flag(sink, M, *, W=1.5, H=None, pole=None, r=None, res=1, low=True, edge=False, both=True, th=None,
             lift=None, bend=0.0, layers=None):
    """원경·작은 깃발 (탑 꼭대기, 가로등, 천막). 로컬: pole이 있으면 깃대 = +Z (z 0 → pole), 천 위 모서리 = 깃대 끝.
    pole=None이면 원점 = 천을 매단 위 모서리. 천은 +X로, 앞면 = -Y. bend = 끝을 앞뒤로 살짝 꺾는 정도(0이면 평판)."""
    H = W / ASPECT if H is None else H
    th = max(0.01, H * 0.03) if th is None else th
    lift = max(0.006, H * 0.012) if lift is None else lift
    L = {"pole": "main", "cloth": "main", "emblem": "fine"}
    L.update(layers or {})
    o = _Out(sink, M)
    z = 0.0
    if pole:
        r = max(0.02, W * 0.02) if r is None else r
        o.cyl("erf_pole", L["pole"], 0.0, pole + r * 2, r, segs=4, smooth=False)
        z = pole
    co = _Out(sink, M @ Matrix.Translation(((r or 0.0) * 0.5, 0.0, z)))
    flag_cloth(co, W, H, cols=2 if bend else 1, amp=bend, waves=0.5, th=th, lift=lift, res=res, low=low, edge=edge,
               strokes=False, both=both, cloth_layer=L["cloth"], emblem_layer=L["emblem"])


def emblem(sink, M, size, *, res=2, low=False, edge=True, strokes=True, lift=0.004, layers=None):
    """평면 위 나비 문장만. 로컬: 가운데 원점, 면 = X-Z, 바깥 = -Y. size = 나비 폭."""
    L = layers or {}
    o = _Out(sink, M)
    for key, layer, poly in emblem_parts(size, res=res, low=low, edge=edge, strokes=strokes):
        lf = lift if layer == "under" else lift * 2.2
        o.poly(key, L.get(layer, layer), [(x, -lf, y) for x, y in poly], (0, -1, 0))



def grid_tris(poly, step):
    """오목 다각형을 안쪽 격자점(간격 step)과 함께 제약 들로네 분할 (mathutils delaunay_2d_cdt). 고른 삼각형이라
    곡면에 감쌀 때(warp_sink, 머스킷 개머리 부조) 긴 삼각형이 곡면 아래로 가라앉거나 뒤집히지 않는다.
    반환: 점 튜플 삼각형들 (poly의 점은 넘겨받은 그대로, 격자점은 새 튜플)."""
    n = len(poly)
    xs, zs = [p[0] for p in poly], [p[1] for p in poly]

    def inside(x, z):
        c = False
        for i in range(n):
            (x0, z0), (x1, z1) = poly[i], poly[(i + 1) % n]
            if (z0 > z) != (z1 > z) and x < x0 + (z - z0) * (x1 - x0) / (z1 - z0):
                c = not c
        return c

    def near(x, z, d):
        for i in range(n):
            a_, b_ = Vector(poly[i]), Vector(poly[(i + 1) % n])
            ab = b_ - a_
            t = max(0.0, min(1.0, (Vector((x, z)) - a_).dot(ab) / max(ab.length_squared, 1e-12)))
            if (a_ + ab * t - Vector((x, z))).length < d:
                return True
        return False
    pts = [tuple(p) for p in poly]
    z = min(zs) + step * 0.5
    row = 0
    while z < max(zs):
        x = min(xs) + step * (0.5 if row % 2 else 0.0)
        while x < max(xs):
            if inside(x, z) and not near(x, z, step * 0.45):
                pts.append((x, z))
            x += step
        z += step * 0.866
        row += 1
    r = delaunay_2d_cdt([Vector(p) for p in pts], [(i, (i + 1) % n) for i in range(n)], [list(range(n))], 1, 1e-9)
    vs = [pts[o[0]] if o else (v.x, v.y) for v, o in zip(r[0], r[3])]     # 입력 점 그대로 (Vector는 float32)
    return [tuple(vs[i] for i in f) for f in r[2] if len(f) == 3]


def _cap(poly, y, inner, front, grid=0.0):
    """판의 한쪽 면 (y 평면). inner가 있으면 둘레 고리(poly → inner 사각형) + 안쪽 삼각 분할: 아웃라인 헐(toon.ts)이
    정점을 이웃 면 법선 평균으로 밀 때 오목한 홈끼리 잇는 긴 삼각형이 뒤집혀 면을 가로지르는 금이 보이지 않게, 둘레 정점과
    안쪽 정점을 나눈다. 반환 (정점, 면): 앞면(front, -Y) 또는 뒷면(+Y)을 본다."""
    n = len(poly)
    verts = [(x, y, z) for x, z in poly]
    faces = []
    ring = inner or poly
    if inner:
        verts += [(x, y, z) for x, z in inner]
        for i in range(n):
            j = (i + 1) % n
            faces.append([i, j, n + j, n + i])
    base = n if inner else 0
    idx = {p: base + i for i, p in enumerate(ring)}

    def vid(p):
        key = (round(p[0], 7), round(p[1], 7))
        if p not in idx and key not in idx:
            verts.append((p[0], y, p[1]))
            idx[key] = len(verts) - 1
        return idx[p] if p in idx else idx[key]
    for tri in (grid_tris(ring, grid) if grid > 0 else [tuple(t) for t in _tris(ring)]):
        a, b, c = (vid(p) for p in tri)
        (ax, az), (bx, bz), (cx, cz) = tri
        if (bx - ax) * (cz - az) - (bz - az) * (cx - ax) < 0:
            b, c = c, b
        faces.append([a, b, c])
    if not front:
        faces = [f[::-1] for f in faces]
    return verts, faces


def _slab(o, key, layer, poly, y0, y1, *, ring=0.0, hole=None, bottom=True, grid=0.0):
    """2D 다각형 (x, z) (반시계)을 y0(안쪽)에서 y1(바깥, y0보다 작음)까지 세운 판. 앞면 = -Y. 오목해도 된다.
    ring > 0: 앞뒤 면을 둘레 고리(폭 ring) + 안쪽으로 나눈다 (_cap). hole = 안쪽 둘레(같은 점 수): 고리 판(윤곽선 테).
    bottom=False: 붙는 면(+Y, 안 보임)을 빼서 삼각형을 아낀다."""
    n = len(poly)
    verts, faces = [], []

    def add(vs, fs):
        b = len(verts)
        verts.extend(vs)
        faces.extend([[b + i for i in f] for f in fs])
    if hole:
        for y, front in ((y1, True), (y0, False))[:2 if bottom else 1]:
            vs = [(x, y, z) for x, z in poly] + [(x, y, z) for x, z in hole]
            fs = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
            add(vs, fs if front else [f[::-1] for f in fs])
    else:
        inner = _offset(poly, -ring) if ring > 0 else None
        add(*_cap(poly, y1, inner, True, grid))
        if bottom:
            add(*_cap(poly, y0, inner, False, grid))
    vs = [(x, y0, z) for x, z in poly] + [(x, y1, z) for x, z in poly]
    add(vs, [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)])
    o.mesh(key, layer, verts, faces, smooth=False)


def badge(sink, M, size, *, depth=0.004, rim=0.6, res=2, low=False, edge=True, strokes=True, sink_in=0.0,
          both=False, fine=False, layers=None):
    """두께 있는 나비 문장 (배지·부조·조형). emblem()과 같은 도안(outline·STROKES)을 판으로 세운다.
    노란 바탕 판(y = sink_in → -depth) + 그 둘레 금 윤곽선 테(한 단 낮게, -depth × rim까지) + 바탕 위 금 말린 선(얇은 판).
    로컬: 가운데 원점, 면 = X-Z, 바깥 = -Y (emblem()과 같다). size = 나비 폭(윤곽선 제외).
    sink_in > 0이면 판 밑을 면 안으로 묻는다(곡면 위에서 가장자리가 뜨지 않게).
    both = 앞뒤 대칭 조형(지붕 꼭대기처럼 뒤에서도 보이는 것): 판이 y = +depth → -depth, 말린 선도 양면.
    색 키 erf_yellow(바탕)·erf_gold(윤곽선·말린 선). 금속 배지는 buf_sink(buf, {"erf_yellow": 금, "erf_gold": 짙은 금})처럼
    키를 그 모델의 재질에 맞춘다. 아웃라인 헐이 두꺼운 인물에서는 strokes=False (말린 선이 헐에 묻혀 검은 덩어리가 된다).
    fine = 바탕 면 안쪽을 고른 격자 삼각형으로 (곡면에 감싸 붙일 때: warp_sink).
    layers: {"fill", "edge", "line"} → 종류 (기본 detail, detail, fine)."""
    L = {"fill": "detail", "edge": "detail", "line": "fine"}
    L.update(layers or {})
    s = size / 2
    sc = lambda pts: [(x * s, z * s) for x, z in pts]  # noqa: E731
    fill = outline(res, low)
    o = _Out(sink, M)
    _slab(o, "erf_yellow", L["fill"], sc(fill), depth if both else sink_in, -depth, ring=EDGE * s, bottom=both,
          grid=size * 0.15 if fine else 0.0)
    if edge:
        _slab(o, "erf_gold", L["edge"], sc(_offset(fill, EDGE)), depth * rim if both else sink_in, -depth * rim,
              hole=sc(fill), bottom=both)
    if strokes:
        h = max(depth * 0.3, size * 0.004)
        for sg in ((1, -1) if both else (1,)):
            so = _Out(sink, M @ Matrix.Rotation(math.pi, 4, "Z")) if sg < 0 else o     # 뒷면 (선이 좌우 대칭이라 돌려도 같다)
            for st in STROKES:
                for sx in (1, -1):
                    for quad in _strip([(sx * x, y) for x, y in st], STROKE_W, STROKE_W * 0.45):
                        quad = [tuple(p) for p in quad]
                        if (quad[1][0] - quad[0][0]) * (quad[2][1] - quad[0][1]) - \
                                (quad[1][1] - quad[0][1]) * (quad[2][0] - quad[0][0]) < 0:
                            quad.reverse()
                        _slab(so, "erf_gold", L["line"], sc(quad), -depth * 0.8, -depth - h, bottom=False)
