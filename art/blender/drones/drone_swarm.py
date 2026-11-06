"""R41 D-1 '모기' 군집 드론.

턱 아래 소형 기관총 포드('침')로 근거리 연사하며 떼로 덮치는 소형 드론. 하나는 약하지만 수십 대가 한꺼번에 온다.
R41이 물량전에 쓰는 기본 단위다. 폭 0.37 m, 삼각형 3k 이하.

규약: 정면 -Y, 가장 낮은 점 z=0. 회전부(rotor_FL/FR/BL/BR)는 각자 원점(허브)에서 Z축으로 돈다.

npm run model -- art/blender/drones/drone_swarm.py
npm run shot -- drones/drone_swarm.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import r41  # noqa: E402

cb.reset()
M = r41.mats()

# ---------------------------------------------------------------- 동체 (말벌 허리)
POD = [
    (-0.088, 0.018, 0.016, 0.074),
    (-0.076, 0.033, 0.026, 0.075),
    (-0.046, 0.040, 0.031, 0.076),
    (0.020, 0.038, 0.030, 0.078),
    (0.044, 0.024, 0.020, 0.080),
    (0.058, 0.032, 0.026, 0.081),
    (0.094, 0.030, 0.024, 0.083),
    (0.120, 0.012, 0.010, 0.086),
]
r41.loft("pod", POD, mat=M["shell"])
r41.band("saddle", POD, -0.050, 0.018, base=r41.clip_unit(r41.OCT_UNIT, 0.05), inflate=0.003, mat=M["ceramic"])
r41.band("abd_band", POD, 0.070, 0.082, inflate=0.0025, steps=1, mat=M["ceramic"])
for sx in (1, -1):
    r41.slits(f"side_slit{sx}", (sx * 0.0405, -0.030, 0.071), (0, 0.016, 0), 2, (0.0016, 0.010, 0.004), M["glow"])

# 엘프 로고 (동체 양옆 평면)
for sx in (1, -1):
    r41.elf_logo(f"pod{sx}_", (sx * 0.0392, 0.004, 0.0765), 0.022, axis="X", sign=sx, mat=M["ceramic"])

# 센서 얼굴: 아래를 향한 오각판 + 고리-점 눈
r41.ngon_prism("face_plate", 5, 0.024, 0.010, (0, -0.090, 0.074), rot_deg=90, mat=M["metal"], ch=0.0015)
r41.ring_eye("eye_", (0, -0.0955, 0.0755), 0.0140, axis="Y", sign=-1, mat_ring=M["glow"], mat_dot=M["glow"],
             depth=0.0016, verts=16)

# 턱 아래 기관총 포드 ('침'): 짧은 총열 + 소염기 + 앰버 띠, 아래 탄통
GUN_T = math.radians(10)          # 앞으로 10° 숙임
gun_c = (0, -0.080, 0.0565)
barrel = r41.cyl_y("gun_barrel", 0.0036, 0.046, gun_c, verts=8, mat=M["metal"])
barrel.rotation_euler = (math.radians(-90 + 10), 0, 0)
fwd = (0, -math.cos(GUN_T), -math.sin(GUN_T))     # 총구 방향 (-Y, 아래로 10°)
fh_c = tuple(c + f * 0.027 for c, f in zip(gun_c, fwd))
fh = r41.cyl_y("gun_flash_hider", 0.0058, 0.012, fh_c, verts=8, mat=M["shell"])
fh.rotation_euler = barrel.rotation_euler
r41.cyl_y("gun_collar", 0.0068, 0.010, (0, -0.064, 0.0590), verts=10, mat=M["amber"])
r41.chbox("gun_receiver", (0.016, 0.034, 0.014), (0, -0.050, 0.0545), ch=0.002, mat=M["metal"])
r41.chbox("ammo_box", (0.024, 0.030, 0.014), (0, -0.018, 0.052), ch=0.002, mat=M["shell"])
r41.chbox("ammo_stripe", (0.0245, 0.004, 0.0142), (0, -0.030, 0.052), mat=M["amber"])
stinger_tip = tuple(c + f * 0.033 for c, f in zip(gun_c, fwd))

# 배 아래 착지 스키드 (짧은 두 줄)
for sx in (1, -1):
    r41.chbox(f"skid{sx}", (0.006, 0.090, 0.006), (sx * 0.020, -0.004, 0.046), ch=0.0015, mat=M["polymer"])
    for y in (-0.034, 0.026):
        r41.chbox(f"skid_strut{sx}{y}", (0.005, 0.006, 0.012), (sx * 0.020, y, 0.052), ch=0.001, mat=M["polymer"])

# 꼬리 안테나
r41.cyl_z("antenna", 0.0018, 0.030, (0, 0.090, 0.120), verts=6, mat=M["metal"])
r41.cyl_z("antenna_tip", 0.0035, 0.005, (0, 0.090, 0.137), verts=8, mat=M["glow"])

# ---------------------------------------------------------------- 팔 · 덕트 · 다리
ROT_Z = 0.090
ROTORS = {"FL": (0.118, -0.072), "FR": (-0.118, -0.072), "BL": (0.118, 0.078), "BR": (-0.118, 0.078)}
DUCT_R = 0.052
rotor_parts = {}
for key, (cx, cy) in ROTORS.items():
    ang = math.degrees(math.atan2(cy, cx))
    d0 = 0.030
    d1 = math.hypot(cx, cy) + DUCT_R - 0.002
    mid = (d0 + d1) / 2
    r41.chbox(f"arm_{key}", (d1 - d0, 0.011, 0.008), (mid * math.cos(math.radians(ang)), mid * math.sin(math.radians(ang)), 0.080),
              rot=(0, 0, ang), ch=0.0015, mat=M["polymer"])
    # 육각 덕트 (꼭짓점이 팔 방향) + 세라믹 테
    for nm, ro, ri, h, z, mt in (("duct", DUCT_R, DUCT_R - 0.0065, 0.018, ROT_Z - 0.002, M["shell"]),
                                 ("duct_rim", DUCT_R + 0.001, DUCT_R - 0.0045, 0.0035, ROT_Z + 0.0080, M["ceramic"])):
        d = r41.tube(f"{nm}_{key}", ro, ri, h, (cx, cy, z), axis="Z", verts=6, mat=mt)
        d.rotation_euler.z = math.radians(ang)
    r41.cyl_z(f"motor_{key}", 0.011, 0.016, (cx, cy, 0.081), verts=10, mat=M["metal"], ch=0.0012)
    # 항법등 (덕트 바깥쪽)
    ux, uy = cx / math.hypot(cx, cy), cy / math.hypot(cx, cy)
    cb.box(f"nav_{key}", size=(0.0025, 0.0025, 0.007), loc=(cx + ux * (DUCT_R + 0.0012), cy + uy * (DUCT_R + 0.0012), ROT_Z - 0.002),
           rot=(0, 0, ang + 90), material=M["glow"])
    # 로터 (움직이는 파츠)
    hub = r41.cyl_z(f"hub_{key}", 0.0065, 0.007, (cx, cy, ROT_Z + 0.003), verts=10, mat=M["metal"])
    blades = []
    spin = 25 if key in ("FL", "BR") else -25
    for b in (0, 180):
        a = math.radians(spin + b)
        L = DUCT_R * math.cos(math.radians(30)) - 0.0105
        blades.append(cb.box(f"blade_{key}{b}", size=(L, 0.011, 0.0018),
                             loc=(cx + math.cos(a) * L / 2, cy + math.sin(a) * L / 2, ROT_Z + 0.002),
                             rot=(12 if b == 0 else -12, 0, spin + b), bevel=0.0006, bevel_segments=1, material=M["ceramic"]))
    rotor_parts[key] = ([hub] + blades, (cx, cy, ROT_Z + 0.002))

root = r41.finish(
    "drone_swarm", "drones/drone_swarm.glb",
    moving={f"rotor_{k}": v for k, v in rotor_parts.items()},
    anchors={
        "eye": (0, -0.097, 0.0755),
        "muzzle": stinger_tip,
        "center": (0, 0, 0.080),
    },
    props={"outline": 0.0035},
    ground=True,
    node_props={f"rotor_{k}": {"outline": 0.0018} for k in ROTORS},
)
