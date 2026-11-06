"""노획 미군 나무 탄약 상자 (올리브 드랍 칠한 판자 상자, 끝 받침목, 양끝 밧줄 손잡이, 뒤 경첩, 앞 걸쇠, 노란 스텐실).

npm run model -- art/blender/props/us_ammo_crate.py
npm run shot -- props/us_ammo_crate.glb --views front,34,side,top
규약: 원점 = 바닥 가운데, 정면 -Y. 몸통 0.76(X) x 0.40(Y) x 0.38(Z) m. 밧줄 손잡이만 양끝(±X)으로 0.05 m 안에서 나온다.
그 밖에는 몸통 상자 밖으로 나오는 것이 없다. 미션이 런타임에 전투 구역의 탄약 보급함으로 세운다
(src/game/missions/ammoCaches.ts). 충돌 상자는 게임 코드가 만든다. 그래서 크기와 원점을 바꾸지 않는다.
앞뒤 스텐실: US GOVT PROPERTY / AMMO / US ARMY (판자 세 장에 한 줄씩). 노획 미군 물자라 엘프 로고는 넣지 않는다.
머티리얼 4개: od(판자·받침목), od_hw(판자 틈·안쪽·쇠붙이), rope(밧줄), stencil_y(노란 글자).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

mk.PAL["od"] = "#4f5a3a"          # 올리브 드랍 칠 (나무)
mk.PAL["od_hw"] = "#33362e"       # 판자 틈, 상자 안쪽, 칠한 쇠 경첩·걸쇠
mk.PAL["rope"] = "#b39a6b"        # 마닐라 밧줄
mk.PAL["stencil_y"] = "#e6c94a"   # 노란 스텐실
mk._DARK.update({"od", "od_hw"})  # 어두운 바탕은 짙은 외곽선

cb.reset()
C = mk.City("us_ammo_crate", prop=True)

LX, LY, H = 0.38, 0.20, 0.38      # 몸통 반폭 X, 반깊이 Y, 높이
CX, CY = 0.36, 0.188              # 판자 면 (받침목이 그 밖으로 LX, LY까지 나온다)
ZS, ZL = 0.296, 0.302             # 몸통 위 / 뚜껑 아래 (그 사이 6 mm 이음매)
ZT = 0.370                        # 뚜껑 판자 윗면 (끝 덧댐목이 그 위로 H까지)
BX = 0.300                        # 앞뒤 세로 받침목 안쪽 X
GAP = 0.003                       # 판자 틈
LIFT = 0.003


def stencil(key, s, size, center, normal, *, up=(0, 0, 1), font="din", bold=0.0, spacing=1.0):
    """평평한 스텐실 글자 (fine 데칼). 글자 외곽 상자의 가운데를 center에 맞춘다(글꼴 기준선이 아니라 실제 글자 모양 기준).
    bold > 0이면 글자 곡선을 그만큼(m) 바깥으로 밀어 획을 굵게 한다. 반환: (너비, 높이) m."""
    cu = bpy.data.curves.new(C.uid("txt") + "_crv", "FONT")
    cu.body = s
    f = hw._font(font)
    if f:
        cu.font = f
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.resolution_u = 2
    cu.space_character = spacing
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


def box(key, x0, x1, y0, y1, z0, z1, kind="main"):
    mk._bm_box(C.bm(key, kind), x0, x1, y0, y1, z0, z1)


def tube(key, pts, r, segs=6, kind="detail"):
    """폴리라인을 따라가는 둥근 관 (밧줄). 끝은 막지 않는다(받침목 구멍 속에 묻힌다)."""
    b = C.bm(key, kind)
    P = [Vector(p) for p in pts]
    rings = []
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(a).normalized()
        v = t.cross(u).normalized()
        rings.append([b.verts.new(p + (u * math.cos(2 * math.pi * k / segs) + v * math.sin(2 * math.pi * k / segs)) * r)
                      for k in range(segs)])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(segs):
            k1 = (k + 1) % segs
            f = b.faces.new((r0[k], r0[k1], r1[k1], r1[k]))
            f.smooth = True
    bmesh.ops.recalc_face_normals(b, faces=[f for f in b.faces])


# ------------------------------------------------------------------ 상자 몸통
# 안쪽 (판자 틈과 이음매로 보이는 어두운 속)
box("od_hw", -CX + 0.004, CX - 0.004, -CY + 0.004, CY - 0.004, 0.004, ZT - 0.004, kind="detail")
# 앞뒤 판자 세 장 (몸통), 뚜껑 옆판 한 장
PLANKS = [(0.0, 0.0985), (0.0985 + GAP, 0.1985), (0.1985 + GAP, ZS)]
for sy in (-1, 1):
    y0, y1 = sorted((sy * CY, sy * (CY - 0.006)))
    for z0, z1 in PLANKS:
        box("od", -CX, CX, y0, y1, z0, z1)
    y0, y1 = sorted((sy * (CY + 0.002), sy * (CY - 0.006)))
    box("od", -CX, CX, y0, y1, ZL, ZT)
# 끝판 (몸통 두 장 + 뚜껑 끝판)
for sx in (-1, 1):
    x0, x1 = sorted((sx * CX, sx * (CX - 0.006)))
    box("od", x0, x1, -CY, CY, 0.0, 0.148)
    box("od", x0, x1, -CY, CY, 0.148 + GAP, ZS)
# 뚜껑 윗판 세 장 (X 방향으로 길게)
W3 = (2 * (CY + 0.002) - 2 * GAP) / 3
for i in range(3):
    y0 = -(CY + 0.002) + i * (W3 + GAP)
    box("od", -CX, CX, y0, y0 + W3, ZT - 0.008, ZT)

# ------------------------------------------------------------------ 받침목 (끝을 감싸는 틀)
for sx in (-1, 1):
    xa, xb = sorted((sx * BX, sx * CX))      # 앞뒤 세로 받침목 X 범위
    xe0, xe1 = sorted((sx * CX, sx * LX))    # 끝면 받침목 두께
    for sy in (-1, 1):
        ya, yb = sorted((sy * CY, sy * LY))
        box("od", xa, xb, ya, yb, 0.0, ZS)                          # 몸통 앞(뒤) 세로 받침목
        ya2, yb2 = sorted((sy * (CY + 0.002), sy * LY))
        box("od", xa, xb, ya2, yb2, ZL, ZT)                         # 뚜껑 쪽 받침목
        ys0, ys1 = sorted((sy * 0.150, sy * LY))
        box("od", xe0, xe1, ys0, ys1, 0.0, ZS)                      # 끝면 세로 기둥
    box("od", xe0, xe1, -0.150, 0.150, 0.180, 0.256)               # 끝면 가로 받침목 (밧줄이 지난다)
    box("od", xe0, xe1, -0.150, 0.150, 0.0, 0.040)                 # 끝면 아래 받침목
    box("od", xe0, xe1, -LY, LY, ZL, ZT)                           # 뚜껑 끝 받침목
    xt0, xt1 = sorted((sx * BX, sx * LX))
    box("od", xt0, xt1, -LY, LY, ZT, H)                            # 뚜껑 위 끝 덧댐목

# ------------------------------------------------------------------ 밧줄 손잡이 (끝면 가로 받침목 구멍 두 개)
RZ, RY, RR = 0.218, 0.078, 0.0075
for sx in (-1, 1):
    pts = []
    n = 10
    for i in range(n + 1):
        th = math.pi * i / n
        out = 0.030 * math.sin(th) ** 0.8
        pts.append((sx * (LX + 0.002 + out), -RY * math.cos(th), RZ - 0.058 * math.sin(th)))
    pts = [(sx * (LX - 0.012), -RY, RZ)] + pts + [(sx * (LX - 0.012), RY, RZ)]
    tube("rope", pts, RR)
    for sy in (-1, 1):   # 구멍 둘레의 밧줄 매듭
        C.blob("rope", (sx * (LX + 0.003), sy * RY, RZ), 0.011, (0.55, 1.0, 1.0), segs=6, rings=4, kind="detail")

# ------------------------------------------------------------------ 쇠붙이: 뒤 경첩 두 개, 앞 걸쇠 두 개
HXS = 0.262
for sx in (-1, 1):
    x = sx * HXS
    # 경첩 (+Y 면): 뚜껑 날개, 몸통 날개, 이음매 위 축
    box("od_hw", x - 0.024, x + 0.024, CY + 0.002, CY + 0.005, ZL + 0.006, ZT - 0.012, kind="detail")
    box("od_hw", x - 0.024, x + 0.024, CY, CY + 0.003, ZS - 0.050, ZS - 0.003, kind="detail")
    C.cyl("od_hw", (x - 0.026, CY + 0.005, (ZS + ZL) / 2), (x + 0.026, CY + 0.005, (ZS + ZL) / 2), 0.0045, segs=8,
          kind="detail")
    # 걸쇠 (-Y 면): 뚜껑 판, 내려오는 고리판, 몸통 고리쇠
    box("od_hw", x - 0.020, x + 0.020, -(CY + 0.005), -(CY + 0.002), ZL + 0.014, ZT - 0.010, kind="detail")
    box("od_hw", x - 0.011, x + 0.011, -(CY + 0.008), -(CY + 0.005), ZS - 0.040, ZL + 0.030, kind="detail")
    box("od_hw", x - 0.016, x + 0.016, -(CY + 0.003), -CY, ZS - 0.034, ZS - 0.016, kind="detail")
    box("od_hw", x - 0.0035, x + 0.0035, -(CY + 0.011), -(CY + 0.003), ZS - 0.032, ZS - 0.018, kind="detail")
    C.cyl("od_hw", (x - 0.012, -(CY + 0.0085), ZS - 0.025), (x + 0.012, -(CY + 0.0085), ZS - 0.025), 0.0025, segs=6,
          kind="detail")   # 고리쇠에 꽂은 핀

# ------------------------------------------------------------------ 스텐실 (앞뒤, 판자 한 장에 한 줄)
LINES = [("US GOVT PROPERTY", 0.072, (PLANKS[2][0] + PLANKS[2][1]) / 2),
         ("AMMO", 0.128, (PLANKS[1][0] + PLANKS[1][1]) / 2),
         ("US ARMY", 0.072, (PLANKS[0][0] + PLANKS[0][1]) / 2)]
for sy in (-1, 1):
    N = (0, sy, 0)
    for s, size, z in LINES:
        w, h = stencil("stencil_y", s, size, (0, sy * CY, z), N, bold=0.0006, spacing=1.05)
        if sy < 0:
            print(f"[crate] {s!r}: {w:.3f} x {h:.3f} m")

C.cols.clear()
C.finish("props/us_ammo_crate.glb", root_props={"outline": 0.006}, detail_outline=0.003)
