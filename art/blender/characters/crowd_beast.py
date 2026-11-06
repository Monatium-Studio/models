"""대관식 군중: 수인 마을 주민 (crowd_beast_a..f). [오리지널] 무명 군중. 빌더: crowd_common.py.

원작: 수인은 사람 형태에 원형 동물의 귀·뿔·꼬리가 난 모습이고 대부분 포유류(털 수인)다. 촌장 디아나가 첫 헌사를 했다
(「수인(트릭컬 리바이브)」, 「에르핀(왕도)」 문서). 엘프 귀를 지우고 머리 위 동물 귀와 꼬리(본 tail_01..02)를 단다.
옷은 숲속 부족 마을의 축제 차림(흙빛 튜닉, 끈 허리띠, 잎 고리·꽃)이다.

npm run model -- art/blender/characters/crowd_beast.py
CROWD_ONLY=a,c npm run model -- art/blender/characters/crowd_beast.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crowd_common as cc  # noqa: E402

VARIANTS = {
    # 고양이: 주황 단발, 세모 귀, 가늘고 긴 꼬리, 초록 튜닉
    "a": dict(bust=0.25, hair="#e8954e", hair_d="#c06a2e", hair_l="#ffc08a", eye="#6aa84a", style="bob", ear="cat",
              tail="cat", ear_in="#f6b8b0", top="pants", pants_len=0.30, head_acc=None, seed=3.0,
              pal={"top": "#7fae6a", "skirt": "#8a6a4a", "trim": "#e8d8a8", "belt": "#c9a26a", "socks": "#e8d8a8",
                   "shoe": "#6a4a32"}),
    # 개: 갈색 짧은 머리, 늘어진 귀, 말린 꼬리, 크림 튜닉 + 빨간 스카프
    "b": dict(bust=0.0, hair="#9a6a46", hair_d="#6e4a30", hair_l="#c49472", eye="#7a4a2a", style="short", ear="dog",
              tail="dog", ear_col="#6e4a30", top="pants", pants_len=0.80, head_acc=None, seed=5.0,
              pal={"top": "#efe0bc", "skirt": "#6a7a54", "trim": "#c9a26a", "belt": "#7a5a3a", "scarf": "#d8504a",
                   "shoe": "#5a4030"}),
    # 여우: 붉은 주황 긴 머리, 큰 세모 귀(끝 짙음), 굵은 붓 꼬리(끝 흰색), 잎 고리
    "c": dict(bust=0.45, hair="#d8683a", hair_d="#a8461e", hair_l="#f6a070", eye="#e0a83a", style="long", ear="fox",
              tail="fox", tail_tip="#fff6ea", tip_d="#4a2a20", ear_in="#fff0e4", top="dress", hem=0.30,
              head_acc="garland", acc="#f6d36a", acc2="#ffffff", seed=7.0,
              pal={"top": "#f2e2c0", "skirt": "#b8603a", "trim": "#f6d36a", "belt": "#6a4a32", "socks": "#f2e2c0",
                   "shoe": "#6a4a32"}),
    # 토끼: 흰 머리 양 갈래, 긴 귀, 동그란 꼬리, 분홍 원피스 + 꽃관
    "d": dict(bust=0.3, hair="#f6f2ee", hair_d="#d4ccc6", hair_l="#ffffff", eye="#d0546a", style="twin", ear="rabbit",
              tail="rabbit", tail_tip="#ffffff", ear_in="#f6b4c0", top="dress", hem=0.28, head_acc="flower",
              acc="#f6a0b8", acc2="#fff6c8", seed=9.0,
              pal={"top": "#f6c4d0", "skirt": "#f6c4d0", "trim": "#ffffff", "belt": "#e07a90", "socks": "#ffffff",
                   "shoe": "#b46470"}),
    # 곰: 짙은 갈색 단발, 둥근 귀, 동그란 꼬리, 갈색 조끼 + 반바지
    "e": dict(bust=0.35, hair="#6a4634", hair_d="#4a2e22", hair_l="#8e6650", eye="#c9842e", style="bob", ear="bear",
              tail="bear", ear_in="#c9a08a", top="pants", pants_len=0.32, head_acc=None, seed=11.0,
              pal={"top": "#f0e6d0", "skirt": "#5a6a4a", "trim": "#c9a26a", "belt": "#8a5a3a", "vest": "#8a5a3a",
                   "socks": "#f0e6d0", "shoe": "#4a3428"}),
    # 양: 크림 곱슬기 단발, 늘어진 귀 + 말린 뿔, 동그란 꼬리, 하늘색 원피스
    "f": dict(bust=0.4, hair="#f2e6cc", hair_d="#cdbb98", hair_l="#fff8e8", eye="#8a6a9a", style="bob", ear="sheep",
              tail="sheep", tail_tip="#f6eedc", ear_in="#e8c8b8", top="apron", hem=0.30, head_acc=None, volume=1.15,
              seed=13.0,
              pal={"top": "#b8d4ec", "skirt": "#b8d4ec", "trim": "#ffffff", "apron": "#fffaf0", "belt": "#7a90b0",
                   "socks": "#ffffff", "shoe": "#6a5a4a"}),
    # ---- 아이 (키 0.98 m): 회색 고양이 꼬마, 세모 귀·긴 꼬리, 민트 원피스 + 리본
    "g": dict(height=0.98, head=0.42, limb=1.08, cheek=0.16, hair="#9a96a6", hair_d="#6e6a7a", hair_l="#c4c0ce",
              eye="#e0a83a", style="bob", ear="cat", tail="cat", ear_in="#f6b8c0", top="dress", hem=0.26,
              head_acc="ribbon", acc="#f06a8a", seed=18.0, eye_size=1.08,
              pal={"top": "#a8e0cc", "skirt": "#a8e0cc", "trim": "#ffffff", "belt": "#f06a8a", "socks": "#ffffff",
                   "shoe": "#6a5a7a"}),
}

only = os.environ.get("CROWD_ONLY")
for key, v in VARIANTS.items():
    if only and key not in only.split(","):
        continue
    cc.build(f"crowd_beast_{key}", "beast", v)
