"""모나티엄 진압반 MR-W1 '찬물' 물대포 (차량 거치).

[원작] 교주 차원 진압반은 비살상 장비만 쓴다(고무탄, 고전압 전기충격기). 칸나는 진압반장.
[오리지널] "찬물을 끼얹는다." 진압 장갑차 포탑의 오른쪽 받침(mount_water)에 붙는 고압 물대포.
           곧은 물줄기(밀어내기·넘어뜨리기)와 넓게 퍼지는 분무(시야 가림)를 노즐 고리로 바꾼다.

규약: 원점 = 받침 피벗, 총구 +Y, 위 +Z, 사수 오른쪽 +X. 차량 쪽 mount_* 노드에 변환 없이 붙인다.
움직이는 파츠: nozzle (노즐 고리, rotAxis z: 0 = 물줄기, 90 = 분무)
npm run model -- art/blender/weapons/monatium/mount_water_cannon.py
npm run shot -- weapons/monatium/mount_water_cannon.glb --views side,34,top,muzzle
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import vehicles_elf as ve  # noqa: E402

cb.reset()
W = ve.Mount("mount_water_cannon", "monatium")
M = W.M
BZ = 0.075

# ------------------------------------------------------------------ 받침 + 회전 관절 (둥근 몸통)
W.s(ve.rbox("mount_block", -0.05, 0.05, -0.08, 0.06, -0.01, 0.03, r=0.008, seg=2, mat=M["gear"]))
body_side = ve.round_poly([(-0.20, 0.02), (0.08, 0.02), (0.10, 0.12), (0.04, 0.15), (-0.16, 0.15), (-0.21, 0.10)],
                          [0.02, 0.03, 0.03, 0.03, 0.04, 0.03], 3)
W.s(ve.sculpt("valve_body", body_side, hw.rrect(0.13, 0.14, 0.05, 3, cy=0.085), bevel=0.006, seg=2, mat=M["hull"]))
W.s(cb.sphere("ball", radius=0.060, loc=(0, 0.085, BZ), segments=20, rings=10, material=M["hull_d"]))
# 압력계 (위, 시안 바늘 판)
W.s(hw.zcyl("gauge", 0.030, 0.145, 0.165, y=-0.06, verts=18, mat=M["steel"]))
W.s(hw.zcyl("gauge_face", 0.024, 0.165, 0.167, y=-0.06, verts=18, mat=M["lens"]))
W.s(ve.decal("gauge_needle", [(-0.002, 0.0), (0.002, 0.0), (0.012, 0.018), (0.009, 0.019)], (0, -0.06, 0.167),
             ve.FACE_T, lift=0.0006, mat=M["glow"]))
# 뒤 호스 (주름 고리)
for i in range(6):
    t = i / 5
    y = -0.21 - 0.05 * t
    z = 0.08 - 0.10 * t * t
    W.s(hw.ycyl("hose_ring", 0.040 if i % 2 == 0 else 0.036, y - 0.012, y + 0.012, z=z, verts=16, mat=M["gear"]))
W.s(ve.bar("hose", (0, -0.20, 0.08), (0, -0.27, -0.03), 0.034, verts=14, mat=M["rubber"]))

# ------------------------------------------------------------------ 노즐관 (가늘어지는 관) · 청록 띠 · 고압 경고 · 금색 고리
W.s(hw.ycyl("pipe", 0.050, 0.10, 0.46, z=BZ, verts=24, r2=0.034, bevel=0.004, seg=1, mat=M["hull"]))
W.s(hw.tube("pipe_band", 0.050, 0.030, 0.16, 0.20, c=(0, BZ), verts=24, r_out2=0.048, mat=M["teal"]))
W.s(hw.tube("pipe_hz", 0.042, 0.030, 0.33, 0.35, c=(0, BZ), verts=24, r_out2=0.041, mat=M["hazard"]))
W.s(ve.text("mk_less", "비살상", 0.018, (-0.0505, 0.18, BZ), ve.frame((-1, 0, 0)), mat=M["steel"], lift=0.001))
frx = ve.frame((-1, 0, 0))
W.s(ve.logo_disc("valve_", (-0.066, -0.05, 0.085), 0.050, frx, disc=M["hull_d"], rim=M["gold"], mark=M["gold"],
                 lift=0.0006))
W.s(ve.text("mk_type", "MR-W1", 0.016, (-0.066, -0.05, 0.035), frx, mat=M["steel"], lift=0.0006))
W.s(ve.text("mk_hz", "고압", 0.016, (0.066, -0.05, 0.085), ve.frame((1, 0, 0)), mat=M["hazard"], lift=0.0006))
# 노즐 고리 (돌리면 분무): 금색 나팔 + 구멍 6개
W.p("nozzle", hw.tube("nozzle_collar", 0.040, 0.020, 0.455, 0.52, c=(0, BZ), verts=24, r_out2=0.046, mat=M["gold"]),
    hw.tube("nozzle_lip", 0.050, 0.016, 0.515, 0.53, c=(0, BZ), verts=24, mat=M["gold"]),
    hw.ycyl("nozzle_core", 0.016, 0.47, 0.525, z=BZ, verts=12, mat=M["rubber"]))
for k in range(6):
    a = 2 * math.pi * k / 6
    W.p("nozzle", ve.bar(f"nozzle_tab{k}", (math.cos(a) * 0.041, 0.47, BZ + math.sin(a) * 0.041),
                         (math.cos(a) * 0.047, 0.50, BZ + math.sin(a) * 0.047), 0.006, verts=6, mat=M["steel"]))
W.pivot("nozzle", (0, 0.49, BZ), rotAxis="z", rotDeg="0,90", note="0 = jet, 90 = spray")

W.anchor("muzzle", (0, 0.53, BZ))
W.finish("weapons/monatium/mount_water_cannon.glb", outline=0.0035, budget=8000, props={
    "displayName": "MR-W1 '찬물' 물대포", "ammo": "water"})
