"""알레트: 교주 차원 모나티엄 진압반의 막내 하사. 1막 M2 시청 방어선에 투입된다(사용자 결정, 원작 침공전 모나티엄 배치).

원작 알레트(트릭컬 리바이브)의 진압 장비 차림(로비 스탠딩·카드)을 따른다. 전투복 언어는 엘피니아 군 전투복 계열
(reference-notes 5장)이고 프롤로그 캐시의 전투복과 같은 계열이다. 근거: docs/art/characters-cameo3.md.
- 식별 요소: 재빛 분홍 갈색 단발, 짙은 회색 동그란 눈과 굵은 눈썹, 작은 웃는 입, 진회색 진압 헬멧(앞 챙, 정수리 오른쪽
  세로 통풍구, 옆 나사), 진회색 전술 조끼(높은 깃, 가슴 파우치, 가운데 표식 판), 둥근 어깨 보호대, 팔꿈치 보호대,
  진회색 장갑, 밝은 회색 상하의, 2단 무릎 보호대, 진회색 군화와 가로 띠, 진압 방패.
- 재해석: 조끼 가운데 판의 원작 날개 표식은 옮기지 않고 기하 갈매기 패치로 바꿨다(reference-notes 5.4). 방패는
  원작 디자인 대신 모나티엄 진압 방패로 새로 그렸다(시야창, 고무 테, 엘프 로고 휘장: ART_GUIDE 1장 예외).
  별도 노드 alette_shield(socket_hand_L). 오른손은 비워 두고 런타임에 진압반 권총·전기충격봉을 붙인다.
- 표정: 키트 5종 + salute(경례의 다부진 얼굴) + panic(겁에 질린 막내) + shout(돌격 구호) + blink 교정 키.

npm run model -- art/blender/characters/alette.py
npm run shot -- characters/alette.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import elf_trio_common as tc  # noqa: E402
from elf import V, Matrix, Buf, band, rbox, disc, lerp  # noqa: E402

cb.reset()
e = elf.Elf("alette", height=1.20, segs=0.66, hand_q=0.45, cheek=0.12)
k = e.k
M_ = elf.mat
gray = M_("al_gray", "#a39ca1")          # 밝은 회색 상하의 (원작 #a1999e)
gray_d = M_("al_gray_d", "#837c82")
vest = M_("al_vest", "#625a62")          # 진회색 조끼·장비 (원작 #655c63)
vest_d = M_("al_vest_d", "#4b444c")
pad = M_("al_pad", "#57505a")
helm = M_("al_helmet", "#5c5660")        # 진압 헬멧 (원작 #645c64)
helm_d = M_("al_helmet_d", "#433e47")
vent = M_("al_vent", "#36323a")
boot = M_("al_boot", "#55505a")
boot_d = M_("al_boot_d", "#403b44")
patch_m = M_("al_patch", "#b9b3bb")

# ---- 얼굴: 짙은 회색 동그란 눈, 굵은 짙은 눈썹, 작은 웃는 입
e.face(eye_color="#6b6872", iris_dark="#3c3943", iris_light="#c3c0ca", pupil="#2a2830",
       lash="#3a2a2c", brow="#4a3434", brow_th=1.4, blush="#f6a3a6", blush_size=1.15,
       base={"eye": {"top": 0.030, "ktop": 3.0},
             "brow": {"ang": -4.0, "dz": 0.066, "arch": 0.002},
             "mouth": {"w": 0.018, "curve": 0.0040}},
       expr={
           # 경례: 다부지게 뜬 눈, 다문 웃음
           "salute": {"eye": {"top": 0.032, "ktop": 2.8, "tilt_in": -0.004},
                      "brow": {"ang": -10.0, "dz": 0.064, "th": 0.0076},
                      "mouth": {"w": 0.018, "curve": 0.0030}},
           # 겁에 질린 막내: 작은 동공, 올라간 눈썹, 떨리는 입
           "panic": {"eye": {"top": 0.036, "ktop": 2.2, "bot": 0.058},
                     "iris": {"pupil": 0.45, "rx": 0.024, "ry": 0.032},
                     "brow": {"ang": 20.0, "dz": 0.074},
                     "mouth": {"w": 0.026, "curve": -0.0050, "open": 0.0120, "wave": 0.0025}},
           # 돌격 구호: 내린 눈썹, 크게 벌린 입
           "shout": {"eye": {"top": 0.030, "ktop": 3.0, "tilt_in": -0.010},
                     "brow": {"ang": -20.0, "dz": 0.058, "th": 0.0078},
                     "mouth": {"w": 0.032, "curve": 0.0, "open": 0.026, "top_arch": 0.005}},
       })

# ---- 머리: 재빛 분홍 갈색 단발 (헬멧 아래)
h = e.hair("#8f6f6a", dark="#6a4e4c", light="#b8968e")
h.cap(front=28, side=-10, back=-50, segs=16, rows=4)
h.bangs(n=6, spread=52, tip_el=-2, seed=4.0)
h.sides(length=0.07, width=0.076, curl=0.6)
h.back(length=0.05, n=7)

# ---- 진압 헬멧: 앞 챙, 정수리 통풍구, 턱끈
e.helmet(helm, off=0.040, front=12.0, side=0.0, back=-24.0, rim=helm_d, ridge=helm_d, vents=vent, strap=vest_d)
# 정수리 오른쪽 세로 통풍구 줄 + 옆 나사 (원작 실루엣의 오른쪽 홈 줄)


def helmet_bits(buf):
    w = {"head": 1.0}
    # 앞 챙: 이마 위에서 앞·아래로 튀어나온 두툼한 진압 헬멧 챙 (원작 실루엣)
    n = 15
    top_i, out_i, bot_i, bin_i = [], [], [], []
    for j in range(n):
        az = lerp(-84.0, 84.0, j / (n - 1))
        p0, n0 = e.head_point(az, 13.0, 0.044 * k)
        a = math.radians(az)
        out = V((math.sin(a), -math.cos(a), 0.0))
        f = math.cos(a) ** 0.6
        p1 = p0 + out * (0.030 * k * f + 0.006 * k) + V((0, 0, -0.012 * k * f))
        top_i.append(buf.vert(p0 + V((0, 0, 0.010 * k)), w))
        out_i.append(buf.vert(p1, w))
        bot_i.append(buf.vert(p1 + V((0, 0, -0.012 * k)), w))
        bin_i.append(buf.vert(p0 + V((0, 0, -0.010 * k)), w))
    for j in range(n - 1):
        buf.face((top_i[j], top_i[j + 1], out_i[j + 1], out_i[j]), helm)
        buf.face((out_i[j], out_i[j + 1], bot_i[j + 1], bot_i[j]), helm_d)
        buf.face((bot_i[j], bot_i[j + 1], bin_i[j + 1], bin_i[j]), helm_d)
    for j in (0, n - 1):
        q = (top_i[j], out_i[j], bot_i[j], bin_i[j])
        buf.face(q if j == 0 else q[::-1], helm_d)
    for i in range(3):
        el = 30.0 + 14.0 * i
        p, n = e.head_point(-46.0, el, 0.044 * k)
        Mx = Matrix.Translation(p) @ elf.frame(n, (0, 0, 1))
        rbox(buf, (0.012 * k, 0.006 * k, 0.026 * k), Mx, mat=vent, w=w, r=0.3, segs=1)
    for s in (1, -1):
        p, n = e.head_point(s * 92.0, 14.0, 0.043 * k)
        disc(buf, p, n, (0, 0, 1), 0.008 * k, 0.008 * k, 0.003 * k, segs=10, mat=helm_d, w=w)


e.part("helmet_bits", "head", helmet_bits)

# ---- 상의·하의: 밝은 회색 + 진회색 전술 조끼
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
sz = e.shoulder_z
e.shirt(gray, collar="stand", collar_mat=gray_d, flare=0.010)
e.sleeves(gray, length=0.90, off=0.012, cuff=(gray_d, 0.018, 0.004))
m = tc.base_gear(e, "al", pants=gray, pants_d=gray_d, boots=boot, boots_d=boot_d, glove=vest_d, glove_cuff=vest,
                 belt_z=hz - 0.024 * k)
vs = c2.Shell(e, vest, e.torso_top - 0.004 * k, hz - 0.004 * k, off=0.024, th=0.007, rows=6, cols=20,
              flare=[(0.0, 0.0), (1.0, 0.006)])
vs.hem_trim(vest_d, width=0.010, th=0.003)
vs.done("vest")
e.part("vest_collar", "body", lambda buf: band(buf, (0, 0.006 * k, e.torso_top + 0.004 * k), (0, 0, 1), (1, 0, 0),
                                               0.074 * k, 0.068 * k, 0.034 * k, 0.007 * k, segs=16, mat=vest,
                                               w={"neck": 0.3, "chest": 0.7}, taper=0.06))
# 가운데 표식 판 + 기하 갈매기 패치 (원작 날개 표식 대신)
e.pouch(vest_d, ("torso", cz - 0.004 * k, 0, 0.030 * k), size=(0.056, 0.010, 0.060), name="plate")
e.patch(patch_m, ("torso", cz - 0.004 * k, 0, 0.042 * k), size=(0.030, 0.020), shape="chevron", name="plate_mark")
for i, a in enumerate((-34, 34)):
    e.pouch(vest_d, ("torso", cz + 0.020 * k, a, 0.032 * k), size=(0.036, 0.020, 0.046), flap=vest,
            button=m["metal"], name=f"chest_pouch_{i}")
for i, a in enumerate((-64, 64)):
    e.pouch(vest_d, ("torso", wz - 0.012 * k, a, 0.032 * k), size=(0.040, 0.022, 0.044), flap=vest,
            button=m["metal"], name=f"belly_pouch_{i}")
# 보호대: 둥근 어깨, 팔꿈치, 2단 무릎
for sd, s in (("L", 1), ("R", -1)):
    e.pad(pad, (f"arm_{sd}", 0.10, s * 70, 0.020 * k), size=(0.074, 0.020, 0.070), name=f"shoulder_pad_{sd}")
    e.pad(pad, (f"arm_{sd}", 0.50, 180, 0.016 * k), size=(0.050, 0.016, 0.050), name=f"elbow_pad_{sd}")
    e.pad(pad, (f"leg_{sd}", 0.52, 0, 0.018 * k), size=(0.064, 0.020, 0.056), strap=vest_d, name=f"knee_pad_{sd}")
    e.pad(pad, (f"leg_{sd}", 0.62, 0, 0.020 * k), size=(0.056, 0.018, 0.044), name=f"shin_pad_{sd}")
    for t in (0.80, 0.90):
        e.ring(vest_d, f"leg_{sd}", t, h=0.012, th=0.004, off=0.020, name=f"boot_strap_{sd}{t}")

e.finalize()

# ---- 진압 방패 (별도 노드 shield): 왼손, 앞면이 바깥 앞을 본다
sh = tc.riot_shield(e)
sock = bpy.data.objects["socket_hand_L"]
pos = sock.matrix_world.translation.copy()
front = V((0.45, -1.0, 0.0)).normalized()         # 방패 앞면(로컬 -Y)이 향할 방향
Mw = tc.frame_world(-front, (0, 0, 1))
Mw.translation = pos + V((0.020 * k, -0.010 * k, 0.0))
tc.attach(e, sh, "socket_hand_L", Mw, "shield")

e.export("characters/alette.glb")
