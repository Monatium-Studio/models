"""로네 (인터루드 포로 생활 ~ 엘리아스 불시착): 주황 죄수복 차림.

사용자 확정(docs/scenario.md 인터루드 2번): 포로 생활부터 탈출 직후까지 엘프들은 미국 교도소식 주황 죄수복을 입는다.
- 얼굴·머리·체격은 rone.py와 같다(코드를 그대로 옮김, rone.py는 고치지 않았다): 회갈색 졸린 눈, 긴 갈색 생머리,
  크림빛 금색 머리띠, 오른쪽 가슴까지 오는 옆머리, 왼쪽 가슴 높이에서 묶어 종아리까지 늘어뜨린 낮은 사이드테일.
  표정: 키트 5종 + fluster, cry, dreamy, smug.
- 판금 갑옷·감비슨·검은 없다(압수). 수용 번호 0233 (원작의 '창문 프로그램' 증언을 남긴 포로).
- 복장: 공용 죄수복 모듈(art/blender/lib/prisoner.py).

npm run model -- art/blender/characters/rone_prisoner.py
npm run shot -- characters/rone_prisoner.glb
npm run shot -- characters/rone_prisoner.glb --focus rone_prisoner_face --views front,34
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import prisoner as pr  # noqa: E402
from elf import V  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("rone_prisoner", height=1.20, head=0.45, leg=1.02, chest=0.15, bust=0.20, segs=0.76, hand_q=0.6, cheek=0.10)
k = e.k
leather_d = M_("rnpr_leather_d", "#4f3429")
band_m = M_("rnpr_band", "#f1dba3")

# ---- 얼굴 (rone.py와 같다): 회갈색 졸린 눈 (윗눈꺼풀이 무겁게 내려옴), 살짝 벌린 입, 걱정 많은 눈썹
e.face(eye_color="#8c7d77", iris_dark="#4a3c38", iris_light="#e0d6cf", pupil="#2a2020",
       lash="#4a2e2a", brow="#6e4c40", blush="#f7a7a4", blush_size=1.1,
       base={"eye": {"top": 0.016, "ktop": 3.8, "tilt_out": -0.004, "cout": 0.012},
             "iris": {"cz": 0.0020},
             "brow": {"dz": 0.062, "ang": 7.0, "arch": 0.002},
             "mouth": {"w": 0.018, "curve": 0.0020, "open": 0.0035, "top_arch": 0.0010}},
       expr={
           # 허둥지둥: 동그래진 눈, 작은 동공, 올라간 눈썹, 물결 입
           "fluster": {"eye": {"top": 0.034, "ktop": 2.4, "bot": 0.056},
                       "iris": {"pupil": 0.55, "rx": 0.026, "ry": 0.034},
                       "brow": {"ang": 18.0, "dz": 0.074, "arch": 0.004},
                       "mouth": {"w": 0.024, "curve": -0.0020, "open": 0.0080, "wave": 0.0018}},
           # 오열 (돈까스가 날아갔을 때): 처진 눈썹, 가늘게 젖은 눈, 크게 벌린 입
           "cry": {"eye": {"top": 0.008, "tilt_in": 0.012, "tilt_out": -0.012, "lift": 0.016},
                   "brow": {"ang": 26.0, "dz": 0.062},
                   "mouth": {"w": 0.032, "curve": -0.0070, "open": 0.020, "wave": 0.0020}},
           # 돈까스 상상: 반달 눈웃음, 벌린 입
           "dreamy": {"eye": {"top": 0.014, "lift": 0.026, "kbot": 2.6},
                      "brow": {"ang": 10.0, "dz": 0.068, "arch": 0.006},
                      "mouth": {"w": 0.030, "curve": 0.0070, "open": 0.012, "top_arch": -0.001}},
       })
c2.face_expr(e, "smug",
             both={"eye": {"top": 0.013, "lift": 0.010}, "mouth": {"w": 0.026, "curve": 0.0035, "open": 0.0}},
             L={"brow": {"dz": 0.066, "ang": -2.0}}, R={"brow": {"dz": 0.060, "ang": -8.0}},
             corner=(0.0070, -0.0005), mouth_dx=0.0020 * k)


# ---- 머리 (rone.py와 같다): 갈색 생머리, 옆으로 쓸린 앞머리, 오른쪽 긴 옆머리, 머리띠, 왼쪽 낮은 사이드테일
HAIR = "#8b6456"


def rone_locks(h, lk):
    if lk["region"] == "side" and lk.get("side") == "R":
        lk["L"] += 0.14 * k          # 오른쪽 옆머리는 가슴까지
        lk["free"] += 0.06 * k
    if lk["region"] == "front":
        lk["p"] = 1.7


h = c2.hair(e, HAIR, dark="#664539", light="#b48d7c", lock_fn=c2.lock_edit(rone_locks))
h.cap(front=30, side=-8, back=-48, part=16)
h.bangs(n=6, spread=60, tip_el=0, jag=0.25, sweep=-12, seed=3.0)
h.sides(length=0.10, width=0.080)
h.back(length=0.10, n=7, spread=96)
h.shine(el=50, spread=70, size=1.1)
c2.on_hair_band(e, h, band_m, az0=-104, az1=104, el_fn=lambda az: 56.0 - 46.0 * (abs(az) / 104.0) ** 1.8,
                width=0.022, th=0.005, lift=-0.003)

# 낮은 사이드테일 (왼쪽): 귀 뒤 아래에서 모아 가슴 높이에서 묶고 종아리까지
o = h.vol
root, rn = h.path(124.0, h.s_of_el(124.0, -16.0), -o * 0.3)
sz, wz, hz, cz = e.shoulder_z, e.waist_z, e.hipj_z, e.chest_z
ctrl = [root,
        V((0.168 * k, 0.034 * k, e.chin - 0.010 * k)),
        V((0.178 * k, -0.018 * k, sz + 0.010 * k)),
        V((0.196 * k, -0.040 * k, cz - 0.020 * k)),
        V((0.208 * k, -0.026 * k, wz - 0.030 * k)),
        V((0.220 * k, -0.004 * k, hz - 0.040 * k)),
        V((0.232 * k, 0.020 * k, e.knee_z + 0.010 * k)),
        V((0.248 * k, 0.050 * k, 0.150 * k))]
tl = c2.Tail(h, "hair_tail_L", ctrl, 0.108 * k, 0.060 * k, bones=3, parent="chest", root_bone="head", t_hold=0.62,
             root_w=1.0,
             clumps=((0.32, 0.55, 0.92), (-0.30, 0.55, 0.88)),
             ref_fn=lambda t, q: V((1.0, 0.25, 0.0)))
tl.tie(leather_d, t=0.30, size=1.0, h_=0.026, th=0.008)

# ---- 죄수복
P = pr.mats("rnpr")
pr.outfit(e, P, number="0233")

e.finalize()
e.export("characters/rone_prisoner.glb")
