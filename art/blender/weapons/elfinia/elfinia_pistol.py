"""엘피니아 5식 권총 '나사' (엘피니아 군 제식 권총).

[오리지널] 지구 침공 당시 엘피니아 정규군 장교·정찰조의 제식 권총. 화약식 실탄, 단열 9발 탄창, 노출 공이치기.
7식 소총과 같은 형태 문법: 둥근 슬라이드, 회녹 프레임, 금색 총구 고리, 둥근 구멍 줄, 손잡이의 남색 원판 + 엘프 로고.
[원작] 엘프는 화약식 총기를 쓴다(시스트의 권총들이 엘프 출처). 4손가락 엘프 손에 맞춰 손잡이는 짧고 방아쇠울은 크다.

npm run model -- art/blender/weapons/elfinia/elfinia_pistol.py
npm run shot -- weapons/elfinia/elfinia_pistol.glb --views side,34,top,muzzle --focus elfinia_pistol
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402

cb.reset()
g = hw.Gun("elfinia_pistol")

BZ = 0.062          # 총열 축
W_SL = 0.0235       # 슬라이드 폭
W_FR = 0.0215       # 프레임 폭
SL_TOP = 0.0790
SIGHT_Z = 0.0855    # 조준선 (가늠쇠 윗면 = 가늠자 홈 바닥)
GRIP_TILT = -16

# ================================================================== 슬라이드 (움직이는 파츠)
sl_side = [(-0.046, 0.0465), (0.100, 0.0465), (0.104, 0.050), (0.104, 0.066)] + \
    hw.arc_pts(0.091, 0.066, 0.013, 0, 90, 4)[1:] + [(-0.040, SL_TOP), (-0.046, 0.073)]
slide = [hw.sculpt("slide_body", sl_side, hw.rrect(W_SL, 0.034, 0.0085, n=3, cy=0.0628), bevel=0.0016, seg=2,
                   mat="metal")]
slide.append(hw.boxr("rear_sight", -0.0080, 0.0080, -0.040, -0.031, SL_TOP - 0.001, SIGHT_Z, bevel=0.0012,
                     mat="dark"))
slide.append(hw.boxr("front_sight", -0.0019, 0.0019, 0.086, 0.094, SL_TOP - 0.001, SIGHT_Z, bevel=0.0008,
                     mat="dark"))
slide.append(hw.tube("bushing", 0.0088, 0.0046, 0.101, 0.1075, c=(0, BZ), verts=20, mat="gold"))
fine = []
# 가늠자 홈 (어두운 판 위 밝은 홈 대신, 가늠자 두 귀를 남기고 가운데를 뚫어 보이게)
notch = hw.slot_cutter("notch_cut", hw.rrect(0.0068, 0.012, 0.0010, 1, cy=SIGHT_Z + 0.001), (0, -0.0355, 0),
                       axis="Y", depth=0.02)
hw.cut(slide[1], notch)
fine.append(hw.decal("front_dot", hw.circle(0.0012, 10), (0, 0.0858, SIGHT_Z - 0.0020), mat="glow", **hw.BACK))
for sx in (-1, 1):
    fine.append(hw.decal(f"rear_dot{sx}", hw.circle(0.0010, 8), (sx * 0.0058, -0.0403, SIGHT_Z - 0.0022),
                         mat="steel", **hw.BACK))
# 슬라이드 옆: 앞쪽 스타디움 창, 뒤쪽 둥근 구멍 줄 (엘프식 미끄럼 방지)
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    x = sx * W_SL / 2
    fine.append(hw.decal(f"sl_win{sx}", hw.stadium(0.022, 0.0072, 5), (x, 0.074, 0.0640), mat="dark", **fr))
    fine.extend(hw.holes(f"sl_hole{sx}", (x, -0.031, 0.0640), 3, 0.0085, 0.0030, along=(-sx, 0), mat="dark", **fr))
fine.append(hw.text("mk_type", "5식", 0.0072, (-W_SL / 2, 0.030, 0.0650), mat="steel", **hw.LEFT))
# 약실 표시 (윗면, 시안 점: 장전되면 켜짐)
fine.append(hw.decal("chamber_dot", hw.stadium(0.006, 0.0024, 3, angle=90), (0, 0.010, SL_TOP), mat="glow",
                     **hw.TOP))
# 배출구 (오른쪽)
fine.append(hw.decal("eject_port", hw.rrect(0.024, 0.0105, 0.0025, 2), (W_SL / 2, 0.018, 0.0655), mat="dark",
                     **hw.RIGHT))
slide.append(hw.boxr("chamber_hood", W_SL / 2 - 0.004, W_SL / 2 + 0.0006, 0.010, 0.025, 0.0622, 0.0690,
                     bevel=0.0008, mat="steel"))
g.p("slide", *slide)
g.pf("slide", *fine)
g.pivot("slide", (0, -0.046, BZ), move=hw.mv(0, -0.032, 0))

# ================================================================== 프레임 (회녹)
fr_side = [(-0.034, 0.024), (0.014, 0.024), (0.058, 0.032), (0.094, 0.034), (0.098, 0.040), (0.098, 0.0480),
           (-0.040, 0.0480), (-0.046, 0.040)]
g.s(hw.sculpt("frame", fr_side, hw.rrect(W_FR, 0.034, 0.006, n=2, cy=0.034), bevel=0.0018, seg=2, mat="olive"))
# 레일 대신 둥근 앞 덮개 아래 홈 2줄
for i in range(2):
    g.f(hw.decal(f"dust_groove{i}", hw.rrect(0.026, 0.0016, 0.0007, 1), (0, 0.078, 0.0331 - i * 0.0001),
                 mat="olive_d", right=(0, -1, 0), up=(-1, 0, 0)))
# 슬라이드 레일 틈 (어두운 줄)
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    g.f(hw.decal(f"rail_gap{sx}", hw.rrect(0.134, 0.0012, 0.0005, 1), (sx * W_FR / 2, 0.028, 0.0478),
                 mat="dark", **fr))
    g.f(hw.decal(f"pin{sx}", hw.circle(0.0019, 10), (sx * W_FR / 2, 0.052, 0.040), mat="steel", **fr))
    g.f(hw.decal(f"pin2{sx}", hw.circle(0.0016, 10), (sx * W_FR / 2, -0.030, 0.038), mat="steel", **fr))

# 방아쇠울 (크게: 4손가락 손)
guard_path = [(0.004, 0.026), (0.004, 0.002)] + hw.arc_pts(0.020, 0.002, 0.016, 180, 270, 3)[1:] + \
    [(0.040, -0.014)] + hw.arc_pts(0.040, 0.004, 0.018, 270, 360, 4)[1:] + [(0.058, 0.030)]
g.s(hw.side("trigger_guard", hw.strip(guard_path, 0.0058), 0.0105, bevel=0.0022, seg=2, mat="olive"))

# ================================================================== 손잡이 (짧게, 아래 둥근 끝 + 끈 고리)
grip = [hw.side("grip", hw.rrect(0.031, 0.074, 0.011, n=3, cy=-0.009), W_FR, bevel=0.0035, seg=2, mat="olive")]
for sx in (-1, 1):
    grip.append(hw.side(f"grip_panel{sx}", hw.rrect(0.022, 0.050, 0.008, n=2, cy=-0.010), 0.0024,
                        x=sx * (W_FR / 2 + 0.0006), bevel=0.0009, seg=1, mat="olive_d"))
for o in grip:
    hw.xform(o, rot=(GRIP_TILT, 0, 0), pivot=(0, 0, 0.024))
    g.s(o)
# 손잡이 원판 (엘피니아 남색 + 금테 + 엘프 로고): 양쪽
gt = math.radians(GRIP_TILT)


def on_grip(y, z, sx):
    """손잡이 판 위의 (y, z) 점을 기울기만큼 돌린다 (pivot z=0.024)."""
    dz = z - 0.024
    return (sx * (W_FR / 2 + 0.0026), y * math.cos(gt) - dz * math.sin(gt), 0.024 + y * math.sin(gt) + dz * math.cos(gt))


for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    c = on_grip(0.0, -0.006, sx)
    up = (0, -math.sin(gt), math.cos(gt))
    rt = (0, sx * math.cos(gt), sx * math.sin(gt))      # 법선 = rt x up = sx·X (바깥)
    g.f(hw.decal(f"medal{sx}", hw.circle(0.0080, 20), c, right=rt, up=up, mat="navy"))
    g.f(hw.ring_decal(f"medal_rim{sx}", c, 0.0080, 0.0070, right=rt, up=up, mat="gold", lift=0.0008))
    g.logo(c, 0.0100, right=rt, up=up, mat="gold", name=f"elf_logo{sx}")
    for i in range(3):   # 아래쪽 미끄럼 방지 홈
        g.f(hw.decal(f"grip_groove{sx}{i}", hw.rrect(0.016, 0.0015, 0.0006, 1), on_grip(0.0, -0.024 - i * 0.0055, sx),
                     right=rt, up=up, mat="olive"))
# 끈 고리 (손잡이 아래 끝)
bot = on_grip(-0.0175, -0.040, 0)
g.s(hw.torus("lanyard", 0.0050, 0.0013, loc=(0, bot[1] - 0.003, bot[2]), rot=(0, 90, 0), seg=14, rseg=6,
             mat="steel"))

# ================================================================== 공이치기 (노출형, 둥근 머리)
HAM = (0, -0.040, 0.054)
ham = [hw.side("hammer", [(-0.003, -0.006), (0.003, -0.006), (0.002, 0.010), (-0.004, 0.017), (-0.010, 0.016),
                          (-0.008, 0.010)], 0.0060, bevel=0.0012, seg=2, mat="dark")]
ham.append(hw.xcyl("hammer_spur", 0.0042, -0.0032, 0.0032, y=-0.008, z=0.015, verts=14, mat="dark"))
for o in ham:
    o.location = (o.location.x + HAM[0], o.location.y + HAM[1], o.location.z + HAM[2])
g.p("hammer", *ham)
g.pivot("hammer", HAM, rotAxis="x", rotDeg=-35, note="cocked = rotate back")

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
SAF = (-W_FR / 2 - 0.0010, -0.028, 0.0445)
saf = [hw.side("safety_lever", hw.stadium(0.013, 0.0048, 3, cx=0.004), 0.0022, bevel=0.0006, seg=1, mat="dark")]
saf[0].location = SAF
g.p("safety", *saf)
g.pivot("safety", SAF, rotAxis="x", rotDeg=-30)
g.f(hw.decal("safe_dot", hw.circle(0.0013, 8), (-W_FR / 2, -0.020, 0.0405), mat="glow", **hw.LEFT))

# ================================================================== 탄창 (손잡이 축 따라 아래로)
mag = [hw.side("mag_body", hw.rrect(0.022, 0.060, 0.004, n=2, cy=-0.016), 0.015, bevel=0.0012, seg=1,
               mat="dark"),
       hw.side("mag_base", hw.rrect(0.030, 0.0085, 0.0035, n=2, cy=-0.0505), W_FR + 0.001, bevel=0.0018, seg=2,
               mat="olive_d")]
for o in mag:
    hw.xform(o, rot=(GRIP_TILT, 0, 0), pivot=(0, 0, 0.024))
g.p("mag", *mag)
MAGP = on_grip(0.0, 0.0, 0)
g.pivot("mag", (0, MAGP[1], MAGP[2]), move=hw.mv(0, math.sin(-gt) * 0.12 * -1, -math.cos(gt) * 0.12))

# ================================================================== 앵커
g.anchor("muzzle", (0, 0.1075, BZ))
g.anchor("grip_support", (-0.016, 0.004, -0.010))
g.anchor("sight_eye", (0, -0.160, SIGHT_Z))
g.anchor("eject", (W_SL / 2 + 0.006, 0.018, 0.0655))
g.anchor("mag_well", (0, MAGP[1], MAGP[2]))

g.finish("weapons/elfinia/elfinia_pistol.glb", outline=0.0017, fp="0.115,-0.13,-0.27", fprot="0,6,0")
