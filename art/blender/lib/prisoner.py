"""죄수복 모듈 (prisoner): 미국 교도소식 주황 점프슈트.

[오리지널] 지구 포로수용소의 엘프 포로복. 포로 생활부터 엘리아스 불시착 직후까지 엘프들이 입는다(docs/scenario.md
인터루드 2번 '복장', 사용자 확정). 투항 장면은 아직 엘피니아 군복이다.
- 원피스형 커버올: 접힌 깃, 앞 똑딱단추 여밈, 왼쪽 가슴 주머니, 고무줄 허리(주름이 모임), 속에 흰 티셔츠(V 사이로 보임).
- 인간 규격을 그대로 지급받아 헐렁하다: 처진 어깨 솔기, 두 번 걷어 올린 소매와 바짓단(단 위 천 뭉침, 밑으로 흰 양말),
  넉넉한 통. 맨손이다.
- 스텐실: 등에 큰 'P.O.W.'와 수용 번호, 오른쪽 가슴에 'P.O.W.', 왼쪽 가슴(주머니 위)에 번호. 실존 교정 시설·기관 이름이나
  로고는 쓰지 않는다. 글자는 DIN Condensed를 평면 메시로 바꿔 천 곡면에 감고, 속이 막힌 글자(P, O, 0, 4, 8 …)는 가운데를
  세로로 끊어 스텐실 다리를 낸다.
- 신발: 남색 캔버스 슬립온 + 흰 고무 밑창 + 옆 고무 밴드. 실내 장면이라 모자는 없다.
- 툰 화풍: 주름·솔기는 천 표면에 붙인 가는 먹선(아웃라인 없는 데칼 노드 <이름>_decal, <이름>_decal_arms)으로 그리고,
  걷은 단은 울퉁불퉁한 고리 두 겹, 단 위 천 뭉침은 반지름 물결로 낸다. 큰 형태(깃, 주머니, 고무 허리, 걷은 단)는
  두께가 있어 몸 아웃라인을 받는다.

    import prisoner as pr
    P = pr.mats("rita_p")
    js = pr.outfit(e, P, number="0417")   # 점프슈트 + 양말 + 슬립온. 팔(소매·걷은 단)은 arms 그룹
    # 다수 등장 단역: pr.outfit(e, P, number="1146", lean=True)  (먹선·스텐실 일부 생략)

치수는 기본 체격 기준 m이고 안에서 e.k를 곱한다. 문서: docs/art/ELF_KIT.md(키트), docs/art/interlude-earth.md(세트).
"""
from __future__ import annotations

import bisect
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
from elf import Buf, band, clamp, disc, keys, lerp, loft, smoothstep  # noqa: E402

V = Vector

# =========================================================================== palette

PAL = {
    # 천: 미국 교도소 주황을 툰 파스텔 쪽으로 조금 누름 (세트의 노을·밤 조명에서 갈색으로 죽지 않고, 낮에 형광처럼 튀지 않게)
    "suit": "#ee7d3c",
    "suit_d": "#d4642c",    # 깃 띠·고무 허리·여밈단·주머니 단 (한 톤 어둡게)
    "roll": "#e2702f",      # 걷은 단 (천 안쪽이 바깥으로 나온 면)
    "seam": "#bd5426",      # 솔기 먹선
    "fold": "#9c3f1c",      # 주름 먹선
    "stencil": "#2c2427",   # 스텐실 글자 (검정에 가까운 갈색)
    "tee": "#ebe6de",       # 속 흰 티셔츠
    "snap": "#d6d0c6",      # 똑딱단추 (무광 금속)
    "sock": "#eeeae3",
    "shoe": "#3d4458",      # 남색 캔버스 슬립온
    "shoe_d": "#2a2f3e",    # 옆 고무 밴드
    "sole": "#ebe6dc",      # 흰 고무 밑창
}


def mats(prefix: str, over: dict | None = None) -> dict:
    """PAL로 머티리얼 사전. over={"suit": "#..."}로 바꾼다."""
    pal = dict(PAL)
    pal.update(over or {})
    return {k: elf.mat(f"{prefix}_{k}", v) for k, v in pal.items()}


# =========================================================================== small geometry

def _ring_pt(rx, ry, cy, z, a_deg, p=2.3):
    """몸통 단면(초타원) 위 점. a: 0=앞(-Y), 90=왼쪽(+X), 180=뒤. 키트 torso_point·loft와 같은 곡선."""
    a = math.radians(a_deg)
    dx, dy = math.sin(a), -math.cos(a)
    ee = 2.0 / p
    x = math.copysign(abs(dx) ** ee, dx) * rx
    y = math.copysign(abs(dy) ** ee, dy) * ry + cy
    return V((x, y, z))


def _ink(buf, pts, nrms, width, mat, w, *, closed=False, taper=0.25):
    """천 위의 먹선 (두께 없는 띠, 법선 쪽이 앞면). width: 가운데 폭(m), taper: 양 끝 폭 비율.
    w: 웨이트 사전 목록(점마다) 또는 사전 하나."""
    n = len(pts)
    L, R = [], []
    for i in range(n):
        p, nn = V(pts[i]), V(nrms[i]).normalized()
        a = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        b = pts[(i + 1) % n] if closed else pts[min(i + 1, n - 1)]
        tan = V(b) - V(a)
        tan = (tan - nn * tan.dot(nn)).normalized()
        s = tan.cross(nn).normalized()
        u = i / (n - 1) if n > 1 else 0.5
        f = 1.0 if closed else lerp(taper, 1.0, math.sin(math.pi * u) ** 0.7)
        hw = width * f / 2
        ww = w[i] if isinstance(w, list) else w
        L.append(buf.vert(p - s * hw, ww))
        R.append(buf.vert(p + s * hw, ww))
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        j = (i + 1) % n
        buf.face((L[i], R[i], R[j], L[j]), mat)


def _slab(buf, grid_p, grid_n, th, mat, w):
    """곡면 격자(행×열의 점·법선) 위에 두께 th인 판. 윗면·아랫면·옆면. w: 웨이트 격자 또는 사전."""
    R, C = len(grid_p), len(grid_p[0])
    wf = (lambda i, j: w[i][j]) if isinstance(w, list) else (lambda i, j: w)
    bot = [[buf.vert(grid_p[i][j], wf(i, j)) for j in range(C)] for i in range(R)]
    top = [[buf.vert(grid_p[i][j] + grid_n[i][j] * th, wf(i, j)) for j in range(C)] for i in range(R)]
    # 격자: 행 i는 위→아래, 열 j는 시청자 기준 왼쪽→오른쪽 (법선 쪽에서 봐서 반시계가 되게)
    for i in range(R - 1):
        for j in range(C - 1):
            buf.face((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]), mat)
            buf.face((bot[i][j], bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j]), mat)
    ring = [(0, j) for j in range(C)] + [(i, C - 1) for i in range(1, R)] + \
           [(R - 1, j) for j in range(C - 2, -1, -1)] + [(i, 0) for i in range(R - 2, 0, -1)]
    for a in range(len(ring)):
        i0, j0 = ring[a]
        i1, j1 = ring[(a + 1) % len(ring)]
        buf.face((bot[i0][j0], top[i0][j0], top[i1][j1], bot[i1][j1]), mat)


def _roll(buf, c, tan, A, rx, ry, rt, ht, *, segs, tsegs, mat, w, lump=0.18, lumps=5, phase=0.0):
    """걷은 단 한 겹: 팔다리 축(tan)을 감는 울퉁불퉁한 고리. rx, ry: 고리 안쪽이 닿는 천 반지름(A, B 축),
    rt: 단면 반지름(바깥 방향), ht: 단면 반높이(축 방향)."""
    tan = V(tan).normalized()
    A = (V(A) - tan * V(A).dot(tan)).normalized()
    B = tan.cross(A).normalized()
    rings = []
    for i in range(segs):
        th = 2 * math.pi * i / segs
        radial = (A * (math.cos(th) / max(rx, 1e-6)) + B * (math.sin(th) / max(ry, 1e-6))).normalized()
        q = 1 + lump * math.sin(lumps * th + phase) + 0.5 * lump * math.sin(2 * lumps * th + 1.7 * phase + 0.6)
        r = rt * q
        base = V(c) + A * ((rx + r * 0.85) * math.cos(th)) + B * ((ry + r * 0.85) * math.sin(th))
        h = ht * (1 + 0.6 * lump * math.sin(lumps * th + phase + 1.3))
        ring = []
        for j in range(tsegs):
            b = 2 * math.pi * j / tsegs
            ring.append(buf.vert(base + radial * (r * math.cos(b)) + tan * (h * math.sin(b)), w))
        rings.append(ring)
    for i in range(segs):
        r0, r1 = rings[i], rings[(i + 1) % segs]
        for j in range(tsegs):
            j2 = (j + 1) % tsegs
            buf.face((r0[j], r1[j], r1[j2], r0[j2]), mat)


# =========================================================================== stencil text

_FONT_PATH = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
_font_cache: dict = {}
_text_cache: dict = {}


def _font():
    if "din" not in _font_cache:
        f = None
        if os.path.exists(_FONT_PATH):
            try:
                f = bpy.data.fonts.load(_FONT_PATH, check_existing=True)
            except Exception:  # noqa: BLE001
                f = None
        _font_cache["din"] = f
    return _font_cache["din"]


def stencil_text(s: str, height: float, *, gap=0.11, res=2):
    """글자열 → 평면 삼각형 메시 (x 오른쪽, y 위, 가운데 정렬, 글자 높이 = height).
    속이 막힌 글자(구멍이 있는 섬)는 가운데를 세로로 gap×height 폭만큼 끊어 스텐실 다리를 낸다.
    반환: (점 목록 [(x, y)], 삼각형 목록 [(i, j, k)])."""
    key = (s, round(height, 6), gap, res)
    if key in _text_cache:
        return _text_cache[key]
    cu = bpy.data.curves.new("pr_text_crv", "FONT")
    cu.body = s
    f = _font()
    if f:
        cu.font = f
    cu.size = 1.0
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.resolution_u = res
    ob = bpy.data.objects.new("pr_text_tmp", cu)
    cb.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bm.faces.ensure_lookup_table()
    bm.faces.index_update()
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    sc = height / max(max(ys) - min(ys), 1e-6)
    cx0, cy0 = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    for v in bm.verts:
        v.co = V(((v.co.x - cx0) * sc, (v.co.y - cy0) * sc, 0.0))
    # 섬 나누기 (면이 변을 공유하면 같은 섬)
    seen, islands = set(), []
    for f0 in bm.faces:
        if f0.index in seen:
            continue
        stack, isl = [f0], []
        seen.add(f0.index)
        while stack:
            fc = stack.pop()
            isl.append(fc)
            for ed in fc.edges:
                for f2 in ed.link_faces:
                    if f2.index not in seen:
                        seen.add(f2.index)
                        stack.append(f2)
        islands.append(isl)
    cuts = []
    for isl in islands:
        vs = {v for fc in isl for v in fc.verts}
        es = {ed for fc in isl for ed in fc.edges}
        holes = 1 - (len(vs) - len(es) + len(isl))
        if holes < 1:
            continue
        x0, x1 = min(v.co.x for v in vs), max(v.co.x for v in vs)
        y0, y1 = min(v.co.y for v in vs), max(v.co.y for v in vs)
        cuts.append(((x0 + x1) / 2, x0, x1, y0, y1))
    g = gap * height / 2
    for cx, x0, x1, y0, y1 in cuts:
        for px in (cx - g, cx + g):
            geom = []
            for fc in bm.faces:
                c = fc.calc_center_median()
                if x0 - 1e-6 <= c.x <= x1 + 1e-6 and y0 - 1e-6 <= c.y <= y1 + 1e-6:
                    geom.append(fc)
            gset = set(geom)
            gv = {v for fc in gset for v in fc.verts}
            ge = {ed for fc in gset for ed in fc.edges}
            bmesh.ops.bisect_plane(bm, geom=list(gv) + list(ge) + geom, dist=1e-7, plane_co=(px, 0, 0),
                                   plane_no=(1, 0, 0))
        kill = []
        for fc in bm.faces:
            c = fc.calc_center_median()
            if cx - g < c.x < cx + g and y0 - 1e-6 <= c.y <= y1 + 1e-6:
                kill.append(fc)
        bmesh.ops.delete(bm, geom=kill, context="FACES")
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.verts.index_update()
    pts = [(v.co.x, v.co.y) for v in bm.verts]
    tris = [tuple(v.index for v in fc.verts) for fc in bm.faces]
    bm.free()
    _text_cache[key] = (pts, tris)
    return pts, tris


# =========================================================================== jumpsuit

class Jumpsuit:
    """주황 점프슈트 한 벌. 몸판·바지·소매를 직접 만들고(헐렁한 통, 단 위 천 뭉침) 그 표면을 다시 계산할 수 있어
    깃·주머니·스텐실·먹선을 천에 정확히 붙인다.

    off      몸판이 몸에서 떨어진 거리(m). 기본 0.017 (키트 셔츠 0.010보다 헐렁)
    flare    고무 허리 위로 블라우징되는 양(m)
    pants_off, bag  바지 띄움, 통
    sleeve   소매 끝(팔 비율, 걷은 단 아래 끝). 기본 0.80 (아래팔 중간)
    hem      바짓단(다리 비율). 기본 0.82 (발목 위, 밑으로 양말)
    number   수용 번호 (가슴·등 스텐실 'EL-<번호>')
    lean     다수 등장 단역용: 먹선 일부·가슴 'P.O.W.'·단추 일부 생략
    """

    def __init__(self, e, M, *, number="0000", off=0.017, flare=0.008, pants_off=0.011, bag=0.013, sleeve=0.80,
                 hem=0.82, lean=False, seed=0.0, back_text="P.O.W.", prefix="EL-"):
        self.e, self.M, self.k = e, M, e.k
        self.number = number
        self.off, self.flare, self.pants_off, self.bag = off, flare, pants_off, bag
        self.L, self.hem = sleeve, hem
        self.lean = lean
        self.seed = seed
        self.back_text = back_text
        self.prefix = prefix
        k = e.k
        self.top = e.torso_top
        self.zb = e.waist_z + 0.002 * k               # 고무 허리 가운데
        self.z_hem = self.zb - 0.006 * k               # 몸판 밑단 (고무 허리 띠 안)
        self.zw = self.zb + 0.016 * k                  # 바지 윗단 (몸판 안)
        self.fl_tab = [(0.0, flare * k), (0.25, flare * k * 0.3), (0.45, 0.0), (1.0, 0.0)]
        self.st_top = e.torso_stations(self.z_hem, self.top, off=off * k, flare=self.fl_tab, p=2.3)
        self.top_off = 0.004
        self.st_top[-1]["rx"] = 0.056 * k + self.top_off * k
        self.st_top[-1]["ry"] = 0.048 * k + self.top_off * k
        self.st_bot = e.torso_stations(e.crotch_z + 0.002 * k, self.zw, off=pants_off * k, p=2.2)
        self.fr_top = self._frames(self.st_top, (1, 0, 0))
        self.fr_bot = self._frames(self.st_bot, (1, 0, 0))
        self.limb = {}       # (kind, side) → dict(t=[...], c, A, rx, ry)
        self.dec = Buf()     # 몸 먹선·스텐실 (아웃라인 없음)
        self.dec_arms = Buf()

    # ------------------------------------------------------------------ surfaces
    @staticmethod
    def _frames(st, ref):
        """키트 loft와 같은 단면 좌표계: 접선은 이웃 단면 중심의 차분, A는 ref를 접선에 수직으로, B = 접선 × A.
        (단면 중심이 앞뒤로 움직이면 링이 기울어진다. 그대로 따라야 옷 위 데칼이 천 속으로 묻히지 않는다)"""
        cs = [V(x["c"]) for x in st]
        n = len(cs)
        out = []
        prevA = None
        for i in range(n):
            t = cs[min(i + 1, n - 1)] - cs[max(i - 1, 0)]
            t = t.normalized() if t.length > 1e-9 else V((0, 0, 1))
            r = V(ref)
            A = r - t * r.dot(t)
            if A.length < 1e-6:
                A = prevA if prevA is not None else V((1, 0, 0))
            A = A.normalized()
            prevA = A
            out.append((cs[i], A, t.cross(A).normalized()))
        return out

    def _ring(self, st, fr, i, a):
        """단면 i에서 각도 a(0=앞, +90=왼쪽) 점. 몸통 loft의 ring_pts와 같은 식 (th = a - 90°)."""
        x_ = st[i]
        c, A, B = fr[i]
        p = x_.get("p", 2.0)
        th = math.radians(a - 90.0)
        ee = 2.0 / p
        ca, sa = math.cos(th), math.sin(th)
        x = math.copysign(abs(ca) ** ee, ca) * x_["rx"]
        y = math.copysign(abs(sa) ** ee, sa) * x_["ry"]
        q = c + A * x + B * y
        dsp = x_.get("disp")            # 키트 가슴 볼륨(Elf.bust): loft와 같은 밀기
        if dsp is not None:
            d = dsp(q, x_)
            if d is not None:
                q = q + d
        return q

    def _stations_at(self, st, z):
        """높이 z에서 단면 (rx, ry, cy, p): 이웃 단면 선형 보간 (띠·고리 크기용)."""
        zs = [x["c"][2] for x in st]
        z = clamp(z, zs[0], zs[-1])
        i = min(max(bisect.bisect_right(zs, z) - 1, 0), len(st) - 2)
        u = (z - zs[i]) / max(zs[i + 1] - zs[i], 1e-9)
        s0, s1 = st[i], st[i + 1]
        return lerp(s0["rx"], s1["rx"], u), lerp(s0["ry"], s1["ry"], u), lerp(s0["c"][1], s1["c"][1], u), \
            s0.get("p", 2.3)

    def _surf_s(self, st, fr, s_, a):
        n = len(st)
        s_ = clamp(s_, 0.0, n - 1.0)
        i = min(int(s_), n - 2)
        u = s_ - i
        return self._ring(st, fr, i, a).lerp(self._ring(st, fr, i + 1, a), u)

    def tsurf(self, z, a):
        """몸통 옷 바깥 면 점 (a: 0=앞, +90=왼쪽(+X), 180=등). 밑단 아래는 바지 윗부분.
        loft 링이 기울어 있어 같은 높이 z가 되는 단면 매개변수를 이분법으로 찾는다."""
        if z >= self.z_hem:
            st, fr = self.st_top, self.fr_top
        else:
            st, fr = self.st_bot, self.fr_bot
        lo, hi = 0.0, len(st) - 1.0
        if self._surf_s(st, fr, lo, a).z >= z:
            return self._surf_s(st, fr, lo, a)
        if self._surf_s(st, fr, hi, a).z <= z:
            return self._surf_s(st, fr, hi, a)
        for _ in range(26):
            mid = (lo + hi) / 2
            if self._surf_s(st, fr, mid, a).z < z:
                lo = mid
            else:
                hi = mid
        return self._surf_s(st, fr, (lo + hi) / 2, a)

    def tframe(self, z, a, lift=0.0):
        """(점, 법선): 법선은 면을 따라 잰 차분 (어깨 경사에서도 맞다)."""
        k = self.k
        dz, da = 0.003 * k, 1.0
        p = self.tsurf(z, a)
        zr = p.z                                   # 맨 위·아래를 넘으면 링에 붙은 실제 높이에서 잰다
        lo, hi = (self.z_hem, self.top + 0.02 * k) if z >= self.z_hem else (self.st_bot[0]["c"][2], self.z_hem - 1e-5)
        z0, z1 = max(zr - dz, lo), min(zr + dz, hi)
        if z >= self.z_hem and zr < self.z_hem:
            z0 = zr
        pz = self.tsurf(z1, a) - self.tsurf(z0, a)
        pa = self.tsurf(zr, a + da) - self.tsurf(zr, a - da)
        n = pa.cross(pz)
        if n.length < 1e-9:
            n = V((p.x, p.y, 0))
        n.normalize()
        return p + n * lift, n

    def twt(self, p):
        return self.e._torso_wfn(p, 0)

    def lsurf(self, kind, side, t, a, lift=0.0):
        """팔다리 옷 바깥 면 (점, 법선, 웨이트). a: 0=앞, +90=캐릭터 왼쪽(+X). loft 단면 좌표계를 그대로 쓴다."""
        L = self.limb[(kind, side)]
        ts = L["t"]
        tt = clamp(t, ts[0], ts[-1])
        i = min(max(bisect.bisect_right(ts, tt) - 1, 0), len(ts) - 2)
        u = (tt - ts[i]) / max(ts[i + 1] - ts[i], 1e-9)
        ar = math.radians(a)

        def ring(j):
            c, A, B = L["fr"][j]          # loft B = 접선 × A → 캐릭터 왼쪽(+X)은 -B
            return c + A * (L["rx"][j] * math.cos(ar)) - B * (L["ry"][j] * math.sin(ar)), \
                (A * (math.cos(ar) / L["rx"][j]) - B * (math.sin(ar) / L["ry"][j])).normalized()
        p0, n0 = ring(i)
        p1, n1 = ring(i + 1)
        p = p0.lerp(p1, u)
        n = n0.lerp(n1, u).normalized()
        return p + n * lift, n, L["ch"].weights(clamp(t))

    # ------------------------------------------------------------------ cloth
    def torso(self):
        e, M, k = self.e, self.M, self.k
        e.cover["torso"].append((self.z_hem, self.top + 0.05))
        e.cover["torso"].append((e.crotch_z - 0.05, self.zw))
        st, sb = self.st_top, self.st_bot
        st[0]["lip"] = 0.005 * k
        sb[-1]["lip"] = 0.004 * k
        q = e.q

        def fn(buf):
            loft(buf, st, segs=int(22 * q), cap0="lip", cap1="flat", mat=M["suit"], wfn=e._torso_wfn)
        e.part("suit_top", "body", fn)

        def fn2(buf):
            loft(buf, sb, segs=int(24 * q), cap0="round", cap1="lip", mat=M["suit"], wfn=e._torso_wfn,
                 cap_len0=0.04 * k)
        e.part("suit_hips", "body", fn2)
        # 고무 허리: 몸판 블라우징 바깥을 감는 띠
        rx, ry, cy, _ = self._stations_at(st, self.zb)
        hh = 0.022 * k

        def fn3(buf):
            band(buf, (0, cy, self.zb), (0, 0, 1), (1, 0, 0), rx + 0.0005 * k, ry + 0.0005 * k, hh, 0.0045 * k,
                 segs=e._s(26), mat=M["suit_d"], w=e._torso_wfn(V((0, 0, self.zb)), 0), p=2.3)
        e.part("suit_waist", "body", fn3)

    def _limb_cloth(self, kind, side, t0, t1, off, extra, *, n, segs, name, group):
        e, M, k = self.e, self.M, self.k
        ch = e.arm_chain(side) if kind == "arm" else e.leg_chain(side)
        rfn = e.arm_r if kind == "arm" else e.leg_r
        e.cover[f"{kind}_{side}"].append((-0.2 if kind == "leg" else 0.0, t1))
        ts, cs, rxs, rys, st = [], [], [], [], []
        for i in range(n):
            t = lerp(t0, t1, i / (n - 1))
            c, tan = ch.at(t)
            rx, ry = rfn(clamp(t))
            ex = extra(t)
            ts.append(t)
            cs.append(V(c))
            rxs.append(rx + off * k + ex)
            rys.append(ry + off * k + ex)
            st.append({"c": c, "rx": rxs[-1], "ry": rys[-1], "w": ch.weights(t)})
        st[-1]["lip"] = 0.0045 * k
        self.limb[(kind, side)] = dict(t=ts, c=cs, rx=rxs, ry=rys, ch=ch, fr=self._frames(st, (0, -1, 0)))

        def fn(buf):
            loft(buf, st, segs=segs, cap0="round", cap1="lip", mat=M["suit"], ref=(0, -1, 0),
                 cap_len0=min(rxs[0], rys[0]) * 0.8)
        e.part(name, group, fn)
        return ch

    def legs(self):
        e, k, M = self.e, self.k, self.M
        H = self.hem
        bag = self.bag

        def extra(t):
            ex = bag * keys([(-0.12, 0.30), (0.0, 0.55), (0.20, 1.0), (0.45, 0.80), (0.62, 0.70), (H, 0.45)], t)
            # 걷은 단 위 천 뭉침: 단 바로 위 두세 겹 물결
            z0 = H - 0.30
            if z0 < t < H - 0.12:
                u = (t - z0) / 0.18
                ex += 0.0042 * math.sin(math.pi * u) * (0.5 + 0.5 * math.cos(2 * math.pi * u * 2.5))
            return ex * k

        for side in ("L", "R"):
            ch = self._limb_cloth("leg", side, -0.12, H, self.pants_off, extra, n=21, segs=int(16 * e.q),
                                  name=f"suit_leg_{side}", group="body")
            self._rolls("leg", side, ch, H, rt=0.0072, ht=0.0098, segs=max(12, int(18 * e.q)),
                        tsegs=6, gap=0.0)

    def sleeves(self):
        e, k = self.e, self.k
        L = self.L

        def extra(t):
            ex = 0.006 * math.sin(math.pi * clamp(t / 0.62)) + 0.002
            z0 = L - 0.30
            if z0 < t < L - 0.12:
                u = (t - z0) / 0.18
                ex += 0.0034 * math.sin(math.pi * u) * (0.5 + 0.5 * math.cos(2 * math.pi * u * 2.5))
            return ex * k

        for side in ("L", "R"):
            ch = self._limb_cloth("arm", side, -0.04, L, self.off - 0.001, extra, n=18, segs=int(14 * e.q),
                                  name=f"suit_sleeve_{side}", group="arms")
            self._rolls("arm", side, ch, L, rt=0.0060, ht=0.0082, segs=max(12, int(16 * e.q)), tsegs=6, gap=0.0)

    def _rolls(self, kind, side, ch, t_end, *, rt, ht, segs, tsegs, gap):
        """걷어 올린 단 두 겹 (바깥 겹이 조금 더 크다)."""
        e, k, M = self.e, self.k, self.M
        total = ch.total
        group = "arms" if kind == "arm" else "body"
        Lm = self.limb[(kind, side)]

        def fn(buf):
            for j in range(2):
                # 고리 가운데: 단 끝에서 위로 반 겹, 한 겹씩 위로
                tc = t_end - (ht * k * (1.0 + 2.0 * j) * 0.92) / total
                _, tan = ch.at(tc)
                ts = Lm["t"]
                i = min(max(bisect.bisect_right(ts, tc) - 1, 0), len(ts) - 2)
                u = (tc - ts[i]) / max(ts[i + 1] - ts[i], 1e-9)
                rx = lerp(Lm["rx"][i], Lm["rx"][i + 1], u)
                ry = lerp(Lm["ry"][i], Lm["ry"][i + 1], u)
                cc = Lm["c"][i].lerp(Lm["c"][i + 1], u)
                grow = 1.0 + 0.10 * (1 - j)
                _roll(buf, cc, tan, (0, -1, 0), rx - 0.0015 * k, ry - 0.0015 * k, rt * k * grow, ht * k,
                      segs=segs, tsegs=tsegs, mat=M["roll"], w=ch.weights(clamp(tc)), lump=0.16,
                      lumps=4 + j, phase=1.1 * j + self.seed + (0.7 if side == "R" else 0.0))
        e.part(f"suit_roll_{kind}_{side}", group, fn)

    # ------------------------------------------------------------------ collar, front
    def a_of_x(self, z, x):
        """앞판에서 가로 위치 x(m, +X = 캐릭터 왼쪽)가 되는 각도 a (−90~90)."""
        lo, hi = 0.0, 89.0
        ax = abs(x)
        for _ in range(28):
            mid = (lo + hi) / 2
            if self.tsurf(z, mid).x < ax:
                lo = mid
            else:
                hi = mid
        return math.copysign((lo + hi) / 2, x)

    def collar(self):
        e, M, k = self.e, self.M, self.k
        top = self.top
        z_v = top - 0.104 * k                      # V 바닥 (첫 단추 위)

        def vhw(z):                                # V 반폭 (가로 거리, 목둘레에서 0.036)
            return 0.036 * k * clamp((z - z_v) / (top - z_v))
        self.vhw = vhw
        # 흰 티셔츠: V 사이로 보이는 앞판 + 목둘레 립
        rows, cols = 5, 5

        # 행 높이에 몸판 단면 높이를 끼워 넣는다: 어깨 경사가 꺾이는 단면 사이를 현으로 건너뛰면 몸판이 뚫고 나온다
        z0 = top + 0.012 * k                       # 몸판 맨 위 링까지 (링이 앞으로 기울어 앞쪽이 top보다 높다)
        zs = [lerp(z0, z_v, i / (rows - 1)) for i in range(rows)]
        zs += [st["c"][2] for st in self.st_top if z_v + 0.004 * k < st["c"][2] < z0 - 0.004 * k]
        zs = sorted(zs, reverse=True)
        zs = [z for i, z in enumerate(zs) if i == 0 or zs[i - 1] - z > 0.003 * k]

        def tee(buf):
            P, N, W = [], [], []
            for z in zs:
                v = (z0 - z) / (z0 - z_v)
                hw = vhw(z) + 0.006 * k * (1 - v)
                rp, rn, rw = [], [], []
                for j in range(cols):
                    a = self.a_of_x(z, lerp(-hw, hw, j / (cols - 1)))
                    p, n = self.tframe(z, a, 0.0004 * k)
                    rp.append(p)
                    rn.append(n)
                    rw.append(self.twt(p))
                P.append(rp)
                N.append(rn)
                W.append(rw)
            _slab(buf, P, N, 0.0006 * k, M["tee"], W)
            # 목둘레 립 (앞 반쪽만: 뒤는 깃 띠가 덮는다)
            pts, nrm, ups = [], [], []
            for j in range(11):
                a = math.radians(-62 + 124 * j / 10)
                c = V((0.0515 * k * math.sin(a), 0.004 * k - 0.0465 * k * math.cos(a), top + 0.004 * k))
                n = V((math.sin(a), -math.cos(a), 0)).normalized()
                pts.append(c)
                nrm.append(n)
                ups.append(V((0, 0, 1)))
            elf._loop(buf, pts, nrm, ups, 0.011 * k, 0.0028 * k, mat=M["tee"], closed=False,
                      w={"neck": 0.4, "chest": 0.6})
        e.part("suit_tee", "body", tee)

        # 깃 띠: 목 뒤로 도는 열린 띠 (앞 V는 열려 있다)
        def band_(buf):
            pts, nrm, ups = [], [], []
            n_ = 15
            for j in range(n_):
                a = math.radians(36 + (360 - 72) * j / (n_ - 1))
                c = V((0.0525 * k * math.sin(a), 0.004 * k - 0.0475 * k * math.cos(a), top + 0.005 * k))
                n = V((math.sin(a), -math.cos(a), 0)).normalized()
                pts.append(c)
                nrm.append(n)
                ups.append(V((0, 0, 1)))
            elf._loop(buf, pts, nrm, ups, 0.019 * k, 0.0048 * k, mat=M["suit_d"], closed=False,
                      w={"neck": 0.35, "chest": 0.65})
        e.part("suit_collar_band", "body", band_)

        # 접힌 깃 두 장: 안쪽 가장자리는 V를 따라 내려와 끝이 뾰족하고, 바깥은 목 옆에서 어깨 경사로 퍼진다
        z_tip = top - 0.074 * k

        def leaf(buf, s):
            R, C = 5, 5
            P, N, W = [], [], []
            for i in range(R):
                v = i / (R - 1)
                zi = lerp(top + 0.012 * k, z_tip, v)
                ai = self.a_of_x(zi, s * max(vhw(zi) - 0.0025 * k, 0.004 * k))
                ao, zo = s * lerp(88.0, 60.0, v), lerp(top + 0.012 * k, top - 0.048 * k, v)
                rp, rn, rw = [], [], []
                for jj in range(C):
                    u = jj / (C - 1)
                    if s < 0:
                        u = 1 - u      # 법선 쪽에서 봐서 반시계가 되게 열 순서를 뒤집는다
                    a, z = lerp(ai, ao, u), lerp(zi, zo, u)
                    # 깃은 바깥쪽이 살짝 들려 두께감이 있다
                    lift = (0.0024 + 0.0020 * u * (1 - v * 0.5)) * k
                    p, n = self.tframe(z, a, lift)
                    rp.append(p)
                    rn.append(n)
                    rw.append(mixw_neck(self, p))
                P.append(rp)
                N.append(rn)
                W.append(rw)
            _slab(buf, P, N, 0.0034 * k, M["suit"], W)
        e.part("suit_collar_L", "body", lambda b: leaf(b, 1))
        e.part("suit_collar_R", "body", lambda b: leaf(b, -1))

    def front(self):
        """앞 여밈단 + 똑딱단추, V 아래 가장자리 먹선."""
        e, M, k = self.e, self.M, self.k
        top = self.top
        z_v = top - 0.106 * k
        z_end = e.crotch_z + 0.040 * k

        def fn(buf):
            zs = [lerp(z_v, z_end, i / 15) for i in range(16)]
            pts, nrm, ups, ws = [], [], [], []
            for z in zs:
                p, n = self.tframe(z, 0.0, 0.0006 * k)
                pts.append(p)
                nrm.append(n)
                ups.append(V((1, 0, 0)))
                ws.append(self.twt(p))
            elf._loop(buf, pts, nrm, ups, 0.015 * k, 0.0018 * k, mat=M["suit_d"], closed=False,
                      w=lambda t, ws=ws: ws[min(int(round(t * (len(ws) - 1))), len(ws) - 1)])
            snaps = [top - 0.118 * k, lerp(top - 0.112 * k, self.zb + 0.030 * k, 0.5), self.zb + 0.030 * k,
                     self.zb - 0.034 * k]
            if not self.lean:
                snaps.append(lerp(self.zb - 0.034 * k, z_end, 0.55))
            for z in snaps:
                p, n = self.tframe(z, 0.0, 0.0024 * k)
                disc(buf, p, n, (0, 0, 1), 0.0046 * k, 0.0046 * k, 0.0016 * k, segs=8, mat=M["snap"],
                     w=self.twt(p))
        e.part("suit_placket", "body", fn)
        # V 아래쪽 앞 가장자리 (깃 끝에서 V 바닥까지)
        for s in (1, -1):
            zz = [top - 0.072 * k, top - 0.088 * k, top - 0.103 * k]
            self.ink_torso([(z, self.a_of_x(z, s * max(self.vhw(z), 0.001 * k))) for z in zz], 0.0022,
                           self.M["suit_d"], taper=0.6)

    def pocket(self):
        """왼쪽 가슴 주머니 (+ 주머니 단). 반환: 주머니 위 끝 높이."""
        e, M, k = self.e, self.M, self.k
        zc, ac = e.chest_z + 0.020 * k, 33.0
        w, h = 0.050 * k, 0.054 * k
        amap = self._arcmap(zc, ac)

        def grid(x0, x1, y0, y1, R, C, lift):
            P, N, W = [], [], []
            for i in range(R):
                y = lerp(y1, y0, i / (R - 1))
                rp, rn, rw = [], [], []
                for j in range(C):
                    x = lerp(x0, x1, j / (C - 1))
                    # 아래 모서리를 둥글게 깎는다
                    if i == R - 1 and j in (0, C - 1):
                        y = y0 + 0.006 * k
                        x = x0 + 0.004 * k if j == 0 else x1 - 0.004 * k
                    p, n = self.tframe(zc + y, amap(x), lift)
                    rp.append(p)
                    rn.append(n)
                    rw.append(self.twt(p))
                    y = lerp(y1, y0, i / (R - 1))
                P.append(rp)
                N.append(rn)
                W.append(rw)
            return P, N, W

        def fn(buf):
            P, N, W = grid(-w / 2, w / 2, -h / 2, h / 2, 4, 4, 0.0010 * k)
            _slab(buf, P, N, 0.0026 * k, M["suit"], W)
            P, N, W = grid(-w / 2 + 0.0008 * k, w / 2 - 0.0008 * k, h / 2 - 0.009 * k, h / 2 - 0.0005 * k, 2, 4,
                           0.0036 * k)
            _slab(buf, P, N, 0.0010 * k, M["suit_d"], W)
        e.part("suit_pocket", "body", fn)
        self.pocket_top = zc + h / 2
        # 주머니 바느질 (양옆·바닥)
        if not self.lean:
            for x in (-w / 2 + 0.0035 * k, w / 2 - 0.0035 * k):
                self.ink_torso([(zc + h / 2 - 0.010 * k, amap(x)), (zc - h / 2 + 0.006 * k, amap(x))], 0.0010,
                               M["seam"], lift=0.0040, taper=1.0)
        return self.pocket_top

    # ------------------------------------------------------------------ decals
    def _arcmap(self, z, a_c):
        """높이 z에서 가로 거리 x(m, 시청자 기준 오른쪽 +) → 각도 a. 곡면을 따라 잰 호 길이로 감는다."""
        angs = [a_c + (d - 240) * 0.5 for d in range(481)]
        pts = [self.tsurf(z, a) for a in angs]
        s = [0.0]
        for i in range(1, len(pts)):
            s.append(s[-1] + (pts[i] - pts[i - 1]).length)
        s0 = s[240]
        s = [x - s0 for x in s]

        def f(x):
            i = min(max(bisect.bisect_right(s, x) - 1, 0), len(s) - 2)
            u = (x - s[i]) / max(s[i + 1] - s[i], 1e-9)
            return lerp(angs[i], angs[i + 1], u)
        return f

    def text_torso(self, s, height, z_c, a_c, *, mat=None, lift=0.0016, gap=0.11):
        """몸통 천에 스텐실 글자를 감는다 (데칼 노드). height: 글자 높이(m, 기본 체격)."""
        k = self.k
        pts, tris = stencil_text(s, height * k, gap=gap)
        amap = self._arcmap(z_c, a_c)
        buf = self.dec
        idx = []
        for x, y in pts:
            p, n = self.tframe(z_c + y, amap(x), lift * k)
            idx.append(buf.vert(p, self.twt(p)))
        m = mat or self.M["stencil"]
        for t in tris:
            buf.face((idx[t[0]], idx[t[1]], idx[t[2]]), m)

    def ink_torso(self, za, width, mat, *, lift=0.0012, taper=0.25, closed=False, n=None):
        """몸통 먹선: (z, a) 제어점 목록을 부드럽게 이어 천 위에 그린다."""
        k = self.k
        ctrl = [V((a, z, 0)) for z, a in za]
        m = n or max(4, len(za) * 2)
        P = elf.catmull(ctrl, m) if len(ctrl) > 2 else [ctrl[0].lerp(ctrl[-1], i / (m - 1)) for i in range(m)]
        pts, nrm, ws = [], [], []
        for q in P:
            p, nn = self.tframe(q.y, q.x, lift * k)
            pts.append(p)
            nrm.append(nn)
            ws.append(self.twt(p))
        _ink(self.dec, pts, nrm, width * k, mat, ws, closed=closed, taper=taper)

    def ink_limb(self, kind, side, ta, width, mat, *, lift=0.0016, taper=0.25, closed=False, n=None):
        """팔다리 먹선: (t, a) 제어점. 팔은 arms 데칼 노드에 들어간다."""
        k = self.k
        ctrl = [V((a, t, 0)) for t, a in ta]
        m = n or max(4, len(ta) * 2)
        if closed:
            P = ctrl
        else:
            P = elf.catmull(ctrl, m) if len(ctrl) > 2 else [ctrl[0].lerp(ctrl[-1], i / (m - 1)) for i in range(m)]
        pts, nrm, ws = [], [], []
        for q in P:
            p, nn, w = self.lsurf(kind, side, q.y, q.x, lift * k)
            pts.append(p)
            nrm.append(nn)
            ws.append(w)
        _ink(self.dec_arms if kind == "arm" else self.dec, pts, nrm, width * k, mat, ws, closed=closed,
             taper=taper)

    def stencils(self):
        e, k = self.e, self.k
        cz = e.chest_z
        num = f"{self.prefix}{self.number}"
        # 등: 큰 P.O.W. + 수용 번호
        self.text_torso(self.back_text, 0.052, cz + 0.026 * k, 180.0)
        self.text_torso(num, 0.022, cz - 0.026 * k, 180.0, gap=0.10)
        # 가슴: 오른쪽 P.O.W., 왼쪽 주머니 위 번호
        if not self.lean:
            self.text_torso(self.back_text, 0.019, cz + 0.030 * k, -33.0)
        self.text_torso(num, 0.0125, self.pocket_top + 0.012 * k, 33.0, gap=0.10)

    def seams_and_folds(self):
        e, M, k = self.e, self.M, self.k
        cz, sz, top, zb = e.chest_z, e.shoulder_z, self.top, self.zb
        seam, fold = M["seam"], M["fold"]
        lean = self.lean
        # 등 요크 솔기
        self.ink_torso([(sz - 0.012 * k, 112), (sz - 0.020 * k, 150), (sz - 0.024 * k, 180), (sz - 0.020 * k, 210),
                        (sz - 0.012 * k, 248)], 0.0013, seam, taper=0.8)
        # 옆구리 솔기 (몸판)
        for s in (1, -1):
            self.ink_torso([(sz - 0.040 * k, s * 92), (zb + 0.016 * k, s * 90)], 0.0013, seam, taper=0.8)
        # 고무 허리 주름: 띠 위(블라우징)와 아래로 짧은 세로 먹선
        rnd = [(0.7 + 0.3 * math.sin(i * 2.3 + self.seed)) for i in range(32)]
        step = 30 if lean else 20
        for i, a in enumerate(range(-170, 181, step)):
            if abs(a) < 12:
                continue
            L = 0.016 + 0.012 * rnd[i % 32]
            tilt = 5.0 * math.sin(i * 1.7)
            self.ink_torso([(zb + 0.0115 * k, a), (zb + (0.0115 + L) * k, a + tilt)], 0.0026, fold, taper=0.10)
            if i % 2 == 0:
                self.ink_torso([(zb - 0.0115 * k, a + 6), (zb - (0.0115 + L * 0.6) * k, a + 6 - tilt * 0.5)], 0.0022,
                               fold, taper=0.10)
        # 겨드랑이 주름 (앞)
        for s in (1, -1):
            self.ink_torso([(sz - 0.030 * k, s * 74), (sz - 0.050 * k, s * 64), (sz - 0.068 * k, s * 54)], 0.0020,
                           fold, taper=0.15)
            if not lean:
                self.ink_torso([(sz - 0.052 * k, s * 80), (sz - 0.072 * k, s * 70), (sz - 0.086 * k, s * 62)], 0.0017,
                               fold, taper=0.15)
        # ---- 바지
        for side, s in (("L", 1), ("R", -1)):
            H = self.hem
            # 바깥 옆 솔기
            self.ink_limb("leg", side, [(0.02, s * 90), (0.35, s * 90), (H - 0.16, s * 90)], 0.0013, seam,
                          taper=0.9)
            # 가랑이에서 허벅지 앞으로 퍼지는 주름
            self.ink_limb("leg", side, [(0.02, -s * 48), (0.10, -s * 28), (0.20, -s * 10)], 0.0021, fold)
            if not lean:
                self.ink_limb("leg", side, [(0.10, -s * 62), (0.17, -s * 46), (0.26, -s * 32)], 0.0018, fold)
            # 무릎 뒤
            self.ink_limb("leg", side, [(0.50, 150), (0.54, 180), (0.50, 210)], 0.0020, fold)
            if not lean:
                self.ink_limb("leg", side, [(0.56, 160), (0.585, 180), (0.56, 200)], 0.0016, fold)
            # 무릎 앞 가로 주름
            self.ink_limb("leg", side, [(0.46, -s * 28), (0.475, -s * 4), (0.465, s * 20)], 0.0017, fold)
            # 단 위 뭉침 (앞과 옆)
            for j, tt in enumerate((H - 0.25, H - 0.19)):
                for a0 in ((-60, 60) if lean else (-70, 40, 150)):
                    self.ink_limb("leg", side, [(tt, a0), (tt + 0.012, a0 + 22), (tt - 0.006, a0 + 44)], 0.0018, fold)
        # ---- 소매
        for side, s in (("L", 1), ("R", -1)):
            L = self.L
            # 처진 어깨 솔기 (위팔에 걸친 고리)
            ring = [(0.15 - 0.02 * math.cos(math.radians(a)), a) for a in range(0, 360, 30)]
            self.ink_limb("arm", side, ring, 0.0013, seam, closed=True)
            # 팔꿈치 안쪽 주름 (앞)
            self.ink_limb("arm", side, [(0.47, -32), (0.515, 0), (0.47, 32)], 0.0020, fold)
            if not lean:
                self.ink_limb("arm", side, [(0.40, -22), (0.43, 0), (0.40, 22)], 0.0016, fold)
            # 단 위 뭉침
            for tt in ((L - 0.24,) if lean else (L - 0.25, L - 0.19)):
                for a0 in (-80, 60, 180):
                    self.ink_limb("arm", side, [(tt, a0), (tt + 0.012, a0 + 24), (tt - 0.006, a0 + 48)], 0.0017, fold)

    # ------------------------------------------------------------------ build
    def build(self):
        self.torso()
        self.legs()
        self.sleeves()
        self.collar()
        self.front()
        self.pocket()
        self.stencils()
        self.seams_and_folds()
        e = self.e
        if self.dec.f:
            e.add(self.dec.obj(f"{e.name}_suit_decal", angle=180.0), group="body", tag="decal", node="decal",
                  props={"noOutline": 1})
        if self.dec_arms.f:
            e.add(self.dec_arms.obj(f"{e.name}_suit_decal_arms", angle=180.0), group="arms", tag="decal_arms",
                  node="decal_arms", props={"noOutline": 1})
        return self


def mixw_neck(js, p):
    """깃: 목 가까운 위쪽은 neck을 조금 섞는다."""
    w = js.twt(p)
    a = smoothstep(js.top - 0.03 * js.k, js.top, p.z) * 0.35
    return elf.mixw(w, {"neck": 1.0}, a) if a > 0 else w


def socks(e, M, side, t0, t1):
    """흰 양말 (걷은 바짓단 아래로 보인다)."""
    k = e.k
    e.cover[f"leg_{side}"].append((t0, t1))
    ch = e.leg_chain(side)
    buf = Buf()
    e._limb_loft(buf, ch, e.leg_r, t0, t1, M["sock"], segs=int(14 * e.q), cap0=None, cap1=None, off=0.0055 * k,
                 extra=lambda t: 0.0012 * k * math.sin((t - t0) * 90) ** 2)
    e.add(buf.obj(f"{e.name}_sock_{side}", angle=60.0), group="body", tag="sock")


def shoes(e, M, *, top=0.915):
    """남색 캔버스 슬립온: 흰 고무 밑창, 발목 고무 테두리."""
    k = e.k
    e.boots(M["shoe"], top=top, sole=(M["sole"], 0.019), toe=0.004, off=0.010, cuff=M["shoe_d"])


def outfit(e, M, *, number="0000", sock_top=None, shoe_top=0.915, **kw):
    """점프슈트 + 흰 양말 + 슬립온 한 벌. 반환: Jumpsuit."""
    js = Jumpsuit(e, M, number=number, **kw).build()
    for side in ("L", "R"):
        socks(e, M, side, js.hem - 0.06 if sock_top is None else sock_top, shoe_top + 0.05)
    shoes(e, M, top=shoe_top)
    return js
