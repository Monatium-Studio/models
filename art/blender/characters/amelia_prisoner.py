"""아멜리아 (인터루드 포로 생활 ~ 엘리아스 불시착): 주황 죄수복 차림.

사용자 확정(docs/scenario.md 인터루드 2번): 포로 생활부터 탈출 직후까지 엘프들은 미국 교도소식 주황 죄수복을 입는다.
- 체격·눈·머리색·머리 모양은 amelia_common.py(secretary_hair)로 amelia.py와 같이 쓰고, 표정은 amelia.py와 같다.
  옅은 분홍빛 베이지 머리, 가운데 가르마 커튼 앞머리, 가슴까지 오는 옆머리(끝이 분홍빛 갈색), 머리를 두르는 크라운
  브레이드와 뒤통수 경단, 왼쪽 위 하늘색 초승달 머리핀, 연두빛 초록 눈의 반쯤 감은 무표정이 그대로다.
  표정: 키트 5종 + annoyed, tired(수용소), glare, smug.
- 정장 재킷·태블릿·이어피스는 없다. 수용 번호 0112 (엘레나 0109 근처: 시장 비서의 원형).
- 복장: 공용 죄수복 모듈(art/blender/lib/prisoner.py).

npm run model -- art/blender/characters/amelia_prisoner.py
npm run shot -- characters/amelia_prisoner.glb
npm run shot -- characters/amelia_prisoner.glb --focus amelia_prisoner_face --views front,34
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import amelia_common as am  # noqa: E402
import prisoner as pr  # noqa: E402

cb.reset()
M_ = elf.mat
e = am.body("amelia_prisoner")
k = e.k

# ---- 얼굴 (amelia.py와 같다)
am.face(e, expr={
    # 짜증: 눈을 더 가늘게, 눈썹 안쪽 내림, 입은 ∩
    "annoyed": {"eye": {"top": 0.013, "ktop": 4.6, "tilt_in": -0.006},
                "brow": {"ang": -14.0, "dz": 0.054, "th": 0.0062},
                "mouth": {"w": 0.019, "curve": -0.0032}},
    # 지친 눈 (수용소): 처진 눈꼬리와 눈썹, 시무룩한 입
    "tired": {"eye": {"top": 0.011, "tilt_out": -0.007, "ktop": 3.4, "lift": 0.004},
              "brow": {"ang": 14.0, "dz": 0.058},
              "mouth": {"w": 0.016, "curve": -0.0016, "open": 0.0015}},
    # 째려봄: 눈을 조금 뜨고 동공이 작아진다, 입은 꾹
    "glare": {"eye": {"top": 0.021, "ktop": 3.8, "tilt_in": -0.010, "bot": 0.050},
              "iris": {"pupil": 0.70},
              "brow": {"ang": -20.0, "dz": 0.052, "th": 0.0066},
              "mouth": {"w": 0.014, "curve": -0.0010}},
})
c2.face_expr(e, "smug",
             both={"eye": {"top": 0.015, "lift": 0.010}, "mouth": {"w": 0.024, "curve": 0.0030}},
             L={"brow": {"dz": 0.064, "ang": 4.0}}, R={"brow": {"dz": 0.058, "ang": -4.0}},
             corner=(0.0075, -0.0005), mouth_dx=0.0020 * k)


# ---- 머리 (amelia_common.secretary_hair: amelia.py, amelia_prisoner.py 공용): 가운데 가르마 커튼 앞머리 + 가슴까지
# 오는 넓은 옆머리 + 크라운 브레이드 + 경단(뒷머리는 올림) + 하늘색 초승달 핀
h = am.secretary_hair(e, "ampr_braid")

# ---- 죄수복
P = pr.mats("ampr")
pr.outfit(e, P, number="0112")

am.done_hair(e, q=0.82)   # 죄수복 스텐실·먹선 몫만큼 머리 분할을 조금 낮춰 18k 안
e.finalize()
am.tip_gradient(e, 0.21)
e.export("characters/amelia_prisoner.glb")
