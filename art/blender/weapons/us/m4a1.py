"""M4A1 카빈 (노획 미군 화기, 주무기).

npm run model -- art/blender/weapons/us/m4a1.py
npm run shot -- weapons/us/m4a1.glb --views side,34,top,muzzle
npm run shot -- weapons/us/m4a1.glb --mode fp

원점 = 권총 손잡이 중앙(오른손), 총구 +Y, 위 +Z. 실측 기준(총열 14.5", 개머리판 최대로 접은 상태 OAL ≈ 0.76 m).
엘프는 팔이 짧아 개머리판을 끝까지 접어 쓴다.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402

cb.reset()
b = us.Build("m4a1")

ZB = 0.092            # 총열 축 높이 (손잡이 중앙 기준)
RAIL_TOP = ZB + 0.027  # 리시버 레일 장착면
GA = math.radians(22)  # 손잡이 기울기


def gp(t, s):
    """손잡이 로컬 (t=앞, s=손잡이 축 위쪽) → (y, z)"""
    return (t * math.cos(GA) + s * math.sin(GA), -t * math.sin(GA) + s * math.cos(GA))


# ================================================================== lower receiver
lower = us.side("lower", [
    (-0.060, ZB - 0.004), (-0.060, ZB - 0.020), (-0.054, ZB - 0.031), (-0.043, ZB - 0.039),
    (-0.028, ZB - 0.044), (0.090, ZB - 0.044), (0.090, ZB - 0.040), (0.166, ZB - 0.040),
    (0.172, ZB - 0.032), (0.178, ZB - 0.022), (0.178, ZB - 0.004),
], 0.025, bevel=0.0018, mat="black")
b.s(lower)
# 탄창 삽입구 (아래로 벌어진 입구)
magwell = us.side("magwell", [
    (0.086, ZB - 0.036), (0.086, ZB - 0.070), (0.081, ZB - 0.081), (0.165, ZB - 0.081),
    (0.163, ZB - 0.070), (0.162, ZB - 0.036),
], 0.031, bevel=0.0022, mat="black")
b.s(magwell)
# 탄창 멈치 둘레 펜스 (오른쪽)
b.s(us.side("magrel_fence", [(0.068, ZB - 0.033), (0.086, ZB - 0.033), (0.086, ZB - 0.008),
                              (0.080, ZB - 0.008), (0.080, ZB - 0.016), (0.068, ZB - 0.024)],
            0.004, x=0.0135, bevel=0.0008, mat="black"))
b.s(us.xcyl("magrel_btn", 0.0042, 0.012, 0.0158, y=0.074, z=ZB - 0.021, verts=10, mat="steel"))
# 노리쇠 멈치 (왼쪽)
b.s(us.side("bolt_catch", [(0.068, ZB - 0.034), (0.080, ZB - 0.034), (0.082, ZB - 0.012),
                            (0.076, ZB - 0.006), (0.070, ZB - 0.010)], 0.003, x=-0.014, bevel=0.0007,
            mat="black"))
# 방아쇠울
tg = us.strip([(0.026, ZB - 0.040), (0.028, ZB - 0.060), (0.038, ZB - 0.067), (0.078, ZB - 0.067),
               (0.088, ZB - 0.058), (0.090, ZB - 0.042)], 0.0045)
b.s(us.side("trigger_guard", tg, 0.014, bevel=0.0012, seg=1, mat="black"))

# ================================================================== pistol grip
g = [(0.017, 0.064), (0.018, 0.036), (0.024, 0.016), (0.023, 0.006), (0.017, -0.004), (0.019, -0.030),
     (0.016, -0.050), (0.010, -0.058), (-0.014, -0.060), (-0.021, -0.052), (-0.023, -0.020),
     (-0.022, 0.030), (-0.026, 0.052), (-0.030, 0.060), (-0.026, 0.066)]
grip = us.side("grip", [gp(t, s) for (t, s) in g], 0.027, bevel=0.0085, seg=2, mat="black")
b.s(grip)
# 손잡이 옆 미끄럼 방지 홈 (양쪽)
for sx in (-1, 1):
    for i in range(4):
        s = -0.040 + i * 0.016
        y0, z0 = gp(-0.012, s)
        y1, z1 = gp(0.010, s)
        o = us.box(f"grip_rib{i}_{sx}", (0.0016, math.hypot(y1 - y0, z1 - z0), 0.0028),
                   (sx * 0.0137, (y0 + y1) / 2, (z0 + z1) / 2), rot=(-22 + 0, 0, 0), mat="black")
        o.rotation_euler = (-GA, 0, 0)
        b.s(o)

# ================================================================== upper receiver
up_sec = [(-0.0128, ZB - 0.004), (0.0128, ZB - 0.004), (0.0128, ZB + 0.018), (0.0098, ZB + 0.027),
          (-0.0098, ZB + 0.027), (-0.0128, ZB + 0.018)]
upper = us.section("upper", up_sec, -0.058, 0.180, bevel=0.0012, mat="black")
port_cut = us.boxr("port_cut", 0.0095, 0.03, 0.036, 0.097, ZB - 0.002, ZB + 0.016)
us.cut(upper, port_cut)
b.s(upper)
# 배출구 안쪽 (어두운 면)
b.s(us.boxr("port_back", 0.0085, 0.0096, 0.036, 0.097, ZB - 0.002, ZB + 0.016, mat="black"))
b.s(us.rail("rail_upper", -0.056, 0.178, origin=(0, RAIL_TOP), up="+z"))
# 장전손잡이 홈 뒤 마감
b.s(us.boxr("upper_rear", -0.0125, 0.0125, -0.061, -0.056, ZB - 0.004, ZB + 0.012, bevel=0.001, mat="black"))
# 전진 보조기 (오른쪽 뒤)
b.s(us.ycyl("fa_housing", 0.0072, -0.040, 0.016, x=0.0150, z=ZB + 0.010, verts=16, r2=0.0058, mat="black"))
b.s(us.boxr("fa_fair", 0.010, 0.016, -0.040, 0.010, ZB + 0.002, ZB + 0.016, bevel=0.002, mat="black"))
b.s(us.ycyl("fa_button", 0.0066, -0.050, -0.040, x=0.0150, z=ZB + 0.010, verts=12, bevel=0.0012, seg=1,
            mat="black"))
# 탄피 디플렉터 (배출구 뒤 혹)
b.s(us.side("deflector", [(0.016, ZB - 0.002), (0.034, ZB - 0.002), (0.034, ZB + 0.022), (0.028, ZB + 0.024)],
            0.006, x=0.0145, bevel=0.0015, mat="black"))
# 왼쪽 위 탄피받이 홈 없음. 노리쇠 멈치 위 '전진 보조기' 반대편 덩어리
# 버퍼튜브 + 캐슬너트 + 엔드플레이트
b.s(us.ycyl("buffer_tube", 0.0145, -0.150, -0.058, z=ZB + 0.003, verts=16, mat="steel"))
b.s(us.ycyl("castle_nut", 0.0172, -0.066, -0.059, z=ZB + 0.003, verts=12, mat="steel"))
b.s(us.side("end_plate", [(-0.0595, ZB - 0.030), (-0.0565, ZB - 0.030), (-0.0565, ZB + 0.024),
                          (-0.0595, ZB + 0.024)], 0.027, bevel=0.0006, mat="steel"))
# 엔드플레이트 슬링 고리 (왼쪽)
b.s(us.torus("rear_sling_loop", 0.0055, 0.0013, loc=(-0.0175, -0.058, ZB - 0.020), rot=(0, 90, 0), seg=10,
             rseg=5, mat="steel"))

# ================================================================== stock (collapsed)
# 튜브 하우징 (위, 전폭) + 웹 (아래, 좁음) + 개머리 뒤 (전폭) → 계단형 옆면
b.s(us.side("stock_tube", [(-0.084, ZB + 0.019), (-0.150, ZB + 0.0215), (-0.192, ZB + 0.025),
                           (-0.192, ZB - 0.016), (-0.084, ZB - 0.019)], 0.033, bevel=0.0075, seg=2, mat="coyote"))
b.s(us.side("stock_web", [(-0.096, ZB - 0.010), (-0.192, ZB - 0.010), (-0.192, ZB - 0.080),
                          (-0.182, ZB - 0.080), (-0.150, ZB - 0.052), (-0.118, ZB - 0.031),
                          (-0.096, ZB - 0.024)], 0.021, bevel=0.004, seg=2, mat="coyote"))
b.s(us.side("stock_butt", [(-0.188, ZB + 0.024), (-0.207, ZB + 0.025), (-0.207, ZB - 0.078),
                           (-0.199, ZB - 0.085), (-0.180, ZB - 0.085), (-0.188, ZB - 0.070)],
            0.035, bevel=0.006, seg=2, mat="coyote"))
# 슬링 구멍 (웹 아래쪽 앞)
b.s(us.xcyl("stock_sling_slot", 0.0045, -0.0108, 0.0108, y=-0.168, z=ZB - 0.060, verts=10, mat="black"))
b.s(us.side("butt_pad", [(-0.219, ZB + 0.022), (-0.206, ZB + 0.024), (-0.206, ZB - 0.084),
                          (-0.219, ZB - 0.084), (-0.222, ZB - 0.074), (-0.222, ZB + 0.012)],
            0.037, bevel=0.004, seg=2, mat="black"))
# 개머리판 잠금 레버 (아래)
b.s(us.side("stock_lever", [(-0.098, ZB - 0.024), (-0.086, ZB - 0.024), (-0.088, ZB - 0.032),
                            (-0.120, ZB - 0.036), (-0.118, ZB - 0.030)], 0.012, bevel=0.0015, mat="black"))
# QD 소켓 (양쪽)
for sx in (-1, 1):
    b.s(us.xcyl(f"stock_qd{sx}", 0.0055, sx * 0.0162, sx * 0.0178, y=-0.105, z=ZB + 0.004, verts=10,
                mat="black"))

# ================================================================== handguard (quad rail)
H = 0.0265
C = 0.0095
hg_sec = [(-H + C, ZB - H), (H - C, ZB - H), (H, ZB - H + C), (H, ZB + H - C), (H - C, ZB + H),
          (-H + C, ZB + H), (-H, ZB + H - C), (-H, ZB - H + C)]
b.s(us.section("handguard", hg_sec, 0.186, 0.398, bevel=0.0012, seg=1, mat="black"))
b.s(us.ycyl("barrel_nut", 0.0225, 0.178, 0.188, z=ZB, verts=16, bevel=0.0012, seg=1, mat="black"))
b.s(us.section("hg_cap", [(x * 1.06, ZB + (z - ZB) * 1.06) for (x, z) in hg_sec], 0.393, 0.402,
               bevel=0.0012, seg=1, mat="black"))
b.s(us.rail("rail_top", 0.190, 0.396, origin=(0, ZB + H), up="+z"))
b.s(us.rail("rail_bot", 0.190, 0.396, origin=(0, ZB - H), up="-z"))
b.s(us.rail("rail_R", 0.190, 0.302, origin=(H, ZB), up="+x"))
b.s(us.rail("rail_L", 0.190, 0.302, origin=(-H, ZB), up="-x"))
# 레일 커버 (코요테 사다리형) 양 옆 앞쪽
for sx in (-1, 1):
    x0 = sx * H
    b.s(us.boxr(f"rcover{sx}", min(x0, x0 + sx * 0.0112), max(x0, x0 + sx * 0.0112), 0.300, 0.392,
                ZB - 0.0125, ZB + 0.0125, bevel=0.0025, mat="coyote"))
    for i in range(8):
        y = 0.306 + i * 0.0113
        b.s(us.boxr(f"rcover_rib{sx}{i}", min(x0 + sx * 0.0108, x0 + sx * 0.0128),
                    max(x0 + sx * 0.0108, x0 + sx * 0.0128), y, y + 0.0042, ZB - 0.0105, ZB + 0.0105,
                    mat="coyote"))
# 핸드가드 고정 나사 (양 옆 뒤쪽)
for sx in (-1, 1):
    for y in (0.194, 0.388):
        for sz in (-1, 1):
            b.f(us.xcyl(f"hg_screw{sx}{y}{sz}", 0.0018, sx * (H - 0.0004), sx * (H + 0.0006), y=y,
                        z=ZB + sz * 0.0155, verts=8, mat="bright"))

# 손 테이프 (OD) - 왼손 자리 뒤 · 앞
tape_sec = us.rrect(0.0735, 0.0735, 0.011, n=2, cy=ZB)
b.s(us.section("tape", tape_sec, 0.252, 0.278, bevel=0.001, seg=1, mat="od"))

# ================================================================== barrel, FSB, muzzle
b.s(us.ycyl("barrel", 0.0098, 0.396, 0.442, z=ZB, verts=16, mat="steel"))
b.s(us.ycyl("barrel_m203", 0.0084, 0.442, 0.447, z=ZB, verts=16, mat="steel"))
b.s(us.ycyl("barrel_fwd", 0.0090, 0.447, 0.486, z=ZB, verts=16, mat="steel"))
# 가늠쇠 뭉치 (A-프레임)
b.s(us.ycyl("fsb_ring", 0.0150, 0.404, 0.430, z=ZB, verts=16, bevel=0.0015, seg=1, mat="black"))
b.s(us.side("fsb_tower", [(0.398, ZB + 0.010), (0.430, ZB + 0.010), (0.428, ZB + 0.050), (0.425, ZB + 0.053),
                          (0.416, ZB + 0.053), (0.411, ZB + 0.046)], 0.011, bevel=0.0018, mat="black"))
for sx in (-1, 1):
    b.s(us.side(f"fsb_ear{sx}", [(0.413, ZB + 0.044), (0.428, ZB + 0.044), (0.428, ZB + 0.067),
                                 (0.4235, ZB + 0.069), (0.418, ZB + 0.066)], 0.0032, x=sx * 0.0082,
                bevel=0.0009, mat="black"))
b.s(us.boxr("fsb_post", -0.0018, 0.0018, 0.419, 0.4225, ZB + 0.050, ZB + 0.064, bevel=0.0005, mat="black"))
# 가늠쇠 축광 점 대신 밝은 끝
b.f(us.boxr("fsb_post_tip", -0.0012, 0.0012, 0.4188, 0.4192, ZB + 0.060, ZB + 0.0635, mat="bright"))
# 착검 돌기 + 슬링 고리
b.s(us.boxr("bayonet_lug", -0.0042, 0.0042, 0.418, 0.442, ZB - 0.026, ZB - 0.012, bevel=0.0012, mat="black"))
b.s(us.side("fsb_swivel_tab", [(0.404, ZB - 0.012), (0.418, ZB - 0.012), (0.416, ZB - 0.030),
                               (0.408, ZB - 0.030)], 0.006, bevel=0.0012, mat="black"))
b.s(us.torus("fsb_swivel", 0.0075, 0.0014, loc=(0, 0.412, ZB - 0.035), rot=(0, 90, 0), seg=12, rseg=5,
             mat="steel"))
# 핀 (가늠쇠 뭉치 테이퍼 핀)
for y in (0.408, 0.426):
    b.f(us.xcyl(f"fsb_pin{y}", 0.0017, -0.0152, 0.0152, y=y, z=ZB - 0.006, verts=8, mat="bright"))
# A2 소염기 (새장형, 바닥은 막힘)
fh = us.ytube("flash_hider", 0.0112, 0.0062, 0.483, 0.540, z=ZB, verts=12, mat="steel")
slots = None
for i, a in enumerate((90, 30, 150, -30, 210)):
    ar = math.radians(a)
    c = us.box(f"fh_slot{i}", (0.0035, 0.034, 0.012), (0.011 * math.cos(ar), 0.517, ZB + 0.011 * math.sin(ar)),
               rot=(0, 90 - a, 0))
    slots = c if slots is None else cb.join([slots, c], "fh_cut")
us.cut(fh, slots)
cb.add_bevel(fh, 0.0008, 1)
b.s(fh)
b.s(us.ycyl("fh_collar", 0.0118, 0.483, 0.492, z=ZB, verts=16, mat="steel"))

# ================================================================== rear BUIS (접힘)
b.s(us.boxr("buis_base", -0.0125, 0.0125, -0.034, -0.006, RAIL_TOP + 0.004, RAIL_TOP + 0.0145,
            bevel=0.0015, mat="black"))
b.s(us.boxr("buis_leaf", -0.0095, 0.0095, -0.030, -0.006, RAIL_TOP + 0.0145, RAIL_TOP + 0.019,
            bevel=0.0012, mat="black"))
b.s(us.xcyl("buis_knob", 0.0052, 0.0125, 0.0175, y=-0.020, z=RAIL_TOP + 0.010, verts=12, bevel=0.0008,
            seg=1, mat="black"))
for sx in (-1, 1):
    b.s(us.boxr(f"buis_jaw{sx}", sx * 0.0105 - 0.002, sx * 0.0105 + 0.002, -0.032, -0.008, RAIL_TOP + 0.001,
                RAIL_TOP + 0.007, bevel=0.0008, mat="black"))

# ================================================================== holographic sight
O_Y0, O_Y1 = 0.064, 0.150
OPT = ZB + 0.073   # 광축 높이
b.s(us.boxr("holo_base", -0.0175, 0.0175, O_Y0 + 0.004, O_Y1 - 0.004, RAIL_TOP + 0.0085, RAIL_TOP + 0.019,
            bevel=0.002, mat="black"))
for sx in (-1, 1):
    b.s(us.boxr(f"holo_jaw{sx}", sx * 0.0125 - 0.0025, sx * 0.0125 + 0.0025, O_Y0 + 0.022, O_Y1 - 0.020,
                RAIL_TOP + 0.001, RAIL_TOP + 0.012, bevel=0.001, mat="black"))
b.s(us.xcyl("holo_thumbnut", 0.0068, -0.0230, -0.0150, y=0.106, z=RAIL_TOP + 0.007, verts=12, bevel=0.0012,
            seg=1, mat="black"))
b.s(us.boxr("holo_body", -0.0215, 0.0215, O_Y0, O_Y1, RAIL_TOP + 0.017, OPT - 0.015, bevel=0.0035, seg=2,
            mat="black"))
# 배터리 칸 (앞쪽 가로)
b.s(us.xcyl("holo_batt", 0.0090, -0.0235, 0.0235, y=O_Y1 - 0.011, z=RAIL_TOP + 0.026, verts=16, bevel=0.0015,
            seg=1, mat="black"))
b.s(us.xcyl("holo_batt_cap", 0.0078, 0.0235, 0.0265, y=O_Y1 - 0.011, z=RAIL_TOP + 0.026, verts=16,
            bevel=0.0009, seg=1, mat="black"))
# 버튼 (왼쪽, 고무)
for i, y in enumerate((0.082, 0.095)):
    b.s(us.xcyl(f"holo_btn{i}", 0.0034, -0.0235, -0.0205, y=y, z=RAIL_TOP + 0.026, verts=10, mat="steel"))
# 후드 (창틀): 아치형 U 단면
hood = [(-0.0225, OPT - 0.016), (-0.0225, OPT + 0.011), (-0.0165, OPT + 0.019), (0.0165, OPT + 0.019),
        (0.0225, OPT + 0.011), (0.0225, OPT - 0.016), (0.0175, OPT - 0.016), (0.0175, OPT + 0.009),
        (0.0130, OPT + 0.0145), (-0.0130, OPT + 0.0145), (-0.0175, OPT + 0.009), (-0.0175, OPT - 0.016)]
b.s(us.section("holo_hood", hood, O_Y0 + 0.010, O_Y1 - 0.024, bevel=0.0014, seg=2, mat="black"))
# 창 테두리 (뒤, 앞)
for (y0, y1) in ((O_Y0 + 0.010, O_Y0 + 0.014), (O_Y1 - 0.028, O_Y1 - 0.024)):
    b.s(us.section(f"holo_rim{y0}", [(-0.0175, OPT - 0.016), (-0.0165, OPT - 0.016), (-0.0165, OPT + 0.0085),
                                      (-0.0125, OPT + 0.0135), (0.0125, OPT + 0.0135), (0.0165, OPT + 0.0085),
                                      (0.0165, OPT - 0.016), (0.0175, OPT - 0.016), (0.0175, OPT + 0.009),
                                      (0.0130, OPT + 0.0145), (-0.0130, OPT + 0.0145), (-0.0175, OPT + 0.009)],
                      y0, y1, mat="steel"))
# 레티클 (65MOA 링 + 점), 앞 유리면
RET_Y = O_Y1 - 0.026
b.f(us.torus("reticle_ring", 0.0034, 0.00038, loc=(0, RET_Y, OPT), rot=(90, 0, 0), seg=20, rseg=3,
             mat="reticle"))
b.f(cb.sphere("reticle_dot", radius=0.0006, loc=(0, RET_Y, OPT), segments=8, rings=4, material=us.M("reticle")))

# ================================================================== decals / fine detail
# 핀 (분해 핀, 피벗 핀, 방아쇠/공이치기 핀) 양쪽
for (y, z, r) in ((-0.047, ZB - 0.011, 0.0028), (0.171, ZB - 0.013, 0.0028), (0.052, ZB - 0.031, 0.0021),
                  (0.034, ZB - 0.022, 0.0021)):
    b.f(us.xcyl(f"pin{y}", r, -0.0130, 0.0130, y=y, z=z, verts=10, mat="bright"))
# 왼쪽 탄창 삽입구 각인
L_ = dict(right=(0, -1, 0), up=(0, 0, 1))
R_ = dict(right=(0, 1, 0), up=(0, 0, 1))
mx = -0.0156
b.f(us.text("mk_prop", "PROPERTY OF U.S. GOVT", 0.0056, (mx, 0.124, ZB - 0.050), mat="bright", **L_))
b.f(us.text("mk_model", "M4A1  CAL 5.56 MM", 0.0056, (mx, 0.124, ZB - 0.060), mat="bright", **L_))
# 조정간 표시 (왼쪽)
lx = -0.0126
b.f(us.text("mk_safe", "SAFE", 0.0034, (lx, 0.026, ZB - 0.026), mat="paper", **L_))
b.f(us.text("mk_semi", "SEMI", 0.0034, (lx, 0.003, ZB - 0.0095), mat="paper", **L_))
b.f(us.text("mk_auto", "AUTO", 0.0034, (lx, -0.020, ZB - 0.026), mat="paper", **L_))
# 레일 번호 (윗레일, 몇 개만)
for i, y in enumerate((0.008, 0.028, 0.048)):
    pass

# 모나티엄 창고 스티커 (개머리판 왼쪽)
sx_ = -0.0183
b.f(us.boxr("sticker", sx_ - 0.0002, sx_, -0.178, -0.130, ZB - 0.010, ZB + 0.012, mat="paper"))
b.f(us.boxr("sticker_band", sx_ - 0.0004, sx_ - 0.0002, -0.178, -0.130, ZB + 0.006, ZB + 0.012, mat="paint"))
b.f(us.text("st_t1", "MNT ARMORY", 0.0050, (sx_ - 0.0002, -0.154, ZB + 0.0005), mat="black", **L_))
b.f(us.text("st_t2", "NO. 07-0412", 0.0040, (sx_ - 0.0002, -0.154, ZB - 0.0060), mat="black", **L_))
b.f(us.text("st_kr", "진압반 병기고", 0.0034, (sx_ - 0.0004, -0.154, ZB + 0.0090), mat="paper", font="kr", **L_))

# 가늠쇠 슬링 고리에 매단 창고 태그
tag_top = (0.0, 0.412, ZB - 0.0425)
hole = (0.0, 0.414, ZB - 0.060)
b.s(us.sweep("tag_cord", [tag_top, (0.0004, 0.4135, ZB - 0.050), hole], us.circle_pts(0.0007, 6),
             side_vec=(1, 0, 0), mat="paint"))
TAG_W, TAG_H = 0.024, 0.038
tag_c = (0.0, 0.414, ZB - 0.060 - TAG_H / 2 + 0.004)
tag_pts = [(-TAG_W / 2, -TAG_H / 2), (TAG_W / 2, -TAG_H / 2), (TAG_W / 2, TAG_H / 2 - 0.006),
           (TAG_W / 2 - 0.006, TAG_H / 2), (-TAG_W / 2 + 0.006, TAG_H / 2), (-TAG_W / 2, TAG_H / 2 - 0.006)]
tag = us.side("tag", [(tag_c[1] + u, tag_c[2] + v) for (u, v) in tag_pts], 0.0009, mat="paper")
b.s(tag)
b.f(us.xcyl("tag_eyelet", 0.0026, -0.0006, 0.0006, y=hole[1], z=hole[2] - 0.0005, verts=12, mat="paint"))
for sx, kw in ((-1, L_), (1, R_)):
    xx = sx * 0.00046
    b.f(us.boxr(f"tag_band{sx}", min(xx, xx + sx * 0.0002), max(xx, xx + sx * 0.0002), tag_c[1] - TAG_W / 2,
                tag_c[1] + TAG_W / 2, tag_c[2] - 0.004, tag_c[2] + 0.002, mat="paint"))
    b.f(us.text(f"tag_t1{sx}", "MNT", 0.0085, (xx, tag_c[1], tag_c[2] + 0.0075), mat="black", **kw))
    b.f(us.text(f"tag_t2{sx}", "07-0412", 0.0042, (xx + sx * 0.0002, tag_c[1], tag_c[2] - 0.001), mat="paper",
                **kw))
    b.f(us.text(f"tag_kr{sx}", "모나티엄 창고", 0.0034, (xx, tag_c[1], tag_c[2] - 0.0095), mat="black", font="kr",
                **kw))
# 태그를 살짝 돌려 1인칭(왼쪽 뒤)에서 보이게
# (정지 파츠에 합치기 전에 회전)
for o in [tag] + [o for o in b.fine if o.name.startswith("tag_")]:
    us.xform(o, rot=(0, 0, -35), pivot=hole)
us.xform(b.static[-2], rot=(0, 0, -35), pivot=hole)  # cord

# ================================================================== moving parts
# 탄창 (코요테 폴리머, 30발)
MAG_Y = 0.124
mag_top = ZB - 0.030
path = [(0, MAG_Y, mag_top - 0.0 * i) for i in range(1)]
path = []
for i in range(5):
    path.append((0, MAG_Y, mag_top - i * 0.016))
R_m = 0.38
z0 = mag_top - 0.064
for i in range(1, 9):
    th = (0.128 / R_m) * i / 8
    path.append((0, MAG_Y + R_m * (1 - math.cos(th)), z0 - R_m * math.sin(th)))
mag_sec = us.rrect(0.0235, 0.063, 0.0045, n=2)
b.p("mag", us.sweep("mag_body", path, mag_sec, mat="coyote", smooth=50))
# 옆 리브 (양쪽 2줄)
for sx in (-1, 1):
    for v in (-0.014, 0.012):
        rib = [(sx * 0.0108, v - 0.0024), (sx * 0.0128, v - 0.0020), (sx * 0.0128, v + 0.0020),
               (sx * 0.0108, v + 0.0024)]
        rp = path[3:-1]
        sc = [(0.85, 1.0)] + [(1.0, 1.0)] * (len(rp) - 2) + [(0.85, 1.0)]
        b.p("mag", us.sweep(f"mag_rib{sx}{v}", rp, rib, mat="coyote", smooth=50, scales=sc))
th_end = 0.128 / R_m
end = path[-1]
tdir = (math.sin(th_end), -math.cos(th_end))
fp_c = (0, end[1] + tdir[0] * 0.003, end[2] + tdir[1] * 0.003)
b.p("mag", us.box("mag_floor", (0.0285, 0.071, 0.009), fp_c, rot=(math.degrees(th_end), 0, 0), bevel=0.0025,
                  mat="paint"))
# 맨 위 탄 (탄창을 뺐을 때 보임)
b.p("mag", us.ycyl("mag_round", 0.0047, MAG_Y - 0.028, MAG_Y + 0.020, z=mag_top + 0.004, verts=10, mat="coyote"))
b.p("mag", us.ycyl("mag_bullet", 0.0047, MAG_Y + 0.020, MAG_Y + 0.031, z=mag_top + 0.004, r2=0.0012, verts=10,
                   mat="steel"))
b.pivot("mag", (0, MAG_Y, ZB - 0.040), move="0,-0.2,0")
b.pf("mag", us.text("mag_no", "07", 0.010, (-0.0119, MAG_Y + 0.004, mag_top - 0.090), mat="paint", **L_))

# 방아쇠
trig = [(0.050, ZB - 0.036), (0.057, ZB - 0.036), (0.057, ZB - 0.044), (0.059, ZB - 0.052), (0.062, ZB - 0.058),
        (0.059, ZB - 0.060), (0.054, ZB - 0.056), (0.051, ZB - 0.050), (0.050, ZB - 0.043)]
b.p("trigger", us.side("trigger_blade", trig, 0.0055, bevel=0.0012, mat="steel"))
b.pivot("trigger", (0, 0.054, ZB - 0.034), rotAxis="x", rotDeg=-12)

# 조정간 (왼쪽)
SEL = (-0.0138, 0.008, ZB - 0.022)
b.p("selector", us.xcyl("sel_hub", 0.0048, -0.0150, -0.0128, y=SEL[1], z=SEL[2], verts=12, mat="black"))
b.p("selector", us.side("sel_lever", [(SEL[1], SEL[2] - 0.0032), (SEL[1] + 0.016, SEL[2] - 0.0022),
                                      (SEL[1] + 0.018, SEL[2]), (SEL[1] + 0.016, SEL[2] + 0.0022),
                                      (SEL[1], SEL[2] + 0.0032)], 0.0026, x=-0.0158, bevel=0.0008, mat="black"))
b.pivot("selector", SEL, rotAxis="x", rotDeg="0,90,180", note="SAFE,SEMI,AUTO")

# 장전손잡이
CH_Z = ZB + 0.019
b.p("charging_handle", us.boxr("ch_stem", -0.0055, 0.0055, -0.068, -0.056, CH_Z - 0.004, CH_Z + 0.0045,
                               bevel=0.0012, mat="black"))
b.p("charging_handle", us.boxr("ch_bar", -0.019, 0.019, -0.078, -0.067, CH_Z - 0.0035, CH_Z + 0.0045,
                               bevel=0.0025, mat="black"))
b.p("charging_handle", us.boxr("ch_latch", -0.026, -0.016, -0.075, -0.061, CH_Z - 0.003, CH_Z + 0.004,
                               bevel=0.002, mat="black"))
b.pivot("charging_handle", (0, -0.062, CH_Z), move="0,0,0.075")

# 노리쇠 뭉치 (배출구 안)
b.p("bolt", us.boxr("bolt_carrier", 0.0035, 0.0108, 0.034, 0.099, ZB - 0.0012, ZB + 0.0145, bevel=0.0012,
                    mat="bright"))
b.p("bolt", us.boxr("bolt_head", 0.0035, 0.0112, 0.084, 0.093, ZB + 0.002, ZB + 0.009, bevel=0.0008,
                    mat="steel"))
b.pivot("bolt", (0, 0.066, ZB + 0.006), move="0,0,0.088")

# 먼지 덮개 (오른쪽, 아래 경첩)
b.p("dust_cover", us.boxr("dc_plate", 0.0128, 0.0143, 0.035, 0.098, ZB - 0.0025, ZB + 0.0165, bevel=0.0006,
                          mat="steel"))
b.p("dust_cover", us.boxr("dc_lip", 0.0140, 0.0154, 0.040, 0.093, ZB + 0.010, ZB + 0.0135, bevel=0.0004,
                          mat="steel"))
b.p("dust_cover", us.ycyl("dc_hinge", 0.0016, 0.034, 0.099, x=0.0136, z=ZB - 0.0028, verts=8, mat="steel"))
b.pivot("dust_cover", (0.0136, 0.066, ZB - 0.0028), rotAxis="z", rotDeg=-150)

# ================================================================== anchors
b.anchor("muzzle", (0, 0.541, ZB))
b.anchor("grip_support", (0, 0.266, ZB))
b.anchor("sight_eye", (0, -0.115, OPT))
b.anchor("eject", (0.018, 0.066, ZB + 0.007))
b.anchor("mag_well", (0, MAG_Y, ZB - 0.081))

b.finish("weapons/us/m4a1.glb", outline=0.002, fp="0.12,-0.2,-0.26")
