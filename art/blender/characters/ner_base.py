"""네르(기본): 세계수 교단의 사제장, 엘다인 각성 전 평소 모습 (원작 기본 카드 스탠딩·초상).

이 작품에서는 M9 로딩 브리핑(A3_M9_BRIEF)의 뮤트 영상 피드 한 장면에만 쓴다: 수인 마을 동굴 집회장에서 교주가 네르의
손을 붙잡고, 둘의 격노가 공명해 네르가 엘다인으로 각성한다(빛 속에서 각성 판 ner.glb로 바뀐다) [원작 「엘리아스 침공전」].
근거: 원작 기본 네르 카드 스탠딩·초상(레퍼런스로만 보고 저장소에 넣지 않는다), docs/art/characters-cameo3.md 1.0절.
얼굴·머리·몸은 각성 판 ner.glb와 같은 공용 코드(cameo3.ner_body, ner_face, ner_hair)라 한눈에 같은 사람이다.

원작을 요소마다 옮긴 것 (2026-11-04 사용자 「대충 십자만 보고 십자가 덜렁 붙여놓고 땡이야?」, 「사제장 네르 복장은 여전히 찐빠구나」 뒤 다시 만듦)
- 두건: 머리 위에 얹힌 부드러운 남색 천 (공용 cameo3.veil이 아니라 이 파일의 draped_veil). 흰 머리띠 뒤에서 머리에 붙어
  덮고, 귀 아래로는 머리카락 뒤로 늘어지며 둥근 세로 주름과 함께 조금 퍼진다. 옆은 턱선 바로 아래, 뒤는 어깨 높이에서
  끝나고 단이 조금 물결친다. 아랫단은 적갈색 띠.
- 머리: 채도 낮은 크림빛 금발, 일자 앞머리, 턱 아래부터 복숭앗빛 (정점색). 물결·부피는 이 파일에서만 (hair_wave).
- 어깨 깃: 어깨 곡선을 따라 위팔까지 드리운 짧고 둥근 연보랏빛 흰 어깨 망토. 앞이 V로 열리고 열린 가장자리의 먹색 띠가
  목 앞에서 엇갈린다. 가슴 가운데 표장 뒤로 좁은 연보랏빛 흰 띠.
- 가슴: 흰 판 없이 남색 몸판 위에 세계수 교단 금 표장(깃의 마름모 매듭 → 금 줄기 → 가로대 둘). 십자가로 바꾸지 않는다.
- 소매: 남색 긴 소매, 흰 소맷단. 평소 자세(두 손을 허리 앞에 모음)는 컷신 자세 feed_ner_clasp.
- 아래: 짙은 밤색 짧은 겉치마 밑으로 남색 주름치마, 물결진 흰 레이스 밑단. 허리에서 늘어진 짧은 흰 앞자락(굵은 금 테,
  가운데 금 마름모, 끝이 뾰족한 방패꼴, 치마 중간까지). 밤색 허리띠와 도끼 멜빵(허리 앞 → 왼쪽 엉덩이).
- 다리: 검은 타이츠, 흰 접단의 밝은 밤색 부츠.
- 무기: 왼쪽(캐릭터 +X) 허리에 비스듬히 찬 손도끼 「세계수의 도끼」(각성하면 도끼창이 된다). 회색 자루와 주황빛 금 고리,
  반원 머리에 주황빛 금 테와 바퀴살 꼴 금 삼각 창 셋, 뒤쪽 회색 갈고리. 별도 노드 ner_base_axe.
- 날개: 허리 높이의 작고 가는 옅은 하늘빛 날개 (fairy.wings style='slender').
- 표정: 공용 세트(키트 5종 + rage, glare, teary, smug) + blink 교정 키.

npm run model -- art/blender/characters/ner_base.py
npm run shot -- characters/ner_base.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bpy  # noqa: E402,F401
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
from elf import V, Matrix, Buf, rbox, lerp, frame, smoothstep, mixw  # noqa: E402

cb.reset()
e = c3.ner_body("ner_base")
k = e.k
M_ = elf.mat

# ---- 팔레트 (원작 기본 카드에서 눈으로 뽑음)
veil_m = M_("nb_veil", "#4d5476")       # 두건: 회청빛 남색
veil_in = M_("nb_veil_in", "#3a3f5c")
veil_hem = M_("nb_veil_hem", "#5a3437")  # 두건 아랫단 띠 (짙은 적갈색)
band_w = M_("nb_band", "#fbfaf8")       # 흰 머리띠
cape = M_("nb_cape", "#dcd8e8")         # 어깨 깃 (연보랏빛 흰색)
cape_hi = M_("nb_cape_hi", "#f7f5fb")    # 어깨 깃 아랫단의 밝은 띠
cape_trim = M_("nb_cape_trim", "#3b3640")
slate = M_("nb_slate", "#5a6696")       # 소매·주름치마 (회청빛 남색)
slate_d = M_("nb_slate_d", "#465180")
white = M_("nb_white", "#fbf9fc")
lace = M_("nb_lace", "#f2eff4")
over = M_("nb_over", "#4b3f43")         # 겉치마 (짙은 밤색)
belt_m = M_("nb_belt", "#5b433b")
gold = M_("nb_gold", "#efb53f")
gold_d = M_("nb_gold_d", "#c98a26")
stock = M_("nb_stocking", "#3c3640")
boot = M_("nb_boot", "#a9786a")
boot_d = M_("nb_boot_d", "#7e5649")
silver = M_("nb_silver", "#b8bcc6")      # 도끼 날 (회색)
silver_d = M_("nb_silver_d", "#8f95a3")
shaft = M_("nb_shaft", "#9a9ea8")        # 도끼 자루 (회색)
axe_gold = M_("nb_axe_gold", "#e2a63c")  # 도끼 바퀴살·테 (주황빛 금)
strap_m = M_("nb_strap", "#6b4c40")      # 도끼 멜빵 (밤색 가죽)

# ---- 얼굴·머리: 각성 판과 같은 공용 코드 (땋은 머리는 각성하면서 생긴 표지라 없다)
# 볼 홍조는 옅고 작게 (원작 기본 카드의 차분한 얼굴)
c3.ner_face(e, blush="#f7c3c2", blush_size=0.92)
h = c3.ner_hair(e)

# ---- 두건: 정수리부터 덮고 얼굴 양옆으로 곧게 내려와 가슴 높이에서 끝난다. 아랫단 짙은 밤색 띠
EL_T = 50.0
def draped_veil(*, el_front=50.0, az_open=66.0, az_full=104.0, rows=18, cols=44, lift=0.006, th=0.004,
                folds=9, fold_amp=0.012, flare=0.030, rim_w=0.024):
    """기본 네르 전용 베일 (공용 cameo3.veil의 딱딱한 후드 대신 늘어진 천).
    흰 머리띠 뒤 정수리부터 머리에 붙어 덮고(얇게 띄움), 귀 높이 아래로는 머리카락 뒤로 늘어지며 아래로 갈수록 바깥으로
    조금 퍼진다. 늘어진 부분에 부드러운 세로 주름(cos² 능선)과 큰 물결이 생기고, 아랫단은 옆이 턱선 바로 아래, 뒤가 어깨 높이,
    단 자체도 조금 물결친다. 아랫단에 적갈색 띠. 웨이트는 머리 → 아래로 갈수록 목·가슴(머리를 돌려도 어깨에서 덜 뜬다)."""
    hc = e.head_c
    z_ear = hc.z - 0.030 * k
    z_side = e.chin - 0.012 * k
    z_back = e.shoulder_z + 0.026 * k

    def s_at_z(az, z):
        lo, hi = 0.0, 2.0 * k
        for _ in range(40):
            mid = (lo + hi) / 2
            if h.path(az, mid)[0].z > z:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def fold_t(az):
        """앞 트임에서 0, 옆·뒤에서 1."""
        a_ = abs(((az + 180.0) % 360.0) - 180.0)
        return a_, smoothstep(az_open, az_full, a_)

    def s_end(az):
        a_, f = fold_t(az)
        s_front = h.s_of_el(az, el_front - 2.0 * (a_ / az_open) ** 2)
        zz = lerp(z_side, z_back, smoothstep(az_full - 6.0, 170.0, a_))
        zz += 0.006 * k * math.sin(math.radians(az) * 5.0) * f       # 단이 조금 물결친다
        return lerp(s_front, s_at_z(az, zz), f ** 0.8)

    def wfn(pt):
        f_ = smoothstep(z_ear, e.shoulder_z - 0.02 * k, pt.z)
        return mixw({"head": 1.0}, {"neck": 0.3, "chest": 0.7}, 1.0 - f_) if f_ < 1.0 else {"head": 1.0}

    buf = Buf()
    S = [s_end(360.0 * j / cols) for j in range(cols)]
    P, N = [], []
    for i in range(1, rows + 1):
        u = i / rows
        rp, rn = [], []
        for j in range(cols):
            az = 360.0 * j / cols
            sj = S[j] * u
            p0, n0 = h.path(az, sj, 0.0)
            _, f = fold_t(az)
            # 귀 아래로 내려간 깊이 (0~1): 늘어진 천의 퍼짐·주름 세기
            dz = smoothstep(z_ear, min(z_back, z_side) - 0.02 * k, p0.z)
            drop = (1.0 - dz) if p0.z < z_ear else 0.0
            drop = max(0.0, min(1.0, (z_ear - p0.z) / max(1e-6, z_ear - z_back))) if p0.z < z_ear else 0.0
            dv = lift * k + flare * k * (drop ** 1.6) * f
            ridge = math.cos(math.radians(az) * folds * 0.5) ** 2           # cos² 능선: 둥근 주름
            dv += fold_amp * k * (drop ** 1.2) * f * (ridge - 0.35)
            dv += 0.006 * k * (drop ** 1.4) * f * math.sin(math.radians(az) * 2.0 + 0.6)   # 큰 물결
            p, n = h.path(az, sj, max(0.003 * k, dv))
            rp.append(p)
            rn.append(n)
        P.append(rp)
        N.append(rn)
    top, _ = h.path(0.0, 0.0, lift * k)
    ti_o = buf.vert(top, {"head": 1.0})
    ti_i = buf.vert(top - V((0, 0, th * k)), {"head": 1.0})
    o = [[buf.vert(P[i][j], wfn(P[i][j])) for j in range(cols)] for i in range(rows)]
    ii = [[buf.vert(P[i][j] - N[i][j] * th * k, wfn(P[i][j])) for j in range(cols)] for i in range(rows)]
    for j in range(cols):
        j2 = (j + 1) % cols
        buf.face((ti_o, o[0][j], o[0][j2]), veil_m)
        buf.face((ti_i, ii[0][j2], ii[0][j]), veil_in)
    for i in range(rows - 1):
        for j in range(cols):
            j2 = (j + 1) % cols
            buf.face((o[i][j], o[i + 1][j], o[i + 1][j2], o[i][j2]), veil_m)
            buf.face((ii[i][j], ii[i][j2], ii[i + 1][j2], ii[i + 1][j]), veil_in)
    R = rows - 1
    for j in range(cols):
        j2 = (j + 1) % cols
        buf.face((o[R][j], ii[R][j], ii[R][j2], o[R][j2]), veil_in)
    ob = buf.obj(f"{e.name}_veil", angle=55.0)
    c3._recalc_outward(ob)
    e.add(ob, group="head", tag="veil")
    # 아랫단 적갈색 띠 (단의 물결을 그대로 따라간다)
    pts = [P[R][j] for j in range(cols)]
    nrm = [N[R][j] for j in range(cols)]
    ups = []
    for j in range(cols):
        d_ = (P[R - 1][j] - P[R][j])
        d_ = (d_ - nrm[j] * d_.dot(nrm[j]))
        ups.append(d_.normalized() if d_.length > 1e-9 else V((0, 0, 1)))
    e.part("veil_rim", "head",
           lambda b_: elf._loop(b_, [q + u_ * rim_w * k * 0.5 + n_ * 0.0012 * k for q, u_, n_ in zip(pts, ups, nrm)],
                                nrm, ups, rim_w * k, 0.0020 * k, mat=veil_hem,
                                w=lambda t: wfn(pts[min(int(t * (cols - 1)), cols - 1)])))


draped_veil(el_front=EL_T, folds=11, fold_amp=0.022, flare=0.040)


def headband(buf):
    """이마의 흰 머리띠 한 줄 (두건 앞 가장자리 바로 아래, 장식 없음)."""
    w = {"head": 1.0}
    lift = 0.0078 * k
    pts, nrm, ups = [], [], []
    n = 21
    for i in range(n):
        az = lerp(-80.0, 80.0, i / (n - 1))
        el = EL_T - 2.0 - 2.0 * (abs(az) / 72.0) ** 2
        s = h.s_of_el(az, el)
        p, nn = h.path(az, s, lift)
        p2, _ = h.path(az, max(s - 0.01 * k, 0.0), lift)
        up = (p2 - p)
        up = (up - nn * up.dot(nn)).normalized()
        pts.append(p)
        nrm.append(nn)
        ups.append(up)
    elf._loop(buf, pts, nrm, ups, 0.016 * k, 0.0030 * k, mat=band_w, w=w, closed=False)


e.part("headband", "head", headband)
h.shine(el=52, spread=76, n=2, size=1.2)

# ---- 몸판·소매: 회청빛 남색 몸판(세운 깃은 앞가슴 색) + 긴 소매 + 넓은 흰 소맷단
wz, hz, sz = e.waist_z, e.hipj_z, e.shoulder_z
e.shirt(slate, hem=hz - 0.010 * k, collar="stand", collar_mat=cape, flare=0.010)
e.sleeves(slate, length=0.86, off=0.012, flare=0.020, puff=0.004, cuff=(white, 0.060, 0.006))

# ---- 가슴 가운데 좁은 연보랏빛 흰 띠 (원작 카드: 남색 몸판 사이로 보이는 안섶). 표장이 그 위에 걸린다
strip = c2.Shell(e, cape_hi, e.torso_top - 0.004 * k, e.chest_z - 0.040 * k, gap=168.0, back_only=True, off=0.013,
                 th=0.002, rows=5, cols=5, flare=[(0.0, 0.0), (1.0, 0.0)], bust_drape=0.010)
strip.done("chest_strip")

# ---- 가슴: 남색 몸판 위 세계수 교단 금 표장 (흰 판 없음). 깃의 마름모 매듭 → 금 줄기 → 가로대 둘 (위는 넓게, 아래는 조금 좁게)
def emblem(buf):
    def at(z, lift=0.0):
        a_ = e.anchor(("torso", z, 0.0, 0.016 * k + lift * k))
        return a_.matrix(), a_.w
    top = e.torso_top - 0.006 * k
    Mk, wk = at(top + 0.004 * k, 0.004)
    c2.prism(buf, c2.diamond_poly(0.022 * k, 0.026 * k), 0.005 * k, Mk, mat=gold,
             w=wk)
    n = 6
    z0, z1 = top - 0.012 * k, e.chest_z + 0.004 * k
    for i in range(n):
        za, zb = lerp(z0, z1, i / n), lerp(z0, z1, (i + 1) / n)
        Mi, wi = at((za + zb) / 2, 0.002)
        rbox(buf, (0.010 * k, 0.004 * k, (za - zb) * 1.06), Mi, mat=gold, w=wi, r=0.2, segs=1)
    for z, wdt, mt in ((lerp(z0, z1, 0.34), 0.056, gold), (z1 + 0.004 * k, 0.046, gold_d)):
        Mb_, wb_ = at(z, 0.003)
        rbox(buf, (wdt * k, 0.004 * k, 0.010 * k), Mb_, mat=mt, w=wb_, r=0.3, segs=1)


e.part("emblem", "body", emblem)

# ---- 어깨 깃: 연보랏빛 흰 짧은 망토, 앞이 V로 열리고 열린 가장자리에 짙은 먹색 띠 (목 앞에서 엇갈린다)
capelet = c2.Shell(e, cape, e.torso_top + 0.020 * k, sz - 0.100 * k, gap=[(0.0, 4.0), (0.25, 12.0), (1.0, 30.0)],
                   off=0.022, th=0.005, shoulder=0.55, cols=32, rows=10,
                   flare=[(0.0, 0.0), (0.2, 0.030), (0.5, 0.056), (1.0, 0.076)])
capelet.edge_trim(cape_trim, width=0.012, th=0.002).hem_trim(cape_hi, width=0.010, th=0.002)
capelet.done("capelet")


# ---- 허리띠 (밤색)
e.belt(belt_m, z=wz - 0.006 * k, h=0.016, th=0.004, off=0.026, buckle=gold, buckle_size=(0.018, 0.016))

# ---- 아래: 회청빛 남색 주름치마 + 흰 레이스 속치마 + 짙은 밤색 겉치마(앞이 열림) + 금 테 흰 앞자락
HEM = e.knee_z + 0.075 * k
petti = c2.Shell(e, lace, wz - 0.040 * k, HEM - 0.030 * k, off=0.014, th=0.003, skirt=True, rows=5, cols=32,
                 flare=[(0.0, 0.0), (0.5, 0.030), (1.0, 0.068)], ruffle=(0.007, 14, 0.6))
petti.done("petticoat")
skirt = c2.Shell(e, slate, wz + 0.004 * k, HEM, off=0.020, th=0.004, skirt=True, rows=7, cols=26,
                 flare=[(0.0, 0.0), (0.4, 0.028), (1.0, 0.066)], cover=True, pleat=(0.008, 12, 0.30), pleat_mat=slate_d)
skirt.done("skirt")
overskirt = c2.Shell(e, over, wz + 0.002 * k, HEM + 0.075 * k, gap=[(0.0, 24.0), (1.0, 36.0)], off=0.026, th=0.004,
                     skirt=True, rows=6, cols=22, flare=[(0.0, 0.0), (0.4, 0.034), (1.0, 0.074)])
overskirt.hem_trim(veil_hem, width=0.006, th=0.0015)
overskirt.done("overskirt")
TAB = lerp(wz, HEM, 0.50)
apron = c2.Shell(e, white, wz - 0.006 * k, TAB, gap=160.0, back_only=True, off=0.036, th=0.003,
                 skirt=True, rows=5, cols=7, flare=[(0.0, 0.0), (1.0, 0.026)])
apron.edge_trim(gold, width=0.016, th=0.0025)
# 방패꼴 끝: 흰 삼각 + 굵은 금 V 테 (앞자락 밑단에서 아래로 뾰족)
cv, nv = apron.surface(1.0, 0.0, 0.002 * k)
Mv = Matrix.Translation(cv) @ frame(nv, (0, 0, 1))
wv = c2.skirt_w(e, cv)
TW, TD = 0.058, 0.064
c2.prism(apron.buf, [(-TW * k, 0.004 * k), (TW * k, 0.004 * k), (0.0, -TD * k)], 0.003 * k, Mv, mat=white, w=wv)
for sg in (1, -1):
    pts = [(sg * TW * k, 0.006 * k), (sg * (TW - 0.024) * k, 0.006 * k), (0.0, -(TD - 0.030) * k), (0.0, -(TD + 0.004) * k)]
    if sg < 0:
        pts = list(reversed(pts))
    c2.prism(apron.buf, pts, 0.004 * k, Mv @ Matrix.Translation((0, 0.001 * k, 0)), mat=gold, w=wv)
cd, nd = apron.surface(0.55, 0.0, 0.004 * k)
c2.prism(apron.buf, c2.diamond_poly(0.013 * k, 0.016 * k), 0.003 * k, Matrix.Translation(cd) @ frame(nd, (0, 0, 1)),
         mat=gold, w=c2.skirt_w(e, cd))
apron.done("apron")

# ---- 도끼 멜빵: 허리 앞에서 캐릭터 왼쪽(+X) 엉덩이로 비스듬히 내려가는 밤색 가죽 끈
e.strap(strap_m, [("torso", wz + 0.002 * k, -26.0, 0.030 * k), ("torso", wz - 0.020 * k, 30.0, 0.034 * k),
                  ("torso", wz - 0.046 * k, 78.0, 0.040 * k)], width=0.018, th=0.005, name="axe_sling")

# ---- 짙은 먹색 허벅지 스타킹 + 흰 접단의 밝은 밤색 부츠
for sd in ("L", "R"):
    c2.leg_tube(e, stock, sd, 0.0, 0.70, off=0.004, name=f"stocking_{sd}", segs=8)
e.boots(boot, top=0.62, sole=(boot_d, 0.012), cuff=white, off=0.012, toe=0.004)

# ---- 작고 가는 옅은 하늘빛 날개 (허리 높이)
fairy.wings(e, span=0.26, height=0.15, sweep=42.0, raise_=-24.0, prim=3, cov=1, color="#eef6ff", color2="#bfe0f5",
            z=wz + 0.010 * k, style="slender")

res = e.finalize()


def hair_wave(ob):
    """원작 카드: 물결치며 끝으로 갈수록 바깥으로 퍼지는 머리. 턱 아래 정점만 옮긴다 (스키닝 웨이트는 그대로)."""
    if ob is None:
        return
    z0 = e.chin - 0.010 * k
    z1 = 0.10 * k
    lam = 0.20 * k
    for v in ob.data.vertices:
        co = v.co
        if co.z >= z0:
            continue
        t = min(1.0, (z0 - co.z) / max(1e-6, z0 - z1))
        side = 1.0 if co.x >= 0 else -1.0
        # 끝으로 갈수록 바깥(옆)으로 벌어진다
        co.x *= 1.0 + 0.40 * t ** 1.2
        co.y = co.y + (0.010 * k * t if co.y > 0 else 0.0)
        # 낮은 주파수 물결 (양옆이 반대 위상이라 대칭이 깨지지 않고 머리 다발처럼 출렁인다)
        ph = (z0 - co.z) / lam * 2.0 * math.pi
        co.x += side * 0.024 * k * t ** 0.8 * math.sin(ph)
        co.y += 0.012 * k * t ** 0.8 * math.cos(ph + 0.8)
    ob.data.update()


for key in ("hair", "hair_in"):
    hair_wave(res.get(key) if isinstance(res, dict) else None)
# 머리끝 복숭앗빛 그라데이션 (원작 기본 네르: 금발이 아래로 갈수록 물든다)
# (원작 카드: 채도 낮은 크림빛 금발, 가슴 아래부터 복숭앗빛. 각성 판 ner.glb의 노란 금발은 그대로 둔다)
z_top, z_hi, z_lo = 2.0 * k, e.chin - 0.02 * k, e.hipj_z - 0.10 * k
for key, base, cream, tip in (("hair", c3.NER_HAIR, "#f1e2c3", "#ebb8a4"), ("hair_in", c3.NER_HAIR_D, "#d9c09b", "#d49d8a"),
                              ("hair", c3.NER_HAIR_L, "#fbf3e2", "#f7dccd")):
    ob = res.get(key) if isinstance(res, dict) else None
    if ob is not None:
        fairy.vc_gradient(ob, base, [(z_lo, tip), (z_hi, cream), (z_top, cream)], tol=10)


# ---- 세계수의 도끼 (각성 전 손도끼): 별도 노드 ner_base_axe
def hand_axe():
    """로컬: 원점 = 파지점, 자루 = +Z(위: 손잡이 끝) / -Z(아래: 도끼머리), 날 = +Y. 길이 단위 m (k 배율)."""
    S = k
    b = Buf()

    def tube(z0, z1, r, mat):
        elf.loft(b, [{"c": V((0, 0, z0 * S)), "rx": r * S, "ry": r * S, "w": {}},
                     {"c": V((0, 0, z1 * S)), "rx": r * S, "ry": r * S, "w": {}}], segs=8, cap0="flat", cap1="flat",
                 mat=mat)
    tube(-0.30, 0.10, 0.012, shaft)
    tube(0.10, 0.135, 0.016, axe_gold)      # 손잡이 끝 금 고리
    tube(-0.06, -0.04, 0.015, silver_d)
    tube(-0.24, -0.215, 0.016, axe_gold)    # 머리 위 금 고리
    tube(-0.40, -0.30, 0.017, shaft)        # 머리 몸통
    core = b.obj("ner_base_axe_core", angle=35.0)
    # 반원 날 (+Y): 안쪽 은 판 + 바깥 금 테(조금 두껍게) + 양면 금 삼각 창 셋
    zc, R, RIM = -0.335, 0.105, 0.011
    rot = Matrix(((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))   # 2D (y, z) → 로컬 (+Y 날, Z 자루)

    def arc(r, a0, a1, n=15):
        return [(0.012 + r * math.cos(math.radians(lerp(a0, a1, i / (n - 1)))),
                 zc + r * 0.95 * math.sin(math.radians(lerp(a0, a1, i / (n - 1))))) for i in range(n)]
    inner = [(0.012, zc + 0.070)] + arc(R - RIM, 78.0, -78.0) + [(0.012, zc - 0.070)]
    blade = c2.poly_object("ner_base_axe_blade", [(y * S, z * S) for y, z in inner], 0.007 * S, rot, silver,
                           bevel=0.0012 * S)
    ring = arc(R, 80.0, -80.0) + arc(R - RIM - 0.002, -80.0, 80.0)
    rim = c2.poly_object("ner_base_axe_rim", [(y * S, z * S) for y, z in ring], 0.009 * S, rot, axe_gold, bevel=0.0012 * S)
    # 금 삼각 창: 가운데를 향해 꼭짓점이 모이는 부채꼴 삼각형 셋 (양면)
    b2 = Buf()
    for xx in (1, -1):
        for ang in (44.0, 0.0, -44.0):
            a = math.radians(ang)
            r0, r1 = 0.036, 0.066
            pts = [(0.012 + r0 * math.cos(a), zc + r0 * math.sin(a)),
                   (0.012 + r1 * math.cos(a + 0.22), zc + r1 * math.sin(a + 0.22)),
                   (0.012 + r1 * math.cos(a - 0.22), zc + r1 * math.sin(a - 0.22))]
            # 날 평면(로컬 Y–Z) 양면에 붙인다: 면의 바깥이 ±X
            Mside = Matrix.Translation(V((xx * 0.0040 * S, 0, 0))) @ Matrix(((0, -xx, 0, 0), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
            tri = [(y * S, z * S) for y, z in pts]
            if xx < 0:
                tri = list(reversed(tri))
            c2.prism(b2, tri, 0.0016 * S, Mside, mat=axe_gold, w={})
    # 뒤쪽 갈고리 (-Y): 뾰족한 은 날
    hook = [(-0.014, zc + 0.030), (-0.044, zc + 0.020), (-0.112, zc - 0.044), (-0.052, zc - 0.012),
            (-0.014, zc - 0.020)]
    hk = c2.poly_object("ner_base_axe_hook", [(y * S, z * S) for y, z in hook], 0.006 * S, rot, silver_d,
                        bevel=0.0012 * S)
    parts = [core, blade, rim, hk, b2.obj("ner_base_axe_trim", angle=35.0)]
    for p in parts:
        cb.apply_modifiers(p)
    return cb.join(parts, "ner_base_axe")


axe = hand_axe()
# 캐릭터 왼쪽(+X) 허리: 머리를 아래로, 날은 바깥(+X)을 향하고 자루가 조금 앞으로 기운다
hip_l = e.torso_point(wz - 0.040 * k, 84.0, 0.050 * k)[0]
Z = V((0.38, 0.22, 1.0)).normalized()
Y = V((1.0, 0.0, -0.10))
X = Y.cross(Z).normalized()
Y = Z.cross(X).normalized()
Mw = Matrix((X, Y, Z)).transposed().to_4x4()
Mw.translation = hip_l + V((0.020 * k, 0.010 * k, 0.040 * k))
# 허리 소켓(hips 본)에 붙인다: 이름은 오른쪽이지만 같은 hips 본이라 왼쪽 자리에서도 몸을 따라간다
c3.socket_prop(e, axe, "socket_hip_R", Mw, name="axe", outline=0.003, props={"grip": "0,0,0"})

e.export("characters/ner_base.glb")
