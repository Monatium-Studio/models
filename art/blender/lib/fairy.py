"""요정 진영 헬퍼 (fairy).

트릭컬 리바이브의 요정(폴랑, 요정 경비대, 에르핀)을 엘프 키트(elf.py) 위에서 만든다. 키트와 카메오 헬퍼
(cameo.py, cameo2.py)는 읽기 전용이라 필요한 기능을 여기에 복사·확장했다. 원작 조사 근거와 인물별 사용처는
docs/art/fairy-faction.md. [키트 후보] 표시는 키트로 올릴 만한 기능이다.

요정 vs 엘프 (원작 「요정(트릭컬 리바이브)」 문서, 2026-11-01 조사)
    - 요정은 엘프와 같은 SD 체형·크기다(다른 엘리아스 종족보다 작지 않다). 그래서 키트 몸·리그·얼굴을 그대로 쓴다.
    - 귀: 엘프의 뾰족한 귀가 아니라 **사람과 같은 둥근 귀**(엘프와 겹치지 않게 한 설정). → round_ears()
    - 날개: 모든 요정에게 **데포르메된 작은 날개**가 있다(리바이브 이후 종족 특성). 날아다니지는 못한다.
      엘다인(각성)은 날개가 훨씬 커지고 일부가 반투명해진다(에르핀(왕도)). → wings(), membrane_wing()

사용
    import fairy
    e = fairy.Fairy("polan", height=1.24, chest=0.45)      # 엘프 키트 몸 + 둥근 귀
    fairy.face(e, eye_color="#5cb3a6", star="sparkle")      # 키트 얼굴 + 눈 속 별(✦) / 별 동공 / 눈 가림
    h = fairy.hair(e, "#f1eff3")                            # 키트 헤어 v2 + 다발 후처리 훅
    fairy.wings(e, span=0.26)                               # 깃털 날개 2단 + 본 wing_L/R_01..02
    fairy.shako(e, P)                                       # 요정 경비대 샤코 (+ 머리카락 눌러 넣기)
    fairy.guard_uniform(e, P, rank="soldier")               # 흰 튜닉 + 초록 연미복 + 흰 바지 + 검은 롱부츠
"""
from __future__ import annotations

import math

import bmesh
import bpy

import cb
import elf
import erpien_flag as ef
from elf import V, Matrix, Buf, loft, band, rbox, disc, keys, lerp, smoothstep, mixw, clamp, frame, catmull

# =========================================================================== 팔레트 (원작 이미지 지배색 근사)

#: 요정 경비대 기본 팔레트. 폴랑 카드·경비대 GIF·PV 2:40~2:55에서 눈으로 뽑았다(docs/art/fairy-faction.md 2장).
GUARD = {
    "green": "#2f6a4f",      # 샤코·연미복 초록
    "green_d": "#21483a",    # 소맷단, 가장자리
    "white": "#f5f2f3",      # 튜닉·바지
    "white_d": "#ddd6dd",    # 튜닉 여밈, 접힘
    "gold": "#e8c178",       # 금장 (나비, 끈, 토글)
    "gold_d": "#c49448",     # 금장 그림자
    "black": "#3a3439",      # 샤코 띠·챙, 롱부츠
    "black_d": "#29242a",    # 밑창
    "glove": "#fbf8f6",      # 흰 장갑
    "wing": "#fffdf9",       # 날개 (위 깃)
    "wing_d": "#f6e6cf",     # 날개 (아래 깃, 크림빛)
}


def mats(prefix, pal):
    """팔레트 사전 → 머티리얼 사전 (이름 = prefix_키)."""
    return {kk: elf.mat(f"{prefix}_{kk}", v) for kk, v in pal.items()}


# =========================================================================== 몸: 엘프 키트 + 둥근 귀

def Fairy(name, *, ears="round", ear_size=1.0, **kw):
    """요정 한 명: 엘프 키트 몸·리그·머리 + 사람 귀(둥근 귀). ears=None이면 귀를 만들지 않는다(머리카락에 덮일 때).
    ear_L/ear_R 본은 리그 호환을 위해 그대로 남는다(둥근 귀는 head 본 100%)."""
    e = elf.Elf(name, ear_inner=False, **kw)
    e.remove("ear_L")
    e.remove("ear_R")
    if ears == "round":
        round_ears(e, size=ear_size)
    e.fairy = True
    return e


def round_ears(e, *, size=1.0, inner="#f2b8b0"):
    """사람 귀: 머리 옆 눈높이 조금 아래, 납작한 반타원 + 안쪽 분홍 홈. head 본 100%. [키트 후보: Elf(ears='round')]"""
    k = e.k
    m = e.skin_mat
    mi = elf.mat(f"{e.name}_ear_in", elf.mix_hex(e.skin_hex, inner, 0.5))
    for side, s in (("L", 1), ("R", -1)):
        z = e.eye_z() - 0.020 * k
        hit = e.head_bvh.ray_cast(V((s * 1.0, 0.010 * k, z)), V((-s, 0, 0)))
        root = hit[0] if hit[0] else V((s * e.hw / 2, 0, z))
        nrm = V((s, 0.18, 0.0)).normalized()
        up = V((0, 0.22, 1.0)).normalized()
        fwd = nrm.cross(up).normalized() * (-s)
        buf = Buf()
        w = {"head": 1.0}
        c = root + nrm * (0.004 * k * size)
        ellipsoid(buf, c, up, fwd, nrm, 0.030 * k * size, 0.019 * k * size, 0.011 * k * size, segs=10, rings=6,
                  mat=m, w=w)
        ellipsoid(buf, c + nrm * (0.0075 * k * size) - up * (0.002 * k * size), up, fwd, nrm,
                  0.019 * k * size, 0.010 * k * size, 0.0032 * k * size, segs=8, rings=5, mat=mi, w=w)
        ob = buf.obj(f"{e.name}_ear_{side}", angle=60.0)
        e.add(ob, group="head", tag=f"ear_{side}")


# =========================================================================== 얼굴: 키트 Face + 별 눈 + 눈 가림

class FairyFace(elf.Face):
    """키트 얼굴 + 요정 인물 표식. [키트 후보: Face(star=, eyes=)]

    star:  None | "sparkle"(홍채 가운데 흰 네 갈래 반짝임 ✦, 폴랑) | "pupil"(동공 대신 노란 다섯 꼭지 별, 에르핀)
    star_color, star_size: 별 색과 크기 배율.
    eyes=False: 눈을 그리지 않고 앞머리 그늘 띠(shade)만 둔다(요정 경비대: 원작 단역은 앞머리로 눈을 가린다).
    mole: (x, z) 얼굴 정면 좌표(눈 중심 기준 배율 단위)의 점(눈물점). side: +1 왼눈(+X), -1 오른눈."""

    def __init__(self, e, *, star=None, star_color="#ffffff", star_size=1.0, eyes=True, shade="#e2b9b8",
                 mole=None, mole_color="#6a3a40", **kw):
        super().__init__(e, **kw)
        self.star = star
        self.star_size = star_size
        self.eyes = eyes
        self.mole = mole
        n = e.name
        self.m["star"] = elf.mat(f"{n}_f_star", star_color, unlit=(star == "sparkle"))
        self.m["shade"] = elf.mat(f"{n}_f_shade", shade)
        self.m["mole"] = elf.mat(f"{n}_f_mole", mole_color)

    def _iris_c(self, side, P):
        ip = P["iris"]
        return side * self.ex + side * ip["cx"] * self.sz, self.ez + ip["cz"] * self.sz

    def _build(self, P):
        if not self.eyes:
            return self._build_hidden(P)
        buf = super()._build(P)
        sz = self.sz
        m = self.m
        for side in (1, -1):
            outline, _ = self.eye_outline(side, P)
            icx, icz = self._iris_c(side, P)
            ip = P["iris"]
            if self.star == "sparkle":
                r = 0.0140 * sz * self.star_size
                pts = []
                for i in range(16):
                    a = math.radians(90 + 22.5 * i)
                    rr = r if i % 4 == 0 else (r * 0.30 if i % 2 else r * 0.18)
                    pts.append((icx + rr * math.cos(a) * 0.92, icz - 0.0030 * sz + rr * math.sin(a)))
                self._fill(buf, elf.clip_to(pts, outline), 0.0028, m["star"], rings=())
            elif self.star == "pupil":
                r = ip["rx"] * sz * 0.62 * self.star_size * ip["pupil"]
                pts = star_poly(r, r * 0.45, 5, 90.0, icx, icz + 0.002 * sz)
                self._fill(buf, elf.clip_to(pts, outline), 0.0027, m["star"], rings=(0.55,))
        if self.mole:
            mx, mz = self.mole
            side = 1 if mx > 0 else -1
            cx = side * self.ex + mx * sz
            pts = elf.ellipse2(cx, self.ez + mz * sz, 0.0026 * sz, 0.0026 * sz, 8)
            self._fill(buf, pts, 0.0012, m["mole"], rings=())
        return buf

    def _build_hidden(self, P):
        """눈 없는 얼굴: 앞머리 그늘 띠 + 볼터치 + 입 (원작 요정 경비대 단역)."""
        buf = Buf()
        m = self.m
        sz = self.sz
        # 앞머리 그늘: 눈썹 위에서 눈 아래까지, 아랫단이 앞머리 끝처럼 물결
        top = []
        bot = []
        n = 15
        W = self.ex + 0.050 * sz
        for i in range(n):
            s = -1 + 2 * i / (n - 1)
            x = s * W
            top.append((x, self.ez + 0.060 * sz - 0.010 * sz * s * s))
            wave = 0.006 * sz * math.cos(s * math.pi * 3.5)
            bot.append((x, self.ez - 0.022 * sz - 0.012 * sz * (1 - s * s) + wave))
        poly = bot + list(reversed(top))
        self._fill(buf, poly, 0.0010, m["shade"], rings=(0.6,))
        # 볼터치 (그늘 아래)
        bs = self.blush_size
        for side in (1, -1):
            bx, bz = side * self.ex + side * 0.034 * sz, self.ez - 0.050 * sz
            self._fill(buf, elf.ellipse2(bx, bz, 0.031 * sz * bs, 0.0175 * sz * bs, 20), 0.0014, m["blush"],
                       rings=(0.7, 0.4))
        # 입 (키트와 같은 방식)
        mq = P["mouth"]
        mw = mq["w"] * sz / 2
        mz = self.ez - 0.074 * sz + mq["dz"] * sz
        nn = 11
        tp, bt = [], []
        for i in range(nn):
            s = -1 + 2 * i / (nn - 1)
            v = mq["curve"] * sz * s * s + mq["top_arch"] * sz * (1 - s * s)
            v += mq["wave"] * sz * math.sin(s * math.pi * 2.0)
            tp.append((s * mw, mz + v))
            o = mq["open"] * sz * elf._sup(s, 1.6)
            bt.append((s * mw, mz + v - o - 0.0002))
        poly = list(reversed(tp + list(reversed(bt[1:-1]))))
        self._fill(buf, poly, 0.0008, m["mouth"], rings=())
        tng = elf.clip_to(elf.ellipse2(0.0, mz - mq["open"] * sz * 0.85, mw * 0.55,
                                       max(mq["open"] * sz * 0.45, 0.0003), 14), poly)
        self._fill(buf, tng, 0.0012, m["tongue"], rings=())
        wl = [0.0026 * sz * keys([(0, 0.45), (0.2, 1.0), (0.8, 1.0), (1, 0.45)], i / (nn - 1)) for i in range(nn)]
        self._stroke(buf, tp, wl, 0.0016, m["mline"])
        wl2 = [0.0016 * sz * keys([(0, 0.3), (0.3, 1.0), (0.7, 1.0), (1, 0.3)], i / (nn - 1)) for i in range(nn)]
        self._stroke(buf, bt, wl2, 0.0014, m["mline"])
        return buf


def face(e, **kw):
    """요정 얼굴 (e.face()와 같은 인자 + FairyFace의 star/eyes/mole). 표정 셰이프 키·교정 키 규칙은 키트와 같다."""
    f = FairyFace(e, **kw)
    ob = f.build()
    vc = elf.vc_material(f"{e.name}_toon_vc", e.line)
    elf.bake_vcol(ob)
    elf.remap_to_vc(ob, vc)
    elf.collapse_slots(ob)
    e.face_obj = ob
    e.face_builder = f
    return ob


# =========================================================================== 날개 (데포르메 깃털 날개, 엘다인 막 날개)

def wing_outline(L, H, lobes=3, *, bulge=0.85, top_bulge=1.12, lobe_w=None, bottom=(0.10, -0.12), n_top=10,
                 n_lobe=6, droop=0.35):
    """데포르메 깃털 날개 2D 외곽선 (x=바깥, z=위, 뿌리 (0,0), 반시계).
    위 테두리는 뿌리에서 바깥 위 끝(tip)까지 매끈한 호. 아랫단은 끝(tip)에서 뿌리 쪽 아래 bottom까지 둥근 깃 끝 lobes개가
    아래·바깥을 향해 늘어진다(끝 쪽 깃이 가장 크다: lobe_w는 뿌리 쪽 → 끝 쪽 순서). droop: 깃 끝을 아래로 기울이는 정도.
    반환: (점 목록, 각 점의 홈 정도 0~1: 깃 사이 오목한 곳 = 1)."""
    tip = (L, H)
    E = (bottom[0] * L, bottom[1] * H)
    lobe_w = lobe_w or [0.70 + 0.30 * i / max(lobes - 1, 1) for i in range(lobes)]
    tot = sum(lobe_w)
    pts, notch = [(0.0, 0.0)], [0.0]
    acc = 0.0
    for i, wv in enumerate(lobe_w):
        t0, t1 = acc / tot, (acc + wv) / tot
        acc += wv
        # 기준선 E → tip (가운데가 살짝 아래로 처진 호)
        def base(t):
            x = lerp(E[0], tip[0], t)
            z = lerp(E[1], tip[1], t ** 1.6) - 0.10 * H * math.sin(math.pi * t)
            return x, z
        p0, p1 = base(t0), base(t1)
        dx, dz = p1[0] - p0[0], p1[1] - p0[1]
        seg = math.hypot(dx, dz) or 1e-6
        nx, nz = dz / seg, -dx / seg          # 진행 방향 오른쪽 = 바깥(아래)
        nx, nz = nx * (1 - droop) + 0.25 * droop, nz * (1 - droop) - droop
        nl = math.hypot(nx, nz)
        nx, nz = nx / nl, nz / nl
        for j in range(n_lobe):
            t = j / n_lobe
            prof = math.sin(math.pi * t) ** 0.65
            b = bulge * seg * prof * (0.85 + 0.15 * wv)
            pts.append((p0[0] + dx * t + nx * b, p0[1] + dz * t + nz * b))
            notch.append(1.0 - math.sin(math.pi * t) ** 0.5)
    # 위 테두리: tip → 뿌리 (2차 베지어)
    c1 = (0.42 * L, top_bulge * H)
    r0 = (0.0, 0.18 * H)
    for j in range(n_top + 1):
        t = j / n_top
        x = (1 - t) ** 2 * tip[0] + 2 * (1 - t) * t * c1[0] + t * t * r0[0]
        z = (1 - t) ** 2 * tip[1] + 2 * (1 - t) * t * c1[1] + t * t * r0[1]
        pts.append((x, z))
        notch.append(1.0 if j == 0 else 0.0)
    return pts, notch


def pillow(buf, outline, notch, center, M, th, *, rings=4, mat=None, wfn=None, groove=0.35, p=2.2, flat=0.0):
    """2D 외곽선을 부푼 쿠션(가장자리 얇고 가운데 두꺼운 렌즈)으로 만든다. M: 2D (x,z) → 월드 (로컬 Y = 두께).
    outline은 center에서 보이는 별 모양이어야 한다. notch(점별 0~1)는 깃 사이 홈 깊이. 닫힌 메시 하나.
    flat: 0이면 양면 대칭, >0이면 뒷면을 그만큼 납작하게."""
    cx, cz = center
    n = len(outline)
    wf = wfn or (lambda q: {})
    mirror = M.to_3x3().determinant() < 0
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(outline, outline[1:] + outline[:1]))
    flip_all = (area > 0) != mirror   # 반시계 외곽선 + 오른손 행렬이면 윗면(+Y)을 뒤집어야 바깥을 본다

    def P(i, s, sign):
        x, z = outline[i]
        u = s
        h = th * (1 - u ** p) ** 0.55
        h *= 1 - groove * notch[i] * smoothstep(0.35, 1.0, u)
        if sign < 0:
            h *= (1 - flat)
        q = (cx + (x - cx) * u, cz + (z - cz) * u)
        return M @ V((q[0], sign * h, q[1]))

    edge = []
    for i in range(n):
        q = P(i, 1.0, 1)
        edge.append(buf.vert(q, wf(q)))
    lay = {1: [], -1: []}
    for sign in (1, -1):
        for r in range(1, rings):
            s = 1.0 - r / rings
            row = []
            for i in range(n):
                q = P(i, s, sign)
                row.append(buf.vert(q, wf(q)))
            lay[sign].append(row)
    ctr = {}
    for sign in (1, -1):
        q = M @ V((cx, sign * th * (1 - flat * (sign < 0)), cz))
        ctr[sign] = buf.vert(q, wf(q))
    for sign in (1, -1):
        rows = [edge] + lay[sign]
        fwd = (sign > 0) != flip_all
        for a in range(len(rows) - 1):
            r0, r1 = rows[a], rows[a + 1]
            for i in range(n):
                j = (i + 1) % n
                f = (r0[i], r0[j], r1[j], r1[i])
                buf.face(f if fwd else tuple(reversed(f)), mat)
        last = rows[-1]
        for i in range(n):
            j = (i + 1) % n
            f = (last[i], last[j], ctr[sign])
            buf.face(f if fwd else tuple(reversed(f)), mat)


def _wing_frame(e, side, *, z, sweep, raise_, inset=0.0, angle=160.0):
    """날개 뿌리 위치와 2D→월드 행렬. 바깥 방향은 옆에서 뒤로 sweep도, 날개 면은 raise_도 들어 올린다."""
    s = 1 if side == "L" else -1
    k = e.k
    root, nrm = e.torso_point(z, s * angle, -inset * k)
    sw = math.radians(sweep)
    ox = V((s * math.cos(sw), math.sin(sw), 0.0))
    up = V((0, 0, 1))
    ra = math.radians(raise_)
    X = (ox * math.cos(ra) + up * math.sin(ra)).normalized()
    Z = (up * math.cos(ra) - ox * math.sin(ra)).normalized()
    # 로컬 +Y(두께 방향)는 양쪽 모두 몸 뒤쪽을 향하게 한다 → 오른쪽 날개 행렬은 왼손 좌표계(행렬식 < 0).
    # pillow()/membrane_wing()이 행렬식을 보고 면 방향을 뒤집는다.
    Y = Z.cross(X).normalized() if s > 0 else X.cross(Z).normalized()
    M = Matrix((X, Y, Z)).transposed().to_4x4()
    M.translation = root
    return M, root, X, Z


def egg_poly(c, a, b, ang, *, n=12, egg=0.18):
    """2D 달걀꼴 (긴 반지름 a, 짧은 반지름 b, ang도 방향). +a 쪽 끝이 egg만큼 더 넓다. 반시계."""
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = a * math.cos(t)
        y = b * math.sin(t) * (1 + egg * math.cos(t))
        pts.append((c[0] + x * ca - y * sa, c[1] + x * sa + y * ca))
    return pts


def feather_poly(base, length, width, ang, *, n=9, tip=1.0, bend=0.0, asym=0.82, root=0.22):
    """깃 하나 2D 외곽선 (반시계). base: 깃 뿌리 (x, z), ang: 뿌리 → 끝 방향(도), length·width: 길이·최대 폭.
    뿌리는 둥글게 좁고, 가운데가 가장 넓고, 끝은 뾰족하다(tip: 1 = 뾰족, 0 = 둥근 끝). bend: 끝을 진행 방향 오른쪽(아래·바깥)
    으로 휘는 정도(길이 비). asym: 앞 깃판(왼쪽)의 폭 비 (실제 깃처럼 앞쪽이 좁다)."""
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    nx, nz = sa, -ca                      # 진행 방향 오른쪽

    def half(u):
        grow = smoothstep(0.0, root, u) ** 0.6
        taper = (1.0 - u ** (2.4 - 1.2 * (1 - tip))) ** (0.55 + 0.25 * tip)
        return 0.5 * width * max(grow * taper, 0.0)

    def at(u, v):
        off = bend * length * u * u
        x = base[0] + ca * length * u + nx * (v + off)
        z = base[1] + sa * length * u + nz * (v + off)
        return (x, z)
    us = [0.0] + [((i / n) ** 0.85) for i in range(1, n + 1)]
    right = [at(u, half(u)) for u in us[1:-1]]
    left = [at(u, -half(u) * asym) for u in reversed(us[1:-1])]
    return [at(0.0, 0.0)] + right + [at(1.0, 0.0)] + left


def _centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def cupid_outline(L, H, lobes=3, *, curl=0.12, depth=0.55, n_top=16, n_lobe=9):
    """큐피드형 날개 한 장 2D 외곽선 (x=바깥, z=위, 뿌리 (0,0)). 앞 테두리는 뿌리에서 위로 볼록하게 올라가 끝(tip)이 살짝
    말려 오르고, 뒤 테두리는 끝에서 뿌리 쪽 아래까지 둥근 물결 lobes개 (끝 쪽 물결이 가장 크다). 원작 에르핀·폴랑 일러의 날개.
    반환: 점 목록 (뿌리 → 앞 테두리 → 끝 → 물결 → 뿌리 아래)."""
    def bez(p0, p1, p2, p3, t):
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t * t
        d = t ** 3
        return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])
    r0 = (0.0, 0.10 * H)
    tip = (L, (1.0 + curl) * H)
    top = [bez(r0, (0.10 * L, 0.80 * H), (0.55 * L, 1.10 * H), tip, j / n_top) for j in range(n_top + 1)]
    # 뒤 테두리 기준선: 끝 → 뿌리 아래 (가운데가 바깥 아래로 처진 호)
    E = (0.04 * L, -0.30 * H)
    ws = [1.0 + 0.45 * (lobes - 1 - i) / max(lobes - 1, 1) for i in range(lobes)]   # 끝 쪽(i=0)이 크다
    tot = sum(ws)
    pts = list(top)
    acc = 0.0

    def base(t):
        x = lerp(tip[0], E[0], t)
        z = lerp(tip[1], E[1], t ** 0.8) - 0.12 * H * math.sin(math.pi * t)
        return x, z
    for i, wv in enumerate(ws):
        t0, t1 = acc / tot, (acc + wv) / tot
        acc += wv
        p0, p1 = base(t0), base(t1)
        dx, dz = p1[0] - p0[0], p1[1] - p0[1]
        seg = math.hypot(dx, dz) or 1e-6
        nx, nz = -dz / seg, dx / seg            # 진행 방향 왼쪽 = 날개 바깥(아래·바깥)
        for j in range(1, n_lobe + 1):
            t = j / n_lobe
            b = depth * 0.5 * seg * math.sin(math.pi * t) ** 0.8
            pts.append((p0[0] + dx * t + nx * b, p0[1] + dz * t + nz * b))
    return pts


def _warc(p0, p1, bulge, n):
    """p0 → p1 호 (끝점 p1 포함, p0 제외). bulge: 진행 방향 왼쪽으로 부풀린 정도(길이 비, 음수면 오른쪽)."""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dz) or 1e-6
    nx, nz = -dz / ln, dx / ln
    out = []
    for j in range(1, n + 1):
        t = j / n
        b = bulge * ln * 4 * t * (1 - t)
        out.append((p0[0] + dx * t + nx * b, p0[1] + dz * t + nz * b))
    return out


def _wpath(start, legs):
    """start에서 (끝점, bulge, 점 수) 다리를 차례로 이어 닫힌 외곽선을 만든다 (마지막 다리는 start로 돌아온다)."""
    pts = [start]
    cur = start
    for end, bulge, n in legs:
        seg = _warc(cur, end, bulge, n)
        pts.extend(seg)
        cur = end
    if math.hypot(pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]) < 1e-6:
        pts.pop()
    return pts


def erpin_wing_outline(L, H):
    """에르핀 날개 (원작 일러, 레퍼런스로만 봄): 뿌리에서 앞 테두리가 위로 솟아 초승달처럼 말린 뾰족한 갈고리 끝,
    그 아래 바깥으로 뻗은 끝이 뾰족한 깃 둘, 아래·뿌리 쪽 테두리는 둥글다. 반환: (흰 외곽선, 분홍 아랫부분 외곽선)."""
    R0, T1, N1, T2, N2, T3, R1 = ((0.0, 0.42 * H), (0.62 * L, 1.30 * H), (0.56 * L, 0.74 * H), (1.0 * L, 0.60 * H),
                                  (0.60 * L, 0.38 * H), (0.86 * L, 0.10 * H), (0.12 * L, 0.0))
    white = _wpath(R0, [(T1, 0.24, 12), (N1, -0.16, 6), (T2, 0.12, 7), (N2, 0.16, 6), (T3, 0.12, 6), (R1, 0.16, 8),
                        (R0, 0.22, 6)])
    pink = _wpath((0.34 * L, 0.56 * H), [((0.58 * L, 0.70 * H), 0.0, 2), (T2, 0.12, 7), (N2, 0.16, 6), (T3, 0.12, 6),
                                          ((0.24 * L, 0.04 * H), 0.16, 6), ((0.34 * L, 0.56 * H), 0.10, 4)])
    return white, pink


def guard_wing_outline(L, H):
    """요정 경비대 날개 (원작 GIF): 뿌리 쪽 둥근 혹에서 바깥 위로 가늘어져 뾰족한 끝 하나 (누운 물방울).
    아래 테두리는 끝에서 돌아오며 얕은 물결 하나. 반환: (바깥 외곽선, 뿌리 쪽 밝은 혹 외곽선)."""
    R0, TOP, TIP, NB, BOT = (0.0, 0.22 * H), (0.26 * L, 0.86 * H), (L, 0.96 * H), (0.56 * L, 0.34 * H), (0.22 * L, -0.24 * H)
    outer = _wpath(R0, [(TOP, 0.26, 8), (TIP, 0.06, 9), (NB, 0.12, 7), (BOT, 0.22, 6), (R0, 0.30, 7)])
    inner = _wpath((0.06 * L, 0.24 * H), [((0.28 * L, 0.70 * H), 0.30, 7), ((0.50 * L, 0.46 * H), 0.12, 4),
                                          ((0.28 * L, -0.08 * H), 0.24, 6), ((0.06 * L, 0.24 * H), 0.26, 6)])
    return outer, inner


def slab(buf, outline, M, th, *, mat=None, wfn=None, y0=0.0):
    """2D 외곽선(오목해도 된다)을 두께 th의 납작한 판으로 (위·아래 면은 n각형, 옆면은 띠). M: 2D (x,z) → 월드 (로컬 Y = 두께).
    y0: 판 가운데의 로컬 Y (겹친 층을 앞뒤로 띄울 때). 부푼 쿠션과 달리 테두리가 또렷해 툰 외곽선이 그림 같은 선이 된다."""
    wf = wfn or (lambda q: {})
    mirror = M.to_3x3().determinant() < 0
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(outline, outline[1:] + outline[:1]))
    flip = (area > 0) != mirror
    top, bot = [], []
    for x, z in outline:
        q1 = M @ V((x, y0 + th / 2, z))
        q2 = M @ V((x, y0 - th / 2, z))
        top.append(buf.vert(q1, wf(q1)))
        bot.append(buf.vert(q2, wf(q2)))
    n = len(outline)
    t = tuple(top) if not flip else tuple(reversed(top))
    b = tuple(reversed(bot)) if not flip else tuple(bot)
    buf.face(t, mat)
    buf.face(b, mat)
    for i in range(n):
        j = (i + 1) % n
        f = (top[i], bot[i], bot[j], top[j])
        buf.face(f if not flip else tuple(reversed(f)), mat)


def wing_pieces(L, H, *, prim=3, cov=3, spread=1.0, droop=0.0, style="feather"):
    """데포르메 날개 조각 (2D, x=바깥, z=위, 뿌리 (0,0)). 조각마다 얇은 판이고, 겹친 경계의 아웃라인이 깃 사이 선이 된다.
    2026-11-04 사용자 「날개라고 무슨 솜뭉텅를 붙여놨네」「요정마다 날개 모양이 다르다는건 알아야 할텐데」로 부푼 달걀 쿠션을
    버리고 원작 그림(나무위키 요정 문서 이미지, 레퍼런스로만 봄)에 맞춰 모양을 셋으로 나눴다:
      'cupid'   둥근 깃 끝 2~3개가 아래로 물결치고 앞 테두리가 위로 볼록한 작은 날개 (폴랑·에르핀·경비대·주민 요정)
      'slender' 가늘고 끝이 뾰족한 깃 몇 장이 바깥 아래로 퍼지는 날개 (각성 전 네르)
      'feather' 긴 깃 여러 장 + 덮깃이 부채처럼 겹친 큰 날개 (엘다인: 에르핀(왕도)·네르(빡침), 벨리타)
    반환: [(외곽선, 중심, 층, 두께 배율), ...] 층: 'arm' | 'cov' | 'prim'."""
    out = []
    D = math.hypot(L, H)
    arm_ang = math.degrees(math.atan2(H, L))

    def along(t):
        # 앞 테두리: 뿌리에서 위로 볼록한 호를 그리며 끝으로
        return (L * t, H * t ** 0.9 + 0.16 * H * math.sin(math.pi * t))

    def add(pts, layer, tk):
        out.append((pts, _centroid(pts), layer, tk))

    if style == "cupid":
        n = max(prim, 2)
        # 앞 테두리 덩어리: 넓고 둥글다 (위로 볼록, 끝이 살짝 말려 오름)
        add(feather_poly((-0.06 * L, -0.02 * H), 1.02 * D, 0.62 * D, arm_ang + 2.0, n=14, tip=0.05, bend=-0.10,
                         asym=1.0, root=0.34), "arm", 1.0)
        # 둥근 깃 끝 (아래로 물결): 끝 쪽이 가장 길고 바깥으로
        for i in range(n):
            u = i / max(n - 1, 1)
            t = lerp(0.80, 0.30, u)
            ln = lerp(0.70, 0.52, u) * D * spread
            wd = lerp(0.46, 0.50, u) * D
            ph = lerp(arm_ang - 46.0, -88.0, u) - droop
            P = along(t)
            add(feather_poly((P[0], P[1] - 0.10 * H), ln, wd, ph, n=10, tip=0.0, bend=0.06, asym=1.0, root=0.3),
                "prim", 1.0)
        for i in range(min(cov, n - 1)):
            u = (i + 0.5) / max(n - 1, 1)
            t = lerp(0.72, 0.36, u)
            ln = lerp(0.42, 0.36, u) * D * spread
            wd = lerp(0.40, 0.42, u) * D
            ph = lerp(arm_ang - 50.0, -86.0, u) - droop
            P = along(t)
            add(feather_poly(P, ln, wd, ph, n=8, tip=0.0, bend=0.04, asym=1.0, root=0.3), "cov", 1.05)
        return out

    if style == "slender":
        n = max(prim, 3)
        add(feather_poly((-0.03 * L, 0.0), 0.62 * D, 0.20 * D, arm_ang + 6.0, n=10, tip=0.6, bend=-0.04, asym=0.9),
            "arm", 1.0)
        for i in range(n):
            u = i / max(n - 1, 1)
            t = lerp(0.62, 0.18, u)
            ln = lerp(1.00, 0.70, u) * D * spread
            wd = lerp(0.20, 0.18, u) * D
            ph = lerp(arm_ang - 18.0, arm_ang - 62.0, u) - droop
            P = (L * 0.62 * t, H * 0.62 * t)
            add(feather_poly(P, ln, wd, ph, n=10, tip=1.0, bend=0.03, asym=0.75), "prim", 1.0)
        return out

    # 'feather': 큰 깃털 날개
    prim = max(prim + 2, 5)
    cov = max(cov + 1, 3)
    add(feather_poly((-0.04 * L, 0.02 * H), 0.98 * D, 0.40 * min(L, H) + 0.14 * D, arm_ang + 4.0, n=12, tip=0.3,
                     bend=-0.06, asym=0.9, root=0.30), "arm", 1.15)
    for i in range(prim):
        u = i / max(prim - 1, 1)
        t = lerp(0.98, 0.28, u)
        ln = lerp(0.78, 0.60, u) * D * spread
        wd = lerp(0.30, 0.34, u) * D
        ph = lerp(arm_ang - 42.0, -96.0, u ** 0.9) - droop
        P = along(t)
        P = (P[0] - 0.03 * D * math.cos(math.radians(ph)), P[1] - 0.05 * H)
        add(feather_poly(P, ln, wd, ph, n=10, tip=0.85, bend=0.05, asym=0.8), "prim", 1.0)
    for i in range(cov):
        u = i / max(cov - 1, 1)
        t = lerp(0.86, 0.22, u)
        ln = lerp(0.42, 0.34, u) * D * spread
        wd = lerp(0.30, 0.32, u) * D
        ph = lerp(arm_ang - 50.0, -95.0, u) - droop
        P = along(t)
        add(feather_poly(P, ln, wd, ph, n=8, tip=0.7, bend=0.04, asym=0.85), "cov", 1.1)
    return out


def wings(e, *, span=0.30, height=None, prim=3, cov=3, sweep=15.0, raise_=8.0, z=None, color=None, color2=None,
          th=0.0075, bones=True, name="wings", rings=2, inset=0.010, mat=None, mat2=None, root_angle=152.0,
          spread=1.0, droop=0.0, lobes=None, style="feather"):
    """데포르메 깃털 날개 한 쌍 (원작 요정의 작은 날개). [키트 후보: e.wings()]
    span: 뿌리에서 끝까지(m), height: 끝의 높이(m). 조각: 위 팔(color) + 덮깃 cov개(color) + 긴 깃 prim개(color2).
    sweep: 옆에서 뒤로 젖힌 각, raise_: 위로 든 각. 본: wing_L_01/02, wing_R_01/02 (chest 자식).
    날개는 등에 붙어 1인칭에서 보이지 않으므로 body 그룹. 반환: {side: (본 사슬, 2D→월드 행렬)}"""
    k = e.k
    L = span * k
    H = (height or span * 0.58) * k
    zc = z if z is not None else e.chest_z + 0.060 * k
    m_prim = mat2 or elf.mat(f"{e.name}_wing_d", color2 or GUARD["wing_d"])
    m_top = mat or elf.mat(f"{e.name}_wing", color or GUARD["wing"])
    if lobes:
        prim, cov = lobes
    pieces = wing_pieces(L, H, prim=prim, cov=cov, spread=spread, droop=droop, style=style)
    out = {}
    for side in ("L", "R"):
        M, root, X, Z = _wing_frame(e, side, z=zc, sweep=sweep, raise_=raise_, inset=inset, angle=root_angle)
        mid = M @ V((0.48 * L, 0.0, 0.42 * H))
        tip = M @ V((L, 0.0, H))
        ch = None
        if bones:
            b1, b2 = f"wing_{side}_01", f"wing_{side}_02"
            e.add_bone(b1, root, mid, "chest")
            e.add_bone(b2, mid, tip, b1)
            ch = elf.Chain([root, mid, tip], [b1, b2], start={"chest": 1.0}, start_blend=0.6)
        Minv = M.inverted()

        def wfn(q, ch=ch, Minv=Minv):
            if ch is None:
                return {"chest": 1.0}
            lq = Minv @ q
            t = clamp(math.hypot(lq.x / L, max(lq.z, 0.0) / H * 0.5) / 1.02)
            return ch.weights(t)

        buf = Buf()
        if style in ("erpin", "guard"):
            # 인물별 한 장짜리 날개 판 + 안쪽 색 판 (원작 일러의 외곽선)
            fn = erpin_wing_outline if style == "erpin" else guard_wing_outline
            a, b = fn(L, H)
            cx, cz = _centroid(b)
            b = [(cx + (x - cx) * 0.86, cz + (z - cz) * 0.86) for x, z in b]   # 안쪽 색 판은 테두리를 남긴다
            slab(buf, a, M, th * k * 1.4, mat=m_top, wfn=wfn)
            slab(buf, b, M, th * k * 0.8, mat=m_prim, wfn=wfn, y0=th * k * 1.2)
            ob = buf.obj(f"{e.name}_{name}_{side}", angle=40.0)
            e.add(ob, group="body", tag=f"{name}_{side}")
            out[side] = (ch, M)
            continue
        if style == "cupid":
            # 큐피드형: 한 장짜리 납작한 판 (위 색) + 안쪽 아래에 작은 물결 판 한 장 (color2: 원작의 크림·분홍 안쪽)
            n_l = max(prim, 2)
            slab(buf, cupid_outline(L, H, n_l + 1, depth=0.85), M, th * k * 1.6, mat=m_top, wfn=wfn)
            inner = [(0.10 * L + 0.80 * x, -0.06 * H + 0.72 * z) for x, z in cupid_outline(L, H, n_l, curl=0.0, depth=0.5)]
            slab(buf, inner, M, th * k * 1.0, mat=m_prim, wfn=wfn, y0=th * k * 1.4)
            ob = buf.obj(f"{e.name}_{name}_{side}", angle=40.0)
            e.add(ob, group="body", tag=f"{name}_{side}")
            out[side] = (ch, M)
            continue
        for pts, c, layer, tk in pieces:
            mm = m_prim if layer == "prim" else m_top
            pillow(buf, pts, [0.0] * len(pts), c, M, th * k * tk, rings=rings, mat=mm, wfn=wfn, groove=0.0, p=5.0)
        ob = buf.obj(f"{e.name}_{name}_{side}", angle=55.0)
        e.add(ob, group="body", tag=f"{name}_{side}")
        out[side] = (ch, M)
    return out


def membrane_wing(e, side, M, outline, mat, *, wfn=None, veins=None, vein_mat=None, vein_r=0.0016, name="membrane",
                  rings=3, center=None, lift=0.0):
    """엘다인 막 날개 한 장: 2D 외곽선(M 평면)을 얇은 반투명 판으로 + 맥(vein) 관. 반투명 재질은 키트 병합에서 빠져
    따로 남고 아웃라인도 생략된다(toon.ts: transparent). veins: [[(x,z), ...], ...] 2D 선 목록. [키트 후보]"""
    n = len(outline)
    cx = sum(p[0] for p in outline) / n if center is None else center[0]
    cz = sum(p[1] for p in outline) / n if center is None else center[1]
    wf = wfn or (lambda q: {})
    buf = Buf()
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
            buf.face((rows[a][i], rows[a][j], rows[a + 1][j], rows[a + 1][i]), mat)
    for i in range(n):
        j = (i + 1) % n
        buf.face((rows[-1][i], rows[-1][j], ci), mat)
    if veins and vein_mat is not None:
        for line in veins:
            P = catmull([M @ V((x, lift, z)) for x, z in line], max(6, 3 * len(line)))
            st = []
            for i, q in enumerate(P):
                t = i / (len(P) - 1)
                r_ = vein_r * (1.0 - 0.6 * t)
                st.append({"c": q, "rx": r_, "ry": r_ * 0.7, "w": wf(q),
                           "ref": tuple(M.to_3x3() @ V((0, 1, 0)))})
            loft(buf, st, segs=5, cap0="flat", cap1="round", mat=vein_mat)
    ob = buf.obj(f"{e.name}_{name}_{side}", angle=60.0)
    # 반투명 막을 불투명 몸 메시와 합치면 toon.ts가 아웃라인 헐을 붙여 막 뒤에 검은 판이 비친다 → 별도 노드 + noOutline
    e.add(ob, group="body", tag=f"{name}_{side}", node=f"wing_{name}", props={"noOutline": 1})
    return ob


# =========================================================================== 나비 문장 (요정 경비대)
# [원작] 요정 왕국 문장 = 에르피엔 군기의 나비 (lib/erpien_flag.py, 사용자 결정 2026-11-02). 경비대 샤코·부츠 원판·망토의
# 금색 나비도 깃발과 같은 도안을 쓴다 (예전 기하 재해석 나비를 바꿨다). 도안은 다시 그리지 않고 키트에서 가져온다.

def butterfly_poly(size, *, n=44, antennae=True, low=False):
    """에르피엔 나비 외곽선 (erpien_flag.outline). 중심 (0,0), 폭 size, 반시계. n < 40이면 성긴 분할(res 1).
    오목한 다각형이라 중심 부채로 채우는 prism()에 넣지 않는다 (emblem()이 키트 badge()로 판을 세운다). antennae는 예전 인자."""
    s = size / 2
    return [(x * s, z * s) for x, z in ef.outline(1 if n < 40 else 2, low)]


def emblem(buf, M, size, mat, *, depth=0.0025, w=None, back=None, back_scale=1.32, back_depth=0.0015, rim=None,
           n=44, back_n=16, line=None, low=False, warp=None):
    """나비 문장 배지: (원판 back + 금테 rim) + 에르피엔 나비 (erpien_flag.badge: 바탕 mat, 윤곽선 테 line).
    M 로컬: X-Z 평면, -Y 바깥. size = 나비 폭. line이 없으면 윤곽선 테 없이 바탕만. 말린 선은 넣지 않는다
    (인물 아웃라인 헐에 묻힌다). n < 40이면 성긴 외곽선(res 1), low면 원경용 점만.
    warp = 곡면에 감싸 붙이는 함수(erpien_flag.warp_sink): M @ 로컬 점을 받아 곡면 위 점을 돌려준다(샤코 앞면)."""
    d0 = 0.0
    if back is not None:
        prism(buf, [(x, z) for x, z in elf.ellipse2(0, 0, size * 0.5 * back_scale, size * 0.5 * back_scale * 0.92,
                                                    back_n)], back_depth, M, mat=back, w=w, chamfer=back_depth * 0.4)
        d0 = back_depth
        if rim is not None:
            band(buf, M @ V((0, -back_depth * 0.5, 0)), M.to_3x3() @ V((0, -1, 0)), M.to_3x3() @ V((1, 0, 0)),
                 size * 0.5 * back_scale, size * 0.5 * back_scale * 0.92, back_depth * 1.6, size * 0.06,
                 segs=back_n, mat=rim, w=w)
    sink = ef.buf_sink(buf, {"erf_yellow": mat, "erf_gold": line or mat}, w)
    ef.badge(ef.warp_sink(sink, warp) if warp else sink, M @ Matrix.Translation((0, -d0, 0)), size, depth=depth, res=1 if n < 40 else 2, low=low, edge=line is not None, strokes=False, sink_in=depth,
             fine=warp is not None)


# =========================================================================== 띠 도우미

def taper_strip(buf, pts, nrm, ups, widths, th, *, mat=None, w=None):
    """폭이 변하는 두께 있는 띠 하나 (금색 쐐기·가는 장식). pts/nrm/ups/widths는 점마다. 끝이 뾰족해도 한 덩어리."""
    n = len(pts)
    rings = []
    for i in range(n):
        c, nn, u = V(pts[i]), V(nrm[i]).normalized(), V(ups[i])
        u = (u - nn * u.dot(nn)).normalized()
        hw = max(widths[i] / 2, 1e-5)
        ww = w(i / max(n - 1, 1)) if callable(w) else (w or {})
        quad = [c + u * hw, c + u * hw + nn * th, c - u * hw + nn * th, c - u * hw]
        rings.append([buf.vert(q, ww) for q in quad])
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for a in range(4):
            b = (a + 1) % 4
            buf.face((r0[a], r0[b], r1[b], r1[a]), mat)
    buf.face(tuple(reversed(rings[0])), mat)
    buf.face(tuple(rings[-1]), mat)


# =========================================================================== 샤코 (요정 경비대 군모)

def shako(e, mats_, *, height=0.075, flare=0.10, tilt=6.0, off=0.030, front=18.0, side=8.0, back=-2.0,
          visor=0.062, cord=True, chevrons=True, butterfly=0.11, plume=None, pompom=None, top_gold=True,
          segs=None, band=0.27, name="shako"):
    """요정 경비대 샤코: 초록 원통(위가 조금 넓고 뒤로 기움) + 검은 아래 띠와 반짝이는 챙 + 금색 윗테 +
    앞을 가로지르는 금색 구슬 끈 + 양옆에서 가운데를 가리키는 금색 쐐기 + 가운데 금색 에르피엔 나비(군기와 같은 도안).
    plume=(재질, 재질2)이면 왼쪽 앞에 깃털 장식(폴랑), pompom=(재질, 재질2)이면 정면 위 방울(지휘관).
    height: 정수리(e.H) 위로 윗면 중심까지 높이(m). 아래 고리는 머리 표면을 따라 이마 위(front도)에 걸친다.
    머리카락은 샤코 안쪽으로 눌러 넣는다(e._hats). mats_: green, black, gold, gold_d 키."""
    k = e.k
    q = e.q
    o = off * k
    g, bl, au, au_d = mats_["green"], mats_["black"], mats_["gold"], mats_["gold_d"]
    nseg = segs or max(24, int(36 * q) // 2 * 2)
    e._hats = getattr(e, "_hats", [])

    def rim_el(az):
        a = abs(((az + 180) % 360) - 180)
        return front + (side - front) * smoothstep(0, 90, a) + (back - side) * smoothstep(90, 180, a)

    hc = e.head_c
    ta = math.radians(tilt)
    axis = V((0, math.sin(ta), math.cos(ta)))
    w = {"head": 1.0}
    # 아래 고리 (머리 표면을 따라)
    base, bn = [], []
    for j in range(nseg):
        az = 360.0 * j / nseg
        p, n_ = e.head_point(az, rim_el(az), o)
        base.append(p)
        bn.append(n_)
    top_c = V((hc.x, hc.y + 0.010 * k, e.H + height * k))
    rx0 = max(abs(p.x - hc.x) for p in base)
    ry0 = max(abs(p.y - hc.y) for p in base)

    def top_pt(j):
        az = math.radians(360.0 * j / nseg)
        d = V((math.sin(az) * (rx0 + flare * 0.5 * k) * 1.02, -math.cos(az) * (ry0 + flare * 0.5 * k), 0.0))
        # 윗면은 축에 수직: 기운 만큼 앞뒤 높이를 맞춘다
        return top_c + d + axis * 0.0 - V((0, 0, d.y * math.tan(ta)))

    tops = [top_pt(j) for j in range(nseg)]
    band_t = band
    ts = [0.0, 0.05, band_t, band_t + 0.02, 0.60, 0.94, 1.0]

    def ring_at(t):
        pts = []
        for j in range(nseg):
            a = base[j]
            b = tops[j]
            # 살짝 볼록한 옆면 (가운데가 조금 부풂)
            c = a.lerp(b, t)
            out = V((c.x - hc.x, c.y - hc.y, 0)).normalized()
            pts.append(c + out * (0.004 * k * math.sin(math.pi * t)))
        return pts

    def fn(buf):
        R = [[buf.vert(p, w) for p in ring_at(t)] for t in ts]
        for i in range(len(ts) - 1):
            mm = bl if ts[i + 1] <= band_t + 1e-6 else g
            for j in range(nseg):
                j2 = (j + 1) % nseg
                buf.face((R[i][j], R[i][j2], R[i + 1][j2], R[i + 1][j]), mm)
        # 윗면 (살짝 볼록)
        ct = buf.vert(top_c + axis * (0.006 * k), w)
        for j in range(nseg):
            j2 = (j + 1) % nseg
            buf.face((R[-1][j], R[-1][j2], ct), g)
        # 안쪽 입구 (머리와 사이를 막음)
        inner = [buf.vert(e.head_point(360.0 * j / nseg, rim_el(360.0 * j / nseg) + 3.0, o * 0.2)[0], w)
                 for j in range(nseg)]
        for j in range(nseg):
            j2 = (j + 1) % nseg
            buf.face((inner[j], inner[j2], R[0][j2], R[0][j]), bl)
        # 금색 윗테
        if top_gold:
            pts, nrm, ups = [], [], []
            for j in range(nseg):
                p = R[-2][j]
                pp = buf.v[p]
                out = V((pp.x - hc.x, pp.y - hc.y, 0)).normalized()
                pts.append(buf.v[R[-1][j]].lerp(pp, 0.5) - axis * 0.004 * k)
                nrm.append(out)
                ups.append(axis)
            elf._loop(buf, pts, nrm, ups, 0.016 * k, 0.003 * k, mat=au, w=w)
        # 챙 (앞쪽 반원, 아래로 기운 반짝이는 검정)
        if visor:
            nv = 13
            vin, vout = [], []
            for i in range(nv):
                u = -1 + 2 * i / (nv - 1)
                az = u * 72.0
                jf = (az % 360.0) / 360.0 * nseg
                j0 = int(jf) % nseg
                pp = buf.v[R[1][j0]].lerp(buf.v[R[1][(j0 + 1) % nseg]], jf - int(jf))
                out = V((pp.x - hc.x, pp.y - hc.y, 0)).normalized()
                L = visor * k * (1 - 0.55 * u * u)
                vin.append(pp - out * 0.004 * k)
                vout.append(pp + out * L + V((0, 0, -0.38 * L)))
            th_ = 0.006 * k
            a_ = [buf.vert(p, w) for p in vin]
            b_ = [buf.vert(p, w) for p in vout]
            a2 = [buf.vert(p - V((0, 0, th_)), w) for p in vin]
            b2 = [buf.vert(p - V((0, 0, th_)), w) for p in vout]
            for i in range(nv - 1):
                buf.face((a_[i], b_[i], b_[i + 1], a_[i + 1]), bl)
                buf.face((a2[i], a2[i + 1], b2[i + 1], b2[i]), bl)
                buf.face((b_[i], b2[i], b2[i + 1], b_[i + 1]), bl)
            buf.face((a_[0], a2[0], b2[0], b_[0]), bl)
            buf.face((a_[-1], b_[-1], b2[-1], a2[-1]), bl)

        def surf(az, t, lift=0.0):
            jf = (az % 360.0) / 360.0 * nseg
            j0 = int(math.floor(jf)) % nseg
            j1 = (j0 + 1) % nseg
            a = jf - math.floor(jf)
            rp = ring_at(t)
            pp = rp[j0].lerp(rp[j1], a)
            out = V((pp.x - hc.x, pp.y - hc.y, 0)).normalized()
            return pp + out * lift, out

        # 금색 쐐기 (양옆에서 가운데를 가리킴)
        if chevrons:
            for sg in (1, -1):
                pts, nrm, ups, wd = [], [], [], []
                for i in range(7):
                    u = i / 6
                    az = sg * lerp(64.0, 17.0, u)
                    t = lerp(0.86, 0.66, u)
                    pp, out = surf(az, t, 0.0015 * k)
                    pts.append(pp)
                    nrm.append(out)
                    ups.append(axis)
                    wd.append(0.050 * k * (1 - u) ** 0.85 + 0.002 * k)
                taper_strip(buf, pts, nrm, ups, wd, 0.0030 * k, mat=au, w=w)
        # 금색 구슬 끈 (앞을 가로질러 처짐)
        if cord:
            nst = max(30, int(42 * q))
            nbead = 15
            st = []
            for i in range(nst):
                u = -1 + 2 * i / (nst - 1)
                az = u * 96.0
                t = band_t * 0.50 + (band_t * 0.50 + 0.36) * u * u
                pp, out = surf(az, t, 0.0075 * k)
                bead = abs(math.sin(math.pi * nbead * (u + 1) / 2))
                r_ = (0.0050 + 0.0030 * bead ** 0.6) * k
                st.append({"c": pp, "rx": r_, "ry": r_ * 0.85, "w": w, "ref": tuple(out)})
            loft(buf, st, segs=5, cap0="round", cap1="round", mat=au)
            # 양옆 끝에 늘어진 술 고리
            for sg in (1, -1):
                pp, out = surf(sg * 96.0, band_t + 0.36, 0.0075 * k)
                st = []
                for i in range(7):
                    tt = i / 6
                    bead = abs(math.sin(math.pi * 3 * tt))
                    r_ = (0.0048 + 0.0026 * bead ** 0.6) * k
                    st.append({"c": pp - V((0, 0, 0.060 * k * tt)) + out * 0.004 * k * tt, "rx": r_, "ry": r_ * 0.85,
                               "w": w, "ref": tuple(out)})
                loft(buf, st, segs=5, cap0="round", cap1="round", mat=au)
        # 나비
        if butterfly:
            # 에르피엔 나비를 앞면 곡면(가로로 둥글고 위로 벌어짐)에 감싸 붙인다: 문장 로컬 x → 둘레 각, z → 높이 t
            T0, DT = 0.66, 0.10
            pc = surf(0.0, T0)[0]
            r_h = (pc - V((hc.x, hc.y, pc.z))).length
            h_t = (surf(0.0, T0 + DT)[0] - surf(0.0, T0 - DT)[0]).length / (2 * DT)

            def wrap(v):
                az, t = math.degrees(v.x / r_h), T0 + v.z / h_t
                p_, o_ = surf(az, t)
                up_ = (surf(az, t + 0.05)[0] - surf(az, t - 0.05)[0]).normalized()
                return p_ + (o_ - up_ * o_.dot(up_)).normalized() * (-v.y)
            emblem(buf, Matrix.Identity(4), butterfly * k, au, depth=0.0032 * k, w=w, n=36, line=au_d, warp=wrap)
        # 정면 위 방울 (지휘관)
        if pompom:
            pm, pm2 = pompom
            pp, out = surf(0.0, 0.97, 0.004 * k)
            c = pp + axis * 0.020 * k
            ellipsoid(buf, c, axis, out.cross(axis).normalized(), out, 0.026 * k, 0.020 * k, 0.018 * k, segs=10,
                      rings=7, mat=pm, w=w)
            ellipsoid(buf, c - axis * 0.019 * k, axis, out.cross(axis).normalized(), out, 0.010 * k, 0.014 * k,
                      0.013 * k, segs=8, rings=5, mat=pm2, w=w)
        # 깃털 장식 (폴랑): 왼쪽 앞 띠에서 솟아 위·뒤로 휘는 큰 깃털 다발
        if plume:
            pm, pm2 = plume
            base_p, out = surf(50.0, 0.42, 0.010 * k)
            Sx = out.cross(axis).normalized()
            fronds = [(0.00, 1.25, 0.080, pm), (-0.55, 1.05, 0.062, pm2), (0.52, 0.95, 0.058, pm2),
                      (-0.25, 1.15, 0.060, pm), (0.28, 1.10, 0.056, pm)]
            for dx, ln, wd, mm in fronds:
                ctrl = [base_p - axis * 0.01 * k,
                        base_p + axis * 0.10 * k * ln + out * 0.022 * k + Sx * dx * 0.04 * k,
                        base_p + axis * 0.21 * k * ln + out * 0.036 * k + Sx * dx * 0.07 * k + V((0, 0.04, 0)) * k * ln,
                        base_p + axis * 0.28 * k * ln + out * 0.020 * k + Sx * dx * 0.10 * k + V((0, 0.11, 0)) * k * ln,
                        base_p + axis * 0.27 * k * ln + out * -0.006 * k + Sx * dx * 0.12 * k + V((0, 0.19, 0)) * k * ln]
                P = catmull(ctrl, max(9, int(12 * q)))
                elf.sweep(buf, P, lambda t, wd=wd: wd * k * 0.5 * keys([(0, 0.30), (0.25, 0.85), (0.6, 1.0), (1, 0.0)],
                                                                         t),
                          lambda t, wd=wd: wd * k * 0.14 * keys([(0, 0.6), (0.3, 1.0), (1, 0.2)], t),
                          segs=6, ref_fn=lambda t, out=out: out, mat=mm, w=w, bend=0.55)
            # 꽂은 자리 금색 단추
            disc(buf, base_p + out * 0.002 * k, out, axis, 0.012 * k, 0.012 * k, 0.004 * k, segs=10, mat=au, w=w)
        e._hats.append((o, rim_el))

    return e.part(name, "head", fn)


# =========================================================================== 경비대 복장 조각

def toggles(e, mat, *, rows=4, z0=None, z1=None, angle=13.0, off=0.012, size=(0.016, 0.005, 0.007), loop=None,
            name="toggles"):
    """앞여밈 금색 토글(막대 단추) 두 줄. 원작 폴랑·경비대 튜닉의 금색 단추 줄. loop=재질이면 가는 고리 끈."""
    k = e.k
    z0 = z0 if z0 is not None else e.chest_z + 0.050 * k
    z1 = z1 if z1 is not None else e.waist_z - 0.010 * k

    def fn(buf):
        for i in range(rows):
            z = lerp(z0, z1, i / max(rows - 1, 1))
            for sg in (1, -1):
                a = e.anchor(("torso", z, sg * angle, off * k))
                M = a.matrix()
                X = M.to_3x3() @ V((1, 0, 0))
                Z = M.to_3x3() @ V((0, 0, 1))
                ellipsoid(buf, a.pos + a.n * (size[1] * k * 0.4), X, Z, a.n, size[0] * k / 2, size[2] * k / 2,
                          size[1] * k / 2, segs=6, rings=4, mat=mat, w=a.w)
                if loop is not None:
                    a2 = e.anchor(("torso", z, sg * angle * 0.35, off * k))
                    elf._loop(buf, [a.pos + a.n * 0.002 * k, a2.pos + a2.n * 0.002 * k], [a.n, a2.n],
                              [V((0, 0, 1)), V((0, 0, 1))], 0.003 * k, 0.0015 * k, mat=loop, w=a.w, closed=False)
    return e.part(name, "body", fn)


def boot_roundel(e, side, mats_, *, t=0.13, size=0.050, off=0.030, name=None):
    """롱부츠 윗단 앞의 원판 + 금색 에르피엔 나비 (원작 경비대·폴랑 부츠)."""
    k = e.k
    a = e.anchor((f"leg_{side}", t, 0.0, off * k))

    def fn(buf):
        M = a.matrix(tilt=0)
        emblem(buf, M, size * 0.72 * k, mats_["gold"], depth=0.0024 * k, w=a.w, back=mats_["black"],
               back_scale=1.45, back_depth=0.003 * k, n=36, back_n=14, line=mats_["gold_d"], low=True)
    return e.part(name or f"boot_roundel_{side}", "body", fn)


def epaulette(e, side, mats_, *, fringe=True, off=0.034, size=1.0, name=None):
    """금색 견장(어깨 위 타원 판 + 바깥으로 늘어진 술). 지휘관·폴랑. 어깨 관절 위, 바깥으로 기운 판."""
    k = e.k
    s = 1 if side == "L" else -1
    w = {f"shoulder_{side}": 1.0}
    n_up = V((s * 0.55, 0.0, 0.84)).normalized()
    c = e.S[side] + V((-s * 0.010 * k, 0.0, 0.0)) + n_up * (0.050 * k + (off - 0.034) * k)

    def fn(buf):
        fw = V((0, -1, 0))
        sd = fw.cross(n_up).normalized() * (-s)
        sd = (sd - n_up * sd.dot(n_up)).normalized()
        ellipsoid(buf, c, sd, fw, n_up, 0.042 * k * size, 0.034 * k * size, 0.008 * k, segs=12, rings=5,
                  mat=mats_["gold"], w=w)
        band(buf, c - n_up * 0.002 * k, n_up, fw, 0.040 * k * size, 0.032 * k * size, 0.007 * k, 0.003 * k, segs=14,
             mat=mats_["gold_d"], w=w)
        if fringe:
            nf = 7
            for i in range(nf):
                ang = math.radians(-62 + 124 * i / (nf - 1))
                d = (sd * math.cos(ang) + fw * math.sin(ang)).normalized()
                if d.x * s < 0:
                    d = d - sd * (2 * d.dot(sd))
                p0 = c + d * 0.038 * k * size - n_up * 0.004 * k
                p1 = p0 + d * 0.006 * k + V((0, 0, -0.030 * k * size))
                loft(buf, [{"c": p0, "rx": 0.0040 * k, "ry": 0.0040 * k, "w": w},
                           {"c": p1, "rx": 0.0034 * k, "ry": 0.0034 * k, "w": w}],
                     segs=4, cap0="flat", cap1="round", mat=mats_["gold"])
    return e.part(name or f"epaulette_{side}", "body", fn)


def aiguillette(e, mat, *, side="R", loops=2, off=0.024, name="aiguillette"):
    """어깨에서 가슴 가운데로 늘어지는 금색 장식끈 (지휘관). side='R'이면 오른 어깨(-X)."""
    k = e.k
    s = 1 if side == "L" else -1
    sz, cz = e.shoulder_z, e.chest_z
    for i in range(loops):
        dz = -0.022 * i
        e.strap(mat, [("torso", sz + 0.006 * k, s * 82, off * k), ("torso", sz - 0.030 * k + dz * k, s * 66, off * k),
                      ("torso", cz + 0.004 * k + dz * k, s * 40, off * k), ("torso", cz + 0.040 * k, s * 14, off * k)],
                width=0.0080, th=0.0045, name=f"{name}_{i}")


def breeches(e, mat, *, t1=0.20, off=0.010, name="breeches"):
    """몸에 붙는 흰 바지(롱부츠 위로 짧게 보이는 부분만): 골반부 + 허벅지 관. 키트 pants보다 단면이 적다."""
    k = e.k
    zw = lerp(e.hipj_z, e.waist_z, 0.6)
    e.cover["torso"].append((e.crotch_z - 0.05, zw))
    st = e.torso_stations(e.crotch_z + 0.002 * k, zw, off=off * k, n=4)

    def fn(buf):
        loft(buf, st, segs=e._s(22), cap0="round", cap1=None, mat=mat, wfn=e._torso_wfn, cap_len0=0.04 * k)
    e.part(f"{name}_top", "body", fn)
    for side in ("L", "R"):
        e.cover[f"leg_{side}"].append((-0.2, t1))
        ch = e.leg_chain(side)
        e.part(f"{name}_{side}", "body",
               lambda buf, ch=ch: e._limb_loft(buf, ch, e.leg_r, -0.10, t1, mat, segs=e._s(16), cap0="round",
                                               cap1=None, off=off * k, n=5))
    return e


def guard_uniform(e, mats_, *, rank="soldier", tail_drop=0.24, coat_hem=None, boots_top=0.12, gloves=True,
                  coat_trim=None, cuff_rank=0, tunic_collar=True, toggles_rows=4):
    """요정 경비대 복장 (원작 경비대 GIF·폴랑 카드·PV): 흰 튜닉(세운 깃, 금색 토글 두 줄) + 초록 연미복(앞이 열리고
    뒤 자락이 무릎까지, 뒤 가운데 트임) + 초록 소매와 짙은 소맷단 + 흰 장갑 + 흰 바지 + 검은 롱부츠(윗단 나비 원판).
    rank: 'soldier' | 'officer' | 'captain' (officer 이상: 금색 소맷단 줄 cuff_rank, 연미복 금 테두리)."""
    k = e.k
    g, gd, wh, whd, au, aud, bl, bld = (mats_[x] for x in ("green", "green_d", "white", "white_d", "gold", "gold_d",
                                                          "black", "black_d"))
    cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
    # 흰 튜닉 (엉덩이 위까지)
    e.shirt(wh, hem=hz + 0.004 * k, collar="stand" if tunic_collar else None, flare=0.006, off=0.011)
    toggles(e, au, rows=toggles_rows, z0=cz + 0.058 * k, z1=wz + 0.004 * k, angle=12.5, off=0.012)
    # 흰 바지 + 검은 롱부츠
    breeches(e, wh, t1=boots_top + 0.06)
    e.boots(bl, top=boots_top, sole=(bld, 0.014), off=0.022, toe=0.004)
    for sd in ("L", "R"):
        # 부츠 윗단 접힘
        ch = e.leg_chain(sd)
        c, tan = ch.at(boots_top + 0.012)
        rx, ry = e.leg_r(boots_top)
        e.part(f"boot_cuff_{sd}", "body",
               lambda buf, c=c, tan=tan, rx=rx, ry=ry, ch=ch: band(buf, c, tan, (0, -1, 0), rx + 0.022 * k, ry + 0.022 * k,
                                                                   0.020 * k, 0.005 * k, segs=e._s(18), mat=bl,
                                                                   w=ch.weights(boots_top)))
        boot_roundel(e, sd, mats_, t=boots_top + 0.04, off=0.028)
    # 초록 연미복: 좌우 두 판(뒤 가운데 트임), 앞은 짧고 뒤는 무릎까지 (Shell drop)
    hem = coat_hem if coat_hem is not None else wz - 0.020 * k
    gap = [(0.0, 24.0), (0.40, 26.0), (0.75, 40.0), (1.0, 64.0)]
    drop = [(0.0, 0.0), (0.45, 0.0), (1.0, tail_drop)]
    shells = []
    for sd in ("L", "R"):
        def a_fn(a, u, sd=sd):
            gg = keys(gap, u)
            f = (a - gg) / max(360.0 - 2 * gg, 1e-6)
            slit = lerp(0.15, 3.2, smoothstep(0.50, 1.0, u))
            if sd == "L":
                return lerp(gg, 180.0 - slit, f)
            return lerp(180.0 + slit, 360.0 - gg, f)
        sh = Shell(e, g, e.torso_top - 0.004 * k, hem, gap=gap, off=0.025, th=0.005, skirt=True, cols=10, rows=10,
                   flare=[(0.0, 0.0), (0.5, 0.004), (1.0, 0.020)], drop=drop, a_fn=a_fn)
        if coat_trim is not None:
            sh.edge_trim(coat_trim, width=0.006, th=0.0025).hem_trim(coat_trim, width=0.006, th=0.0025)
        else:
            sh.edge_trim(gd, width=0.006, th=0.002)
        sh.done(f"coat_{sd}")
        shells.append(sh)
    # 연미복 깃 (어깨 위로 접힌 깃): 목 둘레 낮은 띠
    e.part("coat_collar", "body", lambda buf: band(buf, (0, 0.010 * k, e.torso_top - 0.006 * k), (0, 0, 1), (1, 0, 0),
                                                   0.074 * k, 0.066 * k, 0.016 * k, 0.005 * k, segs=e._s(18), mat=g,
                                                   w={"chest": 1.0}, taper=0.10))
    # 소매 + 소맷단 (+ 지휘관 금줄)
    e.sleeves(g, length=0.95, off=0.014, flare=0.010, cuff=(gd, 0.030, 0.006))
    for sd in ("L", "R"):
        for j in range(cuff_rank):
            e.ring(au, f"arm_{sd}", 0.885 - 0.035 * j, h=0.006, th=0.003, off=0.022, name=f"cuff_rank_{sd}_{j}")
        # 소맷단 금 단추
        e.part(f"cuff_btn_{sd}", "arms", lambda buf, sd=sd: [
            disc(buf, a.pos, a.n, a.up, 0.0045 * k, 0.0045 * k, 0.002 * k, segs=8, mat=au, w=a.w)
            for a in [e.anchor((f"arm_{sd}", tt, 180.0, 0.026 * k)) for tt in (0.90, 0.93)]])
    if gloves:
        e.gloves(mats_.get("glove", wh), inflate=0.0030)
    return shells


# =========================================================================== 이하 cameo2.py 복사본 (읽기 전용 원본)
# 원본: art/blender/lib/cameo2.py (카메오 2차 담당). 바뀌어도 이 모듈이 흔들리지 않게 복사했다. 수정한 곳은 [fairy] 표시.

def face_expr(e, name, *, both=None, L=None, R=None, M=None, corner=(0.0, 0.0), mouth_dx=0.0, blink_fix=True):
    """비대칭 표정 셰이프 키 (윙크, 한쪽 입꼬리, 한쪽 눈썹). [키트 후보]
    both: 공통, L: 캐릭터 왼쪽(+X) 눈·눈썹, R: 오른쪽(-X), M: 입(없으면 both). corner=(왼쪽, 오른쪽) 입꼬리 올림(m)."""
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
        out = []
        for i, q in enumerate(neutral):
            if q.x > th:
                c = bl[i].copy()
            elif q.x < -th:
                c = br[i].copy()
            else:
                c = bm[i].copy()
                if q.z < ez - 0.03 * e.k:
                    mq = P(both, M)["mouth"]
                    mw = mq["w"] * f.sz / 2
                    x = c.x
                    c.z += corner[0] * smoothstep(-0.2 * mw, mw, x) + corner[1] * smoothstep(0.2 * mw, -mw, x)
                    c.x += mouth_dx
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


def face_marks(e, name, strokes, mat, *, off=0.0045, group="head"):
    """얼굴 위 작은 표식. strokes: [[(x, z), ...], ...] 얼굴 정면 좌표의 사각 띠 4점. 아웃라인 없는 노드."""
    b = Buf()
    for st in strokes:
        ids = [b.vert(e.face_project(x, z, off)[0], {"head": 1.0}) for x, z in st]
        b.face(tuple(ids), mat)
    ob = b.obj(f"{e.name}_{name}", smooth=False)
    e.add(ob, group=group, tag=name, node=name, props={"noOutline": 1})
    return ob


class Hair2(elf.Hair):
    """키트 헤어 v2 + 다발 목록 후처리 훅 lock_fn(h, locks) → locks, 그리고 done() 뒤 post 훅. [키트 후보]"""

    def __init__(self, e, color, *, lock_fn=None, **kw):
        super().__init__(e, color, **kw)
        self.lock_fn = lock_fn
        self.post = []

    def _locks(self):
        L = super()._locks()
        if self.lock_fn:
            L = self.lock_fn(self, L) or L
        return L

    def done(self, name=None):
        if getattr(self, "_done", False):
            return None
        ob = super().done(name)
        ob_in = None
        for p in self.e.parts:
            if p.tag == "hair_in" and p.obj.name.startswith(ob.name):
                ob_in = p.obj
        for fn in self.post:
            fn(ob, ob_in)
        return ob


def hair(e, color, *, lock_fn=None, **kw):
    """e.hair()와 같지만 Hair2를 쓴다 (lock_fn, post 훅)."""
    h = Hair2(e, color, lock_fn=lock_fn, **kw)
    e._hairs = getattr(e, "_hairs", []) + [h]
    return h


def lock_edit(fn_each):
    def fn(h, locks):
        for lk in locks:
            fn_each(h, lk)
        return locks
    return fn


def bone_chain(e, prefix, joints, parent="head", start_blend=0.5):
    names = []
    prev = parent
    for i in range(len(joints) - 1):
        nm = f"{prefix}_{i + 1:02d}"
        e.add_bone(nm, joints[i], joints[i + 1], prev)
        names.append(nm)
        prev = nm
    return elf.Chain([V(p) for p in joints], names, start={parent: 1.0}, start_blend=start_blend)


def _path(ctrl, n=72):
    pts = catmull([V(p) for p in ctrl], n)
    cum = [0.0]
    for a_, b_ in zip(pts, pts[1:]):
        cum.append(cum[-1] + (b_ - a_).length)
    return pts, cum


def _at(pts, cum, t):
    s = clamp(t) * cum[-1]
    for i in range(len(cum) - 1):
        if s <= cum[i + 1] or i == len(cum) - 2:
            L = cum[i + 1] - cum[i]
            a = (s - cum[i]) / L if L > 1e-9 else 0.0
            return pts[i].lerp(pts[i + 1], clamp(a)), (pts[i + 1] - pts[i]).normalized()
    return pts[-1], (pts[-1] - pts[-2]).normalized()


class Tail:
    """한 줄기 묶은 머리 + 본 사슬 (cameo2.Tail). ctrl: 뿌리 → 끝 제어점(월드)."""

    def __init__(self, h, prefix, ctrl, width, thick=None, *, bones=3, parent="head", t_hold=0.55, root_w=0.75,
                 clumps=((0.30, 0.55, 0.88), (-0.30, 0.55, 0.82)), mat=None, ref_fn=None, segs=12, n=22,
                 start_blend=0.5):
        e = h.e
        self.h, self.e = h, e
        self.pts, self.cum = _path(ctrl, 96)
        joints = [_at(self.pts, self.cum, i / bones)[0] for i in range(bones + 1)]
        self.chain = bone_chain(e, prefix, joints, parent, start_blend=start_blend)
        thick = thick if thick is not None else width * 0.62
        c0 = V((0, 0, 0))
        ref_fn = ref_fn or (lambda t, q: V((q.x - c0.x, q.y - c0.y, 0.0)))
        self.ref_fn = ref_fn
        self.width, self.thick = width, thick
        self._sweep(self.pts, width, thick, n=n, segs=segs, t_hold=t_hold, root_w=root_w, mat=mat)
        for (dx, wsc, lsc) in clumps or ():
            self.clump(dx, wsc, lsc, mat=mat)

    def at(self, t):
        return _at(self.pts, self.cum, t)

    def w_at(self, t):
        return self.chain.weights(clamp(t))

    def _sweep(self, pts, width, thick, *, n, segs, t_hold, root_w, mat, t0=0.0, t1=1.0, side_off=None):
        q = self.e.q
        nn = max(12, int(n * q))
        P = []
        for i in range(nn):
            t = lerp(t0, t1, i / (nn - 1))
            c, T = self.at(t)
            if side_off:
                c = c + side_off(t, c, T)
            P.append(c)

        def prof(t):
            r = lerp(root_w, 1.0, smoothstep(0.0, 0.16, t))
            return r * elf._tip((t - t_hold) / (1 - t_hold), 2.2)

        def wfn(t):
            return self.w_at(lerp(t0, t1, t))

        def ref(t):
            c, _ = self.at(lerp(t0, t1, t))
            return self.ref_fn(lerp(t0, t1, t), c)
        elf.sweep(self.h.buf, P, lambda t: width / 2 * prof(t), lambda t: thick / 2 * max(prof(t), 0.22),
                  segs=max(10, int(segs * q) // 2 * 2), ref_fn=ref, mat=mat or self.h.m, w=wfn, bend=0.22)

    def clump(self, dx, wsc=0.55, lsc=0.85, *, mat=None, t0=0.08):
        w = self.width

        def off(t, c, T):
            out = self.ref_fn(t, c)
            out = (out - T * out.dot(T))
            out = out.normalized() if out.length > 1e-6 else V((1, 0, 0))
            S = T.cross(out).normalized()
            return S * (dx * w * smoothstep(0.25, 0.9, t)) - out * (0.12 * w)
        self._sweep(self.pts, w * wsc, self.thick * wsc * 1.05, n=16, segs=10, t_hold=0.45, root_w=0.9, mat=mat,
                    t0=t0, t1=lsc, side_off=off)

    def tie(self, mat, t=0.05, size=1.0, h_=0.022, th=0.008):
        c, T = self.at(t)
        out = self.ref_fn(t, c)
        out = (out - T * out.dot(T)).normalized()
        band(self.h.buf, c, T, out, self.width * 0.36 * size, self.thick * 0.42 * size, h_ * self.e.k, th * self.e.k,
             segs=14, mat=mat, w=self.w_at(t))
        return self


def braid(h, ctrl, w0, w1=None, *, beads=12, tilt=34.0, mat=None, face_fn=None, w=None, flat=0.70):
    """경로를 따라 납작한 마디를 좌우로 번갈아 기울여 반씩 겹친 땋은 머리 (cameo2.braid)."""
    e = h.e
    w1 = w0 if w1 is None else w1
    pts, cum = _path(ctrl, 80)
    L = cum[-1]
    sp = L / beads
    c0 = e.head_c
    face_fn = face_fn or (lambda q: (q - c0))
    q = e.q
    for i in range(beads):
        t = (i + 0.5) / beads
        c, T = _at(pts, cum, t)
        F = V(face_fn(c))
        F = (F - T * F.dot(T))
        F = F.normalized() if F.length > 1e-6 else V((0, -1, 0))
        S = T.cross(F).normalized()
        sg = 1 if i % 2 == 0 else -1
        wd = lerp(w0, w1, t)
        th = math.radians(-sg * tilt)
        Ax = (T * math.cos(th) + S * math.sin(th)).normalized()
        cen = c + S * (sg * 0.14 * wd)
        ww = w(t) if callable(w) else (w or {"head": 1.0})
        st = []
        nr = max(5, int(7 * q))
        for r in range(nr):
            u = -1 + 2 * r / (nr - 1)
            rad = math.sqrt(max(0.0, 1 - u * u))
            st.append({"c": cen + Ax * (u * sp * 1.08), "rx": max(0.46 * wd * rad, 0.0006),
                       "ry": max(0.46 * flat * wd * rad, 0.0005), "w": ww, "ref": tuple(S)})
        loft(h.buf, st, segs=max(8, int(10 * q)), cap0="flat", cap1="flat", mat=mat or h.m)
    return pts


def on_hair_band(e, h, mat, *, az0=-100.0, az1=100.0, el_fn=None, width=0.016, th=0.006, lift=0.003, n=40,
                 name="headband", group="head", s_fn=None):
    """머리 덩어리 바깥 면을 따라 두르는 띠 (머리띠·리본 띠·티아라 바탕)."""
    k = e.k
    el_fn = el_fn or (lambda az: 58.0 - 40.0 * (abs(az) / 90.0) ** 2)

    def fn(buf):
        pts, nrm, ups = [], [], []
        for i in range(n):
            az = lerp(az0, az1, i / (n - 1))
            s = s_fn(az) if s_fn else h.s_of_el(az, el_fn(az))
            p, nn = h.path(az, s, lift * k)
            p2, _ = h.path(az, s + 0.01 * k, lift * k)
            up = (p - p2)
            up = (up - nn * up.dot(nn)).normalized()
            pts.append(p + nn * th * k * 0.5)
            nrm.append(nn)
            ups.append(up)
        elf._loop(buf, pts, nrm, ups, width * k, th * k, mat=mat, w={"head": 1.0}, closed=False)
    return e.part(name, group, fn)


def vc_gradient(obj, base_hex, stops, *, tol=8, axis=2, pred=None, fn=None):
    """finalize() 뒤 합쳐진 메시에서 색이 base_hex인 모서리의 정점색을 위치에 따라 바꾼다 (머리끝 물들임)."""
    me = obj.data
    ca = me.color_attributes.get("Col")
    if ca is None:
        return 0
    base = elf.hex_srgb(base_hex)
    cols = [(t, elf.hex_srgb(hx)) for t, hx in stops]

    def col(t):
        if t <= cols[0][0]:
            return cols[0][1]
        for (t0, c0), (t1, c1) in zip(cols, cols[1:]):
            if t <= t1:
                a = smoothstep(t0, t1, t)
                return tuple(lerp(x, y, a) for x, y in zip(c0, c1))
        return cols[-1][1]
    n = 0
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            c = ca.data[li].color_srgb
            if max(abs(c[i] - base[i]) for i in range(3)) * 255 > tol:
                continue
            co = me.vertices[vi].co
            if pred is not None and not pred(co):
                continue
            v = fn(co) if fn else co[axis]
            r, g_, bb = col(v)
            ca.data[li].color_srgb = (r, g_, bb, 1.0)
            n += 1
    return n


def ring_pt(rx, ry, cy, z, a_deg, p=2.3):
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


def section(e, z, skirt=False, shoulder=0.0):
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
    if shoulder:
        sz = e.shoulder_z
        a = math.exp(-((z - sz) / (0.09 * e.k)) ** 2) if z < sz else 1.0
        rx = max(rx, lerp(rx, (0.136 + 0.045) * e.k * e.sh * shoulder, a))
    return rx, ry, cy


def skirt_w(e, p):
    if p.z >= e.hipj_z:
        return e._torso_wfn(p, 0)
    a = smoothstep(e.hipj_z, e.knee_z, p.z)
    s = clamp(p.x / (0.12 * e.k), -1.0, 1.0)
    wl = 0.5 + 0.5 * s
    leg = {kk: v for kk, v in (("thigh_L", wl), ("thigh_R", 1 - wl)) if v > 1e-4}
    return mixw({"hips": 1.0}, leg, a * 0.65)


class Shell:
    """몸통을 감싸는 두께 있는 천 (cameo2.Shell). gap: 앞트임 반각(도) 또는 [(u, 도)] 표.
    drop: [(u, m)] 뒤쪽으로 갈수록 밑단을 더 내림(연미복 꼬리), a_fn(a, u) → 각도 바꾸기(한쪽 판, 한쪽 망토).
    키트 가슴 볼륨(Elf.bust)을 따른다. bust_drape(m, e.k 곱함): 볼륨 모양을 정할 옷 층 거리. 없으면 off+flare
    (바깥 옷일수록 천처럼 걸쳐 떨어짐). 가슴 붕대·성형 흉갑처럼 몸에 붙어야 하는 층은 0~0.012로 준다."""

    def __init__(self, e, mat, z_top, z_hem, *, gap=0.0, off=0.012, flare=None, th=0.005, rows=None, cols=None,
                 skirt=False, p=2.3, cover=False, wfn=None, drop=None, ruffle=None, pleat=None, shoulder=0.0,
                 back_only=False, a_fn=None, pleat_mat=None, bust_drape=None):
        self.e = e
        self.mat = mat
        k = e.k
        self.buf = Buf()
        self.closed = (gap == 0 or gap is None)
        self.prm = dict(z_top=z_top, z_hem=z_hem, off=off, flare=flare, skirt=skirt, p=p, drop=drop, ruffle=ruffle,
                        pleat=pleat, shoulder=shoulder, bust_drape=bust_drape)
        rows = rows or max(4, int(abs(z_top - z_hem) / (0.026 * k)) + 2)
        cols = cols or max(12, int(26 * e.q))
        self.rows, self.cols = rows, cols
        self.col_mat = None
        if pleat and pleat_mat is not None and self.closed:
            nw = pleat[1]
            self.col_mat = lambda j: pleat_mat if ((j + 0.5) / cols * nw) % 1.0 >= 0.5 else mat
        gfn = (lambda u: keys(gap, u)) if isinstance(gap, (list, tuple)) else (lambda u: gap or 0.0)
        wfn = wfn or ((lambda q: skirt_w(e, q)) if skirt else (lambda q: e._torso_wfn(q, 0)))
        self.P, self.N, self.W = [], [], []
        for i in range(rows):
            u = i / (rows - 1)
            z = lerp(z_top, z_hem, u)
            rx, ry, cy = section(e, z, skirt, shoulder)
            fl = keys(flare, u) if flare else 0.0
            dz = keys(drop, u) if drop else 0.0
            g = gfn(u)
            rowP, rowN, rowW = [], [], []
            for j in range(cols):
                if self.closed:
                    a = 360.0 * j / cols
                else:
                    a = g + (360.0 - 2 * g) * j / (cols - 1)
                    if back_only:
                        a = a + 180.0
                if a_fn:
                    a = a_fn(a, u)
                rf = 0.0
                if ruffle:
                    amp, nw, u0 = ruffle
                    rf = amp * smoothstep(u0, 1.0, u) * math.cos(math.radians(a) * nw)
                if pleat:
                    amp, nw, u0 = pleat
                    x = (a / 360.0 * nw) % 1.0
                    rf += amp * smoothstep(u0, u0 + 0.35, u) * (abs(x - 0.5) * 4 - 1)
                q, n = ring_pt(rx + (off + fl + rf) * k, ry + (off + fl + rf) * k, cy, z, a, p)
                bo = bust_off(e, z, a, (off + fl if bust_drape is None else bust_drape) * k)
                if bo > 0.0:
                    q = q + n * bo
                if dz:
                    q.z -= dz * k * (0.5 - 0.5 * math.cos(math.radians(a)))
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
                mo = self.col_mat(j) if self.col_mat else m
                b.face((o[i][j], o[i + 1][j], o[i + 1][j2], o[i][j2]), mo)
                b.face((n[i][j], n[i][j2], n[i + 1][j2], n[i + 1][j]), m)
        for j in jr:
            j2 = (j + 1) % C
            b.face((o[0][j], o[0][j2], n[0][j2], n[0][j]), m)
            b.face((o[R - 1][j], n[R - 1][j], n[R - 1][j2], o[R - 1][j2]), m)
        if not self.closed:
            for i in range(R - 1):
                b.face((o[i][0], n[i][0], n[i + 1][0], o[i + 1][0]), m)
                jl = C - 1
                b.face((o[i][jl], o[i + 1][jl], n[i + 1][jl], n[i][jl]), m)

    def surface(self, u, a_deg, lift=0.0):
        e, q = self.e, self.prm
        k = e.k
        z = lerp(q["z_top"], q["z_hem"], u)
        rx, ry, cy = section(e, z, q["skirt"], q["shoulder"])
        fl = keys(q["flare"], u) if q["flare"] else 0.0
        r2x, r2y = rx + (q["off"] + fl) * k, ry + (q["off"] + fl) * k
        om = (q["off"] + fl if q.get("bust_drape") is None else q["bust_drape"]) * k
        pt, n = ring_pt(r2x, r2y, cy, z, a_deg, q["p"])
        bo = bust_off(e, z, a_deg, om)
        if bo > 0.0:
            pt = pt + n * bo
            n = bust_normal(e, z, a_deg, om, q["p"], r2x, r2y, cy, n)
        return pt + n * lift, n

    def frame_at(self, u, a_deg, lift=0.0):
        pt, n = self.surface(u, a_deg, lift)
        return Matrix.Translation(pt) @ frame(n, (0, 0, 1))

    def _strip(self, pts, nrm, ups, width, th, mat, ws, lift=0.0):
        k = self.e.k
        c = [p + nn * (lift * k) for p, nn in zip(pts, nrm)]
        elf._loop(self.buf, c, nrm, ups, width * k, th * k, mat=mat, closed=False,
                  w=lambda t, ws=ws: ws[min(int(round(t * (len(ws) - 1))), len(ws) - 1)])

    def edge_trim(self, mat, width=0.008, th=0.0025, i0=0, i1=None, lift=0.0004, width_fn=None):
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
        i = self.rows - 1 if row is None else row
        return self._row_trim(i, i - 1, mat, width, th, lift)

    def top_trim(self, mat, width=0.008, th=0.0025, lift=0.0004):
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

    def done(self, name, group="body", angle=50.0):
        ob = self.buf.obj(f"{self.e.name}_{name}", angle=angle)
        return self.e.add(ob, group=group, tag=name)


def leg_tube(e, mat, side, t0, t1, *, off=0.012, extra=None, name=None, cap0=None, cap1=None, segs=None):
    """다리에 감기는 관 (스타킹, 니삭스, 각반). t: 0=고관절, 1=발목. 덮은 구간의 맨살은 만들지 않는다."""
    k = e.k
    e.cover[f"leg_{side}"].append((t0, t1))
    ch = e.leg_chain(side)
    buf = Buf()
    ex = (lambda t: extra(t) * k) if extra else None
    e._limb_loft(buf, ch, e.leg_r, t0, t1, mat, segs=segs or int(16 * e.q), cap0=cap0, cap1=cap1, off=off * k,
                 extra=ex)
    ob = buf.obj(name or f"{e.name}_legtube_{side}{len(e.parts)}", angle=50.0)
    e.add(ob, group="body", tag=name or "legtube")
    return ob


def arm_tube(e, mat, side, t0, t1, *, off=0.012, extra=None, name=None, cap0=None, cap1=None, segs=None):
    """팔에 감기는 관 (긴 장갑, 토시). t: 0=어깨, 1=손목."""
    k = e.k
    e.cover[f"arm_{side}"].append((t0, t1))
    ch = e.arm_chain(side)
    buf = Buf()
    ex = (lambda t: extra(t) * k) if extra else None
    e._limb_loft(buf, ch, e.arm_r, t0, t1, mat, segs=segs or int(14 * e.q), cap0=cap0, cap1=cap1, off=off * k,
                 extra=ex)
    ob = buf.obj(name or f"{e.name}_armtube_{side}{len(e.parts)}", angle=50.0)
    e.add(ob, group="arms", tag=name or "armtube")
    return ob


def ellipsoid(buf, c, A, B, F, ra, rb, rf, *, segs=8, rings=5, mat=None, wfn=None, w=None):
    """타원체. A=긴 축(반경 ra), B·F=단면 축."""
    wf = wfn or (lambda q: w or {})
    c = V(c)
    A, B, F = V(A), V(B), V(F)
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
    # [fairy] 오른손/왼손 축 모두에서 바깥을 향하도록 감는 방향을 맞춘다
    flip = A.cross(B).dot(F) < 0
    for i in range(len(ringv) - 1):
        r0, r1 = ringv[i], ringv[i + 1]
        for j in range(segs):
            j2 = (j + 1) % segs
            f = (r0[j], r0[j2], r1[j2], r1[j])
            buf.face(tuple(reversed(f)) if flip else f, mat)
    for j in range(segs):
        j2 = (j + 1) % segs
        f1 = (i0, ringv[0][j2], ringv[0][j])
        f2 = (ringv[-1][j], ringv[-1][j2], i1)
        buf.face(tuple(reversed(f1)) if flip else f1, mat)
        buf.face(tuple(reversed(f2)) if flip else f2, mat)


def prism(buf, poly, depth, M, *, mat=None, w=None, chamfer=0.0):
    """2D 다각형 poly[(x, z)] (중심에서 별 모양으로 보이는 다각형)를 로컬 -Y(바깥)로 돌출. chamfer: 앞면 모서리 깎기."""
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
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))
    order = list(range(n) if area > 0 else range(n - 1, -1, -1))
    for ii in range(n):
        i = order[ii]
        j = order[(ii + 1) % n]
        buf.face((cb_, back[j], back[i]), mat)
        buf.face((back[i], back[j], mid[j], mid[i]), mat)
        if chamfer > 0:
            buf.face((mid[i], mid[j], front[j], front[i]), mat)
        buf.face((cf, front[i], front[j]), mat)


def star_poly(r_out, r_in, n=5, rot=90.0, cx=0.0, cz=0.0):
    """별 다각형 (반시계, 첫 꼭짓점 rot도)."""
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + 180.0 * i / n)
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def diamond_poly(w, h_, cx=0.0, cz=0.0):
    return [(cx, cz - h_ / 2), (cx + w / 2, cz), (cx, cz + h_ / 2), (cx - w / 2, cz)]


def bow_geo(buf, M, size, mat, *, w=None, tails=0.8, knot_mat=None, segs=8):
    """리본 매듭 (둥근 날개 2개 + 매듭 + 꼬리 2개). M 로컬: +Z 위, -Y 앞, X 옆. size = 전체 폭(m)."""
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
        loft(buf, st[::2] + [st[-1]], segs=segs, cap0="round", cap1="round", mat=mat, cap_len0=0.05 * s,
             cap_len1=0.18 * s, cap_rings=2)
        if tails:
            a = M @ V((sg * 0.12 * s, -0.04 * s, -0.10 * s))
            b = M @ V((sg * 0.42 * s, -0.02 * s, -tails * s))
            rf = tuple(M.to_3x3() @ V((1, 0, 0)))
            st2 = [{"c": a, "rx": 0.16 * s, "ry": 0.05 * s, "w": w or {}, "ref": rf},
                   {"c": a.lerp(b, 0.5), "rx": 0.19 * s, "ry": 0.05 * s, "w": w or {}, "ref": rf},
                   {"c": b, "rx": 0.22 * s, "ry": 0.05 * s, "w": w or {}, "ref": rf}]
            loft(buf, st2, segs=6, cap0="flat", cap1="flat", mat=mat)
    rbox(buf, (0.30 * s, 0.34 * s, 0.36 * s), M @ Matrix.Translation((0, -0.04 * s, 0)), mat=knot_mat or mat, w=w,
         r=0.45, segs=2)


def prop(e, name, ob, bone, *, outline=0.003, merge=True):
    """소품(지팡이 등)을 따로 남긴 노드로 본에 강체로 붙인다. 머티리얼은 인물의 toon_vc로 합친다(UNLIT 제외)."""
    cb.apply_modifiers(ob)
    ob.name = f"{e.name}_{name}"
    if merge:
        vc = elf.vc_material(f"{e.name}_toon_vc", e.line)
        elf.bake_vcol(ob)
        elf.remap_to_vc(ob, vc)
        elf.collapse_slots(ob)
    ob["outline"] = outline
    ob["prop"] = name
    e.add(ob, bone=bone, keep=True)
    return ob
