"""모나티엄 진압반 MR-5P '낮잠' 고무탄 권총 (제식 권총).

[오리지널] 엘피니아 5식 권총을 진압반이 고친 제식 권총. 고무탄 전용 굵은 총열, 단열 8발, 공이치기를 없앤 격침식(걸림 방지).
5식과 공유하는 형태(계보): 둥근 슬라이드, 슬라이드 앞 스타디움 창과 뒤 구멍 줄, 금색 총구 테, 큰 방아쇠울, 손잡이 원판 + 엘프 로고.
진압반 표지: 남보라 프레임, 청록 비살상 띠(슬라이드 앞·탄창 바닥), 소형 손전등.
[원작] 교주 차원 모나티엄 진압반은 고무탄을 쓴다.

npm run model -- art/blender/weapons/monatium/monatium_pistol.py
npm run shot -- weapons/monatium/monatium_pistol.glb --views side,34,top,muzzle --focus monatium_pistol
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402

cb.reset()
g = hw.Gun("monatium_pistol")

BZ = 0.062          # 총열 축 (5식과 같음)
W_SL = 0.0245       # 슬라이드 폭 (굵은 총열 때문에 5식보다 1 mm 넓다)
W_FR = 0.0220
SL_TOP = 0.0800
SIGHT_Z = 0.0865
GRIP_TILT = -16

# ================================================================== 슬라이드 (움직이는 파츠)
sl_side = [(-0.044, 0.0465), (0.098, 0.0465), (0.102, 0.050), (0.102, 0.066)] + \
    hw.arc_pts(0.088, 0.066, 0.014, 0, 90, 4)[1:] + [(-0.038, SL_TOP), (-0.044, 0.074)]
slide = [hw.sculpt("slide_body", sl_side, hw.rrect(W_SL, 0.035, 0.009, n=3, cy=0.0633), bevel=0.0016, seg=2,
                   mat="metal")]
slide.append(hw.boxr("rear_sight", -0.0080, 0.0080, -0.038, -0.029, SL_TOP - 0.001, SIGHT_Z, bevel=0.0012,
                     mat="dark"))
slide.append(hw.boxr("front_sight", -0.0019, 0.0019, 0.082, 0.090, SL_TOP - 0.001, SIGHT_Z, bevel=0.0008,
                     mat="dark"))
slide.append(hw.section("band_teal", hw.rrect(W_SL + 0.0014, 0.0362, 0.0094, n=3, cy=0.0633), 0.074, 0.082,
                        bevel=0.0006, seg=1, mat="teal"))   # 슬라이드 단면을 감싸는 비살상 띠
slide.append(hw.tube("bushing", 0.0098, 0.0062, 0.0985, 0.1060, c=(0, BZ), verts=22, r_out2=0.0104, mat="gold"))
slide.append(hw.ycyl("bore_back", 0.0063, 0.090, 0.093, z=BZ, verts=14, mat="dark"))
notch = hw.slot_cutter("notch_cut", hw.rrect(0.0068, 0.012, 0.0010, 1, cy=SIGHT_Z + 0.001), (0, -0.0335, 0),
                       axis="Y", depth=0.02)
hw.cut(slide[1], notch)
fine = []
fine.append(hw.decal("front_dot", hw.circle(0.0012, 10), (0, 0.0818, SIGHT_Z - 0.0020), mat="glow", **hw.BACK))
for sx in (-1, 1):
    fine.append(hw.decal(f"rear_dot{sx}", hw.circle(0.0010, 8), (sx * 0.0058, -0.0383, SIGHT_Z - 0.0022),
                         mat="steel", **hw.BACK))
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    x = sx * W_SL / 2
    fine.append(hw.decal(f"sl_win{sx}", hw.stadium(0.020, 0.0072, 5), (x, 0.062, 0.0645), mat="dark", **fr))
    fine.extend(hw.holes(f"sl_hole{sx}", (x, -0.029, 0.0645), 3, 0.0085, 0.0030, along=(1, 0), mat="dark", **fr))
fine.append(hw.text("mk_type", "MR-5P", 0.0058, (-W_SL / 2, 0.026, 0.0655), mat="steel", **hw.LEFT))
fine.append(hw.text("mk_rubber", "고무탄", 0.0046, (-W_SL / 2, 0.026, 0.0560), mat="teal", **hw.LEFT))
fine.append(hw.decal("chamber_dot", hw.stadium(0.006, 0.0024, 3, angle=90), (0, 0.010, SL_TOP), mat="glow",
                     **hw.TOP))
fine.append(hw.decal("eject_port", hw.rrect(0.024, 0.0105, 0.0025, 2), (W_SL / 2, 0.018, 0.0660), mat="dark",
                     **hw.RIGHT))
slide.append(hw.boxr("chamber_hood", W_SL / 2 - 0.004, W_SL / 2 + 0.0006, 0.010, 0.025, 0.0627, 0.0695,
                     bevel=0.0008, mat="steel"))
# 뒷면 격침 표시 (청록 점: 장전됨)
fine.append(hw.decal("striker_ind", hw.circle(0.0018, 10), (0, -0.0441, 0.062), mat="teal", **hw.BACK))
g.p("slide", *slide)
g.pf("slide", *fine)
g.pivot("slide", (0, -0.044, BZ), move=hw.mv(0, -0.030, 0))

# ================================================================== 프레임 (남보라)
fr_side = [(-0.034, 0.024), (0.014, 0.024), (0.058, 0.030), (0.096, 0.032), (0.098, 0.040), (0.098, 0.0480),
           (-0.038, 0.0480), (-0.044, 0.040)]
g.s(hw.sculpt("frame", fr_side, hw.rrect(W_FR, 0.034, 0.006, n=2, cy=0.034), bevel=0.0018, seg=2, mat="violet"))
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    g.f(hw.decal(f"rail_gap{sx}", hw.rrect(0.130, 0.0012, 0.0005, 1), (sx * W_FR / 2, 0.028, 0.0478),
                 mat="dark", **fr))
    g.f(hw.decal(f"pin{sx}", hw.circle(0.0019, 10), (sx * W_FR / 2, 0.052, 0.041), mat="steel", **fr))
    g.f(hw.decal(f"pin2{sx}", hw.circle(0.0016, 10), (sx * W_FR / 2, -0.030, 0.038), mat="steel", **fr))
guard_path = [(0.004, 0.026), (0.004, 0.002)] + hw.arc_pts(0.020, 0.002, 0.016, 180, 270, 3)[1:] + \
    [(0.040, -0.014)] + hw.arc_pts(0.040, 0.004, 0.018, 270, 360, 4)[1:] + [(0.058, 0.028)]
g.s(hw.side("trigger_guard", hw.strip(guard_path, 0.0058), 0.0105, bevel=0.0022, seg=2, mat="violet"))

# 소형 손전등 (먼지 덮개 아래)
g.s(hw.ycyl("light_body", 0.0078, 0.062, 0.094, z=0.024, verts=18, bevel=0.0012, mat="dark"))
g.s(hw.ycyl("light_head", 0.0090, 0.090, 0.100, z=0.024, verts=18, bevel=0.0012, mat="metal"))
g.s(hw.boxr("light_mount", -0.0060, 0.0060, 0.066, 0.090, 0.028, 0.0335, bevel=0.0012, mat="dark"))
g.f(hw.decal("light_lens", hw.circle(0.0070, 16), (0, 0.1002, 0.024), mat="steel", **hw.FRONT))
g.s(hw.xcyl("light_switch", 0.0028, -0.0095, 0.0095, y=0.068, z=0.024, verts=10, mat="teal"))

# ================================================================== 손잡이 (남보라, 원판 + 엘프 로고)
grip = [hw.side("grip", hw.rrect(0.031, 0.074, 0.011, n=3, cy=-0.009), W_FR, bevel=0.0035, seg=2, mat="violet")]
for sx in (-1, 1):
    grip.append(hw.side(f"grip_panel{sx}", hw.rrect(0.022, 0.050, 0.008, n=2, cy=-0.010), 0.0024,
                        x=sx * (W_FR / 2 + 0.0006), bevel=0.0009, seg=1, mat="dark"))
for o in grip:
    hw.xform(o, rot=(GRIP_TILT, 0, 0), pivot=(0, 0, 0.024))
    g.s(o)
gt = math.radians(GRIP_TILT)


def on_grip(y, z, sx):
    dz = z - 0.024
    return (sx * (W_FR / 2 + 0.0026), y * math.cos(gt) - dz * math.sin(gt), 0.024 + y * math.sin(gt) + dz * math.cos(gt))


for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    c = on_grip(0.0, -0.006, sx)
    up = (0, -math.sin(gt), math.cos(gt))
    rt = (0, sx * math.cos(gt), sx * math.sin(gt))
    g.f(hw.decal(f"medal{sx}", hw.circle(0.0080, 20), c, right=rt, up=up, mat="violet_d"))
    g.f(hw.ring_decal(f"medal_rim{sx}", c, 0.0080, 0.0070, right=rt, up=up, mat="gold", lift=0.0008))
    g.logo(c, 0.0100, right=rt, up=up, mat="gold", name=f"elf_logo{sx}")
    for i in range(3):
        g.f(hw.decal(f"grip_groove{sx}{i}", hw.rrect(0.016, 0.0015, 0.0006, 1), on_grip(0.0, -0.024 - i * 0.0055, sx),
                     right=rt, up=up, mat="violet"))
bot = on_grip(-0.0175, -0.040, 0)
g.s(hw.torus("lanyard", 0.0050, 0.0013, loc=(0, bot[1] - 0.003, bot[2]), rot=(0, 90, 0), seg=14, rseg=6,
             mat="steel"))

# ================================================================== 방아쇠
TRIG = (0, 0.024, 0.024)
trig = hw.side("trigger_blade", [(-0.0020, 0.0), (0.0030, 0.0), (0.0040, -0.009), (0.0068, -0.017),
                                 (0.0038, -0.021), (-0.0010, -0.018), (-0.0018, -0.008)], 0.0055, bevel=0.0011, seg=2,
               mat="steel")
trig.location = TRIG
g.p("trigger", trig)
g.pivot("trigger", TRIG, rotAxis="x", rotDeg=-14)

# ================================================================== 슬라이드 멈치 · 안전장치 (왼쪽)
g.s(hw.side("slide_stop", hw.stadium(0.020, 0.0052, 4, cx=0.022, cy=0.0435), 0.0020, x=-W_FR / 2 - 0.0012,
            bevel=0.0006, seg=1, mat="dark"))
SAF = (-W_FR / 2 - 0.0010, -0.026, 0.0445)
saf = [hw.side("safety_lever", hw.stadium(0.013, 0.0048, 3, cx=0.004), 0.0022, bevel=0.0006, seg=1, mat="dark")]
saf[0].location = SAF
g.p("safety", *saf)
g.pivot("safety", SAF, rotAxis="x", rotDeg=-30)
g.f(hw.decal("safe_dot", hw.circle(0.0013, 8), (-W_FR / 2, -0.018, 0.0405), mat="glow", **hw.LEFT))

# ================================================================== 탄창 (청록 바닥: 비살상 탄)
mag = [hw.side("mag_body", hw.rrect(0.022, 0.060, 0.004, n=2, cy=-0.016), 0.015, bevel=0.0012, seg=1,
               mat="dark"),
       hw.side("mag_base", hw.rrect(0.030, 0.0085, 0.0035, n=2, cy=-0.0505), W_FR + 0.001, bevel=0.0018, seg=2,
               mat="teal")]
for o in mag:
    hw.xform(o, rot=(GRIP_TILT, 0, 0), pivot=(0, 0, 0.024))
g.p("mag", *mag)
MAGP = on_grip(0.0, 0.0, 0)
g.pivot("mag", (0, MAGP[1], MAGP[2]), move=hw.mv(0, math.sin(-gt) * 0.12 * -1, -math.cos(gt) * 0.12))

# ================================================================== 앵커
g.anchor("muzzle", (0, 0.106, BZ))
g.anchor("grip_support", (-0.016, 0.004, -0.010))
g.anchor("sight_eye", (0, -0.160, SIGHT_Z))
g.anchor("eject", (W_SL / 2 + 0.006, 0.018, 0.0660))
g.anchor("mag_well", (0, MAGP[1], MAGP[2]))
g.anchor("light", (0, 0.101, 0.024))

g.finish("weapons/monatium/monatium_pistol.glb", outline=0.0017, fp="0.11,-0.125,-0.26", fprot="0,6,0")
