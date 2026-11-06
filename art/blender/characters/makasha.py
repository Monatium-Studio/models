"""마카샤: 마녀 왕국 벨리티엔의 책략관, '절구통의 마녀'. 엘리아스 침공전에서 유령 늪 전선을 지휘했고,
에르피엔 결전에서 실라와 함께 요정 성전군의 돌격을 지휘한다(3막 M8 성전 합류 컷신, M9 종막).

원작 마카샤(트릭컬 리바이브, '이야기를 짓는 자')의 외형을 따른다. 근거: docs/art/characters-cameo3.md
- 식별 요소: 크게 부푼 크림빛 회색 웨이브 장발과 오른눈(-X)을 덮는 앞머리, 정수리 바보털, 오른쪽(-X)의 검은 보랏빛
  굽은 뿔과 왼쪽(+X)의 은색 고리를 씌운 짧은 검은 뿔, 위는 분홍·아래는 민트인 반쯤 감은 눈, 흰 케이프(회색 띠),
  흰 둥근 깃 + 남색 목띠 + 은색 관 모양 브로치, 케이프 앞의 은색 고리와 분홍·민트·흰 구슬 줄(끝에 은색 가시),
  민트 상의(분홍 물결 밑단), 땅까지 오는 짙은 갈색 치마와 밑단의 민트 아치 창 무늬, 절구통을 단 지팡이와
  그 위에 얹힌 검은 마녀 모자(민트 안감, 은색 띠, 분홍·민트 마름모 별).
- 재해석: 지팡이·절구통·모자는 별도 노드 makasha_staff(오른손 hand_R에 강체)로 뺐다. 웨이브는 긴 머리가 떨어지는
  구간에 물결을 넣는 머리 클래스(WavyHair)로 낸다. 바바(닭발 집)는 넣지 않는다.
- 표정: 키트 5종 + cackle(이-히힛 웃음), chew(브로치 우물거리기), cold(속마음: 냉철한 고위 마녀), smirk(비웃음)
  + blink 교정 키.

npm run model -- art/blender/characters/makasha.py
npm run shot -- characters/makasha.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import fairy  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep, frame, catmull  # noqa: E402

cb.reset()
M_ = elf.mat
# 마녀: 귀는 장발에 완전히 덮인다 (원작 스탠딩에서 보이지 않음) → 귀를 만들지 않는다
e = fairy.Fairy("makasha", ears=None, height=1.20, head=0.45, chest=0.38, bust=0.40, hips=1.04, segs=0.72, hand_q=0.45,
                cheek=0.11)
k = e.k

# ---- 팔레트 (원작 카드·소개 이미지 눈 실측)
white = M_("mk_white", "#f6f4f2")
sleeve_m = M_("mk_sleeve", "#e6e3e8")   # 소매는 케이프보다 살짝 회색 (케이프와 겹쳐 읽히지 않게)
grey = M_("mk_grey", "#b9b6b8")
grey_d = M_("mk_grey_d", "#8e8a90")
mint = M_("mk_mint", "#8fd2bd")
mint_d = M_("mk_mint_d", "#5fae9a")
pink = M_("mk_pink", "#e87a86")
navy = M_("mk_navy", "#2c3150")
silver = M_("mk_silver", "#c9cbd3")
skirt_m = M_("mk_skirt", "#4a3b3e")
skirt_d = M_("mk_skirt_d", "#3a2e31")
horn_m = M_("mk_horn", "#4f3a48")
horn_d = M_("mk_horn_d", "#352833")
shoe = M_("mk_shoe", "#3a2f33")
black = M_("mk_black", "#2b2a33")

# ---- 얼굴: 위는 분홍, 아래는 민트인 눈. 기본은 졸린 듯 반쯤 감은 능청스러운 눈과 'ω' 입
e.face(eye_color="#7fd6c2", iris_dark="#e0697f", iris_light="#d6fff1", pupil="#3a6f66",
       lash="#5a4a4f", brow="#a89c98", brow_th=0.9, blush="#f6b0b0", blush_size=1.0,
       base={"eye": {"top": 0.019, "ktop": 4.0, "cout": 0.017, "tilt_out": 0.002},
             "brow": {"dz": 0.066, "ang": 4.0, "arch": 0.003},
             "mouth": {"w": 0.018, "curve": 0.0030, "wave": 0.0010}},
       expr={
           # 이-히힛: 눈을 가늘게 휘며 입을 크게 벌린 웃음
           "cackle": {"eye": {"top": 0.014, "lift": 0.014, "ktop": 4.6, "tilt_in": 0.004},
                      "brow": {"dz": 0.070, "ang": 10.0, "arch": 0.005},
                      "mouth": {"w": 0.034, "curve": 0.0080, "open": 0.0240, "top_arch": 0.0010}},
           # 브로치를 물고 우물거리는 버릇: 반쯤 감은 눈, 오므린 작은 입
           "chew": {"eye": {"top": 0.016, "ktop": 4.4},
                    "brow": {"dz": 0.064, "ang": 0.0},
                    "mouth": {"w": 0.012, "curve": -0.0010, "open": 0.0050, "wave": 0.0016}},
           # 속마음: 웃음기를 지운 냉철한 고위 마녀의 눈
           "cold": {"eye": {"top": 0.024, "ktop": 3.4, "tilt_in": -0.006},
                    "iris": {"pupil": 0.80},
                    "brow": {"dz": 0.060, "ang": -10.0, "th": 0.0060},
                    "mouth": {"w": 0.016, "curve": -0.0008}},
       })
c2.face_expr(e, "smirk",
             both={"eye": {"top": 0.016, "lift": 0.010}, "mouth": {"w": 0.026, "curve": 0.0030}},
             L={"brow": {"dz": 0.070, "ang": 6.0, "arch": 0.004}}, R={"brow": {"dz": 0.062, "ang": -6.0}},
             corner=(0.0085, -0.0010), mouth_dx=0.0020 * k)

# ---- 머리: 크림빛 회색 웨이브 장발 (엉덩이 아래까지, 크게 부풂), 오른눈을 덮는 앞머리, 바보털
HAIR, HAIR_D, HAIR_L = "#d6cbc1", "#a3958d", "#f1ebe4"


class WavyHair(c2.Hair2):
    """긴 머리가 떨어지는 구간(머리가 가장 넓은 곳 아래)에 바깥으로 부푸는 물결을 넣는다.
    셸·속층·덧다발이 모두 path()를 쓰므로 같은 물결을 따른다. 물결 위상은 경도마다 조금씩 달라 다발마다 굽이가 엇갈린다."""

    def __init__(self, e, color, *, wave=(0.026, 0.170, 0.02), q_shell=1.15, **kw):
        super().__init__(e, color, **kw)
        self.wave = wave
        self.q_shell = q_shell

    def _shell(self):
        # 물결을 담을 만큼 행(길이 방향)만 촘촘하게: 열 수는 cap(segs=)가 정한다 (elf.Hair._shell의 col_deg)
        q0 = self.e.q
        self.e.q = self.q_shell
        try:
            return super()._shell()
        finally:
            self.e.q = q0

    def _eval(self, L, s):
        p, n = super()._eval(L, s)
        if s > L["sb"]:
            amp, lam, d0 = self.wave
            d = s - L["sb"]
            az = math.atan2(L["rad"].x, -L["rad"].y)
            ph = 0.9 * math.sin(az * 2.0) + 0.35 * az
            f = smoothstep(d0 * self.k, (d0 + 0.16) * self.k, d)
            wv = math.sin(2 * math.pi * d / (lam * self.k) + ph)
            tan = V((-L["rad"].y, L["rad"].x, 0.0))
            p = p + L["rad"] * (amp * self.k * f * (0.55 + 0.45 * wv)) + tan * (0.18 * amp * self.k * f * math.cos(
                2 * math.pi * d / (lam * self.k) + ph))
        return p, n


def wavy_locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.2            # 뭉툭하게 말린 끝 (삐죽한 톱니 대신)
        lk["curl"] *= 1.4
    elif lk["region"] in ("side", "back"):
        lk["curl"] = 0.022 * k      # 끝이 바깥으로 말린다 (웨이브 끝 컬)
        lk["p"] = 2.9
        lk["puff"] *= 1.8


h = WavyHair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.30, lock_fn=c2.lock_edit(wavy_locks))
e._hairs = getattr(e, "_hairs", []) + [h]
h.cap(front=30, side=-6, back=-46, part=-10, segs=16, rows=5)
h.bangs(n=7, spread=60, tip_el=-4, sweep=-10, part=-10, jag=0.30, curl=1.6, seed=3.0)
h.sides(length=0.30, width=0.096, az=64, n=2, curl=0.9, puff=2.4, thick=1.15)
h.back(length=0.46, n=9, spread=100, thick=1.15)
h.ahoge(az=-4, height=0.078, curl=1.6, width=0.024)
h.ahoge(az=16, height=0.058, curl=-1.4, width=0.020)
h.shine(el=48, spread=72, n=2, size=1.15)
o = h.off
# 오른눈(-X)을 덮는 큰 웨이브 다발: 가르마에서 눈 앞을 지나 볼 아래까지 S자로
fb = e.face_builder
ex, ez = fb.ex, fb.ez
r0 = h.sp(-8, 36, o * 0.95)
p1 = e.face_project(-ex * 0.40, ez + 0.080 * k, 0.030 * k)[0]
p2 = e.face_project(-ex * 0.98, ez + 0.012 * k, 0.026 * k)[0]
p3 = e.face_project(-ex * 1.28, ez - 0.050 * k, 0.020 * k)[0]
p4 = h.sp(-58, -26, o * 1.20)
p5 = h.sp(-66, -40, o * 1.00)
h.strand([r0, p1, p2, p3, p4, p5], 0.088 * k, 0.026 * k, n=20, segs=10,
         taper=[(0, 0.70), (0.15, 1.0), (0.55, 0.95), (0.80, 0.62), (1, 0.0)])

# ---- 뿔: 오른쪽(-X) 검은 보랏빛 굽은 뿔, 왼쪽(+X) 은색 고리를 씌운 짧은 검은 뿔
hc = e.head_c


def horns(buf):
    w = {"head": 1.0}
    # 오른쪽 굽은 뿔: 머리 옆 위에서 바깥으로 나왔다가 위로 솟고 끝이 살짝 뒤로
    b0, n0 = e.head_point(-66.0, 30.0, 0.0)
    out = V((-1.0, 0.12, 0.0))
    ctrl = [b0 - n0 * 0.012 * k, b0 + n0 * 0.050 * k, b0 + n0 * 0.072 * k + out * 0.040 * k + V((0, 0, 0.040 * k)),
            b0 + out * 0.105 * k + V((0, 0.012 * k, 0.130 * k)), b0 + out * 0.092 * k + V((0, 0.040 * k, 0.225 * k))]
    P = catmull(ctrl, 16)
    st = []
    for i, q in enumerate(P):
        t = i / (len(P) - 1)
        r = lerp(0.031, 0.0015, t ** 1.15) * k
        st.append({"c": q, "rx": r, "ry": r * 0.92, "w": w, "ref": (0, 1, 0)})
    loft(buf, st, segs=8, cap0="flat", cap1="round", mat=horn_m)
    # 뿔 마디 고리 두 줄 (짙은 띠)
    for t in (0.28, 0.42):
        i = int(t * (len(P) - 1))
        T = (P[i + 1] - P[i]).normalized()
        ref = T.cross(V((0, 1, 0))).normalized()
        r = lerp(0.031, 0.0015, t ** 1.15) * k
        band(buf, P[i], T, ref, r * 1.03, r * 0.97, 0.004 * k, 0.0018 * k, segs=10, mat=horn_d, w=w)
    # 왼쪽 짧은 뿔 (+X): 짙은 기둥 + 은색 고리 + 뾰족한 덮개
    b1, n1 = e.head_point(44.0, 54.0, 0.0)
    ax = (n1 + V((0.15, 0.10, 0.55))).normalized()
    base = b1 - n1 * 0.008 * k
    st2 = [{"c": base, "rx": 0.017 * k, "ry": 0.017 * k, "w": w},
           {"c": base + ax * 0.060 * k, "rx": 0.016 * k, "ry": 0.016 * k, "w": w},
           {"c": base + ax * 0.090 * k, "rx": 0.0165 * k, "ry": 0.0165 * k, "w": w}]
    loft(buf, st2, segs=8, cap0="flat", cap1="flat", mat=black)
    ref = ax.cross(V((0, 1, 0))).normalized()
    band(buf, base + ax * 0.072 * k, ax, ref, 0.020 * k, 0.020 * k, 0.012 * k, 0.004 * k, segs=10, mat=silver, w=w)
    st3 = [{"c": base + ax * 0.088 * k, "rx": 0.019 * k, "ry": 0.019 * k, "w": w},
           {"c": base + ax * 0.104 * k, "rx": 0.016 * k, "ry": 0.016 * k, "w": w},
           {"c": base + ax * 0.128 * k, "rx": 0.0015 * k, "ry": 0.0015 * k, "w": w}]
    loft(buf, st3, segs=6, cap0="flat", cap1="flat", mat=black, p=1.0)


e.part("horns", "head", horns)

# ---- 민트 상의(분홍 물결 밑단) + 흰 소매
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(mint, hem=wz - 0.020 * k, collar=None, flare=0.010)
e.ring(pink, "torso", wz - 0.016 * k, h=0.010, th=0.004, off=0.016, name="top_hem")
e.sleeves(sleeve_m, length=0.93, off=0.012, flare=0.020, puff=0.010, cuff=(grey, 0.016, 0.004))

# ---- 땅까지 오는 짙은 갈색 치마 (세로 주름 + 밑단 민트 아치 창 무늬)
q0 = e.q
e.q = 0.30    # 치마 속 반바지는 보이지 않으니 아주 성글게
e.pants(skirt_d, length=0.10, bag=0.0, blouse=0.0, off=0.006)
e.q = q0
skirt = c2.Shell(e, skirt_m, wz - 0.004 * k, 0.026 * k, off=0.016, th=0.004, skirt=True, cols=26, rows=6,
                 flare=[(0.0, 0.0), (0.25, 0.020), (0.6, 0.050), (1.0, 0.078)], pleat=(0.007, 10, 0.15),
                 pleat_mat=skirt_d, cover=True)
skirt.hem_trim(skirt_d, width=0.010, th=0.002)


def arch_poly(wd, ht, n=7):
    """뾰족 아치 창 (아래는 사각, 위는 두 호가 만나는 첨두)."""
    pts = [(-wd / 2, 0.0), (wd / 2, 0.0), (wd / 2, ht * 0.55)]
    for i in range(1, n):
        t = i / n
        a = math.radians(lerp(0.0, 62.0, t))
        pts.append((wd / 2 - wd * (1 - math.cos(a)) * 0.9, ht * 0.55 + ht * 0.45 * math.sin(a) / math.sin(math.radians(62))))
    pts.append((0.0, ht))
    for x, z in reversed(pts[3:-1]):
        pts.append((-x, z))
    pts.append((-wd / 2, ht * 0.55))
    return pts


for i in range(6):
    a = 30.0 + 60.0 * i
    for (u, sc) in ((0.86, 1.0),):
        Mx = skirt.frame_at(u, a, 0.0015 * k)
        wfn = c2.skirt_w(e, Mx.translation)
        Mo = Mx @ Matrix.Translation((0, 0, -0.040 * k))
        c2.prism(skirt.buf, arch_poly(0.062 * k, 0.118 * k, 5), 0.0020 * k, Mo, mat=mint, w=wfn)
        c2.prism(skirt.buf, [(x * 0.70, z * 0.80 + 0.008 * k) for x, z in arch_poly(0.062 * k, 0.118 * k, 5)],
                 0.0010 * k, Mo @ Matrix.Translation((0, -0.0020 * k, 0)), mat=skirt_d, w=wfn)
        # 창살 (가운데 세로줄)
        rbox(skirt.buf, (0.0040 * k, 0.0016 * k, 0.066 * k),
             Mo @ Matrix.Translation((0, -0.0032 * k, 0.044 * k)), mat=mint, w=wfn, r=0.2)
    # 아치 사이 작은 민트 물방울 장식
    Mx = skirt.frame_at(0.93, a + 30.0, 0.0015 * k)
    c2.prism(skirt.buf, c2.diamond_poly(0.012 * k, 0.020 * k), 0.0018 * k, Mx, mat=mint,
             w=c2.skirt_w(e, Mx.translation))
skirt.done("skirt", angle=30.0)
e.q = 0.5     # 치마 밑으로 코끝만 보인다
e.boots(shoe, top=0.92, sole=(black, 0.012), off=0.010, toe=0.004)
e.q = q0

# ---- 흰 케이프: 목에서 어깨를 둥글게 덮고 엉덩이까지 종처럼 퍼진다. 앞이 살짝 열림. 밑단 위 회색 띠


class Capelet(c2.Shell):
    """목둘레에서 어깨를 둥글게 덮는 돔 케이프 (Shell의 높이별 단면 대신 직접 준 반경표).
    prof: [(u, z, rx, ry)] (rx·ry는 몸 중심축 기준 반경, m). gap: [(u, 앞트임 반각)]."""

    def __init__(self, e, mat, prof, gap, *, rows=11, cols=24, th=0.006, p=2.4):
        self.e, self.mat, self.buf = e, mat, Buf()
        self.closed, self.col_mat = False, None
        self.rows, self.cols = rows, cols
        self.prof, self.gap, self.p = prof, gap, p
        self.P, self.N, self.W = [], [], []
        for i in range(rows):
            u = i / (rows - 1)
            rowP, rowN, rowW = [], [], []
            for j in range(cols):
                q, n = self.at(u, j / (cols - 1))
                rowP.append(q)
                rowN.append(n)
                rowW.append(e._torso_wfn(q, 0))
            self.P.append(rowP)
            self.N.append(rowN)
            self.W.append(rowW)
        self._build(th * e.k)

    def ang(self, u, f):
        g = elf.keys(self.gap, u)
        return g + (360.0 - 2 * g) * f

    def at(self, u, f, lift=0.0, a=None):
        z = elf.keys([(t, zz) for t, zz, _, _ in self.prof], u)
        rx = elf.keys([(t, r) for t, _, r, _ in self.prof], u)
        ry = elf.keys([(t, r) for t, _, _, r in self.prof], u)
        cy = self.e.torso_at(max(min(z, self.e.torso_top), self.e.crotch_z))[2]
        q, n = c2.ring_pt(rx, ry, cy, z, self.ang(u, f) if a is None else a, self.p)
        return q + n * lift, n


tt, sz_ = e.torso_top, e.shoulder_z
cape = Capelet(e, white, [(0.0, tt + 0.014 * k, 0.074 * k, 0.068 * k), (0.10, tt + 0.002 * k, 0.130 * k, 0.098 * k),
                          (0.22, sz_ - 0.010 * k, 0.188 * k, 0.124 * k), (0.40, sz_ - 0.080 * k, 0.222 * k, 0.142 * k),
                          (1.0, hz - 0.030 * k, 0.272 * k, 0.182 * k)],
               [(0.0, 10.0), (0.3, 14.0), (1.0, 22.0)], rows=9, cols=22)
cape.hem_trim(grey, width=0.016, th=0.003, row=cape.rows - 2)
cape.hem_trim(grey_d, width=0.008, th=0.0025)
cape.edge_trim(grey, width=0.008, th=0.002, i0=1)
cape.done("cape")

# 흰 둥근 깃 (두 장) + 남색 목띠 + 은색 관 브로치


def collar(buf):
    w = {"neck": 0.3, "chest": 0.7}
    z = e.torso_top + 0.012 * k
    band(buf, (0, 0.004 * k, z), (0, 0, 1), (1, 0, 0), 0.060 * k, 0.056 * k, 0.020 * k, 0.005 * k, segs=16, mat=navy,
         w=w, taper=-0.03)
    for sg in (1, -1):
        p, n = e.torso_point(e.torso_top + 0.002 * k, sg * 34, 0.030 * k)
        Mx = Matrix.Translation(p) @ frame(n, (0, 0, 1)) @ Matrix.Rotation(math.radians(-sg * 12), 4, "Y")
        poly = elf.ellipse2(sg * 0.012 * k, -0.004 * k, 0.034 * k, 0.020 * k, 14)
        c2.prism(buf, poly, 0.005 * k, Mx @ Matrix.Rotation(math.radians(-24), 4, "X"), mat=white, w=w)
    # 관 모양 브로치 (길쭉한 육각)
    p, n = e.torso_point(e.torso_top - 0.008 * k, 0, 0.040 * k)
    Mx = Matrix.Translation(p) @ frame(n, (0, 0, 1))
    coffin = [(-0.008 * k, 0.012 * k), (-0.011 * k, 0.004 * k), (-0.006 * k, -0.018 * k), (0.006 * k, -0.018 * k),
              (0.011 * k, 0.004 * k), (0.008 * k, 0.012 * k)]
    c2.prism(buf, coffin, 0.005 * k, Mx, mat=silver, w=w, chamfer=0.0015 * k)
    c2.prism(buf, [(x * 0.5, z * 0.5 - 0.001 * k) for x, z in coffin], 0.0015 * k,
             Mx @ Matrix.Translation((0, -0.005 * k, 0)), mat=navy, w=w)


e.part("collar", "body", collar)

# 케이프 앞 은색 고리 + 구슬 줄 (분홍·민트·흰) + 은색 가시 술


def beads(buf, sg):
    u = 0.30
    p, n = cape.at(u, 0.0, 0.004 * k, a=sg * (cape.ang(u, 0.0) + 5.0))
    w = e._torso_wfn(p, 0)
    Mx = Matrix.Translation(p) @ frame(n, (0, 0, 1))
    rbox(buf, (0.016 * k, 0.006 * k, 0.020 * k), Mx, mat=silver, w=w, r=0.3, segs=1)
    rbox(buf, (0.009 * k, 0.008 * k, 0.010 * k), Mx @ Matrix.Translation((0, -0.002 * k, 0.003 * k)), mat=navy, w=w,
         r=0.3, segs=1)
    top = p + n * 0.006 * k - V((0, 0, 0.016 * k))
    for i, m in enumerate((pink, mint, white)):
        c = top - V((0, 0, 0.016 * k * i))
        c2.ellipsoid(buf, c, V((0, 0, 1)), V((1, 0, 0)), V((0, -1, 0)), 0.0078 * k, 0.0078 * k, 0.0078 * k,
                     segs=8, rings=5, mat=m, w=w)
    c = top - V((0, 0, 0.016 * k * 2.6))
    loft(buf, [{"c": c, "rx": 0.004 * k, "ry": 0.004 * k, "w": w},
               {"c": c - V((0, 0, 0.010 * k)), "rx": 0.0035 * k, "ry": 0.0035 * k, "w": w},
               {"c": c - V((0, 0, 0.026 * k)), "rx": 0.0006 * k, "ry": 0.0006 * k, "w": w}], segs=6, cap0="flat",
         cap1="flat", mat=silver, p=1.0)


for sg in (1, -1):
    e.part(f"beads_{sg}", "body", lambda buf, sg=sg: beads(buf, sg))

e.finalize()


# ---- 지팡이 + 절구통 + 마녀 모자 (별도 노드 makasha_staff, 오른손)
def staff():
    buf = Buf()
    W, d, pn = e.W["R"], e.adir["R"], e.palm_n["R"]
    g = W + d * 0.036 * k + pn * 0.024 * k           # 쥔 자리
    up = V((0, 0, 1))
    z0, z1 = 0.020 * k, 1.20 * k
    pole_m = M_("mk_pole", "#4a3a36")
    st = [{"c": V((g.x, g.y, z)), "rx": 0.0105 * k, "ry": 0.0105 * k, "w": {}} for z in (z0, (z0 + z1) / 2, z1)]
    loft(buf, st, segs=8, cap0="round", cap1="flat", mat=pole_m)
    for z in (z0 + 0.03 * k, g.z - 0.07 * k, g.z + 0.07 * k, z1 - 0.05 * k):
        band(buf, V((g.x, g.y, z)), up, (1, 0, 0), 0.0135 * k, 0.0135 * k, 0.010 * k, 0.003 * k, segs=10, mat=silver,
             w={})
    # 가시 고리 (원작 지팡이의 가시 감긴 손잡이)
    for i in range(4):
        a = math.radians(90.0 * i + 15.0)
        for z in (g.z + 0.090 * k,):
            c = V((g.x, g.y, z)) + V((math.cos(a), math.sin(a), 0)) * 0.012 * k
            dd = V((math.cos(a), math.sin(a), 0.3)).normalized()
            loft(buf, [{"c": c, "rx": 0.0030 * k, "ry": 0.0030 * k, "w": {}},
                       {"c": c + dd * 0.010 * k, "rx": 0.0004 * k, "ry": 0.0004 * k, "w": {}}], segs=5,
                 cap0="flat", cap1="flat", mat=silver, p=1.0)
    # 절구통: 팔각 검은 통 + 분홍 물결 띠 + 꼭대기 공
    mz0 = z1 - 0.010 * k
    H = 0.120 * k
    R = 0.046 * k
    st = []
    for i, (t, rf) in enumerate(((0.0, 0.82), (0.06, 1.0), (0.94, 1.0), (1.0, 0.86))):
        st.append({"c": V((g.x, g.y, mz0 + H * t)), "rx": R * rf, "ry": R * rf, "w": {}})
    loft(buf, st, segs=8, cap0="flat", cap1="flat", mat=black, p=2.0)
    band(buf, V((g.x, g.y, mz0 + H * 0.20)), up, (1, 0, 0), R * 1.04, R * 1.04, 0.016 * k, 0.003 * k, segs=16,
         mat=pink, w={})
    for i in range(8):     # 띠 아래 물결 (분홍 반달 조각)
        a = math.radians(45.0 * i + 22.5)
        c = V((g.x, g.y, mz0 + H * 0.115)) + V((math.cos(a), math.sin(a), 0)) * R * 1.02
        Mb = Matrix.Translation(c) @ frame(V((math.cos(a), math.sin(a), 0)), (0, 0, 1))
        c2.prism(buf, [(-0.009 * k, 0.004 * k), (0.009 * k, 0.004 * k), (0.0, -0.007 * k)], 0.002 * k, Mb, mat=pink,
                 w={})
    c2.ellipsoid(buf, V((g.x, g.y, mz0 + H + 0.016 * k)), V((0, 0, 1)), V((1, 0, 0)), V((0, -1, 0)), 0.020 * k,
                 0.020 * k, 0.020 * k, segs=10, rings=6, mat=black, w={})
    # 마녀 모자: 절구통 꼭대기에 비스듬히 얹힘. 챙(민트 안감) + 구부러진 원뿔 + 은색 띠 + 마름모 별
    hb = V((g.x, g.y, mz0 + H + 0.018 * k))
    tilt = Matrix.Rotation(math.radians(-14), 4, "X") @ Matrix.Rotation(math.radians(10), 4, "Y")
    Ht = Matrix.Translation(hb) @ tilt
    br = 0.078 * k
    rim = []
    for i in range(16):
        a = 2 * math.pi * i / 16
        rim.append(a)
    top_i, bot_i, out_i = [], [], []
    for a in rim:
        r_ = br * (1.0 + 0.05 * math.cos(2 * a))
        top_i.append(buf.vert(Ht @ V((math.cos(a) * r_, math.sin(a) * r_, 0.006 * k)), {}))
        out_i.append(buf.vert(Ht @ V((math.cos(a) * r_ * 1.02, math.sin(a) * r_ * 1.02, 0.0)), {}))
        bot_i.append(buf.vert(Ht @ V((math.cos(a) * r_ * 0.98, math.sin(a) * r_ * 0.98, -0.004 * k)), {}))
    hat_m = M_("mk_hat", "#262b3a")
    cin = buf.vert(Ht @ V((0, 0, 0.004 * k)), {})
    cbt = buf.vert(Ht @ V((0, 0, -0.002 * k)), {})
    for i in range(16):
        j = (i + 1) % 16
        buf.face((top_i[i], top_i[j], cin), hat_m)
        buf.face((top_i[j], top_i[i], out_i[i], out_i[j]), hat_m)
        buf.face((out_i[j], out_i[i], bot_i[i], bot_i[j]), grey_d)
        buf.face((bot_i[j], bot_i[i], cbt), mint_d)
    # 원뿔 (끝이 뒤로 꺾임)
    cone = []
    for i in range(9):
        t = i / 8
        bend = V((0, 0.040 * k * t ** 2.2, 0))
        c = Ht @ (V((0, 0, 0.004 * k + 0.130 * k * t)) + bend)
        r = lerp(0.040, 0.002, t ** 0.9) * k
        cone.append({"c": c, "rx": r, "ry": r, "w": {}})
    loft(buf, cone, segs=10, cap0="flat", cap1="round", mat=hat_m)
    band(buf, Ht @ V((0, 0, 0.016 * k)), (Ht.to_3x3() @ V((0, 0, 1))).normalized(), Ht.to_3x3() @ V((1, 0, 0)),
         0.0385 * k, 0.0385 * k, 0.012 * k, 0.003 * k, segs=16, mat=silver, w={})
    # 마름모 별 (모자 앞면)
    fp = Ht @ V((0, -0.033 * k, 0.050 * k))
    fn = (Ht.to_3x3() @ V((0, -1, 0.22))).normalized()
    Mf = Matrix.Translation(fp) @ frame(fn, Ht.to_3x3() @ V((0, 0, 1)))
    c2.prism(buf, c2.star_poly(0.016 * k, 0.005 * k, n=4, rot=90), 0.003 * k, Mf, mat=pink, w={})
    c2.prism(buf, c2.diamond_poly(0.008 * k, 0.012 * k), 0.0015 * k, Mf @ Matrix.Translation((0, -0.003 * k, 0)),
             mat=mint, w={})
    ob = buf.obj("makasha_staff_tmp", angle=40.0)
    return c2.prop(e, "staff", ob, "hand_R", outline=0.003)


staff()
e.export("characters/makasha.glb")
