"""대관식 군중: 요정 왕국 주민 (crowd_fairy_a..f). [오리지널] 무명 군중. 빌더: crowd_common.py.

원작: 3차 대관식 광장에 왕국의 요정들이 발 디딜 틈 없이 모여 만세를 외쳤다. 요정 종족 표식(작은 깃털 날개, 둥근 귀)과
요정 경비대 모델의 색감(흰·크림 날개, 금 장식)을 따르고, 옷은 축제 차림(파스텔 원피스, 앞치마, 꽃관, 리본)이다.

npm run model -- art/blender/characters/crowd_fairy.py          # 여섯 변형을 모두 내보낸다
CROWD_ONLY=a npm run model -- art/blender/characters/crowd_fairy.py   # 한 변형만
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crowd_common as cc  # noqa: E402

VARIANTS = {
    # 꿀빛 금발 단발 + 분홍 원피스 + 흰 앞치마 + 꽃관
    "a": dict(bust=0.35, hair="#f0d08e", hair_d="#c9a15e", hair_l="#fff1cc", eye="#5fae8a", style="bob", top="apron",
              head_acc="flower", acc="#f58aa8", acc2="#fff6d0", seed=2.0,
              pal={"top": "#f6b8c8", "skirt": "#f6b8c8", "trim": "#ffffff", "apron": "#ffffff", "belt": "#e0708c",
                   "socks": "#ffffff", "shoe": "#b4645e"}),
    # 연보라 긴 머리 + 민트 원피스 + 흰 리본
    "b": dict(bust=0.45, hair="#c9b2e6", hair_d="#9a82bd", hair_l="#ece2fb", eye="#d06a8e", style="long", top="dress",
              head_acc="ribbon", acc="#ffffff", acc_az=-40.0, seed=5.0, ears=None,
              pal={"top": "#a8dcc8", "skirt": "#a8dcc8", "trim": "#f6f2e8", "belt": "#5fae8a", "socks": "#ffffff",
                   "shoe": "#6a5a7a"}),
    # 갈색 양 갈래 + 레몬 원피스 + 잎 고리
    "c": dict(bust=0.0, hair="#8a5a44", hair_d="#62402f", hair_l="#b07e62", eye="#4f8ad0", style="twin", top="dress",
              head_acc="garland", acc="#ffffff", acc2="#f6d36a", seed=7.0,
              pal={"top": "#f6e08a", "skirt": "#f6e08a", "trim": "#ffffff", "belt": "#e0a640", "socks": "#ffffff",
                   "shoe": "#8a5a44"}),
    # 흰 머리 경단 + 라벤더 상의 + 짙은 반바지 (활동적인 주민)
    "d": dict(bust=0.2, hair="#f2eef6", hair_d="#c6bfd2", hair_l="#ffffff", eye="#e0884a", style="buns", top="pants",
              pants_len=0.30, head_acc="ribbon", acc="#f06a8a", seed=9.0, legs="socks",
              pal={"top": "#c8b4ea", "skirt": "#5a4f72", "trim": "#ffffff", "belt": "#f06a8a", "socks": "#ffffff",
                   "shoe": "#4a4058", "vest": "#ffffff"}),
    # 분홍 포니테일 + 하늘색 원피스 + 노란 스카프
    "e": dict(bust=0.3, hair="#f2a2b8", hair_d="#d27890", hair_l="#ffd4e0", eye="#5a9ad0", style="pony", top="dress",
              head_acc=None, acc="#f6d36a", seed=11.0,
              pal={"top": "#a6cdf0", "skirt": "#a6cdf0", "trim": "#ffffff", "belt": "#ffffff", "scarf": "#f6d36a",
                   "socks": "#ffffff", "shoe": "#5a6a8a"}),
    # 민트 단발 + 흰 블라우스 + 초록 치마 + 앞치마 (빵집 요정)
    "f": dict(bust=0.4, hair="#9ed8c4", hair_d="#6aa894", hair_l="#d4f4ea", eye="#c06a50", style="bob", top="apron",
              head_acc="cap", acc="#ffffff", acc2="#f2c26a", seed=13.0,
              pal={"top": "#ffffff", "skirt": "#6aa874", "trim": "#e8e2d4", "apron": "#fff4dc", "belt": "#c97a4a",
                   "socks": "#ffffff", "shoe": "#7a5a44"}),
    # ---- 아이 (키 0.98 m, 머리 비율이 크다, bust 0)
    # 귤빛 단발 꼬마 + 하늘색 셔츠 + 멜빵 반바지 느낌의 조끼 + 챙모자
    "g": dict(height=0.98, head=0.42, limb=1.08, cheek=0.16, hair="#f0a868", hair_d="#c8794a", hair_l="#ffd2a4",
              eye="#4f8ad0", style="short", top="pants", pants_len=0.30, head_acc="cap", acc="#f6d36a", acc2="#e0a640",
              seed=15.0, eye_size=1.08,
              pal={"top": "#bfe0f6", "skirt": "#4f6a96", "trim": "#ffffff", "belt": "#4f6a96", "vest": "#4f6a96",
                   "socks": "#ffffff", "shoe": "#c0503a"}),
    # 벚꽃색 긴 머리 꼬마 + 흰 원피스 + 꽃관
    "h": dict(height=0.98, head=0.42, limb=1.08, cheek=0.16, hair="#f6c4d2", hair_d="#d896aa", hair_l="#ffe4ec",
              eye="#7a6ad0", style="long", top="dress", hem=0.26, head_acc="flower", acc="#f6d36a", acc2="#ffffff",
              seed=17.0, eye_size=1.08,
              pal={"top": "#fffaf4", "skirt": "#fffaf4", "trim": "#f6a0b8", "belt": "#f6a0b8", "socks": "#ffffff",
                   "shoe": "#d07890"}),
}

only = os.environ.get("CROWD_ONLY")
for key, v in VARIANTS.items():
    if only and key not in only.split(","):
        continue
    cc.build(f"crowd_fairy_{key}", "fairy", v)
