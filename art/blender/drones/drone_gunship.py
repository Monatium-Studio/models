"""R41 D-9 '장수말벌' 중형 전투 드론.

군집 드론 무리를 이끄는 중형 기체. 턱 아래 포탑의 쌍열 기관총으로 제압 사격을 하고, 큰턱 가드로 들이받는다.
현장 지휘관이 직접 조종하거나 군집 드론의 중계기로 쓴다. 폭 1.2 m, 길이 0.95 m, 삼각형 5k 이하.

규약: 정면 -Y, 가장 낮은 점(스키드) z=0.
움직이는 파츠 계층
  duct_L / duct_R        덕트 기울기 (X축, 원점 = 덕트 중심)
    rotor_L / rotor_R    팬 회전 (Z축)
  turret                 포탑 좌우 (Z축)
    gun                  포신 상하 (X축)
      muzzle_L, muzzle_R (앵커)
  thruster               꼬리 노즐 짐벌
    thruster_fan         노즐 안 팬 회전 (Y축)

npm run model -- art/blender/drones/drone_gunship.py
npm run shot -- drones/drone_gunship.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import r41  # noqa: E402

cb.reset()
M = r41.mats()

# ---------------------------------------------------------------- 동체: 머리 · 가슴 · 말벌 허리 · 배
FUSE = [
    (-0.460, 0.045, 0.045, 0.350),
    (-0.430, 0.090, 0.070, 0.352),
    (-0.330, 0.115, 0.085, 0.358),
    (-0.272, 0.092, 0.068, 0.360),
    (-0.230, 0.145, 0.100, 0.365),
    (-0.060, 0.160, 0.112, 0.370),
    (0.040, 0.140, 0.095, 0.370),
    (0.085, 0.082, 0.062, 0.366),
    (0.125, 0.125, 0.092, 0.364),
    (0.270, 0.128, 0.094, 0.366),
    (0.380, 0.090, 0.072, 0.370),
    (0.430, 0.068, 0.058, 0.372),
]
r41.loft("fuselage", FUSE, mat=M["shell"])
r41.band("saddle", FUSE, -0.215, 0.030, base=r41.clip_unit(r41.OCT_UNIT, 0.0), inflate=0.008, steps=4, mat=M["ceramic"])
r41.band("head_cap", FUSE, -0.425, -0.335, base=r41.clip_unit(r41.OCT_UNIT, 0.35), inflate=0.006, steps=2, mat=M["ceramic"])
for i, (y0, y1) in enumerate(((0.150, 0.180), (0.215, 0.245), (0.290, 0.318))):
    r41.band(f"abd_band{i}", FUSE, y0, y1, inflate=0.006, steps=1, mat=M["ceramic"])
# 가슴 옆 슬릿
for sx in (1, -1):
    r41.slits(f"thorax_slit{sx}", (sx * 0.1615, -0.170, 0.335), (0, 0.040, 0), 3, (0.003, 0.028, 0.008), M["glow"])

# ---------------------------------------------------------------- 얼굴: 오각 센서판 + 세 눈 + 큰턱 충돌 가드
r41.ngon_prism("face_plate", 5, 0.066, 0.016, (0, -0.465, 0.350), rot_deg=90, mat=M["metal"], ch=0.003)
r41.ring_eye("eye_", (0, -0.4745, 0.343), 0.027, axis="Y", sign=-1, mat_ring=M["glow"], mat_dot=M["glow"], depth=0.003, verts=14)
for sx in (1, -1):
    r41.ring_eye(f"ocellus{sx}_", (sx * 0.034, -0.4745, 0.383), 0.010, axis="Y", sign=-1, mat_ring=M["glow"], depth=0.003, verts=8)
    m = r41.cyl_y(f"mandible{sx}", 0.0035, 0.075, (sx * 0.034, -0.478, 0.288), r_front=0.010, verts=8, mat=M["metal"])
    m.rotation_euler = (math.radians(-90 + 18), 0, math.radians(-sx * 14))
    r41.cyl_y(f"mandible_base{sx}", 0.016, 0.026, (sx * 0.040, -0.440, 0.296), verts=8, mat=M["shell"])
    r41.tube(f"mandible_band{sx}", 0.0125, 0.0085, 0.008, (sx * 0.038, -0.4565, 0.293), verts=8, mat=M["amber"])

# ---------------------------------------------------------------- 뿔 지느러미 (가슴 위 한 쌍) + 엠블럼
fin_pts = [(-0.175, 0.462), (0.005, 0.462), (0.060, 0.598), (0.030, 0.616), (-0.060, 0.530)]
for sx in (1, -1):
    parts = [r41.prof(f"fin{sx}", fin_pts, 0.016, loc=(sx * 0.066, 0, 0), ch=0.003, mat=M["shell"])]
    # 앞전 발광 줄
    a, b = (-0.130, 0.494), (0.012, 0.600)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    parts.append(cb.box(f"fin_glow{sx}", size=(0.003, L, 0.007),
                        loc=(sx * (0.066 + 0.0085), (a[0] + b[0]) / 2, (a[1] + b[1]) / 2),
                        rot=(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), 0, 0), material=M["glow"]))
    parts += r41.emblem(f"fin{sx}_", (sx * (0.066 + 0.0081), -0.075, 0.505), 0.050, axis="X", sign=sx, mat=M["ceramic"])
    r41.pivot_rotate(parts, (sx * 0.066, 0, 0.462), "Y", sx * 10)

# ---------------------------------------------------------------- 착지 스키드
for sx in (1, -1):
    r41.cyl_y(f"skid{sx}", 0.013, 0.420, (sx * 0.165, -0.060, 0.013), verts=8, mat=M["polymer"])
    up = r41.cyl_y(f"skid_tip{sx}", 0.013, 0.060, (sx * 0.165, -0.290, 0.029), r_front=0.013, verts=8, mat=M["polymer"])
    up.rotation_euler = (math.radians(-90 - 32), 0, 0)
    for y in (-0.170, 0.070):
        dx = sx * 0.075
        r41.chbox(f"skid_strut{sx}{y}", (0.026, 0.030, 0.262), (sx * 0.128, y, 0.140), rot=(0, -math.degrees(math.atan2(dx, 0.25)), 0),
                  ch=0.004, mat=M["metal"])
        r41.chbox(f"skid_foot{sx}{y}", (0.034, 0.040, 0.016), (sx * 0.165, y, 0.026), ch=0.004, mat=M["metal"])

# ---------------------------------------------------------------- 날개 기둥 (파일런) + 힌지
DUCT_C = {"L": (0.445, -0.100, 0.400), "R": (-0.445, -0.100, 0.400)}
for k, (cx, cy, cz) in DUCT_C.items():
    sx = 1 if cx > 0 else -1
    r41.chbox(f"pylon_{k}", (0.170, 0.075, 0.048), (sx * 0.215, cy, 0.392), ch=0.006, mat=M["shell"])
    r41.chbox(f"pylon_strip_{k}", (0.150, 0.028, 0.006), (sx * 0.215, cy, 0.418), ch=0.002, mat=M["ceramic"])
    r41.cyl_x(f"hinge_{k}", 0.030, 0.034, (sx * 0.288, cy, cz), verts=10, mat=M["metal"])
    r41.stencil_bars(f"pylon_{k}_", (sx * 0.200, cy - 0.0375, 0.395), axis="Y", sign=-1, h=0.020, mat=M["ceramic"],
                     unit=0.007, pattern=(1, 0, 1, 1, 0, 1))

# ---------------------------------------------------------------- 덕트 + 로터 (움직이는 파츠)
APO = math.cos(math.radians(30))
keep = []
for k, (cx, cy, cz) in DUCT_C.items():
    sx = 1 if cx > 0 else -1
    duct = []
    for nm, ro, ri, h, z, mt in (("wall", 0.178, 0.160, 0.100, cz, M["shell"]),
                                 ("rim", 0.181, 0.166, 0.014, cz + 0.051, M["ceramic"]),
                                 ("lip", 0.181, 0.166, 0.010, cz - 0.050, M["metal"]),
                                 ("lift_glow", 0.161, 0.153, 0.008, cz - 0.040, M["glow"])):
        o = r41.tube(f"duct_{nm}_{k}", ro, ri, h, (cx, cy, z), axis="Z", verts=6, mat=mt, ch=0.002 if nm == "wall" else 0.0)
        o.rotation_euler.z = math.radians(30)          # 평면이 ±X (파일런 쪽)를 보도록
        duct.append(o)
    duct.append(r41.ngon_prism(f"duct_hub_{k}", 6, 0.044, 0.070, (cx, cy, cz - 0.010), axis="Z", rot_deg=30, mat=M["metal"], ch=0.003))
    for j, ang in enumerate((180, 300, 60)):
        a = math.radians(ang)
        r = (0.042 + 0.160 * APO) / 2
        duct.append(cb.box(f"stator_{k}{j}", size=(0.160 * APO - 0.040, 0.016, 0.012),
                           loc=(cx + math.cos(a) * r, cy + math.sin(a) * r, cz - 0.030), rot=(0, 0, ang),
                           material=M["metal"]))
    duct.append(cb.box(f"duct_nav_{k}", size=(0.004, 0.030, 0.012), loc=(cx + sx * (0.178 * APO + 0.001), cy - 0.050, cz),
                       material=M["glow"]))
    duct_obj = r41.merge(duct, f"duct_{k}", origin=(cx, cy, cz))
    # 바깥 평면의 엠블럼 (데칼, 덕트 자식)
    dec = r41.emblem(f"duct_{k}_", (cx + sx * 0.178 * APO, cy + 0.030, cz - 0.004), 0.068, axis="X", sign=sx, mat=M["ceramic"])
    dec_obj = r41.merge(dec, f"duct_{k}_decal", origin=(cx, cy, cz))
    dec_obj["noOutline"] = 1
    # 로터: 스피너 + 날개 셋
    rot = [r41.ngon_prism(f"spinner_{k}", 6, 0.036, 0.024, (cx, cy, cz + 0.032), axis="Z", rot_deg=30, r2=0.016, mat=M["shell"])]
    for j in range(3):
        a = math.radians(90 + 120 * j)
        r0, r1 = 0.030, 0.160 * APO - 0.010
        rot.append(cb.box(f"blade_{k}{j}", size=(r1 - r0, 0.046, 0.007),
                          loc=(cx + math.cos(a) * (r0 + r1) / 2, cy + math.sin(a) * (r0 + r1) / 2, cz + 0.024),
                          rot=(sx * 16, 0, math.degrees(a)), material=M["ceramic"]))
    rotor_obj = r41.merge(rot, f"rotor_{k}", origin=(cx, cy, cz + 0.024))
    rotor_obj["outline"] = 0.0025
    r41.parent_keep(rotor_obj, duct_obj)
    r41.parent_keep(dec_obj, duct_obj)
    keep.append(duct_obj)

# ---------------------------------------------------------------- 턱 포탑 (움직이는 파츠)
r41.ngon_prism("turret_mount", 6, 0.060, 0.030, (0, -0.150, 0.252), axis="Z", rot_deg=30, mat=M["metal"], ch=0.003)
TUR = (0, -0.150, 0.235)
turret = [r41.ngon_prism("turret_body", 6, 0.066, 0.052, (0, -0.150, 0.212), axis="Z", rot_deg=30, mat=M["shell"], ch=0.004),
          r41.ngon_prism("turret_band", 6, 0.068, 0.010, (0, -0.150, 0.226), axis="Z", rot_deg=30, mat=M["ceramic"], ch=0.001)]
for sx in (1, -1):
    turret.append(r41.chbox(f"trunnion{sx}", (0.016, 0.040, 0.040), (sx * 0.062, -0.180, 0.200), ch=0.004, mat=M["metal"]))
# 탄통 (포탑 왼쪽, 앰버 줄)
turret.append(r41.chbox("ammo_box", (0.034, 0.056, 0.046), (0.092, -0.160, 0.214), ch=0.004, mat=M["shell"]))
turret.append(r41.chbox("ammo_stripe", (0.0345, 0.008, 0.0465), (0.092, -0.176, 0.214), mat=M["amber"]))
turret.append(r41.chbox("ammo_lid", (0.030, 0.050, 0.004), (0.092, -0.160, 0.2385), ch=0.001, mat=M["metal"]))
turret_obj = r41.merge(turret, "turret", origin=TUR)

GUN = (0, -0.180, 0.200)
gun = [r41.chbox("cradle", (0.104, 0.075, 0.040), (0, -0.190, 0.200), ch=0.006, mat=M["shell"])]
for sx in (1, -1):
    x = sx * 0.030
    gun.append(r41.ngon_prism(f"barrel_root{sx}", 6, 0.017, 0.030, (x, -0.240, 0.200), mat=M["metal"], ch=0.002))
    # 구멍 뚫린 총열 덮개 + 총열 + 소염기 (실탄 기관총)
    gun.append(r41.tube(f"shroud{sx}", 0.0135, 0.0080, 0.080, (x, -0.293, 0.200), verts=8, mat=M["shell"]))
    for j in range(3):
        y = -0.270 - j * 0.022
        gun.append(cb.box(f"vent_top{sx}{j}", size=(0.0060, 0.012, 0.0016), loc=(x, y, 0.2138), material=M["metal"]))
        gun.append(cb.box(f"vent_side{sx}{j}", size=(0.0016, 0.012, 0.0060), loc=(x + sx * 0.0138, y, 0.200),
                          material=M["metal"]))
    gun.append(r41.cyl_y(f"barrel{sx}", 0.0062, 0.030, (x, -0.340, 0.200), verts=8, mat=M["metal"]))
    gun.append(r41.tube(f"tip_band{sx}", 0.0100, 0.0060, 0.006, (x, -0.336, 0.200), verts=8, mat=M["amber"]))
    gun.append(r41.cyl_y(f"flash_hider{sx}", 0.0092, 0.018, (x, -0.352, 0.200), verts=8, mat=M["shell"]))
# 탄띠 급탄 슈트 (포신과 함께 움직임)
gun.append(r41.chbox("feed_chute", (0.034, 0.024, 0.012), (0.062, -0.192, 0.214), rot=(0, -18, 0), ch=0.002, mat=M["metal"]))
gun_obj = r41.merge(gun, "gun", origin=GUN)
r41.parent_keep(gun_obj, turret_obj)
for sx, nm in ((1, "muzzle_L"), (-1, "muzzle_R")):
    e = cb.empty(nm, loc=(sx * 0.030, -0.362, 0.200), size=0.03)
    r41.parent_keep(e, gun_obj)
keep.append(turret_obj)

# ---------------------------------------------------------------- 꼬리 추진기 (움직이는 파츠)
THR = (0, 0.428, 0.372)
thr = [r41.tube("nozzle", 0.068, 0.054, 0.080, (0, 0.468, 0.372), verts=8, mat=M["metal"], ch=0.002),
       r41.tube("nozzle_lip", 0.070, 0.057, 0.010, (0, 0.503, 0.372), verts=8, mat=M["amber"]),
       r41.cyl_y("nozzle_glow", 0.055, 0.004, (0, 0.440, 0.372), verts=8, mat=M["glow"])]
for j in range(4):
    a = math.radians(45 + 90 * j)
    thr.append(cb.box(f"vane{j}", size=(0.010, 0.060, 0.030), loc=(math.cos(a) * 0.070, 0.462, 0.372 + math.sin(a) * 0.070),
                      rot=(0, -math.degrees(a) + 90, 0), material=M["shell"]))
thr_obj = r41.merge(thr, "thruster", origin=THR)
fan = [r41.cyl_y("fan_hub", 0.016, 0.020, (0, 0.456, 0.372), verts=10, mat=M["metal"])]
for j in range(6):
    a = math.radians(60 * j)
    fan.append(cb.box(f"fan_blade{j}", size=(0.034, 0.004, 0.012), loc=(math.cos(a) * 0.032, 0.456, 0.372 + math.sin(a) * 0.032),
                      rot=(0, -math.degrees(a), 20), material=M["shell"]))
fan_obj = r41.merge(fan, "thruster_fan", origin=(0, 0.456, 0.372))
r41.parent_keep(fan_obj, thr_obj)
e = cb.empty("exhaust", loc=(0, 0.510, 0.372), size=0.04)
r41.parent_keep(e, thr_obj)
keep.append(thr_obj)

r41.finish(
    "drone_gunship", "drones/drone_gunship.glb",
    keep=keep,
    anchors={
        "eye": (0, -0.478, 0.343),
        "center": (0, -0.050, 0.370),
    },
    props={"outline": 0.004},
    ground=True,
)
