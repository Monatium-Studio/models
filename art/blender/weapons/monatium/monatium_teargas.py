"""모나티엄 진압반 MR-G4 '눈물바다' 최루 수류탄 (투척).

[오리지널] 진압반 제식 최루 수류탄. 안전핀을 뽑고 던지면 레버가 튀고 1.5초 뒤 위아래 분사구로 최루 가스를 뿜는다.
[원작] 진압반장 칸나: "최루 가스는 정말 완벽한 제압용 무기죠!" → 섬광탄 대신 최루탄을 골랐다.
       교주 차원 진압반은 주말농장 법칙 때문에 비살상 장비만 쓴다.

형태: 둥근 깡통(교주 차원의 둥근 덩어리), 위아래 분사구 고리 = 원작 엘프 화기의 둥근 구멍 줄,
      청록 비살상 띠, 경고 노랑 '최루' 표기, 신관의 금색 고리, 뒷면(-Y, 1인칭에서 카메라 쪽)의 엘프 로고.

원점 = 몸통 중심(오른손이 감싸 쥐는 점). +Z = 신관, +Y = 던지는 방향, 레버는 +X(오른손 손바닥), 안전핀 고리는 -X(왼손).
움직이는 파츠: lever(경첩 축 Y로 회전해 튀어나감), pin(고리+핀, -X로 뽑힘).

npm run model -- art/blender/weapons/monatium/monatium_teargas.py
npm run shot -- weapons/monatium/monatium_teargas.glb --views side,34,top,muzzle --focus monatium_teargas
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402

cb.reset()
g = hw.Gun("monatium_teargas")

R = 0.0235          # 몸통 반지름
Z0, Z1 = -0.048, 0.036
FZ = 0.054          # 핀 높이

# ================================================================== 몸통 (둥근 깡통)
g.s(hw.zcyl("can", R, Z0, Z1, verts=32, bevel=0.0045, seg=3, mat="violet"))
g.s(hw.zcyl("seam_top", R + 0.0010, Z1 - 0.008, Z1 - 0.0055, verts=32, mat="violet_d"))
g.s(hw.zcyl("seam_bot", R + 0.0010, Z0 + 0.007, Z0 + 0.010, verts=32, mat="violet_d"))
# 청록 비살상 띠 + 노랑 경고 띠
g.s(hw.tube("band_teal", R + 0.0008, R - 0.002, -0.014, 0.004, axis="Z", c=(0, 0), verts=32, mat="teal"))
g.s(hw.tube("band_hazard", R + 0.0006, R - 0.002, 0.010, 0.014, axis="Z", c=(0, 0), verts=32, mat="hazard"))

# 분사구: 위 어깨와 아래 둘레에 둥근 구멍 8개씩 (데칼)
for ring_z, tag in ((Z1 - 0.016, "t"), (Z0 + 0.016, "b")):
    for k, deg in enumerate((0, 40, 140, 180, 220, 320)):   # 앞뒤(±Y) 면은 표기 자리로 비운다
        a = math.radians(deg)
        n = (math.cos(a), math.sin(a), 0)
        rt = (-math.sin(a), math.cos(a), 0)
        g.f(hw.decal(f"port_{tag}{k}", hw.circle(0.0032, 12), (n[0] * (R + 0.0002), n[1] * (R + 0.0002), ring_z),
                     right=rt, up=(0, 0, 1), mat="dark"))
# 바닥 분사구 (아래면)
for k in range(5):
    a = math.radians(90 + 72 * k)
    g.f(hw.decal(f"port_floor{k}", hw.circle(0.0030, 12), (math.cos(a) * 0.012, math.sin(a) * 0.012, Z0),
                 right=(1, 0, 0), up=(0, -1, 0), mat="dark"))
g.f(hw.decal("floor_center", hw.circle(0.0045, 14), (0, 0, Z0), right=(1, 0, 0), up=(0, -1, 0), mat="metal"))

# 표기: 뒷면(-Y) = 1인칭에서 카메라 쪽
BK = dict(right=(1, 0, 0), up=(0, 0, 1))      # -Y 면을 바깥으로
g.f(hw.decal("logo_disc", hw.circle(0.0090, 24), (0, -R - 0.0001, 0.0200), mat="violet_d", **BK))
g.logo((0, -R - 0.0001, 0.0200), 0.0118, mat="gold", **BK)
g.f(hw.text("mk_gas", "최루", 0.0105, (0, -R - 0.0001, -0.026), mat="hazard", **BK))
g.f(hw.text("mk_type", "MR-G4", 0.0048, (0, -R - 0.0001, -0.038), mat="steel", **BK))
# 앞면(+Y): 비살상 표기
g.f(hw.text("mk_less", "비살상", 0.0060, (0, R + 0.0001, -0.026), mat="teal", right=(-1, 0, 0), up=(0, 0, 1)))
g.f(hw.text("mk_lot", "LOT 31", 0.0045, (0, R + 0.0001, -0.037), mat="steel", right=(-1, 0, 0), up=(0, 0, 1)))

# ================================================================== 신관 (금색 고리 + 금속 몸체)
g.s(hw.zcyl("fuze_neck", 0.0118, Z1 - 0.002, Z1 + 0.006, verts=22, bevel=0.0012, mat="metal"))
g.s(hw.zcyl("fuze_ring", 0.0128, Z1 + 0.006, Z1 + 0.010, verts=22, bevel=0.0010, mat="gold"))
g.s(hw.zcyl("fuze_body", 0.0100, Z1 + 0.010, 0.064, verts=20, bevel=0.0014, mat="metal"))
g.s(hw.zcyl("fuze_top", 0.0082, 0.064, 0.0675, verts=20, r2=0.0066, mat="metal"))
for sx in (-1, 1):   # 핀 귀
    g.s(hw.boxr(f"pin_ear{sx}", min(sx * 0.0085, sx * 0.0128), max(sx * 0.0085, sx * 0.0128), -0.0042, 0.0042,
                FZ - 0.0048, FZ + 0.0048, bevel=0.0012, mat="metal"))

# ================================================================== 레버 (+X, 경첩 축 Y)
sp = [(-0.0030, 0.0700), (0.0035, 0.0715), (0.0098, 0.0690), (0.0125, 0.0620), (0.0132, 0.0500),
      (0.0160, Z1 + 0.002)]
for zz in (0.030, 0.020, 0.008, -0.004):
    sp.append((R + 0.0022, zz))
path = [(x, 0.0, z) for (x, z) in sp]
w = [(0.65, 1.0)] + [(1.0, 1.0)] * (len(path) - 3) + [(0.85, 1.0), (0.70, 1.0)]
g.p("lever", hw.sweep("lever_strip", path, [(-0.0068, -0.0011), (0.0068, -0.0011), (0.0068, 0.0011),
                                           (-0.0068, 0.0011)], side_vec=(0, 1, 0), mat="metal", smooth=40, scales=w))
g.pivot("lever", (0.0092, 0.0, 0.0690), rotAxis="z", rotDeg=120, note="flies off around hinge on release")
g.pf("lever", hw.decal("lever_teal", hw.rrect(0.010, 0.018, 0.002, 1), (R + 0.0034, 0, 0.016), mat="teal",
                       **hw.RIGHT))

# ================================================================== 안전핀 + 당김 고리 (-X)
g.p("pin", hw.xcyl("pin_wire", 0.0011, -0.0165, 0.0145, y=0.0, z=FZ, verts=8, mat="steel"),
    hw.torus("pull_ring", 0.0110, 0.0017, loc=(-0.0285, 0.0, FZ - 0.003), rot=(90, 0, 0), seg=22, rseg=6,
             mat="steel"),
    hw.torus("pin_loop", 0.0030, 0.0009, loc=(-0.0168, 0.0, FZ - 0.0005), rot=(90, 0, 0), seg=10, rseg=5,
             mat="steel"))
g.pf("pin", hw.decal("ring_tab", hw.rrect(0.010, 0.006, 0.0025, 2), (-0.0285, 0.0, FZ - 0.0155), mat="teal",
                     right=(1, 0, 0), up=(0, 0, 1), lift=0.0022))
g.pivot("pin", (-0.0165, 0.0, FZ), move=hw.mv(-0.05, 0, 0))

# ================================================================== 앵커
g.anchor("grip_support", (-0.0285, 0.0, FZ - 0.003), parent="pin")   # 왼손이 당기는 고리 중심
g.anchor("throw_release", (0, 0, 0))
g.anchor("fuse", (0, 0, 0.0675))
g.anchor("vent_top", (0, 0, Z1 - 0.016))     # 가스 분사 이펙트 원점 (위 고리)
g.anchor("vent_bottom", (0, 0, Z0))          # 가스 분사 이펙트 원점 (바닥)

g.finish("weapons/monatium/monatium_teargas.glb", outline=0.0016, fp="0.10,-0.10,-0.24", fprot="0,-20,0")
