"""에르핀 두 판(기본 에르핀 / 에르핀(왕도))이 같이 쓰는 도우미.

fairy.py(요정 진영 공용)는 부모 작업자 소유라 고치지 않고, 에르핀에게 필요한 것만 여기에 둔다.
[fairy 후보] 표시는 fairy.py나 키트로 올릴 만한 기능이다. 근거: docs/art/fairy-faction.md 에르핀 절.
"""
from __future__ import annotations

import math

import elf
import fairy
from elf import V, Matrix, Buf, loft, band, keys, lerp, smoothstep, clamp, frame


# =========================================================================== 얼굴: 덧니

class ErpinFace(fairy.FairyFace):
    """FairyFace + 덧니(송곳니 하나). 입을 벌린 만큼만 윗입술 아래로 나온다(입 다각형에 잘림 → 정점 수 고정).
    fang: 입 폭 비율 위치(+면 캐릭터 왼쪽 +X). None이면 없음. [fairy 후보: FairyFace(fang=)]"""

    def __init__(self, e, *, fang=0.42, fang_color="#ffffff", star_pupil=None, star_pupil_size=1.0,
                 star_pupil_dz=-0.006, **kw):
        super().__init__(e, **kw)
        self.fang = fang
        self.m["fang"] = elf.mat(f"{e.name}_f_fang", fang_color)
        self.star_pupil = star_pupil
        self.sp_size = star_pupil_size
        self.sp_dz = star_pupil_dz
        if star_pupil:
            self.m["star_p"] = elf.mat(f"{e.name}_f_starp", star_pupil)

    def _build(self, P):
        buf = super()._build(P)
        sz = self.sz
        if self.star_pupil:
            # 별 동공: 홍채 아래쪽 가운데(밝은 반달 위)에 다섯 꼭지 별. FairyFace(star='pupil')보다 낮고 작게
            for side in (1, -1):
                outline, _ = self.eye_outline(side, P)
                icx, icz = self._iris_c(side, P)
                ip = P["iris"]
                r = ip["rx"] * sz * 0.56 * self.sp_size * ip["pupil"]
                pts = fairy.star_poly(r, r * 0.46, 5, 90.0, icx, icz + self.sp_dz * sz)
                self._fill(buf, elf.clip_to(pts, outline), 0.0027, self.m["star_p"], rings=(0.55,))
        if self.fang is None:
            return buf
        mq = P["mouth"]
        mw = mq["w"] * sz / 2
        mz = self.ez - 0.074 * sz + mq["dz"] * sz

        def top(s):
            v = mq["curve"] * sz * s * s + mq["top_arch"] * sz * (1 - s * s) + mq["wave"] * sz * math.sin(s * math.pi * 2)
            return s * mw, mz + v

        def bot(s):
            x, z = top(s)
            return x, z - mq["open"] * sz * elf._sup(s, 1.6) - 0.0002

        n = 11
        poly = [top(-1 + 2 * i / (n - 1)) for i in range(n)] + [bot(1 - 2 * i / (n - 1)) for i in range(1, n - 1)]
        poly = list(reversed(poly))
        s0 = self.fang
        a, b = top(s0 - 0.16), top(s0 + 0.16)
        cx, cz = top(s0)
        depth = min(0.0062 * sz, 0.75 * mq["open"] * sz * elf._sup(s0, 1.6))
        tri = [(a[0], a[1] - 0.0003), (cx, cz - depth), (b[0], b[1] - 0.0003)]
        # 다각형 안으로 당겨 넣기 (입을 다물면 윗입술 선으로 접힌다)
        tri = elf.clip_to(tri, poly)
        self._fill(buf, list(reversed(tri)), 0.0013, self.m["fang"], rings=())
        return buf


def face(e, **kw):
    """fairy.face()와 같지만 ErpinFace(덧니)를 쓴다."""
    f = ErpinFace(e, **kw)
    ob = f.build()
    vc = elf.vc_material(f"{e.name}_toon_vc", e.line)
    elf.bake_vcol(ob)
    elf.remap_to_vc(ob, vc)
    elf.collapse_slots(ob)
    e.face_obj = ob
    e.face_builder = f
    return ob


# =========================================================================== 별도 노드 파츠

def node_part(e, name, fn, *, group="head"):
    """fn(buf)로 만든 파츠를 '<인물>_<name>' 별도 노드로 남긴다 (왕관처럼 장면에서 숨기거나 씌우는 소품).
    웨이트는 buf에 넣은 값(보통 head 100%). 키트 finalize가 정점색 병합·스키닝을 그대로 해 준다."""
    buf = Buf()
    fn(buf)
    ob = buf.obj(f"{e.name}_{name}_src", angle=40.0)
    return e.add(ob, group=group, tag=name, node=name)


# =========================================================================== 털 방울·털 테두리

def bead_tube(buf, pts, r_lo, r_hi, beads, *, segs=8, mat=None, wfn=None, ref=None, n_per=5, flat=1.0):
    """경로를 따라 굵기가 볼록볼록 바뀌는 관 하나 (망토 밑단 털 방울, 어민 털 테두리). 한 덩어리라 아웃라인이 깔끔하다.
    pts: 경로 점(월드), beads: 방울 수, ref(t, 점) → 단면 x축 기준(기본: 위). [fairy 후보]"""
    P = elf.catmull([V(p) for p in pts], max(8, beads * n_per + 1))
    st = []
    n = len(P)
    for i, q in enumerate(P):
        t = i / (n - 1)
        b = abs(math.sin(math.pi * beads * t))
        r = lerp(r_lo, r_hi, b ** 0.55)
        w = wfn(q) if wfn else {}
        rf = ref(t, q) if ref else (0, 0, 1)
        st.append({"c": q, "rx": r, "ry": r * flat, "w": w, "ref": tuple(rf)})
    loft(buf, st, segs=segs, cap0="round", cap1="round", mat=mat)


# =========================================================================== 다이아몬드 장식 (크리스털)

def gem(buf, M, w_, h_, mat, *, depth=0.004, frame_mat=None, frame_w=0.0025, wts=None):
    """마름모 크리스털 (+ 금테). M 로컬: X-Z 평면, -Y 바깥. 앞면 모서리를 깎아 셀 셰이딩에 면이 읽히게 한다."""
    d0 = 0.0
    if frame_mat is not None:
        fairy.prism(buf, fairy.diamond_poly(w_ + frame_w * 2, h_ + frame_w * 2.6), depth * 0.6, M, mat=frame_mat,
                    w=wts, chamfer=depth * 0.2)
        d0 = depth * 0.45
    fairy.prism(buf, fairy.diamond_poly(w_, h_), depth, M @ Matrix.Translation((0, -d0, 0)), mat=mat, w=wts,
                chamfer=depth * 0.7)


def flower(buf, M, r, petal_mat, center_mat, *, petals=5, wts=None, depth=0.003):
    """다섯 잎 꽃 (머리 장식, 훈장). M 로컬: X-Z 평면, -Y 바깥."""
    pts = []
    n = petals * 4
    for i in range(n):
        a = 2 * math.pi * i / n + math.pi / 2
        rr = r * (0.55 + 0.45 * abs(math.cos(petals * (a - math.pi / 2) / 2)) ** 0.7)
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    fairy.prism(buf, pts, depth, M, mat=petal_mat, w=wts, chamfer=depth * 0.5)
    fairy.ellipsoid(buf, M @ V((0, -depth, 0)), M.to_3x3() @ V((1, 0, 0)), M.to_3x3() @ V((0, 0, 1)),
                    M.to_3x3() @ V((0, -1, 0)), r * 0.30, r * 0.30, r * 0.18, segs=8, rings=4, mat=center_mat,
                    w=wts)


# =========================================================================== 옷 위 판 (드레스 앞판)

def shell_panel(shell, u0, u1, a0, a1, mat, *, border=None, bw=0.006, lift=0.0025, rows=5, cols=4, th=0.002):
    """Shell 표면 위에 붙는 판 (드레스 앞판, 망토 장식 띠). border=재질이면 가장자리 띠."""
    e = shell.e
    k = e.k
    b = shell.buf
    P, N, W = [], [], []
    for i in range(rows):
        u = lerp(u0, u1, i / (rows - 1))
        rp, rn, rw = [], [], []
        for j in range(cols):
            a = lerp(a0, a1, j / (cols - 1))
            p, n = shell.surface(min(u, 1.0), a, lift * k)
            if u > 1.0:
                p = p - V((0, 0, (u - 1.0) * (shell.prm["z_top"] - shell.prm["z_hem"])))
            rp.append(p)
            rn.append(n)
            rw.append(fairy.skirt_w(e, p) if shell.prm["skirt"] else e._torso_wfn(p, 0))
        P.append(rp)
        N.append(rn)
        W.append(rw)
    o = [[b.vert(P[i][j], W[i][j]) for j in range(cols)] for i in range(rows)]
    n_ = [[b.vert(P[i][j] - N[i][j] * th * k, W[i][j]) for j in range(cols)] for i in range(rows)]
    for i in range(rows - 1):
        for j in range(cols - 1):
            b.face((o[i][j], o[i + 1][j], o[i + 1][j + 1], o[i][j + 1]), mat)
            b.face((n_[i][j], n_[i][j + 1], n_[i + 1][j + 1], n_[i + 1][j]), mat)
    for j in range(cols - 1):
        b.face((o[-1][j], o[-1][j + 1], n_[-1][j + 1], n_[-1][j]), mat)
    for i in range(rows - 1):
        b.face((o[i][0], n_[i][0], n_[i + 1][0], o[i + 1][0]), mat)
        b.face((o[i][-1], o[i + 1][-1], n_[i + 1][-1], n_[i][-1]), mat)
    if border is not None:
        for jj in (0, cols - 1):
            pts = [P[i][jj] + N[i][jj] * 0.0006 * k for i in range(rows)]
            nr = [N[i][jj] for i in range(rows)]
            ups = [(P[i][1] - P[i][0]).normalized() for i in range(rows)]
            elf._loop(b, pts, nr, ups, bw * k, 0.0022 * k, mat=border, closed=False,
                      w=lambda t, jj=jj: W[min(int(round(t * (rows - 1))), rows - 1)][jj])
        pts = [P[-1][j] + N[-1][j] * 0.0006 * k for j in range(cols)]
        nr = [N[-1][j] for j in range(cols)]
        ups = [(P[-1][j] - P[-2][j]).normalized() for j in range(cols)]
        elf._loop(b, pts, nr, ups, bw * k, 0.0022 * k, mat=border, closed=False,
                  w=lambda t: W[-1][min(int(round(t * (cols - 1))), cols - 1)])
    return P, N, W


# =========================================================================== 반투명 막 날개 (별도 노드, 아웃라인 없음)

def membrane_node(e, side, M, outlines, mat, *, wfn=None, veins=None, vein_mat=None, vein_r=0.0018, rings=3,
                  name="wing_membrane", lift=0.0):
    """fairy.membrane_wing과 같지만 여러 장을 한 버퍼에 넣고 '<인물>_<name>' 별도 노드(noOutline)로 남긴다.
    fairy.membrane_wing은 body 메시에 합쳐져 반투명 판에도 아웃라인 헐이 생긴다(불투명 머티리얼이 섞인 메시는
    toon.ts가 헐을 붙임) → 막 뒤에 검은 판이 비친다. [fairy 후보: membrane_wing(node=, noOutline)]
    outlines: [(2D 외곽선, 중심), ...] (M 평면, x=바깥, z=위), veins: [[(x,z), ...], ...]."""
    wf = wfn or (lambda q: {})
    buf = Buf()
    mirror = M.to_3x3().determinant() < 0
    for outline, center in outlines:
        n = len(outline)
        cx, cz = center
        rows = []
        for r in range(rings):
            s = 1.0 - r / rings
            row = []
            for x, z in outline:
                q = M @ V((cx + (x - cx) * s, lift, cz + (z - cz) * s))
                row.append(buf.vert(q, wf(q)))
            rows.append(row)
        c = M @ V((cx, lift, cz))
        ci = buf.vert(c, wf(c))
        for a in range(len(rows) - 1):
            for i in range(n):
                j = (i + 1) % n
                f = (rows[a][i], rows[a][j], rows[a + 1][j], rows[a + 1][i])
                buf.face(tuple(reversed(f)) if mirror else f, mat)
        for i in range(n):
            j = (i + 1) % n
            f = (rows[-1][i], rows[-1][j], ci)
            buf.face(tuple(reversed(f)) if mirror else f, mat)
    if veins and vein_mat is not None:
        for line in veins:
            P = elf.catmull([M @ V((x, lift, z)) for x, z in line], max(4, 2 * len(line)))
            st = []
            for i, q in enumerate(P):
                t = i / (len(P) - 1)
                r_ = vein_r * (1.0 - 0.55 * t)
                st.append({"c": q, "rx": r_, "ry": r_ * 0.6, "w": wf(q), "ref": tuple(M.to_3x3() @ V((0, 1, 0)))})
            loft(buf, st, segs=3, cap0="flat", cap1="flat", mat=vein_mat)
    ob = buf.obj(f"{e.name}_{name}_{side}_src", angle=60.0)
    return e.add(ob, group="body", tag=f"{name}_{side}", node=name, props={"noOutline": 1})


# =========================================================================== 에르핀(왕도) 공용: 얼굴·머리·각성 날개
# 대관식 판(erpin_royal.py)과 각성 전투 판(erpin_awakened.py)이 같은 사람으로 읽히도록 같이 쓴다.

ROYAL_HAIR, ROYAL_HAIR_D, ROYAL_HAIR_L, ROYAL_HAIR_PINK = "#f7dc94", "#ddb465", "#fff6da", "#f4a3bf"


def royal_face(e, expr=None):
    """에르핀(왕도) 얼굴: 붉은 분홍 눈 + 흰 반짝임, 덧니, 기본은 'ω' 입의 능청스러운 얼굴 (원작 왕도 카드).
    expr: 판마다 더하는 표정 사전."""
    return face(e, eye_color="#e5465d", iris_dark="#5d1d36", iris_light="#ffa3ad", pupil="#6a1c2c",
                lash="#4a2226", brow="#d2a25e", brow_th=0.9, blush="#f8a2a8", blush_size=1.1,
                star="sparkle", star_color="#fff4f6", star_size=0.9, fang=0.40,
                base={"eye": {"top": 0.024, "ktop": 3.6, "cout": 0.019, "tilt_in": -0.004},
                      "brow": {"ang": -6.0, "dz": 0.066, "arch": 0.003},
                      "mouth": {"w": 0.024, "curve": 0.0020, "wave": 0.0016, "open": 0.0}},
                expr=expr or {})


def royal_hair(e, *, back_length=0.03, braid_length=0.46, braid_width=0.062, braid_beads=9, braid_tie=None,
               cap_back=-60.0, volume=1.12, braids=True):
    """에르핀(왕도) 머리 (헤어 v2): 금발, 얼굴을 감싸는 짧은 옆머리, 양 갈래 땋은 머리(끝 분홍은 royal_hair_tint), 바보털.
    대관식 판은 올림머리(보닛 아래), 각성 판은 뒤 포니테일을 더하고 땋은 머리를 길게 쓴다.
    braids=False면 키트 땋은 머리(귀 뒤에서 곧게 떨어짐)를 만들지 않는다 (바닥까지 오는 땋은 머리를 팔 뒤로 따로 돌릴 때)."""
    h = fairy.hair(e, ROYAL_HAIR, dark=ROYAL_HAIR_D, light=ROYAL_HAIR_L, volume=volume)
    h.cap(front=30, side=-4, back=cap_back, part=0, segs=14, rows=4)
    h.bangs(n=6, spread=56, tip_el=-1, sweep=4, part=-6, jag=0.28, curl=1.1, seed=11.0)
    h.sides(length=0.09, width=0.070, az=62, curl=0.6, thick=1.05)
    h.back(length=back_length, n=7)
    for sd in ((1, -1) if braids else ()):
        h.braid(side=sd, az=82.0, el=-16.0, length=braid_length, width=braid_width, beads=braid_beads, tie=braid_tie,
                tuft=0.05)
    h.ahoge(az=-10, height=0.075, curl=1.5, width=0.018)
    h.shine(el=46, spread=70, n=2, size=1.1)
    return h


def royal_wings(e, membrane, vein, *, span=0.42, height=0.24, z=None):
    """각성 날개: 위 흰 깃털 큰 날개 + 아래 분홍 반투명 막 날개(흰 맥). 막은 별도 노드 '<인물>_wing_membrane'."""
    k = e.k
    L, H = span * k, height * k
    # 원작 일러(에르핀(왕도)): 위로 들어 올린 큰 깃털 날개, 긴 깃 끝으로 갈수록 분홍빛
    wg = fairy.wings(e, span=span, height=height, sweep=16.0, raise_=20.0, prim=3, cov=2, color="#ffffff",
                     color2="#f7c9d8", z=z if z is not None else e.chest_z + 0.075 * k, style="feather")
    for sd in ("L", "R"):
        ch, Mw = wg[sd]
        Minv = Mw.inverted()

        def wfn(q, ch=ch, Minv=Minv):
            lq = Minv @ q
            return ch.weights(clamp(math.hypot(lq.x / L, 0.0) / 1.02))

        lobes = []
        veins = []
        for ax, az_, ang, ln, wd in ((0.66, 0.02, -48.0, 1.20, 0.34), (0.42, -0.06, -72.0, 1.42, 0.33),
                                     (0.18, -0.08, -96.0, 1.12, 0.28)):
            a0 = (ax * L, az_ * H)
            d = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
            c = (a0[0] + d[0] * ln * H * 0.5, a0[1] + d[1] * ln * H * 0.5)
            lobes.append((fairy.egg_poly(c, ln * H * 0.56, wd * L * 0.5, ang, n=12, egg=0.30), c))
            tip = (a0[0] + d[0] * ln * H * 0.98, a0[1] + d[1] * ln * H * 0.98)
            veins.append([a0, c, tip])
            for sg in (1, -1):
                pr = (-d[1] * sg, d[0] * sg)
                m1 = (c[0] + pr[0] * wd * L * 0.30 + d[0] * ln * H * 0.25,
                      c[1] + pr[1] * wd * L * 0.30 + d[1] * ln * H * 0.25)
                veins.append([c, m1])
        membrane_node(e, sd, Mw @ Matrix.Translation((0, 0.004 * k, 0)), lobes, membrane, wfn=wfn, veins=veins,
                      vein_mat=vein, vein_r=0.0022 * k)
    return wg


def royal_hair_tint(e, res, *, z_lo=None, z_hi=None):
    """finalize 뒤: 땋은 머리 끝을 분홍으로 물들인다 (원작 왕도: 금발 끝이 분홍). z_lo~z_hi 사이에서 섞는다."""
    k = e.k
    z_hi = z_hi if z_hi is not None else e.chin - 0.04 * k
    z_lo = z_lo if z_lo is not None else e.chin - 0.30 * k
    hair_ob = res.get("hair")
    if hair_ob is not None:
        fairy.vc_gradient(hair_ob, ROYAL_HAIR, [(z_lo, ROYAL_HAIR_PINK), (z_hi, ROYAL_HAIR)], tol=10,
                          pred=lambda co: co.z < e.chin and abs(co.x) > 0.10 * k)
    hair_in = res.get("hair_in")
    if hair_in is not None:
        fairy.vc_gradient(hair_in, ROYAL_HAIR_D, [(z_lo, "#d97c9c"), (z_hi, ROYAL_HAIR_D)], tol=10,
                          pred=lambda co: co.z < e.chin and abs(co.x) > 0.10 * k)
