"""아멜리아(R41) (통칭 사멜리아): R41 모나티엄 제국의 전 시장이자 흑뉴아의 창조주. 흑뉴아를 피해 교주 차원으로
망명해 교단에 들어왔다. 4막 에르피엔 결전에서 죠안과 함께 R41 돌격 편대의 이탈을 설득한다.

원작 아멜리아(R41)(트릭컬 리바이브, '모나티엄 제국의 시장')의 복장을 바탕으로 한 카메오 모델.
- 유지한 식별 요소: 교주 차원 아멜리아와 같은 머리색(끝이 분홍빛 갈색), 헝클어진 앞머리와 바보털, 땋아 감은
  높은 경단, 가슴까지 오는 옆머리, 왼쪽 위 금색 별 + 초승달 머리핀, 연두빛 초록 눈과 다크서클(지친 눈),
  흰 더블 연구 코트(검은 단추, 큰 깃, 헐렁한 소매), 하늘색 셔츠, 검은 짧은 치마와 가터, 갈색 스타킹, 검은 신,
  손에 든 R41 삼각 단말(검은 판 + 마젠타 발광).
- 재해석: 단말은 R41 형태 언어(모따기 판, 짧은 발광)로 다시 그렸고 오른손에 든 별도 노드다. 코트 가슴에
  망명자 신분인 세계수 교단 방문증(흰 카드 + 녹색 잎 표식)을 달았다.
- 교주 차원 아멜리아와의 구분: 실루엣(흰 코트 + 짧은 치마 vs 검은 정장 + 통바지), 머리(헝클어진 앞머리·바보털·
  높은 경단 vs 단정한 크라운 브레이드), 핀 색(금색 vs 하늘색), 기본 표정(능글맞은 반쯤 감은 눈 + 다크서클).
- 표정: 키트 5종 + smirk(능글맞은 미소), sob(오열), shout(갑질 호통), wink(한쪽 눈 감고 하품, 교정 키 없음)
  + blink 교정 키.
근거: docs/art/characters-cameo2.md

npm run model -- art/blender/characters/amelia_r41.py
npm run shot -- characters/amelia_r41.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import amelia_common as am  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep  # noqa: E402

cb.reset()
M_ = elf.mat
e = am.body("amelia_r41")
k = e.k

# ---- 팔레트 (원작 실측: 코트 #f3eeee, 셔츠 #a9cbe8, 치마 #2b2730, 스타킹 #8a6658, 단말 마젠타 #c040ff)
coat = M_("sa_coat", "#f5f1f1")
coat_d = M_("sa_coat_d", "#d8d1d6")
btn = M_("sa_btn", "#2a262e")
shirt = M_("sa_shirt", "#a8cbe9")
shirt_d = M_("sa_shirt_d", "#86aed3")
skirt_m = M_("sa_skirt", "#2c2831")
strap_m = M_("sa_strap", "#1f1c24")
stock = M_("sa_stock", "#8d695b")
shoe = M_("sa_shoe", "#24212a")
sole = M_("sa_sole", "#141218")
gold = M_("sa_gold", "#eab54a")
card = M_("sa_card", "#ffffff")
leaf = M_("sa_leaf", "#5fb36a")
mark = M_("sa_bag", "#b48a9b")
dev_shell = cb.mat("sa_dev_shell", "#2a2733", line="#110c18", roughness=0.4)   # r41 PAL shell
dev_metal = cb.mat("sa_dev_metal", "#4d4959", line="#191422", roughness=0.4)
dev_glow = cb.mat("sa_dev_glow", "#ff4fd8", emission="#ff4fd8", unlit=True)

# ---- 얼굴: 능글맞게 반쯤 감은 눈, 살짝 올린 눈썹, 입꼬리 한쪽
am.face(e, base={"eye": {"top": 0.017, "lift": 0.004},
                 "brow": {"dz": 0.064, "ang": 3.0, "arch": 0.004},
                 "mouth": {"w": 0.019, "curve": 0.0026}},
        expr={
            # 오열: 처진 눈썹, 꽉 감기 직전의 젖은 눈, 크게 벌린 입
            "sob": {"eye": {"top": 0.010, "tilt_in": 0.012, "tilt_out": -0.010, "lift": 0.012},
                    "brow": {"ang": 24.0, "dz": 0.062},
                    "mouth": {"w": 0.030, "curve": -0.0060, "open": 0.016, "wave": 0.0018}},
            # 갑질 호통: 치켜뜬 눈, 내려간 눈썹 안쪽, 크게 벌린 입
            "shout": {"eye": {"top": 0.030, "ktop": 3.0, "tilt_in": -0.012},
                      "iris": {"pupil": 0.70},
                      "brow": {"ang": -22.0, "dz": 0.056, "th": 0.0068},
                      "mouth": {"w": 0.032, "curve": -0.0020, "open": 0.020, "top_arch": 0.004}},
        })
c2.face_expr(e, "smirk",
             both={"eye": {"top": 0.014, "lift": 0.010}, "mouth": {"w": 0.028, "curve": 0.0040, "open": 0.0020}},
             L={"brow": {"dz": 0.068, "ang": 6.0, "arch": 0.005}}, R={"brow": {"dz": 0.060, "ang": -2.0}},
             corner=(0.0085, -0.0010), mouth_dx=0.0025 * k)
# 윙크 하품: 오른눈(-X)을 감고 입을 벌린다 (원작 스탠딩)
c2.face_expr(e, "wink",
             both={"mouth": {"w": 0.022, "curve": 0.0, "open": 0.016, "top_arch": 0.004}},
             R={"eye": {"close": 1.0, "lift": 0.010}, "brow": {"dz": 0.056, "ang": 8.0}},
             L={"eye": {"top": 0.020}, "brow": {"dz": 0.066, "ang": 4.0}})
# 다크서클: 눈 아래 짧은 반달 선 (밤샘 연구)
fx = e.face_builder
bags = []
for sg in (1, -1):
    cx = sg * fx.ex
    cz = fx.ez - 0.036 * fx.sz
    pts = [(cx + sg * 0.024 * fx.sz * math.cos(math.radians(a)), cz - 0.006 * fx.sz * math.sin(math.radians(a)))
           for a in (20, 60, 100, 140)]
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        bags.append([(x0, z0 - 0.0022), (x1, z1 - 0.0022), (x1, z1 + 0.0022), (x0, z0 + 0.0022)])
c2.face_marks(e, "eyebags", bags, mark)


# ---- 머리: 헝클어진 앞머리 + 바보털 + 가슴까지 오는 옆머리 + 땋아 감은 높은 경단 (뒷머리는 올림)
def messy(h, lk):
    am.updo_back(h, lk)
    am.side_lock(h, lk)
    if lk["region"] == "side":
        lk["p"] = 1.8                    # 헝클어진 쪽: 끝이 조금 더 모이고 부풂
        lk["puff"] = 0.010 * k
    if lk["region"] == "front":
        ca = (lk["a0"] + lk["a1"]) / 2
        lk["p"] = 1.4
        lk["sweep"] += -8.0 if ca > 0 else 6.0
        if 6 < ca < 34:      # 왼눈 위로 흘러내리는 긴 다발
            lk["L"] += 0.030 * k
            lk["free"] += 0.020 * k


h = c2.hair(e, am.HAIR, dark=am.HAIR_D, light=am.HAIR_L, lock_fn=c2.lock_edit(messy), hug_fn=am.updo_hug,
            vol_fn=am.updo_vol)
h.cap(front=30, side=-8, back=-58, part=-12)
h.bangs(n=8, spread=64, tip_el=-2, jag=0.55, seed=4.0, sweep=4, curl=1.2)
h.sides(**dict(am.SIDES, length=0.30, n=2, puff=1.4))   # 넓은 옆머리 (교주 차원과 같은 폭), 끝만 두 갈래
h.back(length=-0.03, n=5)
h.ahoge(az=-14, height=0.10, curl=1.6, width=0.020)
h.shine(el=52, spread=64, size=1.0)
braid_m = M_("sa_braid", am.HAIR_BRAID)
am.braided_bun(h, 176, 44, 0.118, braid_m)
am.moon_pin(e, h, 56, 44, size=0.060, mat=gold, star=True, name="hairpin", tilt=-12)

# ---- 옷: 하늘색 셔츠, 검은 짧은 치마 + 가터, 갈색 스타킹, 검은 신
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(shirt, hem=wz - 0.010 * k, collar=None, flare=0.006, placket=shirt_d, buttons=shirt_d)


def shirt_collar(buf):
    w = {"neck": 0.4, "chest": 0.6}
    band(buf, (0, 0.004 * k, e.torso_top + 0.010 * k), (0, 0, 1), (1, 0, 0), 0.055 * k, 0.051 * k, 0.020 * k,
         0.005 * k, segs=16, mat=shirt, w=w, taper=-0.05)
    for sg in (1, -1):
        p, n = e.torso_point(e.torso_top - 0.002 * k, sg * 26, 0.015 * k)
        M = Matrix.Translation(p) @ elf.frame(n, (0, 0, 1)) @ Matrix.Rotation(math.radians(sg * 18), 4, "Y")
        c2.prism(buf, [(-sg * 0.022 * k, 0.012 * k), (sg * 0.016 * k, 0.012 * k), (sg * 0.006 * k, -0.030 * k)],
                 0.004 * k, M, mat=shirt, w=w)


e.part("shirt_collar", "body", shirt_collar)
q0 = e.q
e.q = 0.45    # 치마 속 속바지 (거의 안 보임)
e.pants(strap_m, length=0.05, bag=0.0, blouse=0.0, off=0.005)
e.q = q0
sk = c2.Shell(e, skirt_m, wz - 0.004 * k, hz - 0.090 * k, off=0.012, th=0.004, skirt=True, cols=22, rows=6,
              flare=[(0.0, 0.0), (1.0, 0.008)])
sk.hem_trim(strap_m, width=0.006, th=0.002)
sk.done("skirt")
e.ring(strap_m, "torso", wz - 0.004 * k, h=0.014, th=0.004, off=0.016, name="skirt_band")
for sd in ("L", "R"):
    c2.leg_tube(e, stock, sd, 0.42, 0.99, off=0.003, name=f"stocking_{sd}")
    e.ring(strap_m, f"leg_{sd}", 0.43, h=0.016, th=0.003, off=0.005, name=f"stock_top_{sd}")
    for a in (-22, 26):   # 가터 끈 (치마 밑단 → 스타킹 윗단, 앞쪽 두 줄)
        e.strap(strap_m, [(f"leg_{sd}", 0.16, a, 0.007 * k), (f"leg_{sd}", 0.43, a, 0.0075 * k)], width=0.006,
                th=0.0015, name=f"garter_{sd}{a}")
e.boots(shoe, top=0.95, sole=(sole, 0.014), toe=0.004, off=0.008)

# ---- 흰 더블 연구 코트: 앞이 열리고 무릎 위까지, 큰 깃, 검은 단추, 헐렁한 소매
ztop = e.torso_top - 0.004 * k
zhem = 0.200 * k
ct = c2.Shell(e, coat, ztop, zhem, gap=[(0.0, 30.0), (0.20, 16.0), (0.45, 18.0), (1.0, 34.0)], off=0.024, th=0.005,
              skirt=True, rows=14, cols=20, flare=[(0.0, 0.0), (0.4, 0.014), (1.0, 0.050)], shoulder=0.9)
ct.edge_trim(coat, width=0.030, th=0.004, i1=6)                    # 넓은 깃: 고른 폭 (계단 없음)
ct.edge_trim(coat_d, width=0.006, th=0.002, i0=6)
ct.hem_trim(coat_d, width=0.009, th=0.002)
ct.done("coat")
# 큰 뒷깃: 목 뒤와 옆을 두르고 앞은 열린 세운 깃 (닫힌 고리는 목을 감싼 띠처럼 보였다)
cc = c2.Shell(e, coat, e.torso_top + 0.036 * k, e.torso_top - 0.006 * k, gap=44.0, off=0.026, th=0.005, rows=3,
              cols=18, flare=[(0.0, 0.012), (1.0, 0.0)])
cc.done("coat_collar")
e.sleeves(coat, length=1.02, off=0.020, flare=0.034, puff=0.008, cuff=(coat_d, 0.024, 0.005))
H = ztop - zhem


def coat_bits(buf):
    # 더블 단추: 왼쪽 앞판 2열 3단 + 오른쪽 앞판 1열
    for i, z in enumerate((cz - 0.010 * k, wz - 0.012 * k, hz + 0.006 * k)):
        u = (ztop - z) / H
        for a in (22, 38, -24):
            Mx = ct.frame_at(u, a, 0.001 * k)
            p = Mx.to_translation()
            n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
            w = c2.skirt_w(e, p) if p.z < hz else e._torso_wfn(p, 0)
            disc(buf, p, n, (0, 0, 1), 0.0068 * k, 0.0068 * k, 0.0032 * k, segs=10, mat=btn, w=w)
    # 허리 주머니
    for sg in (1, -1):
        u = (ztop - (hz - 0.030 * k)) / H
        Mx = ct.frame_at(u, sg * 54, 0.001 * k)
        w = c2.skirt_w(e, Mx.to_translation())
        rbox(buf, (0.060 * k, 0.004 * k, 0.050 * k), Mx @ Matrix.Translation((0, -0.002 * k, 0)), mat=coat_d, w=w,
             r=0.15, segs=1)
    # 세계수 교단 방문증 (왼쪽 가슴, 망명자 신분)
    Mi = ct.frame_at((ztop - (cz + 0.020 * k)) / H, 40, 0.003 * k) @ Matrix.Rotation(math.radians(6), 4, "Y")
    w = e._torso_wfn(Mi.to_translation(), 0)
    rbox(buf, (0.030 * k, 0.004 * k, 0.038 * k), Mi @ Matrix.Translation((0, -0.002 * k, -0.020 * k)), mat=card, w=w,
         r=0.15, segs=1)
    c2.prism(buf, c2.diamond_poly(0.012 * k, 0.018 * k), 0.002 * k,
             Mi @ Matrix.Translation((0, -0.004 * k, -0.016 * k)), mat=leaf, w=w)


e.part("coat_bits", "body", coat_bits)

am.done_hair(e)
e.finalize()
am.tip_gradient(e, 0.21)

# ---- R41 삼각 단말 (오른손, 별도 노드): 모따기 삼각 판 + 마젠타 삼각 발광 + 건메탈 테
buf = Buf()
W = e.W["R"]
d = e.adir["R"]
pn = e.palm_n["R"]
cdev = W + d * 0.046 * k + pn * 0.020 * k + V((0, -0.012 * k, 0))
Md = Matrix.Translation(cdev) @ elf.frame(V((0, -1, 0.25)).normalized(), -d) @ Matrix.Rotation(math.radians(12), 4, "Y")
tri = [(0.0, 0.050 * k), (-0.045 * k, -0.026 * k), (0.045 * k, -0.026 * k)]
c2.prism(buf, tri, 0.014 * k, Md @ Matrix.Translation((0, 0.007 * k, 0)), mat=dev_shell, w={}, chamfer=0.004 * k)
c2.prism(buf, [(x * 0.80, z * 0.80) for x, z in tri], 0.004 * k, Md @ Matrix.Translation((0, -0.0065 * k, 0)),
         mat=dev_metal, w={})
c2.prism(buf, [(x * 0.52, z * 0.52 - 0.002 * k) for x, z in tri], 0.003 * k,
         Md @ Matrix.Translation((0, -0.0095 * k, 0)), mat=dev_glow, w={})
ob = buf.obj("amelia_r41_device_tmp", angle=30.0)
c2.prop(e, "device", ob, "hand_R", outline=0.0025)

e.export("characters/amelia_r41.glb")
