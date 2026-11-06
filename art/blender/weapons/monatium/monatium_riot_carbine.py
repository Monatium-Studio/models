"""모나티엄 진압반 MR-7C '자장가' 고무탄 카빈 (1막 초반 기본 무장).

[오리지널] 엘피니아 7식 소총을 진압반이 줄여 고친 제식 카빈. 고무탄 전용 굵은 총열, 15발 직탄창, 단발·연발.
광점 조준기와 운반 손잡이를 떼고 값싼 고리 가늠자를 달았다. 잔탄 표시창은 모나티엄 네트워크(HUD)와 연동된다.
[원작] 교주 차원 모나티엄 진압반은 주말농장 법칙 때문에 고무탄과 고전압 전기충격기를 쓴다. R41 병사들이 이를 보고 당황한다.

7식과 공유하는 형태(계보): 불펍 몸통과 개머리 실루엣, 손을 감싸는 D자 고리, 개머리 구멍 줄, 금색 총구 고리, 시안 표시창.
진압반 표지: 남보라 외장, 청록 비살상 띠(총구·탄창), 탄창 창으로 보이는 청록 고무탄, 앞 손잡이와 손전등.

npm run model -- art/blender/weapons/monatium/monatium_riot_carbine.py
npm run shot -- weapons/monatium/monatium_riot_carbine.glb --views side,34,top,muzzle --focus monatium_riot_carbine
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402

cb.reset()
g = hw.Gun("monatium_riot_carbine")

BZ = 0.070          # 총열 축 (7식과 같음)
SZ = 0.1225         # 조준선 (고리 가늠자 중심 = 가늠쇠 끝)
W_LOW = 0.036
W_UP = 0.030

# ================================================================== 아래 몸통 + 개머리 (남보라, 7식과 같은 실루엣)
low_pts = [
    (-0.200, -0.016), (-0.150, -0.010), (-0.118, -0.002), (-0.112, 0.010), (-0.046, 0.010), (-0.040, 0.020),
    (0.012, 0.022), (0.096, 0.028), (0.108, 0.036), (0.110, 0.062), (-0.150, 0.062), (-0.168, 0.068),
    (-0.178, 0.090), (-0.190, 0.099), (-0.200, 0.097), (-0.206, 0.086), (-0.207, 0.000),
]
g.s(hw.side("low_shell", low_pts, W_LOW, bevel=0.0055, seg=3, mat="violet"))
pad_pts = [(-0.214, -0.012), (-0.204, -0.017), (-0.204, 0.096), (-0.214, 0.090)]
g.s(hw.side("butt_pad", pad_pts, W_LOW + 0.002, bevel=0.003, seg=2, mat="dark"))
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    x = sx * W_LOW / 2
    g.f(*hw.holes(f"butt_hole{sx}", (x, -0.150, 0.026), 4, 0.0135, 0.0036, along=(1, 0), mat="dark", **fr))
    g.f(hw.decal(f"seam{sx}", [(-0.0006, -0.030), (0.0006, -0.030), (0.0006, 0.030), (-0.0006, 0.030)],
                 (x, -0.120, 0.034), mat="dark", **fr))
    for (y, z) in ((-0.135, 0.050), (0.075, 0.046), (-0.030, 0.046)):
        g.f(hw.decal(f"pin{sx}{y}", hw.circle(0.0022, 10), (x, y, z), mat="steel", **fr))
        g.f(hw.decal(f"pinc{sx}{y}", hw.circle(0.0009, 8), (x, y, z), lift=0.0008, mat="dark", **fr))
# 개머리 위 청록 띠 (진압반 비살상 장비 표식)
g.s(hw.side("butt_band", [(-0.191, -0.010), (-0.183, -0.009), (-0.183, 0.097), (-0.191, 0.0995)], W_LOW + 0.0012,
            bevel=0.0012, seg=1, mat="teal"))

# ================================================================== 위 리시버 (짧게 자른 7식 리시버)
up_side = [(-0.184, 0.056), (0.150, 0.056), (0.158, 0.062), (0.158, 0.094), (0.148, 0.102), (-0.168, 0.102),
           (-0.184, 0.092)]
g.s(hw.sculpt("upper", up_side, hw.rrect(W_UP, 0.050, 0.013, n=4, cy=0.079), bevel=0.0025, seg=2, mat="metal"))
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    x = sx * (W_UP / 2 + 0.0004)
    for i, y in enumerate((0.110, 0.134)):
        g.f(hw.decal(f"vent{sx}{i}", hw.stadium(0.019, 0.0075, 5), (x, y, 0.083), mat="dark", **fr))
g.f(hw.decal("eject_port", hw.rrect(0.036, 0.014, 0.004, 2), (W_UP / 2 + 0.0004, -0.070, 0.079),
             mat="dark", **hw.RIGHT))
g.s(hw.boxr("eject_lip", W_UP / 2 - 0.001, W_UP / 2 + 0.0025, -0.090, -0.050, 0.0700, 0.0718, bevel=0.0008,
            mat="metal"))
g.s(hw.side("port_cover", hw.rrect(0.050, 0.020, 0.006, 3, cx=-0.072, cy=0.079), 0.002, x=-W_UP / 2 - 0.0002,
            bevel=0.0007, seg=1, mat="violet_d"))
for y in (-0.092, -0.052):
    g.f(hw.decal(f"cover_screw{y}", hw.circle(0.0018, 8), (-W_UP / 2 - 0.0013, y, 0.079), mat="steel", **hw.LEFT))
g.f(hw.text("mk_type", "MR-7C", 0.0070, (-W_UP / 2 - 0.0004, 0.025, 0.068), mat="steel", **hw.LEFT))
g.f(hw.text("mk_unit", "모나티엄 진압반", 0.0050, (-W_UP / 2 - 0.0004, 0.025, 0.0905), mat="steel", **hw.LEFT))
# 윗면 가늠자 받침 줄 (낮은 리브)
g.s(hw.boxr("sight_rib", -0.0050, 0.0050, -0.080, 0.150, 0.100, 0.1045, bevel=0.0015, mat="metal"))
for i in range(9):
    g.f(hw.decal(f"rib_line{i}", hw.rrect(0.0085, 0.0012, 0.0005, 1), (0, -0.030 + i * 0.020, 0.1046),
                 mat="dark", **hw.TOP))

# ================================================================== 고리 가늠자 (뒤) + 귀 달린 가늠쇠 (앞)
REAR_Y = -0.072
g.s(hw.tube("ghost_ring", 0.0104, 0.0072, REAR_Y - 0.0022, REAR_Y + 0.0022, c=(0, SZ), verts=24, mat="dark"))
g.s(hw.side("ring_post", [(REAR_Y - 0.010, 0.1015), (REAR_Y + 0.010, 0.1015), (REAR_Y + 0.0035, SZ - 0.0095),
                          (REAR_Y - 0.0035, SZ - 0.0095)], 0.008, bevel=0.0018, seg=2, mat="dark"))
for sx in (-1, 1):   # 가늠자 보호 귀
    g.s(hw.side(f"ring_ear{sx}", hw.rrect(0.011, 0.021, 0.004, 2, cx=REAR_Y, cy=0.1125), 0.0030,
                x=sx * 0.0135, bevel=0.0010, seg=1, mat="metal"))
FRONT_Y = 0.140
g.s(hw.side("front_post", [(FRONT_Y - 0.0025, 0.100), (FRONT_Y + 0.0025, 0.100), (FRONT_Y + 0.0020, SZ),
                           (FRONT_Y - 0.0020, SZ)], 0.0034, bevel=0.0006, seg=1, mat="dark"))
g.f(hw.decal("front_dot", hw.circle(0.0012, 10), (0, FRONT_Y - 0.0023, SZ - 0.0020), mat="glow", **hw.BACK))
fe = [(FRONT_Y - 0.008, 0.100)] + hw.arc_pts(FRONT_Y, 0.118, 0.008, 180, 0, 6) + [(FRONT_Y + 0.008, 0.100)]
for sx in (-1, 1):   # 가늠쇠 보호 귀 (둥근 고리 반쪽)
    g.s(hw.side(f"post_ear{sx}", hw.strip(fe, 0.0035), 0.0030, x=sx * 0.0090, bevel=0.0008, seg=1, mat="metal"))
g.s(hw.boxr("post_base", -0.0105, 0.0105, FRONT_Y - 0.010, FRONT_Y + 0.010, 0.099, 0.1035, bevel=0.0015,
            mat="metal"))

# ================================================================== 앞 손받침 + 앞 손잡이 (진압반 개조)
hg_side = [(0.104, 0.060), (0.104, 0.034), (0.116, 0.026), (0.150, 0.026), (0.160, 0.034), (0.160, 0.060)]
g.s(hw.sculpt("handguard", hg_side, hw.rrect(0.034, 0.060, 0.012, n=3, cy=0.042), bevel=0.003, seg=2,
              mat="violet"))
fg = hw.side("fore_grip", hw.rrect(0.024, 0.060, 0.010, n=3, cx=0.132, cy=0.004), 0.022, bevel=0.0045, seg=2,
             mat="dark")
hw.xform(fg, rot=(8, 0, 0), pivot=(0, 0.132, 0.030))
g.s(fg)
for i in range(3):   # 손가락 홈 (엘프 손가락 3개)
    rg = hw.boxr(f"fg_ridge{i}", -0.0116, 0.0116, 0.143, 0.146, -0.0015 - i * 0.012, 0.0005 - i * 0.012,
                 bevel=0.0010, mat="dark")
    hw.xform(rg, rot=(8, 0, 0), pivot=(0, 0.132, 0.030))
    g.s(rg)
fc = hw.boxr("fg_cap", -0.0118, 0.0118, 0.120, 0.145, -0.031, -0.024, bevel=0.0025, mat="teal")   # 청록 손잡이 끝
hw.xform(fc, rot=(8, 0, 0), pivot=(0, 0.132, 0.030))
g.s(fc)

# ================================================================== 굵은 고무탄 총열 · 청록 띠 · 금색 나팔 총구
g.s(hw.ycyl("barrel", 0.0118, 0.150, 0.250, z=BZ, verts=24, mat="dark"))
g.s(hw.muzzle_ring("ring_rear", 0.153, 0.161, 0.0135, z=BZ, mat="gold"))
g.s(hw.ycyl("band_teal", 0.0128, 0.214, 0.236, z=BZ, verts=24, bevel=0.0010, mat="teal"))
g.s(hw.tube("muzzle_bell", 0.0136, 0.0088, 0.236, 0.252, c=(0, BZ), verts=24, r_out2=0.0158, r_in2=0.0098,
            mat="gold"))
g.s(hw.ycyl("bore", 0.0090, 0.240, 0.247, z=BZ, verts=16, mat="dark"))
g.f(hw.text("mk_less", "비살상", 0.0052, (-0.0130, 0.225, BZ), mat="steel", right=(0, -1, 0), up=(0, 0, 1),
            lift=0.0004))

# ================================================================== 손전등 (왼쪽 아래, 1인칭에서 보임)
LX, LZ = -0.0150, 0.044
g.s(hw.ycyl("light_body", 0.0085, 0.160, 0.208, x=LX, z=LZ, verts=18, bevel=0.0012, mat="dark"))
g.s(hw.ycyl("light_head", 0.0100, 0.200, 0.214, x=LX, z=LZ, verts=18, bevel=0.0012, mat="metal"))
g.f(hw.decal("light_lens", hw.circle(0.0078, 16), (LX, 0.2141, LZ), mat="steel", **hw.FRONT))
g.s(hw.boxr("light_clamp", LX, -0.006, 0.168, 0.182, LZ - 0.004, LZ + 0.008, bevel=0.0015, mat="metal"))
g.s(hw.ycyl("light_switch", 0.0035, 0.152, 0.160, x=LX, z=LZ, verts=10, mat="teal"))

# ================================================================== 손잡이 · D자 고리 · 방아쇠 (7식과 같음)
grip = hw.side("grip", hw.rrect(0.029, 0.084, 0.011, n=3, cy=-0.016), 0.025, bevel=0.004, seg=2, mat="dark")
hw.xform(grip, rot=(-13, 0, 0), pivot=(0, 0, 0.02))
g.s(grip)
for sx in (-1, 1):
    p = hw.side(f"grip_panel{sx}", hw.rrect(0.020, 0.058, 0.008, n=2, cy=-0.018), 0.003, x=sx * 0.0128,
                bevel=0.0010, seg=1, mat="violet_d")
    hw.xform(p, rot=(-13, 0, 0), pivot=(0, 0, 0.02))
    g.s(p)
loop_path = [(-0.012, -0.056), (0.050, -0.056)] + hw.arc_pts(0.050, -0.034, 0.022, 270, 360, 5)[1:] + \
    [(0.072, 0.000), (0.080, 0.026)]
g.s(hw.side("d_loop", hw.strip(loop_path, 0.0085), 0.015, bevel=0.0028, seg=2, mat="violet"))
TRIG = (0, 0.030, 0.021)
trig = hw.side("trigger_blade", [(-0.0022, 0.0), (0.0030, 0.0), (0.0038, -0.010), (0.0072, -0.020),
                                 (0.0040, -0.025), (-0.0010, -0.022), (-0.0020, -0.010)], 0.006, bevel=0.0012, seg=2,
               mat="steel")
trig.location = TRIG
g.p("trigger", trig)
g.pivot("trigger", TRIG, rotAxis="x", rotDeg=-14)

# ================================================================== 잔탄 표시창 (HUD 연동) + 엘프 로고 (금색)
g.f(hw.decal("counter_bg", hw.rrect(0.026, 0.011, 0.003, 2), (-W_LOW / 2, -0.076, 0.044), mat="dark", **hw.LEFT))
for i in range(5):
    g.f(hw.decal(f"counter_bar{i}", hw.rrect(0.0032, 0.0062, 0.0006, 1), (-W_LOW / 2, -0.086 + i * 0.0048, 0.044),
                 lift=0.0009, mat="glow", **hw.LEFT))
g.f(hw.decal("logo_disc", hw.circle(0.0165, 24), (-W_LOW / 2, 0.050, 0.042), mat="violet_d", **hw.LEFT))
g.f(hw.ring_decal("logo_rim", (-W_LOW / 2, 0.050, 0.042), 0.0165, 0.0150, mat="gold", lift=0.0008, **hw.LEFT))
g.logo((-W_LOW / 2, 0.050, 0.042), 0.020, mat="gold", **hw.LEFT)
g.f(hw.text("mk_serial", "MNT-R 0731", 0.0050, (-W_LOW / 2, -0.150, 0.046), mat="steel", **hw.LEFT))

# ================================================================== 조정간 (단발·연발)
SEL = (-W_LOW / 2 - 0.0012, 0.000, 0.046)
sel = [hw.xcyl("sel_hub", 0.0042, -0.0010, 0.0014, y=0, z=0, verts=14, mat="dark"),
       hw.side("sel_lever", hw.stadium(0.016, 0.0042, 3, cx=0.006), 0.0022, x=-0.0004, bevel=0.0006, seg=1,
               mat="dark")]
for o in sel:
    o.location = (o.location.x + SEL[0], o.location.y + SEL[1], o.location.z + SEL[2])
g.p("selector", *sel)
g.pivot("selector", SEL, rotAxis="x", rotDeg="0,45,90", note="SAFE/SEMI/AUTO")

# ================================================================== 장전 손잡이 · 노리쇠
CH = (-W_UP / 2, 0.090, 0.084)
ch = [hw.xcyl("ch_stem", 0.0030, -0.012, 0.0, y=0, z=0, verts=10, mat="steel"),
      cb.sphere("ch_knob", radius=0.0052, loc=(-0.013, 0, 0), segments=12, rings=8, material=hw.M("teal"))]
for o in ch:
    o.location = (o.location.x + CH[0], o.location.y + CH[1], o.location.z + CH[2])
g.p("charging_handle", *ch)
g.pivot("charging_handle", CH, move=hw.mv(0, -0.065, 0))
g.f(hw.decal("ch_slot", hw.stadium(0.080, 0.0042, 3), (-W_UP / 2 - 0.0002, 0.058, 0.084), mat="dark", **hw.LEFT))
g.p("bolt", hw.boxr("bolt_body", W_UP / 2 - 0.004, W_UP / 2 + 0.0009, -0.082, -0.058, 0.0748, 0.0836, bevel=0.0010,
                    mat="steel"))
g.pivot("bolt", (W_UP / 2, -0.070, 0.079), move=hw.mv(0, -0.040, 0))

# ================================================================== 탄창 (직탄창 15발, 청록 고무탄이 창으로 보임)
MAGY = -0.079
mag = [hw.side("mag_body", hw.rrect(0.050, 0.110, 0.006, n=2, cx=MAGY, cy=-0.018), 0.022, bevel=0.0018, seg=2,
               mat="dark"),
       hw.side("mag_base", hw.rrect(0.056, 0.010, 0.004, n=2, cx=MAGY, cy=-0.076), 0.026, bevel=0.0020, seg=2,
               mat="teal")]
for sx in (-1, 1):
    mag.append(hw.boxr(f"mag_rib{sx}", sx * 0.0110 - 0.0007, sx * 0.0110 + 0.0007, MAGY - 0.022, MAGY + 0.022,
                       -0.052, -0.049, bevel=0.0004, mat="dark"))
g.p("mag", *mag)
g.pivot("mag", (0, MAGY, 0.010), move=hw.mv(0, 0, -0.16))
for i in range(3):   # 창 (어두운 테) 안의 청록 고무탄
    z = -0.004 - i * 0.0135
    g.pf("mag", hw.decal(f"mag_win{i}", hw.circle(0.0050, 16), (-0.0111, MAGY + 0.006, z), mat="violet_d",
                         **hw.LEFT))
    g.pf("mag", hw.decal(f"mag_ball{i}", hw.circle(0.0038, 16), (-0.0111, MAGY + 0.006, z), lift=0.0009, mat="teal",
                         **hw.LEFT))
g.pf("mag", hw.text("mag_no", "15", 0.0065, (-0.0111, MAGY - 0.012, -0.020), mat="steel", **hw.LEFT))
g.pf("mag", hw.text("mag_less", "비살상", 0.0042, (-0.0111, MAGY - 0.012, -0.040), mat="teal", **hw.LEFT))

# ================================================================== 멜빵 고리 · 탄창 멈치
g.s(hw.torus("sling_rear", 0.0060, 0.0013, loc=(0, -0.186, -0.020), rot=(0, 90, 0), seg=14, rseg=6, mat="steel"))
g.s(hw.boxr("mag_release", -0.008, 0.008, -0.118, -0.110, -0.004, 0.006, bevel=0.0015, mat="dark"))

# ================================================================== 앵커
g.anchor("muzzle", (0, 0.252, BZ))
g.anchor("grip_support", (0, 0.134, 0.000))
g.anchor("sight_eye", (0, -0.150, SZ))
g.anchor("eject", (W_UP / 2 + 0.006, -0.070, 0.079))
g.anchor("mag_well", (0, MAGY, 0.010))
g.anchor("light", (LX, 0.215, LZ))

g.finish("weapons/monatium/monatium_riot_carbine.glb", outline=0.0019, fp="0.155,-0.20,-0.34", fprot="0,6,0")
