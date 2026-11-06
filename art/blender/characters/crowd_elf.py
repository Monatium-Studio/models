"""대관식 군중: 모나티엄 엘프 시민 (crowd_elf_a..f). [오리지널] 무명 군중. 빌더: crowd_common.py.

원작: 모나티엄 시장 엘레나가 두 번째 헌사를 했다(「에르핀(왕도)」 문서). 군중 속 엘프는 키트의 뾰족한 귀(날개 없음)와
모나티엄 도시민의 축제 나들이옷(셔츠·조끼·베레모·스카프·작업복)으로 요정·수인과 구분한다.

npm run model -- art/blender/characters/crowd_elf.py
CROWD_ONLY=a npm run model -- art/blender/characters/crowd_elf.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crowd_common as cc  # noqa: E402

VARIANTS = {
    # 사무직: 갈색 단발, 흰 셔츠 + 남색 조끼 + 회색 치마, 붉은 스카프
    "a": dict(hair="#7a5140", hair_d="#56382c", hair_l="#a0745e", eye="#5a7fb5", style="bob", top="dress", hem=0.32,
              collar="stand", bust=0.30, head_acc=None, seed=4.0,
              pal={"top": "#f6f4f0", "sleeve": "#f6f4f0", "skirt": "#7c7f8a", "trim": "#4a4e66", "vest": "#3e4466",
                   "belt": "#2e3246", "scarf": "#d0485a", "socks": "#4a4e66", "shoe": "#3a3236"}),
    # 나들이: 하늘색 긴 머리, 분홍 블라우스 + 청바지, 베레모
    "b": dict(hair="#a8cde8", hair_d="#78a0c4", hair_l="#d8ecfa", eye="#c0607a", style="long", top="pants",
              pants_len=0.88, sleeve_len=0.85, bust=0.45, head_acc="beret", acc="#c84a5e", acc2="#c84a5e",
              seed=6.0, legs=None,
              pal={"top": "#f6c6d2", "sleeve": "#f6c6d2", "skirt": "#4f6a96", "trim": "#ffffff", "belt": "#5a4030",
                   "shoe": "#f2efe8"}),
    # 정비공: 금발 포니테일, 주황 상의 + 데님 작업 바지 + 챙모자
    "c": dict(hair="#e8c27a", hair_d="#c09a52", hair_l="#fbe6b4", eye="#4f8a6a", style="pony", top="pants",
              pants_len=0.88, sleeve_len=0.40, bust=0.20, head_acc="cap", acc="#3e5a8a", acc2="#2e4470",
              seed=8.0, legs=None,
              pal={"top": "#f0904a", "sleeve": "#f0904a", "skirt": "#4a6a9a", "trim": "#2e4470", "belt": "#2e2a30",
                   "vest": "#4a6a9a", "shoe": "#4a3a30"}),
    # 외출복: 검은 긴 머리, 짙은 녹색 코트형 상의 + 체크 느낌 갈색 치마, 붉은 스카프
    "d": dict(hair="#2e2a32", hair_d="#1c1a20", hair_l="#4e4856", eye="#d08a3a", style="long", top="dress", hem=0.30,
              sleeve_len=0.92, bust=0.40, collar="stand", head_acc="ribbon", acc="#d0485a", seed=10.0,
              pal={"top": "#3e6a52", "sleeve": "#3e6a52", "skirt": "#8a5a42", "trim": "#e8d8b0", "belt": "#e8d8b0",
                   "scarf": "#d0485a", "socks": "#3a3236", "shoe": "#2e2a30"}),
    # 가게 점원: 은회색 짧은 머리, 노란 셔츠 + 흰 앞치마 + 갈색 치마
    "e": dict(hair="#c8c4cc", hair_d="#9a96a2", hair_l="#eae6ee", eye="#6a8ad0", style="short", top="apron", hem=0.32,
              bust=0.0, head_acc=None, seed=12.0,
              pal={"top": "#f6e08a", "sleeve": "#f6e08a", "skirt": "#7a5a44", "trim": "#ffffff", "apron": "#ffffff",
                   "belt": "#7a5a44", "socks": "#ffffff", "shoe": "#5a4436"}),
    # 학생: 분홍 양 갈래, 흰 세일러풍 상의(남색 깃) + 남색 치마
    "f": dict(hair="#f0a0b4", hair_d="#c87890", hair_l="#ffd2de", eye="#6aa86a", style="twin", top="dress", hem=0.30,
              collar="stand", bust=0.15, head_acc=None, seed=14.0,
              pal={"top": "#ffffff", "sleeve": "#ffffff", "skirt": "#3e4a7a", "trim": "#3e4a7a", "belt": "#3e4a7a",
                   "scarf": "#e05a6a", "socks": "#ffffff", "shoe": "#3a3236"}),
    # ---- 아이 (키 0.98 m): 밤색 포니테일 꼬마, 노란 셔츠 + 남색 반바지 + 베레모 (부모 따라 온 모나티엄 아이)
    "g": dict(height=0.98, head=0.42, limb=1.08, cheek=0.16, hair="#8a5a40", hair_d="#62402e", hair_l="#b0805e",
              eye="#5a9a6a", style="pony", top="pants", pants_len=0.30, head_acc="beret", acc="#d0485a",
              acc2="#d0485a", seed=16.0, eye_size=1.08,
              pal={"top": "#f6dc7a", "sleeve": "#f6dc7a", "skirt": "#3e4a7a", "trim": "#ffffff", "belt": "#3e4a7a",
                   "socks": "#ffffff", "shoe": "#5a4436"}),
}

only = os.environ.get("CROWD_ONLY")
for key, v in VARIANTS.items():
    if only and key not in only.split(","):
        continue
    cc.build(f"crowd_elf_{key}", "elf", v)
