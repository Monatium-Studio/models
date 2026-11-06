"""사격장 근접 훈련용 접이식 야전 탁자 + 도마 + 여분 수박 상자 (프롤로그 함내 사격장).

npm run model -- art/blender/props/range_fruit_table.py
npm run shot -- props/range_fruit_table.glb --views front,34,side,top

누가 주방에서 사격 부스로 끌고 온 접이식 탁자. 칼 베기 튜토리얼에서 도마 위에 수박(range_watermelon.glb)을 올린다.
원점 = 탁자 아래 바닥 중심(z=0), 정면(플레이어 쪽) = -Y.
  상판 0.80 x 0.45, 윗면 z=0.52 (남색 판 + 은색 테 + 금색 모서리 덧쇠). 접이식 다리 4개, 양끝 X자 버팀대, 고무발
  도마 0.40 x 0.30 x 0.025, 윗면 z=0.545, 가장자리 안쪽에 즙 받이 홈
  fruit_spot (빈 오브젝트, markers 아래) = 도마 윗면 중심 (0, 0, 0.545). 런타임이 수박 바닥을 여기 놓는다
  탁자 밑 바닥: 여분 수박 두 통이 든 나무 상자 (탁자 발자국 안이라 충돌 상자를 늘리지 않는다)
메시는 collider=0. 충돌은 런타임이 상자 하나로 맡는다.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import level_kit as lk  # noqa: E402

cb.reset()
# 이 소품에만 쓰는 색 (정점색으로 합쳐져 머티리얼이 늘지 않는다)
lk.PAL.update({
    "wood": "#c9a06a",      # 도마
    "wood_d": "#9a6f3e",    # 도마 즙 받이 홈
    "wood_c": "#b5875a",    # 과일 상자 널
    "wood_cd": "#8e6440",   # 상자 기둥·바닥
})

L = lk.Level("range_fruit_table")
L.zone("p")
F, UP = (0, -1, 0), (0, 0, 1)
HUP = dict(up=(0, 1, 0))   # 가로 면(법선 +Z)의 2D 위쪽 = +Y

W, D = 0.80, 0.45
TOP = 0.52
LX, LY = 0.325, 0.15          # 다리 중심
LEG_R = 0.0135


def rivet(p, n, r=0.0048, h=0.0028, key="steel", kind="detail"):
    """작은 리벳·나사 머리 (면에 1 mm 묻힘)."""
    P, N = Vector(p), Vector(n).normalized()
    L.cyl(key, P - N * 0.001, P + N * (h - 0.001), r, verts=6, kind=kind)


# ------------------------------------------------------------------ 상판
# 남색 판 (은색 테 안쪽으로 4 mm 묻힘), 테는 윗면보다 3 mm 솟은 둥근 사각 고리
L.extrude("navy", hw.rrect(0.776, 0.426, 0.022), (0, 0, TOP - 0.024), UP, 0.024, **HUP)
L.ring_extrude("steel", hw.rrect(W, D, 0.03), hw.rrect(W - 0.032, D - 0.032, 0.014), (0, 0, TOP - 0.028), UP, 0.031,
               **HUP)
# 금색 모서리 덧쇠 + 나사
for sx in (-1, 1):
    for sy in (-1, 1):
        cx, cy = sx * (W / 2 - 0.022), sy * (D / 2 - 0.022)
        L.bev("gold", (0.052, 0.052, 0.037), (cx + sx * 0.0015, cy + sy * 0.0015, TOP - 0.0115), bevel=0.009,
              kind="detail")
        rivet((cx - sx * 0.002, cy - sy * 0.002, TOP + 0.0068), UP, r=0.0052)
# 앞치마(테 아래 둘레 틀): 앞면에 로고와 꼬리표
AP_W, AP_D, AP_Z0, AP_Z1 = 0.72, 0.37, 0.438, TOP - 0.022
L.ring_extrude("metal", hw.rrect(AP_W, AP_D, 0.012, n=1), hw.rrect(AP_W - 0.02, AP_D - 0.02, 0.006, n=1),
               (0, 0, AP_Z0), UP, AP_Z1 - AP_Z0, **HUP)
AY = -AP_D / 2           # 앞치마 앞면 y
AZ = (AP_Z0 + AP_Z1) / 2
L.logo((0.0, AY, AZ), 0.036, F, disc="navy", ring="gold", lift=0.0015)
for x in (-0.33, 0.33):
    rivet((x, AY, AZ), F)
# 종이 꼬리표: 앞치마에 핀 두 개로 꽂힌 얇은 판 (살짝 기울어짐)
TAG_C, TAG_ROT = Vector((-0.20, AY - 0.0025, AZ - 0.002)), 4.0
L.rbox("paper", tuple(TAG_C), (0.112, 0.003, 0.036), rot=(0, TAG_ROT, 0), kind="detail")
a = math.radians(TAG_ROT)
tag_r, tag_u = Vector((math.cos(a), 0, -math.sin(a))), Vector((math.sin(a), 0, math.cos(a)))
tag_face = TAG_C + Vector((0, -0.0015, 0))
L.text("navy_d", "주방 물품 · 반납할 것", 0.0088, tuple(tag_face - tag_u * 0.004), F, up=tuple(tag_u), lift=0.0012)
L.strip("red", tuple(tag_face + tag_u * 0.0115 - tag_r * 0.039), tuple(tag_face + tag_u * 0.0115 + tag_r * 0.039),
        0.0028, F, lift=0.0012)
for s in (-1, 1):
    rivet(tuple(tag_face + tag_r * s * 0.047 + tag_u * 0.011), F, r=0.0036, h=0.0024, key="gold", kind="fine")

# ------------------------------------------------------------------ 다리 (접이식)
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = sx * LX, sy * LY
        # 다리 머리 경첩 블록 (상판 밑에 2 mm 묻힘)
        L.bev("metal", (0.046, 0.046, 0.05), (x, y, TOP - 0.024 + 0.002 - 0.025), bevel=0.008)
        L.cyl("metal", (x, y, 0.026), (x, y, TOP - 0.06), LEG_R, verts=8)
        L.cyl("rubber", (x, y, 0.0), (x, y, 0.034), 0.0195, r2=0.0165, verts=8, kind="detail")
        # 경첩 핀 (블록 옆면을 X로 관통)
        L.cyl("steel", (x - 0.028, y, TOP - 0.05), (x + 0.028, y, TOP - 0.05), 0.0055, verts=6, kind="detail")
# 양끝 X자 버팀대 (다리 안쪽 면에 붙은 납작한 띠 두 장, 가운데 피벗 리벳)
BT = 0.006
for sx in (-1, 1):
    xs = (sx * (LX - LEG_R - BT / 2), sx * (LX - LEG_R - BT * 1.5))
    for k, (y0, y1) in enumerate(((-LY, LY), (LY, -LY))):
        z0, z1 = 0.10, 0.405
        dy, dz = y1 - y0, z1 - z0
        ln = math.hypot(dy, dz)
        ang = math.degrees(math.atan2(dz, dy))
        L.rbox("metal", (xs[k], (y0 + y1) / 2, (z0 + z1) / 2), (BT, ln + 0.012, 0.02), rot=(ang, 0, 0), kind="detail")
        for (yy, zz) in ((y0, z0), (y1, z1)):
            yy2 = yy - math.copysign(0.004, yy)
            if k == 1:   # 안쪽 띠는 다리에서 6 mm 떨어져 있어 받침 쇠로 잇는다
                xa, xb = sorted((sx * (LX - LEG_R + 0.001), sx * (LX - LEG_R - BT * 2 - 0.001)))
                L.box("metal", xa, xb, yy2 - 0.01, yy2 + 0.01, zz - 0.012, zz + 0.012, kind="detail")
    L.cyl("steel", (sx * (LX - LEG_R - BT * 2 - 0.004), 0, 0.2525), (sx * (LX - LEG_R + 0.004), 0, 0.2525), 0.0062,
          verts=8, kind="detail")
# 뒤쪽 가로대 (앞은 비워 상자가 보이게)
L.cyl("metal", (-LX, LY, 0.30), (LX, LY, 0.30), 0.009, verts=8)

# ------------------------------------------------------------------ 도마
BW, BD, BH = 0.40, 0.30, 0.025
B0, B1 = TOP, TOP + BH
G_IN, G_W, G_DEPTH = 0.016, 0.009, 0.0032    # 홈: 가장자리에서 16 mm 안, 폭 9 mm, 깊이 3.2 mm
L.ring_extrude("wood", hw.rrect(BW, BD, 0.026), hw.rrect(BW - 2 * G_IN, BD - 2 * G_IN, 0.012), (0, 0, B0), UP, BH,
               **HUP)
L.ring_extrude("wood_d", hw.rrect(BW - 2 * G_IN, BD - 2 * G_IN, 0.012),
               hw.rrect(BW - 2 * (G_IN + G_W), BD - 2 * (G_IN + G_W), 0.006), (0, 0, B0 + 0.006), UP,
               BH - 0.006 - G_DEPTH, **HUP)
L.extrude("wood", hw.rrect(BW - 2 * (G_IN + G_W), BD - 2 * (G_IN + G_W), 0.006), (0, 0, B0), UP, BH, **HUP)
# 칼자국 몇 줄 (아주 얇은 데칼)
for (x0, y0, x1, y1) in ((-0.10, -0.05, -0.02, -0.07), (0.04, 0.06, 0.12, 0.03), (0.07, -0.08, 0.13, -0.05)):
    L.strip("wood_d", (x0, y0, B1), (x1, y1, B1), 0.0018, UP, lift=0.0006)
L.marker("fruit_spot", (0.0, 0.0, B1), props={"boardTop": round(B1, 4)})

# ------------------------------------------------------------------ 여분 수박 상자 (탁자 밑 바닥)
CW, CD, CH = 0.56, 0.30, 0.14
T = 0.012
cx0, cx1, cy0, cy1 = -CW / 2, CW / 2, -CD / 2, CD / 2
for y in (-0.105, 0.105):   # 받침목
    L.box("wood_cd", cx0 + 0.01, cx1 - 0.01, y - 0.015, y + 0.015, 0.0, 0.013)
L.box("wood_cd", cx0, cx1, cy0, cy1, 0.012, 0.024)          # 바닥판
for sx in (-1, 1):                                           # 모서리 기둥
    for sy in (-1, 1):
        x, y = sx * (CW / 2 - T - 0.0125), sy * (CD / 2 - T - 0.0125)
        L.box("wood_cd", x - 0.0125, x + 0.0125, y - 0.0125, y + 0.0125, 0.024, CH)
for (z0, z1) in ((0.030, 0.074), (0.090, CH)):               # 널 두 단 (사이로 수박이 보인다)
    L.box("wood_c", cx0, cx1, cy0, cy0 + T, z0, z1)
    L.box("wood_c", cx0, cx1, cy1 - T, cy1, z0, z1)
    L.box("wood_c", cx0, cx0 + T, cy0 + T, cy1 - T, z0, z1)
    L.box("wood_c", cx1 - T, cx1, cy0 + T, cy1 - T, z0, z1)
for x in (-0.24, 0.24):                                      # 앞 널 못
    for z in (0.052, 0.115):
        rivet((x, cy0, z), F, r=0.0032, h=0.002, key="metal")
L.text("navy_d", "수박", 0.026, (0.0, cy0, (0.090 + CH) / 2), F, lift=0.0012)

# 여분 수박 두 통: 줄무늬 타원체 (range_watermelon.py와 같은 색, 낮은 분할). 정점색 + 해석적 노멀
MELON = {"rind": "#7bcb4e", "stripe": "#2e7031", "stem": "#6f6a2e"}
MK = list(MELON)


def melon_obj(name, a, c, loc, rot, seed, stripes=7, bands=9):
    rng = random.Random(seed)
    P = 2 * math.pi / stripes
    ph = [rng.uniform(0, 2 * math.pi) for _ in range(stripes)]
    dph = [rng.uniform(0.6, 1.4) for _ in range(stripes)]

    def edge(s, th, j, right):
        p = ph[s] + (dph[s] if right else 0.0)
        w = 0.10 * P * math.sin(3.0 * th + p)
        zig = 0.07 * P * (1 if (j + s + right) % 2 else -1) * math.sin(th)
        return s * P + (0.40 * P if right else 0.0) + w + zig

    bm = bmesh.new()
    top, bot = bm.verts.new((0, 0, c)), bm.verts.new((0, 0, -c))
    rings = []
    for j in range(1, bands):
        th = math.pi * j / bands
        az = []
        for s in range(stripes):
            e1 = edge(s, th, j, 1)
            n0 = edge((s + 1) % stripes, th, j, 0) + (2 * math.pi if s + 1 == stripes else 0.0)
            az += [edge(s, th, j, 0), e1, (e1 + n0) / 2]
        rings.append([bm.verts.new((a * math.sin(th) * math.cos(f), a * math.sin(th) * math.sin(f),
                                    c * math.cos(th))) for f in az])
    n = stripes * 3
    for i in range(n):
        i2 = (i + 1) % n
        fs = [bm.faces.new((top, rings[0][i], rings[0][i2]))]
        fs += [bm.faces.new((rings[j][i], rings[j + 1][i], rings[j + 1][i2], rings[j][i2])) for j in range(bands - 2)]
        fs.append(bm.faces.new((rings[-1][i], bot, rings[-1][i2])))
        for f in fs:
            f.material_index = 1 if i % 3 == 0 else 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # 꼭지
    sf = []
    rows = []
    for (z, r, dx) in ((c - 0.004, 0.0065, 0.0), (c + 0.008, 0.005, 0.002), (c + 0.015, 0.0042, 0.008)):
        rows.append([bm.verts.new((dx + r * math.cos(2 * math.pi * i / 5), r * math.sin(2 * math.pi * i / 5), z))
                     for i in range(5)])
    for k in range(2):
        for i in range(5):
            sf.append(bm.faces.new((rows[k][i], rows[k][(i + 1) % 5], rows[k + 1][(i + 1) % 5], rows[k + 1][i])))
    sf.append(bm.faces.new(rows[-1]))
    for f in sf:
        f.material_index = 2
    bmesh.ops.recalc_face_normals(bm, faces=sf)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    keys = [p.material_index for p in me.polygons]
    for p in me.polygons:
        p.material_index = 0
        p.use_smooth = True
    col = me.color_attributes.new(name="Col", type="BYTE_COLOR", domain="CORNER")
    for p in me.polygons:
        h = MELON[MK[keys[p.index]]].lstrip("#")
        cc = (*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)), 1.0)
        for li in p.loop_indices:
            col.data[li].color_srgb = cc
    me.update()
    base = [Vector(nv.vector) for nv in me.corner_normals]
    nl = []
    for p in me.polygons:
        for li in p.loop_indices:
            if keys[p.index] == 2:
                nl.append(base[li])
            else:
                v = me.vertices[me.loops[li].vertex_index].co
                nl.append(Vector((v.x / a ** 2, v.y / a ** 2, v.z / c ** 2)).normalized())
    me.normals_split_custom_set([tuple(v) for v in nl])
    o = bpy.data.objects.new(name, me)
    cb.link(o)
    cb.assign(o, lk.vc_material())
    o.rotation_euler = [math.radians(v) for v in rot]
    bpy.context.view_layer.update()
    # 상자 바닥(z=0.024)에 1 mm 묻히게 높이를 맞춘다
    R = o.rotation_euler.to_matrix()
    zmin = min((R @ v.co).z for v in me.vertices)
    o.location = (loc[0], loc[1], 0.024 - 0.001 - zmin)
    o["collider"] = 0
    L.specials.append((L.zname, o))
    return o


MA, MC = 0.1196, 0.108      # 0.92배 수박
melon_obj("range_fruit_table_melon_a", MA, MC, (0.128, 0.004, 0), (0, 0, 20), seed=11)
melon_obj("range_fruit_table_melon_b", MA, MC, (-0.127, -0.006, 0), (0, -78, -15), seed=23)

st = L.finish("props/range_fruit_table.glb", root_props={"outline": 0.0045}, outline=0.0045, detail_outline=0.003,
              prop=True)
