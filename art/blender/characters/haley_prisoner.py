"""헤일리 (인터루드 포로 생활 ~ 엘리아스 불시착): 주황 죄수복 차림.

사용자 확정(docs/scenario.md 인터루드 2번): 포로 생활부터 탈출 직후까지 엘프들은 미국 교도소식 주황 죄수복을 입는다.
투항 장면(interlude_surrender)은 아직 정복이라 characters/haley.py를 그대로 쓴다.
- 얼굴·머리·체격은 haley.py와 같다(코드를 그대로 옮김, haley.py는 고치지 않았다): 분홍빛 눈과 굵은 눈썹, 무릎까지
  오는 붉은 생머리와 일자 앞머리, 왼쪽 귀의 은색 별 귀걸이. 표정: 키트 5종 + confident, briefing, salute, smirk.
- 정모·망토·견장·훈장은 없다(압수). 계급은 따로 달지 않고, 먼저 나서서 투항한 지휘관이라 수용 번호만 0001이다.
  정모가 없어 머리 덩어리가 눌리지 않은 본래 볼륨으로 나온다. 긴 뒷머리가 등의 스텐실을 덮는다.
- 복장: 공용 죄수복 모듈(art/blender/lib/prisoner.py).

npm run model -- art/blender/characters/haley_prisoner.py
npm run shot -- characters/haley_prisoner.glb
npm run shot -- characters/haley_prisoner.glb --focus haley_prisoner_face --views front,34
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import prisoner as pr  # noqa: E402
from elf import V, Matrix, loft  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("haley_prisoner", height=1.26, head=0.45, leg=1.04, chest=0.50, bust=0.60, hips=1.04, segs=0.74, hand_q=0.6,
            cheek=0.09)
k = e.k
silver = M_("hlpr_silver", "#d7d5e0")

# ---- 얼굴 (haley.py와 같다): 분홍빛 눈, 굵은 붉은 갈색 눈썹, 기본은 여유 있는 표정
e.face(eye_color="#ee5d9a", iris_dark="#a01f5a", iris_light="#ffc2dc", pupil="#4e0d2c",
       lash="#5a1d2a", brow="#8e2a35", brow_th=1.25, blush="#f7a3a8", blush_size=1.05,
       base={"eye": {"top": 0.026, "ktop": 3.4},
             "brow": {"dz": 0.062, "ang": -2.0, "arch": 0.002},
             "mouth": {"w": 0.021, "curve": 0.0035}},
       expr={
           # 자신만만한 미소: 살짝 내리깐 눈, 올라간 입꼬리
           "confident": {"eye": {"top": 0.020, "lift": 0.012, "ktop": 3.8},
                         "brow": {"dz": 0.064, "ang": -5.0, "arch": 0.004},
                         "mouth": {"w": 0.032, "curve": 0.0085, "open": 0.0045, "top_arch": -0.0012}},
           # 브리핑 중 진지함: 눈썹을 모으고 입을 벌려 말하는 중
           "briefing": {"eye": {"top": 0.024, "tilt_in": -0.008, "ktop": 3.6},
                        "brow": {"ang": -12.0, "dz": 0.056, "th": 0.0072, "arch": 0.0},
                        "mouth": {"w": 0.021, "curve": -0.0010, "open": 0.0080, "top_arch": 0.0012}},
           # 경례: 크게 뜬 단호한 눈, 다문 입
           "salute": {"eye": {"top": 0.033, "ktop": 2.8, "tilt_in": -0.004},
                      "brow": {"ang": -8.0, "dz": 0.066, "th": 0.0070},
                      "mouth": {"w": 0.018, "curve": 0.0012}},
       })
c2.face_expr(e, "smirk",
             both={"eye": {"top": 0.021, "lift": 0.008}, "mouth": {"w": 0.030, "curve": 0.0035, "open": 0.0015}},
             L={"brow": {"dz": 0.068, "ang": 2.0, "arch": 0.004}},
             R={"brow": {"dz": 0.058, "ang": -10.0}},
             corner=(0.0095, -0.0015), mouth_dx=0.0025 * k)

# ---- 머리 (haley.py와 같다): 붉은 긴 생머리, 일자 앞머리, 무릎까지 오는 옆·뒷머리
HAIR = "#d4364a"


def blunt(h, lk):
    """일자 앞머리: 끝을 뭉툭하게(p↑), 갈라짐을 짧게."""
    if lk["region"] == "front":
        lk["p"] = 2.6
        lk["free"] *= 0.55


h = c2.hair(e, HAIR, dark="#9c1f33", light="#f58a8f", volume=1.05, lock_fn=c2.lock_edit(blunt))
h.cap(front=28, side=-8, back=-48)
h.bangs(n=7, spread=60, tip_el=-1, jag=0.05, sweep=0, curl=0.8, seed=2.0)
h.sides(length=0.16, width=0.070)
h.back(length=0.52, n=7, spread=100)
h.shine(el=46, spread=70, size=1.1)

# 귀걸이 (haley.py와 같다): 왼쪽 귀 아래 은색 별 (네 갈래)
ear_base, ear_tip = e._ear_axis("L")


def earring(buf):
    w = {"head": 1.0}
    hook = ear_base.lerp(ear_tip, 0.64) + V((0.0, -0.002 * k, -0.012 * k))
    loft(buf, [{"c": hook, "rx": 0.0018 * k, "ry": 0.0018 * k, "w": w},
               {"c": hook + V((0, 0, -0.020 * k)), "rx": 0.0018 * k, "ry": 0.0018 * k, "w": w}], segs=6,
         cap0="round", cap1="round", mat=silver)
    Ms = Matrix.Translation(hook + V((0, 0, -0.040 * k))) @ elf.frame(V((0, -1, 0)), (0, 0, 1))
    c2.prism(buf, c2.star_poly(0.022 * k, 0.007 * k, n=4, rot=90), 0.006 * k,
             Ms @ Matrix.Translation((0, 0.003 * k, 0)), mat=silver, w=w, chamfer=0.002 * k)


e.part("earring", "head", earring)

# ---- 죄수복
P = pr.mats("hlpr")
pr.outfit(e, P, number="0001")

e.finalize()
e.export("characters/haley_prisoner.glb")
