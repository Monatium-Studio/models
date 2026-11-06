"""R41 소총병 (r41_rifleman_a/b/c). 침공군의 기본 적, 가장 많이 나온다.

근거: PV 「여왕님의 마음으로 만든 나라」 3:00~3:03 클로즈업, 4:59~5:07 대열 (docs/art/r41-style.md 7.1)
  - 밝은 회색 베레모(오른쪽으로 눌러 씀, 짙은 머리띠), 얼굴을 감싸는 연기색 고글, 짙은 헤드셋 + 붐 마이크
  - 회갈색이 섞인 밝은 회색 전투복, 짙은 어깨 패치에 앰버 원형 휘장, 손가락 없는 짙은 장갑
  - 전투복 재단은 엘피니아 전투복(_kit_elfinia_soldier) 계보: 칼라, 여밈, 견장, 블라우징 바지, 끈 군화
무장: K-7 '쐐기벌'(socket_hand_R), 허리에 G-5 '땅벌' 1개(모델 포함, 장식)
변형: r41_troops.VARIANTS (a 짙은 단발·고글 내림 / b 밝은 갈색 꼬리머리·고글 내림 / c 구릿빛 숏컷·고글을 베레모 위로 올림)

npm run model -- art/blender/enemies/r41_rifleman.py            # a, b, c 모두
npm run model -- art/blender/enemies/r41_rifleman.py -- b       # 하나만
npm run shot -- enemies/r41_rifleman_a.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import r41_troops as T  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
which = [a for a in argv if a in T.VARIANTS] or list(T.VARIANTS)


def build(tag):
    cb.reset()
    v = T.VARIANTS[tag]
    t = T.Trooper(f"r41_rifleman_{tag}", variant=v)
    k = t.k
    t.hair()
    t.uniform(knee=(tag == "b"), thigh_pouch=(tag != "b"))   # b: 무릎 보호대 대신 허벅지 파우치 생략 (예산 15k)
    t.chest_rig(pouches=3, radio=True, grenades=1)
    t.shoulder_insignia()
    # PV 베레모: 밝은 회색 크라운 + 짙은 머리띠, 왼쪽 앞 앰버 원형 휘장(엘프 로고). 고글을 올린 변형은 휘장을 옆으로.
    t.beret(badge="round", badge_az=38 if v["goggles"] == "down" else 64)
    t.goggles(v["goggles"])
    t.headset()
    t.export(f"enemies/r41_rifleman_{tag}.glb", props={"unit": "rifleman", "variant": tag},
             preview={"socket_hand_R": "weapons/r41/r41_carbine.glb", "pose": "rifle"})
    return t


for tag in which:
    build(tag)
