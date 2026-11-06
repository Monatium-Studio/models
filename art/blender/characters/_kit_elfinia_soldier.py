"""키트 검증용: 엘피니아 군 전투복을 입은 무명 병사 (오리지널 인물).

프롤로그 캐시(지구 침공 당시)와 R41 병사의 바탕이 되는 전투복 기준 모델.
근거: docs/art/reference-notes.md 5장 (알레트·타이다·레이지의 전투복 공통 요소를 재해석)

npm run model -- art/blender/characters/_kit_elfinia_soldier.py
npm run shot -- characters/_kit_elfinia_soldier.glb
npm run shot -- characters/_kit_elfinia_soldier.glb --mode fpbody --pitch -60
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402

cb.reset()
M = elf.mat
e = elf.Elf("elfsoldier", segs=0.85, hand_q=0.8)

# ---- 팔레트 (reference-notes.md 5.3: 원작 실측색을 바탕으로 한 재해석)
#   천(군복)은 회녹색 계열, 장비(헬멧·군화·벨트·웨빙)는 원작 특유의 자줏빛 도는 회색 계열
jacket = M("es_jacket", "#a3ada1")      # 회녹색 상의 (레이지 위장복 바탕색 근처)
jacket_d = M("es_jacket_d", "#7f8a80")   # 여밈·덮개·소맷단
pants = M("es_pants", "#939e98")         # 한 톤 어두운 하의
pants_d = M("es_pants_d", "#76807b")
web = M("es_web", "#635b62")             # 웨빙·파우치 (자줏빛 회색)
web_d = M("es_web_d", "#4f474e")
belt = M("es_belt", "#4a4149")           # 벨트 (원작 실측 #4b424a)
metal = M("es_metal", "#cfcac4")         # 무광 은색 버클·단추
boots = M("es_boots", "#58535d")
boots_d = M("es_boots_d", "#443f48")
sole = M("es_sole", "#2f2b31")
tab = M("es_tab", "#b9b2a8")
glove = M("es_glove", "#4f474e")
helmet = M("es_helmet", "#6a636b")       # 헬멧 (원작 실측 #655d64보다 약간 밝게)
helmet_d = M("es_helmet_d", "#524b53")
rank_bg = M("es_rank_bg", "#2f3644")
rank_fg = M("es_rank_fg", "#d6b25e")
led = M("es_led", "#ffffff", emission="#7ff0ea", unlit=True)

# ---- 얼굴, 머리카락 (헬멧 아래 짧은 단발)
e.face(eye_color="#5f8a86", lash="#3b2326")
h = e.hair("#6b4636")
h.cap(front=28, side=-10, back=-52, segs=20, rows=5)   # 헬멧 아래: 성글게 (v2 해상도 힌트)
h.bangs(n=6, spread=50, tip_el=-2)
h.sides(length=0.035, width=0.07)
h.back(length=0.02, n=5)

# ---- 전투복
e.shirt(jacket, collar="stand", collar_mat=jacket_d, placket=jacket_d, buttons=metal, flare=0.012)
e.sleeves(jacket, length=0.95, cuff=(jacket_d, 0.022, 0.0045))
e.pants(pants, bag=0.013, blouse=0.020)
e.boots(boots, top=0.66, sole=(sole, 0.016), cuff=boots_d, laces=boots_d, tab=tab)
e.gloves(glove, cuff=web_d)
e.belt(belt, buckle=metal, loops=belt)
e.epaulet(jacket_d, button=metal)

k = e.k
cz = e.chest_z
# 왼쪽 가슴 아래 펜 주머니 (덮개 + 단추)
e.pouch(jacket, ("torso", cz - 0.035 * k, 40, 0.010 * k), size=(0.040, 0.006, 0.040), flap=jacket_d, button=metal,
        name="chest_pocket_L")
# 계급장 (가슴 가운데 위, 단순한 막대 두 줄 — 원작 문양 아님)
e.patch(rank_bg, ("torso", cz + 0.072 * k, 22, 0.012 * k), size=(0.026, 0.020), name="rank_bg")
e.patch(rank_fg, ("torso", cz + 0.072 * k, 22, 0.0135 * k), size=(0.018, 0.012), shape="bars2", name="rank_fg")
# 왼팔 부대 패치
e.patch(rank_bg, ("arm_L", 0.16, 60, 0.012 * k), size=(0.028, 0.028), shape="round", name="unit_patch")
e.patch(rank_fg, ("arm_L", 0.16, 60, 0.0135 * k), size=(0.014, 0.014), shape="diamond", name="unit_mark")

# 가벼운 가슴 장비: Y자 멜빵 + 가슴 앞 탄창 파우치 3개 (1인칭에서 내려다보면 덮개가 보이는 높이)
sz = e.shoulder_z
pz = cz + 0.012 * k
for s in (1, -1):
    e.strap(web, [("torso", pz, s * 30, 0.018 * k), ("torso", sz - 0.005 * k, s * 40, 0.014 * k),
                  ("torso", sz + 0.02 * k, s * 58, 0.014 * k), ("torso", sz - 0.01 * k, s * 122, 0.014 * k),
                  ("torso", cz, s * 150, 0.016 * k), ("torso", e.waist_z + 0.02 * k, s * 150, 0.020 * k)],
            width=0.020, th=0.004, name=f"harness_{'L' if s > 0 else 'R'}")
e.ring(web, "torso", pz - 0.035 * k, h=0.020, th=0.004, off=0.014, name="rig_band")
for i, a in enumerate((-26, 0, 26)):
    e.pouch(web, ("torso", pz - 0.004 * k, a, 0.018 * k), size=(0.036, 0.024, 0.056), flap=web_d,
            button=metal, molle=web_d, name=f"mag_pouch_{i}")
# 허벅지 파우치 (오른쪽, 끈으로 고정)
e.pouch(web, ("leg_R", 0.30, -75, 0.024 * k), size=(0.052, 0.026, 0.062), flap=web_d, button=metal, strap=belt,
        name="thigh_pouch")
# 바지 옆 건빵 주머니 (왼쪽)
e.pouch(pants, ("leg_L", 0.34, 85, 0.022 * k), size=(0.05, 0.010, 0.058), flap=pants_d, button=pants_d,
        name="cargo_L")

# ---- 헬멧 + 통신기
e.helmet(helmet, rim=helmet_d, band_mat=web_d, buckle=metal, strap=web_d)


def headset(buf, Mx, w):
    elf.rbox(buf, (0.05 * k, 0.03 * k, 0.045 * k), Mx @ elf.Matrix.Translation((0, -0.012 * k, 0)), mat=web_d, w=w,
             r=0.45, segs=2)
    elf.rbox(buf, (0.032 * k, 0.012 * k, 0.03 * k), Mx @ elf.Matrix.Translation((0, -0.03 * k, 0)), mat=helmet_d,
             w=w, r=0.4, segs=1)
    c = Mx @ elf.V((0.010 * k, -0.037 * k, 0.006 * k))
    n = (Mx.to_3x3() @ elf.V((0, -1, 0))).normalized()
    elf.disc(buf, c, n, (0, 0, 1), 0.0045 * k, 0.0045 * k, 0.0015 * k, segs=10, mat=led, w=w)
    # 짧은 안테나
    base = Mx @ elf.V((-0.014 * k, -0.02 * k, 0.02 * k))
    st = [{"c": base, "rx": 0.003 * k, "ry": 0.003 * k, "w": w},
          {"c": base + elf.V((0, 0.02 * k, 0.06 * k)), "rx": 0.002 * k, "ry": 0.002 * k, "w": w}]
    elf.loft(buf, st, segs=6, cap0="flat", cap1="round", mat=web_d)


e.gear("headset", ("head", -100, 18, 0.034 * k), headset)

e.finalize()
e.export("characters/_kit_elfinia_soldier.glb")
