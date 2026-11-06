"""모나티엄 진압반 고무탄 탄약 상자 (남색 상자 + 노랑·검정 띠 + 흰 엘프 로고 스텐실 「모나티엄 진압반 / 탄약보급함」).

npm run model -- art/blender/props/monatium_ammo_crate.py
npm run shot -- props/monatium_ammo_crate.glb --views front,34,side,top
규약: 원점 = 바닥 가운데, 정면 -Y. 0.70 x 0.44 x 0.42 m. M1 레벨(m1_streets.py)의 ammo_crate와 같은 모양이다.
미션이 런타임에 PICKUP_ weapon=ammo 자리로 세운다 (M1 전선·후퇴로, m1.front.ts). 전투 구역의 탄약 보급함으로도
되풀이해 쓴다 (src/game/missions/ammoCaches.ts). 충돌 상자는 게임 코드가 만든다. 그래서 크기와 원점을 바꾸지 않는다.
앞뒤 띠 아래: 왼쪽 엘프 로고(원작 로고 예외, ART_GUIDE 1장. 교주 차원 제식 장비), 오른쪽 두 줄 표기.
뚜껑 위: 「고무탄」과 MR-7C · 60. 머티리얼 4개(navy_l, hazard, dark, white): 로고는 원판 없이 흰 단색 스텐실이다.
"""
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
C = mk.City("monatium_ammo_crate", prop=True)

HX, HY, H = 0.35, 0.22, 0.42
LIFT = 0.003     # 스텐실을 면에서 띄우는 거리 (fine 데칼은 런타임 깊이 편향으로 몸통 면을 이긴다)
KR_BOLD = 0.0012   # 한글 글꼴(AppleSDGothicNeo 첫 면 = Regular) 획을 바깥으로 1.2 mm 밀어 스텐실답게 굵게


def stencil(key, s, size, center, normal, *, up=(0, 0, 1), font=None, bold=0.0):
    """평평한 스텐실 글자 (fine 데칼). 글자 외곽 상자의 가운데를 center에 맞춘다(글꼴 기준선이 아니라 실제 글자 모양 기준).
    bold > 0이면 글자 곡선을 그만큼(m) 바깥으로 밀어 획을 굵게 한다. 반환: (너비, 높이) m."""
    if font is None:
        font = "kr" if any(ord(ch) > 0x2000 for ch in s) else "din"
    cu = bpy.data.curves.new(C.uid("txt") + "_crv", "FONT")
    cu.body = s
    f = hw._font(font)
    if f:
        cu.font = f
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.resolution_u = 2
    cu.offset = bold
    tmp = bpy.data.objects.new(cu.name + "_tmp", cu)
    cb.link(tmp)
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    R, U, N = mk.frame(normal, up)
    c = Vector(center) + N * LIFT - R * ((min(xs) + max(xs)) / 2) - U * ((min(ys) + max(ys)) / 2)
    o = bpy.data.objects.new("decal_" + me.name, me)
    cb.link(o)
    m4 = Matrix((R, U, N)).transposed().to_4x4()
    m4.translation = c
    o.matrix_world = m4
    C.obj(key, o, kind="fine")
    return max(xs) - min(xs), max(ys) - min(ys)


# 몸통 + 띠 (레벨 상자와 같은 치수)
mk._bm_box(C.bm("navy_l"), -HX, HX, -HY, HY, 0.0, H)
mk._bm_box(C.bm("hazard", "detail"), -HX - 0.01, HX + 0.01, -HY - 0.01, HY + 0.01, 0.30, 0.36)
# 뚜껑 이음매와 바닥 받침
mk._bm_box(C.bm("dark", "detail"), -HX - 0.006, HX + 0.006, -HY - 0.006, HY + 0.006, 0.385, 0.395)
mk._bm_box(C.bm("dark", "detail"), -HX + 0.03, HX - 0.03, -HY + 0.02, HY - 0.02, -0.0, 0.03)
# 양옆 손잡이
for s in (-1, 1):
    x0, x1 = sorted((s * HX, s * (HX + 0.03)))
    mk._bm_box(C.bm("dark", "detail"), x0, x1, -0.09, 0.09, 0.2, 0.245)

# 앞뒤 표기 (띠 아래 z 0.03~0.30): 왼쪽 로고, 오른쪽 두 줄. 면 좌표 (u = 보는 사람 기준 오른쪽, z)
LOGO_U, LOGO_Z, LOGO_H = -0.185, 0.163, 0.170
TXT_U = 0.120
for sy in (-1, 1):
    N = Vector((0, sy, 0))
    R, U, _ = mk.frame(N)
    face = Vector((0, sy * HY, 0))
    # 로고: lift=0이면 logo()가 층 간격 3 mm만 띄운다 (글자와 같은 높이, 서로 겹치지 않음)
    C.logo(tuple(face + R * LOGO_U + Vector((0, 0, LOGO_Z))), LOGO_H, tuple(N), key="white", lift=0.0)
    txt = face + R * TXT_U
    w1, h1 = stencil("white", "모나티엄 진압반", 0.056, tuple(txt + Vector((0, 0, 0.208))), tuple(N), bold=KR_BOLD)
    w2, h2 = stencil("white", "탄약보급함", 0.082, tuple(txt + Vector((0, 0, 0.122))), tuple(N), bold=KR_BOLD)
    if sy < 0:
        print(f"[crate] line1 {w1:.3f} x {h1:.3f}  line2 {w2:.3f} x {h2:.3f}")

# 뚜껑 위: 고무탄 / MR-7C · 60 (앞에서 읽힌다)
stencil("white", "고무탄", 0.075, (0, 0.035, H), (0, 0, 1), up=(0, 1, 0), bold=KR_BOLD)
stencil("white", "MR-7C · 60", 0.05, (0, -0.055, H), (0, 0, 1), up=(0, 1, 0))

C.cols.clear()
C.finish("props/monatium_ammo_crate.glb", root_props={"outline": 0.006})
