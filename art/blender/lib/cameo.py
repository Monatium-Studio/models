"""원작 카메오 공용 헬퍼 (cameo).

캐시·칸나·엘레나·흑뉴아 모델이 같이 쓰는 도구다. 엘프 키트(elf.py)는 읽기 전용이라 키트에 없는 기능을 여기에 둔다.
근거와 인물별 사용처는 docs/art/characters-cameo.md. [키트 후보] 표시는 키트로 올릴 만한 기능이다.

    import cameo
    cameo.face_expr(e, "smirk", L={...}, R={...}, corner=(0.004, -0.001))   # 비대칭 표정 + blink 교정 키
    s = cameo.Shell(e, coat, z_top, z_hem, gap=14, skirt=True)                # 몸에서 떨어지는 천 (코트·치마)
    s.edge_trim(gold, 0.008); s.done("coat")
    t = cameo.Tail(e, h, "hair_tail", ctrl, width=0.15, thick=0.11)          # 포니테일·트윈테일 (헤어 v2)
    b = cameo.Braid(e, "hair_braid_L", ctrl, w0=0.07, w1=0.045); b.done()     # 연속 볼륨 땋은 머리
    cameo.shade_braids(cameo.hair_obj(e), [t, b], base_hex, stops)            # finalize 뒤 끝 색 그라데이션

헤어 v2 (2026-11-01): 키트 h.bangs/sides/back은 사양만 기록하고 h.done()에서 기하를 만든다. 영역 색은 키트의
mat= 인자로 주고, 브릿지 같은 한 다발은 h.strand(..., mat=)로 만든다. 꼬리·땋은 머리는 <이름>_hair 노드에 합친다
(라인 0.0035). 환경 변수 CAMEO_SPLIT=1이면 꼬리·땋은 머리를 <이름>_tails 노드로 따로 남긴다(근접 스크린샷용,
--focus <이름>_tails). 커밋하는 모델은 합친 상태로 내보낸다.
"""
from __future__ import annotations

import math
import os

import elf
from elf import V, Matrix, Buf, loft, band, rbox, disc, keys, lerp, smoothstep, mixw, clamp, frame, catmull

# =========================================================================== 얼굴: 비대칭 표정

def face_expr(e, name, *, both=None, L=None, R=None, M=None, corner=(0.0, 0.0), mouth_dx=0.0, blink_fix=True):
    """비대칭 표정 셰이프 키를 얼굴에 더한다 (윙크, 한쪽 입꼬리 웃음, 한쪽 눈썹 치켜뜨기). [키트 후보]

    키트 표정 사전은 좌우 대칭이라 같은 Face로 '왼쪽용', '오른쪽용', '입용' 얼굴을 따로 계산한 뒤
    정점을 기본 얼굴의 x 위치로 골라 합친다 (정점 수와 순서가 같으므로 셰이프 키가 된다).
      both: 양쪽 공통 덮어쓰기, L: 캐릭터 왼쪽(+X) 눈·눈썹·볼, R: 오른쪽(-X), M: 입 (없으면 both)
      corner=(왼쪽, 오른쪽): 입꼬리를 위로(+) 올리는 양(m). mouth_dx: 입 전체를 옆으로 미는 양(m).
    키트 규칙과 같게 blink 교정 키 'blink_<이름>'도 만든다(blink × 이 표정, ELF_KIT.md 6장).
    눈을 감는(close ≥ 1) 쪽이 있는 표정은 교정 키를 만들지 않는다."""
    f = e.face_builder
    ob = e.face_obj
    base = f.base

    def P(*ovs):
        p = base
        for o in ovs:
            if o:
                p = elf._merge_expr(p, o)
        return p

    neutral = f._build(base).v
    th = f.ex * 0.45
    ez = f.ez

    def comp(extra=None):
        bl = f._build(P(both, L, extra)).v
        br = f._build(P(both, R, extra)).v
        bm = f._build(P(both, M, extra)).v
        mq = P(both, M)["mouth"]
        mw = mq["w"] * f.sz / 2
        out = []
        for i, q in enumerate(neutral):
            if q.x > th:
                c = bl[i].copy()
            elif q.x < -th:
                c = br[i].copy()
            else:
                c = bm[i].copy()
                if q.z < ez - 0.03 * e.k and (corner != (0.0, 0.0) or mouth_dx):   # 입
                    x = c.x
                    y0 = e.face_project(c.x, c.z)[0].y
                    c.z += corner[0] * smoothstep(-0.2 * mw, mw, x) + corner[1] * smoothstep(0.2 * mw, -mw, x)
                    c.x += mouth_dx
                    # 얼굴 곡면을 따라 앞뒤 위치를 다시 맞춘다 (위로 올린 입꼬리가 볼 속으로 묻히지 않게. cameo2와 같음)
                    c.y += e.face_project(c.x, c.z)[0].y - y0
            out.append(c)
        return out

    co = comp()
    _add_key(ob, name, co)
    closes = [((o or {}).get("eye", {}).get("close", 0.0)) for o in (both, L, R)]
    if blink_fix and max(closes) < 1.0 and ob.data.shape_keys and "blink" in ob.data.shape_keys.key_blocks:
        vb = [v.co.copy() for v in ob.data.shape_keys.key_blocks["blink"].data]
        comb = comp({"eye": {"close": 1.0}})
        _add_key(ob, f"blink_{name}", [c - x - b + o * 2 for c, x, b, o in zip(comb, co, vb, neutral)])
    return name


def _add_key(ob, name, co_list):
    assert len(co_list) == len(ob.data.vertices), f"표정 {name}: 정점 수 불일치"
    key = ob.shape_key_add(name=name, from_mix=False)
    for i, c in enumerate(co_list):
        key.data[i].co = c
    key.value = 0.0
    return key


# =========================================================================== 머리카락 색

def _centroid(buf, fi):
    idx = buf.f[fi]
    return sum((buf.v[i] for i in idx), V()) / len(idx)


def recolor(h, f0, f1=None, mat=None, pred=None):
    """[v1 호환, 쓰지 않음] 머리카락 버퍼의 면 [f0, f1) 중 pred(중심점)이 참인 면을 mat으로 칠한다.
    헤어 v2에서는 bangs/sides/back이 h.done()에서 만들어지므로 호출 직후의 면 범위가 비어 있다(효과 없음).
    영역 색은 h.bangs(mat=)/sides(mat=)/back(mat=), 한 다발은 h.strand(..., mat=)로 준다."""
    buf = h.buf
    f1 = len(buf.f) if f1 is None else f1
    mi = buf.mi(mat)
    for i in range(f0, f1):
        if pred is None or pred(_centroid(buf, i)):
            buf.fm[i] = mi


def gradient(h, stops, f0=0, f1=None, pred=None, axis=2):
    """[v1 호환, 쓰지 않음] 머리카락 끝으로 갈수록 색이 바뀌는 띠 (면 단위 계단).
    헤어 v2에서는 recolor와 같은 이유로 셸에는 효과가 없다. 꼬리·땋은 머리는 shade_braids(정점색)를 쓴다.
    stops: [(z, mat), ...] 높은 z부터. 면 중심이 z보다 낮으면 그 재질 (더 낮은 띠가 덮어쓴다).
    정점색 병합(merge=True)과 맞도록 면 단위로 칠한다."""
    buf = h.buf
    f1 = len(buf.f) if f1 is None else f1
    mis = [(z, buf.mi(m)) for z, m in stops]
    for i in range(f0, f1):
        c = _centroid(buf, i)
        if pred is not None and not pred(c):
            continue
        for z, mi in mis:
            if c[axis] < z:
                buf.fm[i] = mi


def tail_chain(e, prefix, pts, parent="head"):
    """머리 꼬리(땋은 머리, 트윈테일)용 본 2개를 경로 pts(3점)에 만든다 → Chain(웨이트 계산용). [키트 후보]"""
    p0, p1, p2 = (V(p) for p in pts)
    e.add_bone(f"{prefix}_01", p0, p1, parent)
    e.add_bone(f"{prefix}_02", p1, p2, f"{prefix}_01")
    return elf.Chain([p0, p1, p2], [f"{prefix}_01", f"{prefix}_02"], start={parent: 1.0})


def chain_w(chain, pts):
    """경로 위 점의 웨이트를 chain에서 가장 가까운 t로 구하는 함수 (strand w=에 쓴다)."""
    ts = [i / 40 for i in range(41)]
    cps = [chain.at(t)[0] for t in ts]

    def fn(t, pts=pts):
        q = catmull(pts, 41)[min(int(t * 40), 40)]
        best = min(range(41), key=lambda i: (cps[i] - q).length)
        return chain.weights(ts[best])
    return fn


# =========================================================================== 몸에서 떨어지는 천 (셸)

def ring_pt(rx, ry, cy, z, a_deg, p=2.3):
    """몸통 단면(초타원) 위 점과 바깥 법선. a: 0=앞(-Y), 90=왼쪽(+X), 180=뒤."""
    a = math.radians(a_deg)
    dx, dy = math.sin(a), -math.cos(a)
    ee = 2.0 / p
    x = math.copysign(abs(dx) ** ee, dx) * rx
    y = math.copysign(abs(dy) ** ee, dy) * ry + cy
    n = V((x / (rx * rx), (y - cy) / (ry * ry), 0.0))
    n = n.normalized() if n.length > 1e-9 else V((dx, dy, 0))
    return V((x, y, z)), n


def bust_off(e, z, a_deg, off_m):
    """키트 가슴 볼륨(Elf.bust)이 이 높이·방위·옷 층에서 더하는 바깥 두께(m). 키트에 없거나 0이면 0."""
    fn = getattr(e, "bust_off", None)
    return fn(z, a_deg, off_m) if fn is not None else 0.0


def bust_normal(e, z, a_deg, off_m, p, rx, ry, cy, n):
    """가슴 볼륨이 있는 곳의 셸 바깥 법선 (유한 차분). 볼륨이 없으면 n 그대로."""
    if bust_off(e, z, a_deg, off_m) <= 1e-7:
        return n

    def S(zz, aa):
        q, nn = ring_pt(rx, ry, cy, zz, aa, p)
        return q + nn * bust_off(e, zz, aa, off_m)
    dz = 0.003 * e.k
    n2 = (S(z, a_deg + 1.5) - S(z, a_deg - 1.5)).cross(S(z + dz, a_deg) - S(z - dz, a_deg))
    if n2.length < 1e-12:
        return n
    return (n2 if n2.dot(n) >= 0 else -n2).normalized()


def section(e, z, skirt=False):
    """높이 z의 몸통 단면 (rx, ry, cy). skirt=True면 엉덩이 아래로는 가장 넓은 골반과 다리 바깥을 감싼다
    (허리에서 엉덩이까지 부드럽게 넓어진다)."""
    rx, ry, cy = e.torso_at(z)
    if skirt:
        zw = e.crotch_z + 0.17 * (e.torso_top - e.crotch_z)
        a = smoothstep(zw + 0.10 * e.k, zw - 0.02 * e.k, z)
        if a > 0:
            hx, hy, hc = e.torso_at(min(z, zw) if z > zw else zw)
            tx = max(hx, 0.158 * e.k * e.hp)
            ty = max(hy, ry)
            rx = max(rx, lerp(rx, tx, a))
            ry = max(ry, lerp(ry, ty, a))
            cy = lerp(cy, hc, a)
    return rx, ry, cy


def skirt_w(e, p):
    """치마·코트 자락 웨이트: 골반 위는 몸통 규칙, 아래로 갈수록 좌우 허벅지를 반쯤 따라간다."""
    if p.z >= e.hipj_z:
        return e._torso_wfn(p, 0)
    a = smoothstep(e.hipj_z, e.knee_z, p.z)
    s = clamp(p.x / (0.12 * e.k), -1.0, 1.0)
    wl = 0.5 + 0.5 * s
    leg = {k: v for k, v in (("thigh_L", wl), ("thigh_R", 1 - wl)) if v > 1e-4}
    return mixw({"hips": 1.0}, leg, a * 0.65)


class Shell:
    """몸통을 감싸는 두께 있는 천 (앞이 열린 재킷·가운, 치마, 코트 자락, 어깨 없는 상의). [키트 후보]

    z_top → z_hem (z_top > z_hem). gap: 앞트임 반각(도) 또는 [(u, 도)] 표 (u=0 위, 1 밑단). 0이면 닫힌 고리.
    off: 몸 표면에서 띄우는 거리(m, e.k 곱함). flare: [(u, 추가 반경 m)]. th: 천 두께(m).
    skirt=True면 엉덩이 아래를 다리 바깥까지 감싸고(section) 웨이트를 허벅지와 섞는다(skirt_w).
    cover=True면 덮은 구간의 맨살을 만들지 않는다 (닫힌 셸만).
    ruffle=(진폭 m, 물결 수, 시작 u): 밑단 쪽 반경을 물결치게 해 프릴·주름을 낸다.
    drop=[(u, m)]: 뒤쪽 자락을 더 내린다 (코트 뒤트임 없이 뒤가 긴 실루엣).
    만든 뒤 edge_trim / hem_trim / top_trim / lapel로 테두리를 더하고 done()으로 등록한다."""

    def __init__(self, e, mat, z_top, z_hem, *, gap=0.0, off=0.012, flare=None, th=0.005, rows=None, cols=None,
                 skirt=False, p=2.3, cover=False, wfn=None, drop=None, ruffle=None):
        self.e = e
        self.mat = mat
        k = e.k
        self.buf = Buf()
        self.closed = (gap == 0 or gap is None)
        self.prm = dict(z_top=z_top, z_hem=z_hem, off=off, flare=flare, skirt=skirt, p=p, drop=drop, ruffle=ruffle)
        rows = rows or max(4, int(abs(z_top - z_hem) / (0.026 * k)) + 2)
        cols = cols or max(12, int(26 * e.q))
        self.rows, self.cols = rows, cols
        gfn = (lambda u: keys(gap, u)) if isinstance(gap, (list, tuple)) else (lambda u: gap or 0.0)
        wfn = wfn or ((lambda q: skirt_w(e, q)) if skirt else (lambda q: e._torso_wfn(q, 0)))
        self.P, self.N, self.W = [], [], []
        for i in range(rows):
            u = i / (rows - 1)
            z = lerp(z_top, z_hem, u)
            rx, ry, cy = section(e, z, skirt)
            fl = keys(flare, u) if flare else 0.0
            dz = keys(drop, u) if drop else 0.0
            g = gfn(u)
            rowP, rowN, rowW = [], [], []
            for j in range(cols):
                if self.closed:
                    a = 360.0 * j / cols
                else:
                    a = g + (360.0 - 2 * g) * j / (cols - 1)
                rf = 0.0
                if ruffle:
                    amp, nw, u0 = ruffle
                    rf = amp * smoothstep(u0, 1.0, u) * math.cos(math.radians(a) * nw)
                q, n = ring_pt(rx + (off + fl + rf) * k, ry + (off + fl + rf) * k, cy, z, a, p)
                bo = bust_off(e, z, a, (off + fl) * k)
                if bo > 0.0:
                    q = q + n * bo
                if dz:
                    q.z -= dz * k * (0.5 - 0.5 * math.cos(math.radians(a)))   # 뒤가 더 내려옴 (dz>0)
                rowP.append(q)
                rowN.append(n)
                rowW.append(wfn(q))
            self.P.append(rowP)
            self.N.append(rowN)
            self.W.append(rowW)
        self._build(th * k)
        if cover and self.closed:
            e.cover["torso"].append((z_hem, z_top))

    def _build(self, th):
        b, P, N, W = self.buf, self.P, self.N, self.W
        R, C = self.rows, self.cols
        m = self.mat
        o = [[b.vert(P[i][j], W[i][j]) for j in range(C)] for i in range(R)]
        n = [[b.vert(P[i][j] - N[i][j] * th, W[i][j]) for j in range(C)] for i in range(R)]
        jr = range(C) if self.closed else range(C - 1)
        for i in range(R - 1):
            for j in jr:
                j2 = (j + 1) % C
                b.face((o[i][j], o[i + 1][j], o[i + 1][j2], o[i][j2]), m)
                b.face((n[i][j], n[i][j2], n[i + 1][j2], n[i + 1][j]), m)
        for j in jr:
            j2 = (j + 1) % C
            b.face((o[0][j], o[0][j2], n[0][j2], n[0][j]), m)                # 윗단
            b.face((o[R - 1][j], n[R - 1][j], n[R - 1][j2], o[R - 1][j2]), m)  # 밑단
        if not self.closed:
            for i in range(R - 1):
                b.face((o[i][0], n[i][0], n[i + 1][0], o[i + 1][0]), m)
                jl = C - 1
                b.face((o[i][jl], o[i + 1][jl], n[i + 1][jl], n[i][jl]), m)

    def surface(self, u, a_deg, lift=0.0):
        """셸 바깥면 위의 점과 법선 (u: 0=윗단, 1=밑단, a: 0=앞, 90=왼쪽). 주머니·명찰을 옷 위에 붙일 때 쓴다."""
        e, q = self.e, self.prm
        k = e.k
        z = lerp(q["z_top"], q["z_hem"], u)
        rx, ry, cy = section(e, z, q["skirt"])
        fl = keys(q["flare"], u) if q["flare"] else 0.0
        r2x, r2y, om = rx + (q["off"] + fl) * k, ry + (q["off"] + fl) * k, (q["off"] + fl) * k
        pt, n = ring_pt(r2x, r2y, cy, z, a_deg, q["p"])
        bo = bust_off(e, z, a_deg, om)
        if bo > 0.0:
            pt = pt + n * bo
            n = bust_normal(e, z, a_deg, om, q["p"], r2x, r2y, cy, n)
        return pt + n * lift, n

    def frame_at(self, u, a_deg, lift=0.0):
        """surface 위치의 배치 행렬 (로컬 -Y=바깥, +Z=위)."""
        pt, n = self.surface(u, a_deg, lift)
        return Matrix.Translation(pt) @ frame(n, (0, 0, 1))

    # ---- 테두리
    def _strip(self, pts, nrm, ups, width, th, mat, ws, lift=0.0):
        k = self.e.k
        c = [p + nn * (lift * k) for p, nn in zip(pts, nrm)]
        elf._loop(self.buf, c, nrm, ups, width * k, th * k, mat=mat, closed=False,
                  w=lambda t, ws=ws: ws[min(int(round(t * (len(ws) - 1))), len(ws) - 1)])

    def edge_trim(self, mat, width=0.008, th=0.0025, i0=0, i1=None, lift=0.0004, width_fn=None):
        """앞트임 양쪽 가장자리 띠 (금색 테두리, 가운 여밈단). width_fn(u)로 위아래 폭을 바꿀 수 있다."""
        if self.closed:
            return self
        i1 = self.rows if i1 is None else i1
        for jj, jn in ((0, 1), (self.cols - 1, self.cols - 2)):
            pts, nrm, ups, ws = [], [], [], []
            for i in range(i0, i1):
                u = i / (self.rows - 1)
                wd = width * (width_fn(u) if width_fn else 1.0)
                d = (self.P[i][jn] - self.P[i][jj]).normalized()
                pts.append(self.P[i][jj] + d * (wd * self.e.k * 0.45))
                nrm.append(self.N[i][jj])
                ups.append(d)
                ws.append(self.W[i][jj])
            # 폭을 점마다 바꾸려면 _loop가 상수 폭이라 나눠서 만든다
            if width_fn:
                for a in range(len(pts) - 1):
                    u = (i0 + a) / (self.rows - 1)
                    wd = width * width_fn(u)
                    if wd < 1e-4:
                        continue
                    self._strip(pts[a:a + 2], nrm[a:a + 2], ups[a:a + 2], wd, th, mat, ws[a:a + 2], lift)
            else:
                self._strip(pts, nrm, ups, width, th, mat, ws, lift)
        return self

    def hem_trim(self, mat, width=0.008, th=0.0025, lift=0.0004, row=None):
        """밑단 띠."""
        i = self.rows - 1 if row is None else row
        return self._row_trim(i, i - 1, mat, width, th, lift)

    def top_trim(self, mat, width=0.008, th=0.0025, lift=0.0004):
        """윗단 띠 (어깨 없는 상의의 가슴선)."""
        return self._row_trim(0, 1, mat, width, th, lift)

    def _row_trim(self, i, ia, mat, width, th, lift):
        C = self.cols
        idx = list(range(C)) + ([0] if self.closed else [])
        pts, nrm, ups, ws = [], [], [], []
        for j in idx:
            d = (self.P[ia][j] - self.P[i][j]).normalized()
            pts.append(self.P[i][j] + d * (width * self.e.k * 0.45))
            nrm.append(self.N[i][j])
            ups.append(d)
            ws.append(self.W[i][j])
        self._strip(pts, nrm, ups, width, th, mat, ws, lift)
        return self

    def done(self, name, group="body"):
        ob = self.buf.obj(f"{self.e.name}_{name}", angle=50.0)
        return self.e.add(ob, group=group, tag=name)


# =========================================================================== 긴 생머리 (등을 덮는 뒷머리)

def long_back_hair(e, h, *, z_end, n=9, width=0.075, thick=0.026, x=(0.15, 0.19, 0.18, 0.17, 0.19),
                   y_c=(0.13, 0.14, 0.14, 0.15, 0.18), y_s=(0.10, 0.10, 0.10, 0.10, 0.11), spread=92.0,
                   bones=3, mat=None, prefix="hair_back"):
    """[v1, 쓰지 않음] 허리 아래까지 늘어지는 긴 뒷머리 커튼. 헤어 v2의 키트 h.back(length=)이 긴 머리 모드
    (hair_back 흔들림 본, 팔 뒤로 도는 drift)를 갖춰 엘레나도 키트로 옮겼다. 다른 스크립트 호환용으로만 남긴다.
    (v1 설명) 키트 h.back()은 머리 본 100%로 뒤통수에서 수직으로 떨어져 긴 머리면 어깨·팔을 뚫는다. 여기서는 뭉치마다
    뒤통수 → 목덜미 → 어깨 뒤 → 등 → 끝 경로를 몸 단면 바깥으로 잡고, 가장자리 뭉치는 팔 뒤(y_s)로 돌린다.
    웨이트는 뿌리 쪽 head, 아래쪽은 chest에 붙은 본 사슬(prefix_01..)로 섞어 고개를 돌려도 등에서 떨어지지 않는다.
    x, y_c(가운데 뭉치), y_s(가장자리 뭉치)는 목·어깨·가슴·허리·끝 다섯 높이의 값(m, e.k 곱함)."""
    k = e.k
    zs = [e.torso_top + 0.035 * k, e.shoulder_z - 0.05 * k, e.chest_z - 0.04 * k, e.waist_z - 0.05 * k, z_end]
    jz = [lerp(zs[0], zs[-1], i / bones) for i in range(bones + 1)]
    ch = bone_chain(e, prefix, [V((0, lerp(y_c[0], y_c[-1], i / bones) * k, z)) for i, z in enumerate(jz)],
                    parent="chest")
    span = zs[0] - zs[-1]
    for i in range(n):
        u = (i / (n - 1)) * 2 - 1 if n > 1 else 0.0
        az = 180 + u * spread
        root = h.sp(180 + u * spread * 0.4, 62, h.off * 0.3)
        p1 = h.sp(az, 18, h.off * 1.25)
        p2 = h.sp(az * 0.98 + 180 * 0.02, -30, h.off * 1.45)
        a = abs(u) ** 1.5
        body = [V((u * x[j] * k, lerp(y_c[j], y_s[j], a) * k, zs[j])) for j in range(5)]
        ln = 1.0 - 0.10 * (i % 2) - 0.06 * abs(u)
        body[-1] = body[-2].lerp(body[-1], ln)
        pts = [root, p1, p2] + body
        z0 = p2.z

        def wfn(t, pts=pts):
            q = catmull(pts, 41)[min(int(t * 40), 40)]
            tt = clamp((zs[0] - q.z) / span)
            hb = smoothstep(z0 + 0.02 * k, zs[0] - 0.06 * k, q.z)
            return mixw(ch.weights(tt), {"head": 1.0}, hb)
        h.strand(pts, width * k * (1 - 0.15 * abs(u)), thick * k, n=16, segs=8, w=wfn, mat=mat,
                 taper=[(0, 0.6), (0.15, 1.0), (0.85, 0.85), (1, 0.0)])
    return ch


# =========================================================================== 둥근 상자 (키트 rbox 보정판)

def rrbox(buf, size, M, *, mat=None, w=None, r=0.25, segs=1, taper=0.0):
    """둥근 상자. 키트 elf.rbox와 같은 인자다.
    키트 rbox는 위아래 링 순서가 뒤집혀 있어 옆면이 가장 좁은 반경(sx-rr)에 놓이고, 둥근 모서리가 테두리처럼
    밖으로 접힌다(r이 0.4 이상이면 납작한 실패처럼 보인다). 여기서는 바닥(작은 링) → 옆면(큰 링) → 윗면 순서로 만든다.
    [키트 버그 보고: elf.rbox의 zs 순서]"""
    sx, sy, sz = (s / 2 for s in size)
    rr = min(sx, sy, sz) * 2 * clamp(r, 0.02, 0.5)
    rr = min(rr, sx, sy, sz)
    p = 2 + 8 * (1 - clamp(r * 2))
    n = 4 * (segs + 1)
    m = max(segs, 1)
    prof = []   # (z, 모서리 각 θ: 0=옆면 최대 반경, π/2=윗·아랫면)
    for j in range(m, -1, -1):
        th = j / m * (math.pi / 2)
        prof.append((-(sz - rr) - rr * math.sin(th), th))
    for j in range(0, m + 1):
        th = j / m * (math.pi / 2)
        prof.append(((sz - rr) + rr * math.sin(th), th))
    rings = []
    for z, th in prof:
        tz = 1 - taper * ((z + sz) / (2 * sz))
        rx = max((sx - rr) * tz + rr * math.cos(th), 1e-5)
        ry = max((sy - rr) * tz + rr * math.cos(th), 1e-5)
        pts = elf.ring_pts(V((0, 0, z)), V((1, 0, 0)), V((0, 1, 0)), rx, ry, n, p=p, rot=math.pi / n)
        rings.append([buf.vert(M @ q, w) for q in pts])
    for a in range(len(rings) - 1):
        r0, r1 = rings[a], rings[a + 1]
        for kk in range(n):
            k2 = (kk + 1) % n
            buf.face((r0[kk], r0[k2], r1[k2], r1[kk]), mat)
    for end, rg in ((0, rings[0]), (1, rings[-1])):
        ctr = sum((buf.v[i] for i in rg), V()) / len(rg)
        c = buf.vert(ctr, w)
        for kk in range(n):
            k2 = (kk + 1) % n
            buf.face((c, rg[k2], rg[kk]) if end == 0 else (c, rg[kk], rg[k2]), mat)


# =========================================================================== 팔다리 덧옷

def leg_tube(e, mat, side, t0, t1, *, off=0.012, extra=None, name=None, cap0=None, cap1=None, segs=None):
    """다리에 감기는 관 (헐렁한 양말, 각반, 사이하이 부츠 윗단). t: 다리 길이 비율(0=고관절, 1=발목).
    extra(t) → 추가 반경(m, e.k 곱함). 덮은 구간의 맨살은 만들지 않는다."""
    k = e.k
    e.cover[f"leg_{side}"].append((t0, t1))
    ch = e.leg_chain(side)
    buf = Buf()
    ex = (lambda t: extra(t) * k) if extra else None
    rings = e._limb_loft(buf, ch, e.leg_r, t0, t1, mat, segs=segs or int(16 * e.q), cap0=cap0, cap1=cap1,
                         off=off * k, extra=ex)
    ob = buf.obj(name or f"{e.name}_legtube_{side}{len(e.parts)}", angle=50.0)
    e.add(ob, group="body", tag=name or "legtube")
    return rings


def arm_tube(e, mat, side, t0, t1, *, off=0.012, extra=None, name=None, cap0=None, cap1=None, segs=None):
    """팔에 감기는 관 (긴 장갑, 토시, 건틀릿 바탕). t: 팔 길이 비율(0=어깨, 1=손목)."""
    k = e.k
    e.cover[f"arm_{side}"].append((t0, t1))
    ch = e.arm_chain(side)
    buf = Buf()
    ex = (lambda t: extra(t) * k) if extra else None
    e._limb_loft(buf, ch, e.arm_r, t0, t1, mat, segs=segs or int(14 * e.q), cap0=cap0, cap1=cap1, off=off * k,
                 extra=ex)
    ob = buf.obj(name or f"{e.name}_armtube_{side}{len(e.parts)}", angle=50.0)
    e.add(ob, group="arms", tag=name or "armtube")


def ellipsoid(buf, c, A, B, F, ra, rb, rf, *, segs=8, rings=5, mat=None, wfn=None):
    """타원체. A=긴 축(반경 ra), B·F=단면 축(rb, rf). (B, F, A)는 오른손 좌표계여야 한다 (B = F × A).
    wfn(점) → 웨이트 사전."""
    wf = wfn or (lambda q: {})
    c = V(c)
    ringv = []
    for i in range(1, rings - 1):
        ph = -math.pi / 2 + math.pi * i / (rings - 1)
        row = []
        for j in range(segs):
            t = 2 * math.pi * j / segs
            q = c + A * (ra * math.sin(ph)) + (B * (rb * math.cos(t)) + F * (rf * math.sin(t))) * math.cos(ph)
            row.append(buf.vert(q, wf(q)))
        ringv.append(row)
    p0 = c - A * ra
    p1 = c + A * ra
    i0 = buf.vert(p0, wf(p0))
    i1 = buf.vert(p1, wf(p1))
    for i in range(len(ringv) - 1):
        r0, r1 = ringv[i], ringv[i + 1]
        for j in range(segs):
            j2 = (j + 1) % segs
            buf.face((r0[j], r0[j2], r1[j2], r1[j]), mat)
    for j in range(segs):
        j2 = (j + 1) % segs
        buf.face((i0, ringv[0][j2], ringv[0][j]), mat)
        buf.face((ringv[-1][j], ringv[-1][j2], i1), mat)


def bone_chain(e, prefix, joints, parent="head"):
    """joints(N점)를 잇는 본 N-1개 (prefix_01, _02, ...) → elf.Chain. 첫 본은 parent의 자식."""
    names = []
    prev = parent
    for i in range(len(joints) - 1):
        nm = f"{prefix}_{i + 1:02d}"
        e.add_bone(nm, joints[i], joints[i + 1], prev)
        names.append(nm)
        prev = nm
    return elf.Chain([V(p) for p in joints], names, start={parent: 1.0}, start_blend=0.5)


class Braid:
    """세 가닥 땋은 머리 한 줄: 매끈한 스플라인을 따라 납작한 타원체 마디를 좌우로 번갈아 기울여 겹친다. [키트 braid() 교체 후보]

    키트 h.braid()는 둥근 상자를 수직으로 띄엄띄엄 놓고 head 본 100%라 염주처럼 끊겨 보이고 흔들 수 없다.
    여기서는
      - 마디(납작 타원체, 폭 0.88w)를 경로 좌우로 ±0.17w 엇갈리게 두고 ±tilt° 기울인다 → 실루엣에 지그재그(세 가닥 결)
      - 마디 길이 = 간격의 2배 → 이웃 마디와 50% 겹쳐 틈이 없다. 한 Buf(한 메시)에 모은다
      - 본 bones개를 경로에 사슬로 두고(첫 본은 parent 자식) 정점마다 경로 위치로 웨이트를 섞는다
      - 끝: 묶음 띠 + 리본(선택) + 작은 꼬리털
      - 색: shade()로 정점색 그라데이션 (finalize 뒤에 부른다, 면 단위 계단이 아니라 부드럽게)
    ctrl: 경로 제어점(월드, 뿌리 → 끝). w0/w1: 뿌리/끝 폭(m, 실제 값). face: 마디 넓은 면이 향할 방향."""

    def __init__(self, e, name, ctrl, *, w0=0.056, w1=0.036, lobes=14, tilt=35.0, face=(0, 1, 0), mat=None,
                 bones=3, parent="head", segs=8, rings=5, tie=None, tie_at=0.90, tuft=0.05, bow=None, bow_size=0.08):
        self.e = e
        self.name = name
        self.mat = mat
        pts = catmull([V(p) for p in ctrl], 72)
        cum = [0.0]
        for a_, b_ in zip(pts, pts[1:]):
            cum.append(cum[-1] + (b_ - a_).length)
        self.pts, self.cum, self.total = pts, cum, cum[-1]
        joints = [self.at(i / bones)[0] for i in range(bones + 1)]
        self.chain = bone_chain(e, name, joints, parent)
        self.buf = Buf()
        L = self.total
        sp = (tie_at * L) / lobes
        face = V(face).normalized()
        for i in range(lobes):
            t = (i + 0.5) * sp / L
            c, T = self.at(t)
            F = (face - T * face.dot(T))
            F = F.normalized() if F.length > 1e-6 else V((0, 1, 0))
            S = T.cross(F).normalized()
            sg = 1 if i % 2 == 0 else -1
            w = lerp(w0, w1, t / tie_at)
            th = math.radians(-sg * tilt)
            A = (T * math.cos(th) + S * math.sin(th)).normalized()
            Bv = F.cross(A).normalized()
            cen = c + S * (sg * 0.15 * w)
            ra = sp * (1.12 if i not in (0, lobes - 1) else 1.0)
            ellipsoid(self.buf, cen, A, Bv, F, ra, 0.44 * w, 0.30 * w, segs=segs, rings=rings, mat=mat,
                      wfn=lambda q, c=c, T=T, t=t: self.w_at(t + (q - c).dot(T) / L))
        self.tip_c, self.tip_T = self.at(tie_at)
        Ft = (face - self.tip_T * face.dot(self.tip_T)).normalized()
        self.tip_F = Ft
        wt = self.w_at(tie_at)
        if tie is not None:
            band(self.buf, self.tip_c, self.tip_T, Ft, 0.30 * w1, 0.22 * w1, 0.012, 0.004, segs=12, mat=tie, w=wt)
        if tuft:
            S = self.tip_T.cross(Ft).normalized()
            for j, (dx, ln, wd) in enumerate(((-0.30, 1.0, 0.55), (0.30, 0.9, 0.55), (0.0, 1.15, 0.65))):
                a0 = self.tip_c + S * (dx * w1 * 0.5)
                a1 = a0 + self.tip_T * (tuft * ln * 0.55) + S * (dx * w1 * 0.6)
                a2 = a0 + self.tip_T * (tuft * ln) + S * (dx * w1 * 1.2)
                st = [{"c": a0, "rx": wd * w1 * 0.5, "ry": wd * w1 * 0.32, "w": wt, "ref": tuple(S)},
                      {"c": a1, "rx": wd * w1 * 0.42, "ry": wd * w1 * 0.26, "w": wt, "ref": tuple(S)},
                      {"c": a2, "rx": 0.0008, "ry": 0.0008, "w": wt, "ref": tuple(S)}]
                loft(self.buf, st, segs=6, cap0="flat", cap1="flat", mat=mat)
        if bow is not None:
            fwd = Ft
            M = Matrix.Translation(self.tip_c + fwd * (0.30 * w1 + 0.004)) @ frame(fwd, -self.tip_T)
            bow_geo(self.buf, M, bow_size, bow, w=wt, tails=0.85, segs=6)

    def at(self, t):
        """경로 비율 t(0~1) → (점, 접선)."""
        s = clamp(t, 0.0, 1.0) * self.total
        cum, pts = self.cum, self.pts
        for i in range(len(cum) - 1):
            if s <= cum[i + 1] or i == len(cum) - 2:
                L = cum[i + 1] - cum[i]
                a = (s - cum[i]) / L if L > 1e-9 else 0.0
                T = (pts[i + 1] - pts[i]).normalized()
                return pts[i].lerp(pts[i + 1], clamp(a)), T
        return pts[-1], (pts[-1] - pts[-2]).normalized()

    def w_at(self, t):
        return self.chain.weights(clamp(t, 0.0, 1.0))

    def t_of(self, q):
        """점 q에서 가장 가까운 경로 비율."""
        best, bi = 1e9, 0
        for i, p in enumerate(self.pts):
            d = (p - q).length_squared
            if d < best:
                best, bi = d, i
        return self.cum[bi] / self.total

    def done(self, group="head", outline=0.0035):
        """<이름>_hair 노드에 합친다 (헤어 v2: 라인 0.0035, fpHide head). CAMEO_SPLIT=1이면 <이름>_tails 노드."""
        ob = self.buf.obj(f"{self.e.name}_{self.name}", angle=60.0)
        return self.e.add(ob, group=group, tag=self.name, node=tail_node(), props={"outline": outline})


def hair_surface_off(e, h, az, el):
    """머리 표면 (az, el)에서 헤어 v2 셸 바깥 면까지의 거리(m, 두피 법선 방향). 머리핀·헤드셋을 머리카락 위에 얹을 때.
    셸이 덮지 않는 곳(머리선 아래)이면 0에 가깝다."""
    sp, n = e.head_point(az, el, 0.0)
    p, _ = h.path(az, h.s_of_el(az, el))
    return max(0.0, (p - sp).dot(n))


def flip_from(buf, f0, f1=None):
    """buf의 면 [f0, f1)의 감김 방향을 뒤집는다.
    [키트 버그 보고] elf.sweep은 면이 안쪽을 보게 감는다(법선이 안쪽). 그래서 sweep으로 만든 다발(h.strand,
    h.ahoge, 키트 꼬리)은 아웃라인 헐이 안쪽으로 밀려 윤곽선이 사라진다. 카메오 쪽에서 만든 다발은 이걸로 바로잡는다."""
    # 키트가 sweep 면 방향을 바깥으로 고친 뒤(ce65bbc, elf.SWEEP_WINDING == "outward")에는 뒤집으면 오히려 망가진다
    if getattr(elf, "SWEEP_WINDING", "inward") == "outward":
        return
    f1 = len(buf.f) if f1 is None else f1
    for i in range(f0, f1):
        buf.f[i] = tuple(reversed(buf.f[i]))


def strand(h, pts, width, thick=None, **kw):
    """h.strand + 면 방향 바로잡기 (flip_from). 인자는 키트 h.strand와 같다."""
    n0 = len(h.buf.f)
    h.strand(pts, width, thick, **kw)
    flip_from(h.buf, n0)
    return h


def ahoge(h, **kw):
    """h.ahoge + 면 방향 바로잡기 (flip_from). 인자는 키트 h.ahoge와 같다."""
    n0 = len(h.buf.f)
    h.ahoge(**kw)
    flip_from(h.buf, n0)
    return h


def tail_node():
    """꼬리·땋은 머리가 들어갈 노드 이름. 근접 스크린샷 때만 CAMEO_SPLIT=1로 따로 뗀다."""
    return "tails" if os.environ.get("CAMEO_SPLIT") else "hair"


def hair_obj(e):
    """finalize 뒤 꼬리·땋은 머리가 든 메시 (shade_braids 대상)."""
    return e.result.get(tail_node()) or e.result["hair"]


class Tail:
    """묶은 머리 꼬리 (포니테일·트윈테일), 헤어 v2 원칙. [키트 후보: ponytail/twintails의 경로·위치 인자]

    키트 h.ponytail()은 묶는 방위가 뒤통수 가운데로 고정이고 경로 모양이 정해져 있다. 여기서는 경로 ctrl을 직접 준다.
      - 몸통: 한 덩어리의 매끈한 스윕 볼륨. 묶은 자리(tie_at)에서는 root 비율로 모였다가 puff까지 부풀고,
        hold부터 body_end까지 끝에서만 모인다(키트 _tip 곡선). 렌즈 단면, 넓은 면이 바깥(lat × 접선)을 본다.
      - 끝: ends개의 다발이 split 근처 몸통 안에서 시작해 폭 방향으로 벌어지며 길이를 달리해 끝난다.
        몸통이 먼저 모여서 실루엣은 '끝에서만 갈라진' 모양이 된다.
      - 본: 묶은 자리부터 끝까지 bones개 사슬(<name>_01..), 첫 본은 parent 자식. 웨이트는 경로 위치로 섞는다.
      - 묶음 띠(tie): 뿌리를 덮는다. 뿌리 첫 점은 머리 덩어리 안에 묻는다.
    ctrl: 경로 제어점(월드, 뿌리 → 끝). width/thick: 가장 굵은 곳의 폭·두께(m, 실제 값).
    lat: 폭 방향 축 (포니테일 (1,0,0), 왼쪽 트윈테일 (0,-1,0), 오른쪽 (0,1,0) → 넓은 면이 바깥).
    curl=(t, 벡터): t 이후로 경로를 벡터만큼 휘게 한다(끝 말림, m). shade_braids와 같은 인터페이스(name, t_of)."""

    def __init__(self, e, h, name, ctrl, *, width, thick=None, lat=(1, 0, 0), bones=3, parent="head", tie_at=0.06,
                 root=0.50, puff=0.20, hold=0.50, body_end=0.88, ends=3, split=0.60, spread=0.55, end_w=0.48,
                 end_len=(1.0, 0.94, 0.88), curl=None, mat=None, tie=None, tie_h=0.020, tie_th=0.007, n=26, segs=12,
                 bend=0.15):
        self.e, self.h, self.name = e, h, name
        k = e.k
        q = e.q
        self.ctrl = [V(p) for p in ctrl]
        pts = catmull(self.ctrl, 120)
        if curl:
            t_c, vec = curl
            vec = V(vec)
            nn = len(pts)
            pts = [p + vec * (max(0.0, (i / (nn - 1) - t_c) / max(1e-6, 1 - t_c)) ** 2) for i, p in enumerate(pts)]
        cum = [0.0]
        for a_, b_ in zip(pts, pts[1:]):
            cum.append(cum[-1] + (b_ - a_).length)
        self.pts, self.cum, self.total = pts, cum, cum[-1]
        self.t0 = tie_at
        joints = [self.at(tie_at + (1 - tie_at) * i / bones)[0] for i in range(bones + 1)]
        self.chain = bone_chain(e, name, joints, parent)
        self.parent = parent
        self.lat = V(lat).normalized()
        self.buf = Buf()
        m = mat or h.m
        thick = thick if thick is not None else width * 0.72
        self.width, self.thick = width, thick
        nseg = max(6, int(segs) // 2 * 2)                 # 단면 분할은 그대로 (꼬리는 가까이서 보인다)
        nn = max(10, int(round(n * max(q, 0.75))))       # 길이 분할은 키트 품질 배율을 따른다

        def frame_at(t):
            c, T = self.at(t)
            Lx = self.lat - T * self.lat.dot(T)
            Lx = Lx.normalized() if Lx.length > 1e-6 else V((1, 0, 0))
            return c, T, Lx, Lx.cross(T).normalized()    # 중심, 접선, 폭 방향, 바깥(두께) 방향

        self.frame_at = frame_at

        # ---- 몸통
        def prof(t):
            r = root if t <= tie_at else lerp(root, 1.0, smoothstep(tie_at, puff, t))
            x = (t - hold) / max(1e-6, body_end - hold)
            return r * (elf._tip(x, 2.0) if x > 0 else 1.0)

        ts = [body_end * i / (nn - 1) for i in range(nn)]
        P = [frame_at(t)[0] for t in ts]
        f0 = len(self.buf.f)
        elf.sweep(self.buf, P, lambda u: width / 2 * prof(u * body_end),
                  lambda u: thick / 2 * max(prof(u * body_end), 0.22), segs=nseg,
                  ref_fn=lambda u: frame_at(u * body_end)[3], mat=m, w=lambda u: self.w_at(u * body_end), bend=bend)
        # ---- 끝 다발
        for i in range(ends):
            u_i = (i - (ends - 1) / 2) / max(1.0, (ends - 1) / 2) if ends > 1 else 0.0
            te = min(1.0, end_len[i % len(end_len)])
            ts_ = split - 0.18
            m_ = max(10, nn // 2 + 2)
            tt = [lerp(ts_, te, j / (m_ - 1)) for j in range(m_)]
            Pi = []
            for t in tt:
                c, T, A, B = frame_at(min(t, 1.0))
                a = smoothstep(ts_, te, t) ** 1.3
                Pi.append(c + A * (u_i * spread * width * 0.5 * a) + B * (thick * 0.04 * (1 - abs(u_i)) * a))
            ln = te - ts_

            def eprof(u, ln=ln):
                t = ts_ + u * ln
                r = lerp(0.62, 1.0, smoothstep(ts_, split + 0.04, t))
                return r * elf._tip((u - 0.40) / 0.60, 2.0) if u > 0.40 else r

            elf.sweep(self.buf, Pi, lambda u: end_w * width / 2 * eprof(u),
                      lambda u: end_w * thick / 2 * 1.05 * max(eprof(u), 0.25), segs=max(8, nseg - 2),
                      ref_fn=lambda u, tt=tt: frame_at(min(tt[min(int(u * (len(tt) - 1)), len(tt) - 1)], 1.0))[3],
                      mat=m, w=lambda u, ln=ln: self.w_at(ts_ + u * ln), bend=bend)
        flip_from(self.buf, f0)      # elf.sweep 면 방향 바로잡기 (아웃라인이 바깥으로)
        # ---- 묶음 띠
        if tie is not None:
            c, T, A, B = frame_at(tie_at)
            band(self.buf, c, T, A, root * width / 2 + 0.002 * k, root * thick / 2 + 0.002 * k, tie_h * k,
                 tie_th * k, segs=16, mat=tie, w=self.w_at(tie_at))

    at = Braid.at

    def w_at(self, t):
        if t <= self.t0:
            return {self.parent: 1.0}
        return self.chain.weights(clamp((t - self.t0) / (1 - self.t0)))

    t_of = Braid.t_of

    def done(self, group="head"):
        ob = self.buf.obj(f"{self.e.name}_{self.name}", angle=180.0)
        return self.e.add(ob, group=group, tag=self.name, node=tail_node(), props={"outline": self.h.outline})



class PathTail:
    """[v1, 쓰지 않음] 경로를 따라 늘어지는 머리 꼬리 + 본 사슬. 뭉치를 strand()로 여러 개 겹친다.
    헤어 v2에서는 가늘고 납작한 판이 겹쳐 보여 Tail로 바꿨다. 다른 스크립트 호환용으로만 남긴다."""

    def __init__(self, e, name, ctrl, *, bones=3, parent="head"):
        self.e = e
        self.name = name
        pts = catmull([V(p) for p in ctrl], 72)
        cum = [0.0]
        for a_, b_ in zip(pts, pts[1:]):
            cum.append(cum[-1] + (b_ - a_).length)
        self.pts, self.cum, self.total = pts, cum, cum[-1]
        self.ctrl = [V(p) for p in ctrl]
        joints = [Braid.at(self, i / bones)[0] for i in range(bones + 1)]
        self.chain = bone_chain(e, name, joints, parent)

    at = Braid.at
    t_of = Braid.t_of
    w_at = Braid.w_at

    def strand(self, h, *, off=(0.0, 0.0), width=0.07, thick=0.03, t0=0.0, t1=1.0, n=16, segs=8, taper=None,
               mat=None, side=None, curl=None):
        """경로 [t0, t1] 구간을 따라 뭉치 하나. off=(옆, 앞뒤) 이동(m, 실제 값). side: 옆 방향 벡터(기본 X)."""
        side = V(side or (1, 0, 0)).normalized()
        fwd = V((0, -1, 0))
        pts = []
        m = 9
        for i in range(m):
            t = lerp(t0, t1, i / (m - 1))
            c, T = self.at(t)
            S = (side - T * side.dot(T))
            S = S.normalized() if S.length > 1e-6 else V((1, 0, 0))
            Fw = (fwd - T * fwd.dot(T))
            Fw = Fw.normalized() if Fw.length > 1e-6 else V((0, -1, 0))
            q = c + S * off[0] * smoothstep(0.0, 0.25, t) + Fw * off[1] * smoothstep(0.0, 0.25, t)
            if curl and t > curl[0]:
                a = (t - curl[0]) / max(1e-6, 1 - curl[0])
                q = q + S * (curl[1] * a * a)
            pts.append(q)
        L = self.total
        h.strand(pts, width, thick, n=n, segs=segs, mat=mat,
                 w=lambda tt: self.w_at(lerp(t0, t1, tt)),
                 taper=taper or [(0, 0.7), (0.15, 1.0), (0.7, 0.85), (1, 0.0)])
        _ = L
        return pts


def shade_braids(obj, braids, base_hex, stops, *, tol=6):
    """finalize() 뒤 합쳐진 메시(hair_obj(e))에서 땋은 머리·꼬리(본 그룹 이름이 braid 이름으로 시작하고 색이
    base_hex인 면 모서리)의 정점색을 경로 위치에 따라 부드럽게 바꾼다. stops: [(t, hex), ...].
    리본·묶음 띠는 색이 달라서 건드리지 않는다. 셸은 head 웨이트뿐이라 건드리지 않는다."""
    me = obj.data
    ca = me.color_attributes.get("Col")
    if ca is None:
        return 0
    base = elf.hex_srgb(base_hex)
    gidx = {}
    for g in obj.vertex_groups:
        for b in braids:
            if g.name.startswith(b.name):
                gidx[g.index] = b
    vb = {}
    for v in me.vertices:
        for g in v.groups:
            if g.group in gidx and g.weight > 1e-3:
                vb[v.index] = gidx[g.group]
                break
    cols = [(t, elf.hex_srgb(h)) for t, h in stops]

    def col(t):
        if t <= cols[0][0]:
            return cols[0][1]
        for (t0, c0), (t1, c1) in zip(cols, cols[1:]):
            if t <= t1:
                a = smoothstep(t0, t1, t)
                return tuple(lerp(x, y, a) for x, y in zip(c0, c1))
        return cols[-1][1]
    n = 0
    tcache = {}
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            b = vb.get(vi)
            if b is None:
                continue
            c = ca.data[li].color_srgb
            if max(abs(c[i] - base[i]) for i in range(3)) * 255 > tol:
                continue
            if vi not in tcache:
                tcache[vi] = b.t_of(me.vertices[vi].co)
            r, g_, bb = col(tcache[vi])
            ca.data[li].color_srgb = (r, g_, bb, 1.0)
            n += 1
    return n


# =========================================================================== 작은 소품 도형

def prism(buf, poly, depth, M, *, mat=None, w=None, chamfer=0.0):
    """2D 볼록 다각형 poly[(x, z)]를 로컬 -Y(바깥)로 depth만큼 돌출. chamfer>0이면 앞면 모서리를 45°로 깎는다.
    R41식 깎인 판(헤드기어 지느러미, 갑주판)에 쓴다. [키트 후보]"""
    n = len(poly)
    cx = sum(p[0] for p in poly) / n
    cz = sum(p[1] for p in poly) / n

    def ins(p, d):
        if d <= 0:
            return p
        vx, vz = p[0] - cx, p[1] - cz
        L = math.hypot(vx, vz) or 1.0
        s = max(L - d, L * 0.2) / L
        return (cx + vx * s, cz + vz * s)
    back = [buf.vert(M @ V((x, 0.0, z)), w) for x, z in poly]
    mid = [buf.vert(M @ V((x, -(depth - chamfer), z)), w) for x, z in poly]
    front = [buf.vert(M @ V((ins((x, z), chamfer)[0], -depth, ins((x, z), chamfer)[1])), w) for x, z in poly]
    cb_ = buf.vert(M @ V((cx, 0.0, cz)), w)
    cf = buf.vert(M @ V((cx, -depth, cz)), w)
    # poly가 반시계(로컬 x→z)라고 가정
    for i in range(n):
        j = (i + 1) % n
        buf.face((cb_, back[j], back[i]), mat)
        buf.face((back[i], back[j], mid[j], mid[i]), mat)
        if chamfer > 0:
            buf.face((mid[i], mid[j], front[j], front[i]), mat)
        buf.face((cf, front[i], front[j]), mat)


def bow_geo(buf, M, size, mat, *, w=None, tails=0.8, knot_mat=None, segs=8):
    """리본 매듭 (둥근 날개 2개 + 매듭 + 꼬리 2개). M 로컬: +Z 위, -Y 앞, X 옆. size = 전체 폭(m). [키트 후보]"""
    s = size / 2
    for sg in (1, -1):
        st = []
        for i in range(6):
            t = i / 5
            x = sg * lerp(0.10, 0.92, t) * s
            rz = keys([(0.0, 0.16), (0.45, 0.44), (0.8, 0.40), (1.0, 0.22)], t) * s
            ry = keys([(0.0, 0.14), (0.5, 0.22), (1.0, 0.14)], t) * s
            c = M @ V((x, 0.0, 0.06 * s * math.sin(t * math.pi)))
            st.append({"c": c, "rx": rz, "ry": ry, "w": w or {}, "ref": tuple(M.to_3x3() @ V((0, 0, 1)))})
        loft(buf, st[::1] if segs >= 10 else st[::2] + [st[-1]], segs=segs, cap0="round", cap1="round", mat=mat,
             cap_len0=0.05 * s, cap_len1=0.18 * s, cap_rings=2)
        if tails:
            a = M @ V((sg * 0.12 * s, -0.04 * s, -0.10 * s))
            b = M @ V((sg * 0.42 * s, -0.02 * s, -tails * s))
            st2 = [{"c": a, "rx": 0.16 * s, "ry": 0.05 * s, "w": w or {}, "ref": tuple(M.to_3x3() @ V((1, 0, 0)))},
                   {"c": a.lerp(b, 0.5), "rx": 0.19 * s, "ry": 0.05 * s, "w": w or {},
                    "ref": tuple(M.to_3x3() @ V((1, 0, 0)))},
                   {"c": b, "rx": 0.22 * s, "ry": 0.05 * s, "w": w or {}, "ref": tuple(M.to_3x3() @ V((1, 0, 0)))}]
            loft(buf, st2, segs=6, cap0="flat", cap1="flat", mat=mat)
    rrbox(buf, (0.30 * s, 0.34 * s, 0.36 * s), M @ Matrix.Translation((0, -0.04 * s, 0)), mat=knot_mat or mat, w=w,
         r=0.45, segs=1)


def skull(buf, M, size, bone, dark, *, w=None):
    """SD 해골 장식 (머리핀·브로치). M 로컬: +Z 위, -Y 앞. size = 높이(m). 눈구멍·코·이 자국은 dark."""
    s = size
    rrbox(buf, (0.98 * s, 0.62 * s, 0.80 * s), M @ Matrix.Translation((0, -0.31 * s, 0.10 * s)), mat=bone, w=w, r=0.5,
          segs=1)
    rrbox(buf, (0.60 * s, 0.50 * s, 0.34 * s), M @ Matrix.Translation((0, -0.30 * s, -0.30 * s)), mat=bone, w=w,
          r=0.45, segs=1)
    n = (M.to_3x3() @ V((0, -1, 0))).normalized()
    up = M.to_3x3() @ V((0, 0, 1))
    for sg in (1, -1):
        c = M @ V((sg * 0.21 * s, -0.615 * s, 0.03 * s))
        disc(buf, c, n, up, 0.15 * s, 0.17 * s, 0.012 * s, segs=12, mat=dark, w=w)
    disc(buf, M @ V((0, -0.62 * s, -0.17 * s)), n, up, 0.06 * s, 0.06 * s, 0.01 * s, segs=3, mat=dark, w=w)
    for sg in (-1, 1):
        rrbox(buf, (0.025 * s, 0.03 * s, 0.14 * s), M @ Matrix.Translation((sg * 0.09 * s, -0.55 * s, -0.36 * s)),
             mat=dark, w=w, r=0.3, segs=1)


# =========================================================================== 엘피니아 군 전투복

def elfinia_uniform(e, pre, *, rank="bars2", helmet=True, headset=True):
    """엘피니아 군 전투복 일체 (알레트·타이다·레이지 계열, reference-notes 5장). [키트 후보: 복장 세트]
    _kit_elfinia_soldier.py와 같은 함수·같은 색을 쓴다 (프롤로그 캐시와 무명 병사가 똑같이 보이도록).
    rank: 가슴 계급장 모양 ('bars2' 병, 'bars3' 선임). 반환: 머티리얼 사전."""
    M = elf.mat
    m = {
        "jacket": M(f"{pre}_jacket", "#a3ada1"), "jacket_d": M(f"{pre}_jacket_d", "#7f8a80"),
        "pants": M(f"{pre}_pants", "#939e98"), "pants_d": M(f"{pre}_pants_d", "#76807b"),
        "web": M(f"{pre}_web", "#635b62"), "web_d": M(f"{pre}_web_d", "#4f474e"),
        "belt": M(f"{pre}_belt", "#4a4149"), "metal": M(f"{pre}_metal", "#cfcac4"),
        "boots": M(f"{pre}_boots", "#58535d"), "boots_d": M(f"{pre}_boots_d", "#443f48"),
        "sole": M(f"{pre}_sole", "#2f2b31"), "tab": M(f"{pre}_tab", "#b9b2a8"),
        "glove": M(f"{pre}_glove", "#4f474e"), "helmet": M(f"{pre}_helmet", "#6a636b"),
        "helmet_d": M(f"{pre}_helmet_d", "#524b53"), "rank_bg": M(f"{pre}_rank_bg", "#2f3644"),
        "rank_fg": M(f"{pre}_rank_fg", "#d6b25e"),
        "led": M(f"{pre}_led", "#ffffff", emission="#7ff0ea", unlit=True),
    }
    k = e.k
    cz = e.chest_z
    e.shirt(m["jacket"], collar="stand", collar_mat=m["jacket_d"], placket=m["jacket_d"], buttons=m["metal"],
            flare=0.012)
    e.sleeves(m["jacket"], length=0.95, cuff=(m["jacket_d"], 0.022, 0.0045))
    e.pants(m["pants"], bag=0.013, blouse=0.020)
    e.boots(m["boots"], top=0.66, sole=(m["sole"], 0.016), cuff=m["boots_d"], laces=m["boots_d"], tab=m["tab"])
    e.gloves(m["glove"], cuff=m["web_d"])
    e.belt(m["belt"], buckle=m["metal"], loops=m["belt"])
    e.epaulet(m["jacket_d"], button=m["metal"])
    e.pouch(m["jacket"], ("torso", cz - 0.035 * k, 40, 0.010 * k), size=(0.040, 0.006, 0.040), flap=m["jacket_d"],
            button=m["metal"], name="chest_pocket_L")
    e.patch(m["rank_bg"], ("torso", cz + 0.072 * k, 22, 0.012 * k), size=(0.026, 0.024 if rank == "bars3" else 0.020),
            name="rank_bg")
    e.patch(m["rank_fg"], ("torso", cz + 0.072 * k, 22, 0.0135 * k),
            size=(0.018, 0.016 if rank == "bars3" else 0.012), shape=rank, name="rank_fg")
    e.patch(m["rank_bg"], ("arm_L", 0.16, 60, 0.012 * k), size=(0.028, 0.028), shape="round", name="unit_patch")
    e.patch(m["rank_fg"], ("arm_L", 0.16, 60, 0.0135 * k), size=(0.014, 0.014), shape="diamond", name="unit_mark")
    sz = e.shoulder_z
    pz = cz + 0.012 * k
    for s in (1, -1):
        e.strap(m["web"], [("torso", pz, s * 30, 0.018 * k), ("torso", sz - 0.005 * k, s * 40, 0.014 * k),
                           ("torso", sz + 0.02 * k, s * 58, 0.014 * k), ("torso", sz - 0.01 * k, s * 122, 0.014 * k),
                           ("torso", cz, s * 150, 0.016 * k), ("torso", e.waist_z + 0.02 * k, s * 150, 0.020 * k)],
                width=0.020, th=0.004, name=f"harness_{'L' if s > 0 else 'R'}")
    e.ring(m["web"], "torso", pz - 0.035 * k, h=0.020, th=0.004, off=0.014, name="rig_band")
    for i, a in enumerate((-26, 0, 26)):
        e.pouch(m["web"], ("torso", pz - 0.004 * k, a, 0.018 * k), size=(0.036, 0.024, 0.056), flap=m["web_d"],
                button=m["metal"], molle=m["web_d"], name=f"mag_pouch_{i}")
    e.pouch(m["web"], ("leg_R", 0.30, -75, 0.024 * k), size=(0.052, 0.026, 0.062), flap=m["web_d"],
            button=m["metal"], strap=m["belt"], name="thigh_pouch")
    e.pouch(m["pants"], ("leg_L", 0.34, 85, 0.022 * k), size=(0.05, 0.010, 0.058), flap=m["pants_d"],
            button=m["pants_d"], name="cargo_L")
    if helmet:
        e.helmet(m["helmet"], rim=m["helmet_d"], band_mat=m["web_d"], buckle=m["metal"], strap=m["web_d"])
    if headset:
        def fn(buf, Mx, w):
            rbox(buf, (0.05 * k, 0.03 * k, 0.045 * k), Mx @ Matrix.Translation((0, -0.012 * k, 0)), mat=m["web_d"],
                 w=w, r=0.45, segs=2)
            rbox(buf, (0.032 * k, 0.012 * k, 0.03 * k), Mx @ Matrix.Translation((0, -0.03 * k, 0)),
                 mat=m["helmet_d"], w=w, r=0.4, segs=1)
            c = Mx @ V((0.010 * k, -0.037 * k, 0.006 * k))
            n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
            disc(buf, c, n, (0, 0, 1), 0.0045 * k, 0.0045 * k, 0.0015 * k, segs=10, mat=m["led"], w=w)
            base = Mx @ V((-0.014 * k, -0.02 * k, 0.02 * k))
            st = [{"c": base, "rx": 0.003 * k, "ry": 0.003 * k, "w": w},
                  {"c": base + V((0, 0.02 * k, 0.06 * k)), "rx": 0.002 * k, "ry": 0.002 * k, "w": w}]
            loft(buf, st, segs=6, cap0="flat", cap1="round", mat=m["web_d"])
        e.gear("headset", ("head", -100, 18, 0.034 * k), fn)
    return m


bow = bow_geo
