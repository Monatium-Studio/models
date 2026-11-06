"""모나티엄 진압반 MR-37 '단잠' 진압 발사기 (근거리 제압).

[오리지널] 37 mm 펌프식 진압 발사기. 관형 탄창 3발 + 약실 1발. 고무 충격탄(맞으면 넘어지고 정신을 잃음)과 최루탄을 쓴다.
[원작] 진압반장 칸나는 포탄을 쏘는 대포(바주카)를 쓰고, 그 강화 공격은 '충격 포탄'으로 적을 기절시킨다.
       칸나: "최루 가스는 정말 완벽한 제압용 무기죠!" → 산탄총 대신 진압용 유탄 발사기를 골랐다.
       R41 진압반의 회전 약실 산탄총(S-3)과도 겹치지 않는다.

형태 근거: 칸나 발사기의 굵은 관, 앞으로 벌어진 금색 총구 테, 사각 고리 손잡이. 교주 차원 문법(둥근 판, D자 고리, 구멍 줄).
진압반 표지: 남보라 외장, 청록 비살상 띠, 왼쪽 탄띠의 고무 충격탄 2발(금색 탄피 + 청록 탄두).

npm run model -- art/blender/weapons/monatium/monatium_riot_launcher.py
npm run shot -- weapons/monatium/monatium_riot_launcher.glb --views side,34,top,muzzle --focus monatium_riot_launcher
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402

cb.reset()
g = hw.Gun("monatium_riot_launcher")

BZ = 0.078          # 총열 축
R_BAR = 0.0235      # 총열 바깥 반지름 (37 mm 구경)
TZ = 0.031          # 관형 탄창 축
R_TUBE = 0.0200
SZ = 0.132          # 조준선
W_REC = 0.054

# ================================================================== 리시버 (둥근 상자)
rec_side = [(-0.058, 0.004), (0.072, 0.004), (0.074, 0.010), (0.074, 0.098), (0.066, 0.106), (-0.050, 0.106),
            (-0.060, 0.096)]
g.s(hw.sculpt("receiver", rec_side, hw.rrect(W_REC, 0.104, 0.017, n=4, cy=0.055), bevel=0.0028, seg=2,
              mat="metal"))
# 아래 장전구 (어두운 창) + 오른쪽 배출구
g.f(hw.decal("load_port", hw.rrect(0.026, 0.060, 0.008, 2), (0, 0.035, 0.0040), mat="dark",
             right=(1, 0, 0), up=(0, 1, 0)))
g.f(hw.decal("eject_port", hw.rrect(0.052, 0.034, 0.010, 3), (W_REC / 2 + 0.0002, 0.022, 0.070), mat="dark",
             **hw.RIGHT))
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    x = sx * (W_REC / 2 + 0.0002)
    for (y, z) in ((-0.045, 0.020), (0.060, 0.020), (-0.045, 0.092)):
        g.f(hw.decal(f"rpin{sx}{y}{z}", hw.circle(0.0024, 10), (x, y, z), mat="steel", **fr))
# 왼쪽: 남보라 원판 + 금색 엘프 로고, 구경 각인
g.f(hw.decal("logo_disc", hw.circle(0.0200, 28), (-W_REC / 2 - 0.0002, 0.012, 0.064), mat="violet_d", **hw.LEFT))
g.f(hw.ring_decal("logo_rim", (-W_REC / 2 - 0.0002, 0.012, 0.064), 0.0200, 0.0184, mat="gold", lift=0.0008,
                  **hw.LEFT))
g.logo((-W_REC / 2 - 0.0002, 0.012, 0.064), 0.025, mat="gold", **hw.LEFT)
g.f(hw.text("mk_cal", "37", 0.016, (-W_REC / 2 - 0.0002, -0.034, 0.066), mat="steel", **hw.LEFT))
g.f(hw.text("mk_type", "MR-37", 0.0060, (-W_REC / 2 - 0.0002, -0.034, 0.048), mat="steel", **hw.LEFT))
g.f(hw.text("mk_unit", "모나티엄 진압반", 0.0050, (-W_REC / 2 - 0.0002, 0.012, 0.030), mat="steel", **hw.LEFT))

# ================================================================== 총열 (굵은 관) · 청록 띠 · 금색 나팔 총구
g.s(hw.tube("barrel", R_BAR, 0.0190, 0.070, 0.308, c=(0, BZ), verts=32, mat="metal"))
g.s(hw.ycyl("barrel_collar", R_BAR + 0.0025, 0.068, 0.084, z=BZ, verts=32, bevel=0.0015, mat="metal"))
# 총열 위 방열 덮개의 스타디움 창 (양쪽) — 원작 엘프 화기의 긴 원형 창
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    for i, y in enumerate((0.180, 0.212, 0.244)):
        g.f(hw.decal(f"bar_win{sx}{i}", hw.stadium(0.022, 0.0082, 5), (sx * (R_BAR + 0.0003), y, BZ + 0.004),
                     mat="dark", **fr))
g.s(hw.tube("band_teal", R_BAR + 0.0016, 0.0190, 0.268, 0.290, c=(0, BZ), verts=32, mat="teal"))
g.s(hw.ycyl("bore_back", 0.0192, 0.086, 0.092, z=BZ, verts=24, mat="dark"))   # 총열 안쪽 끝 (깊이감)
g.f(hw.text("mk_less", "비살상 진압탄 전용", 0.0050, (-(R_BAR + 0.0018), 0.279, BZ), mat="violet_d",
            right=(0, -1, 0), up=(0, 0, 1)))
g.s(hw.tube("muzzle_bell", R_BAR + 0.0015, 0.0192, 0.290, 0.318, c=(0, BZ), verts=32, r_out2=R_BAR + 0.0048,
            r_in2=0.0205, mat="gold"))
g.s(hw.tube("muzzle_lip", R_BAR + 0.0060, 0.0205, 0.316, 0.322, c=(0, BZ), verts=32, mat="gold"))

# ================================================================== 관형 탄창 (총열 아래)
g.s(hw.ycyl("mag_tube", R_TUBE, 0.070, 0.292, z=TZ, verts=28, mat="dark"))
g.s(hw.ycyl("tube_cap", R_TUBE + 0.0022, 0.288, 0.300, z=TZ, verts=28, bevel=0.0018, mat="metal"))
g.s(hw.ycyl("tube_cap_teal", R_TUBE - 0.006, 0.299, 0.302, z=TZ, verts=20, mat="teal"))
# 총열-탄창 고정 고리
g.s(hw.side("barrel_clamp", hw.rrect(0.014, BZ - TZ + R_BAR + R_TUBE + 0.006, 0.012, 3, cx=0.274,
                                     cy=(BZ + TZ) / 2 + (R_BAR - R_TUBE) / 2), 0.050, bevel=0.0028, seg=2,
            mat="metal"))

# ================================================================== 손잡이 · D자 방아쇠울 · 방아쇠 · 안전장치
grip = hw.side("grip", hw.rrect(0.030, 0.082, 0.012, n=3, cy=-0.022), 0.026, bevel=0.0045, seg=2, mat="dark")
hw.xform(grip, rot=(-15, 0, 0), pivot=(0, 0, 0.006))
g.s(grip)
for sx in (-1, 1):
    p = hw.side(f"grip_panel{sx}", hw.rrect(0.020, 0.054, 0.008, n=2, cy=-0.022), 0.003, x=sx * 0.0133,
                bevel=0.0010, seg=1, mat="violet_d")
    hw.xform(p, rot=(-15, 0, 0), pivot=(0, 0, 0.006))
    g.s(p)
loop_path = [(-0.016, -0.062), (0.040, -0.062)] + hw.arc_pts(0.040, -0.040, 0.022, 270, 360, 5)[1:] + \
    [(0.062, -0.006), (0.064, 0.008)]
g.s(hw.side("d_loop", hw.strip(loop_path, 0.0090), 0.016, bevel=0.0030, seg=2, mat="violet"))
TRIG = (0, 0.026, 0.004)
trig = hw.side("trigger_blade", [(-0.0024, 0.0), (0.0032, 0.0), (0.0042, -0.011), (0.0078, -0.022),
                                 (0.0044, -0.027), (-0.0010, -0.024), (-0.0022, -0.011)], 0.0065, bevel=0.0013, seg=2,
               mat="steel")
trig.location = TRIG
g.p("trigger", trig)
g.pivot("trigger", TRIG, rotAxis="x", rotDeg=-14)
SAF = (0, 0.050, 0.010)
g.p("safety", hw.xcyl("safety_bolt", 0.0034, -0.0105, 0.0105, y=SAF[1], z=SAF[2], verts=12, mat="dark"),
    hw.xcyl("safety_red", 0.0036, -0.0115, -0.0095, y=SAF[1], z=SAF[2], verts=12, mat="teal"))
g.pivot("safety", SAF, move=hw.mv(0.004, 0, 0), note="crossbolt: +x = fire")

# ================================================================== 개머리 (짧게) + 패드 + 구멍 줄
st_side = [(-0.054, 0.012), (-0.054, 0.096), (-0.150, 0.090), (-0.196, 0.092), (-0.202, 0.084), (-0.202, -0.004),
           (-0.194, -0.012), (-0.150, 0.002), (-0.090, 0.004)]
g.s(hw.sculpt("stock", st_side, hw.rrect(0.040, 0.120, 0.014, n=3, cy=0.042), bevel=0.003, seg=2, mat="violet"))
g.s(hw.side("butt_pad", [(-0.211, -0.006), (-0.201, -0.012), (-0.201, 0.093), (-0.211, 0.087)], 0.042,
            bevel=0.0035, seg=2, mat="dark"))
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    if sx > 0:   # 왼쪽 면은 탄띠가 덮는다
        g.f(*hw.holes(f"st_hole{sx}", (sx * 0.0201, -0.135, 0.042), 3, 0.016, 0.0055, along=(1, 0), mat="dark",
                      n=12, **fr))
    g.f(hw.decal(f"st_band{sx}", hw.rrect(0.008, 0.086, 0.002, 1), (sx * 0.0201, -0.178, 0.040), mat="teal", **fr))
g.s(hw.torus("sling_rear", 0.0065, 0.0015, loc=(0, -0.180, -0.008), rot=(0, 90, 0), seg=14, rseg=6, mat="steel"))

# ================================================================== 가늠자 (고리, 뒤) + 가늠쇠 (앞, 시안 점)
REAR_Y = -0.040
g.s(hw.tube("ring_sight", 0.0112, 0.0080, REAR_Y - 0.0024, REAR_Y + 0.0024, c=(0, SZ), verts=24, mat="dark"))
g.s(hw.side("ring_post", [(REAR_Y - 0.012, 0.105), (REAR_Y + 0.012, 0.105), (REAR_Y + 0.004, SZ - 0.010),
                          (REAR_Y - 0.004, SZ - 0.010)], 0.009, bevel=0.0020, seg=2, mat="dark"))
FRONT_Y = 0.300
g.s(hw.side("front_post", [(FRONT_Y - 0.004, BZ + R_BAR - 0.002), (FRONT_Y + 0.004, BZ + R_BAR - 0.002),
                           (FRONT_Y + 0.0022, SZ), (FRONT_Y - 0.0022, SZ)], 0.0036, bevel=0.0006, seg=1, mat="dark"))
g.f(hw.decal("front_dot", hw.circle(0.0013, 10), (0, FRONT_Y - 0.0024, SZ - 0.0022), mat="glow", **hw.BACK))
fe = [(FRONT_Y - 0.009, BZ + R_BAR - 0.002)] + hw.arc_pts(FRONT_Y, SZ - 0.012, 0.009, 180, 0, 6) + \
    [(FRONT_Y + 0.009, BZ + R_BAR - 0.002)]
for sx in (-1, 1):
    g.s(hw.side(f"post_ear{sx}", hw.strip(fe, 0.0036), 0.0032, x=sx * 0.0095, bevel=0.0008, seg=1, mat="metal"))

# ================================================================== 펌프 + 사각 고리 손잡이 (칸나 발사기의 고리 손잡이)
PUMP_Y0, PUMP_Y1 = 0.150, 0.250
pump = [hw.ycyl("pump_sleeve", R_TUBE + 0.0055, PUMP_Y0, PUMP_Y1, z=TZ, verts=28, bevel=0.0028, mat="violet")]
for i in range(5):
    pump.append(hw.ycyl(f"pump_rib{i}", R_TUBE + 0.0068, PUMP_Y0 + 0.020 + i * 0.015, PUMP_Y0 + 0.025 + i * 0.015,
                        z=TZ, verts=28, mat="violet_d"))
handle = [(0.168, 0.010), (0.168, -0.030)] + hw.arc_pts(0.180, -0.030, 0.012, 180, 270, 3)[1:] + \
    [(0.222, -0.042)] + hw.arc_pts(0.222, -0.030, 0.012, 270, 360, 3)[1:] + [(0.234, 0.010)]
pump.append(hw.side("pump_loop", hw.strip(handle, 0.0105), 0.018, bevel=0.0035, seg=2, mat="dark"))
pump.append(hw.boxr("pump_loop_teal", -0.0095, 0.0095, 0.186, 0.216, -0.0485, -0.0405, bevel=0.0028, mat="teal"))
g.p("pump", *pump)
g.pivot("pump", (0, PUMP_Y0, TZ), move=hw.mv(0, -0.065, 0))
g.anchor("grip_support", (0, 0.174, -0.012), parent="pump")
# 펌프 막대 (리시버까지)
g.s(hw.boxr("action_bar", -0.0230, -0.0190, 0.072, 0.152, TZ - 0.003, TZ + 0.003, bevel=0.0010, mat="dark"))
# 노리쇠 (배출구 안, 펌프와 함께)
g.p("bolt", hw.boxr("bolt_face", W_REC / 2 - 0.006, W_REC / 2 + 0.0004, 0.004, 0.040, 0.058, 0.082, bevel=0.0020,
                    mat="steel"))
g.pivot("bolt", (W_REC / 2, 0.022, 0.070), move=hw.mv(0, -0.065, 0), note="moves with pump")

# ================================================================== 개머리 왼쪽 탄띠: 고무 충격탄 2발 (1인칭 오른쪽 아래에서 보임)
STX = -0.0200                     # 개머리 왼쪽 면
SX = STX - 0.0030 - 0.0180
for k, z in enumerate((0.064, 0.025)):
    g.s(hw.ycyl(f"shell_case{k}", 0.0180, -0.160, -0.100, x=SX, z=z, verts=22, bevel=0.0012, mat="gold"))
    g.s(hw.ycyl(f"shell_rim{k}", 0.0192, -0.164, -0.158, x=SX, z=z, verts=22, bevel=0.0008, mat="gold"))
    nose = cb.sphere(f"shell_nose{k}", radius=0.0172, loc=(SX, -0.100, z), scale=(1, 1.35, 1), segments=20, rings=10,
                     material=hw.M("teal"))
    g.s(nose)
    g.f(hw.decal(f"shell_primer{k}", hw.circle(0.0045, 12), (SX, -0.1642, z), mat="steel", **hw.BACK))
for i, y in enumerate((-0.146, -0.116)):
    g.s(hw.side(f"saddle_strap{i}", hw.rrect(0.010, 0.082, 0.004, 2, cx=y, cy=0.0445), 0.043, x=SX + 0.0010,
                bevel=0.0020, seg=2, mat="dark"))
g.s(hw.side("saddle_plate", hw.rrect(0.060, 0.082, 0.008, 2, cx=-0.130, cy=0.0445), 0.004, x=STX - 0.0015,
            bevel=0.0012, seg=1, mat="dark"))

# ================================================================== 앵커
g.anchor("muzzle", (0, 0.322, BZ))
g.anchor("sight_eye", (0, -0.120, SZ))
g.anchor("eject", (W_REC / 2 + 0.010, 0.022, 0.070))
g.anchor("mag_well", (0, 0.035, 0.004))

g.finish("weapons/monatium/monatium_riot_launcher.glb", outline=0.002, fp="0.15,-0.205,-0.35", fprot="0,6,0")
