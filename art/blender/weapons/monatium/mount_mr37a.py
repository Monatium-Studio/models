"""모나티엄 진압반 MR-37A '자장자장' 자동 충격탄 발사기 (차량 거치).

[원작] 칸나의 강화 공격 '충격 포탄'은 적을 기절시킨다. 교주 차원 진압반은 고무탄·전기충격기만 쓴다.
[오리지널] MR-37 '단잠'(펌프식 37 mm)을 원격 포탑용 자동식으로 바꾼 것. 옆 드럼 탄창(고무 충격탄 12발).
           MRV-1 '요람' 포탑의 왼쪽 받침(mount_mr37a)에 붙는다.

규약: 원점 = 받침 피벗(받침판 윗면 중앙), 총구 +Y, 위 +Z, 사수 오른쪽 +X (ART_GUIDE 7장, VEHICLES.md)
      차량 쪽 mount_* 노드는 Z축 180° 돌아 있어 이 glb를 변환 없이 자식으로 붙이면 차량 정면을 본다.
npm run model -- art/blender/weapons/monatium/mount_mr37a.py
npm run shot -- weapons/monatium/mount_mr37a.glb --views side,34,top,muzzle
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import vehicles_elf as ve  # noqa: E402

cb.reset()
W = ve.Mount("mount_mr37a", "monatium")
M = W.M

BZ = 0.085                 # 포신 축 높이
R_B = 0.030                # 포신 바깥 반지름 (37 mm)
REC_W = 0.15

# ------------------------------------------------------------------ 받침 + 리시버 (둥근 상자)
W.s(ve.rbox("mount_block", -0.05, 0.05, -0.10, 0.06, -0.01, 0.03, r=0.008, seg=2, mat=M["gear"]))
rec_side = ve.round_poly([(-0.25, 0.02), (0.13, 0.02), (0.13, 0.15), (0.06, 0.165), (-0.20, 0.165), (-0.25, 0.13)],
                         [0.02, 0.02, 0.02, 0.03, 0.04, 0.03], 3)
W.s(ve.sculpt("receiver", rec_side, hw.rrect(REC_W, 0.15, 0.03, 3, cy=0.09), bevel=0.006, seg=2, mat=M["hull"]))
# 윗덮개 + 골 (급탄 덮개)
W.s(ve.rbox("feed_cover", -0.055, 0.055, -0.20, 0.02, 0.160, 0.185, r=0.010, seg=2, mat=M["hull_d"]))
for i in range(4):
    y = -0.17 + i * 0.05
    W.s(ve.rbox("cover_rib", -0.050, 0.050, y - 0.008, y + 0.008, 0.183, 0.191, r=0.003, mat=M["gear"]))
# 앞 위 레이저 거리측정기 (시안 렌즈)
W.s(ve.rbox("lrf", -0.035, 0.035, 0.03, 0.12, 0.168, 0.215, r=0.010, seg=2, mat=M["gear"]))
W.s(hw.ycyl("lrf_lens", 0.016, 0.119, 0.124, z=0.192, verts=14, mat=M["glow"]))
# 뒤 완충기
W.s(hw.ycyl("buffer", 0.040, -0.31, -0.24, z=0.09, verts=16, bevel=0.006, seg=1, mat=M["gear"]))
W.s(hw.ycyl("buffer_cap", 0.030, -0.325, -0.30, z=0.09, verts=16, mat=M["steel"]))

# ------------------------------------------------------------------ 포신: 방열 덮개(스타디움 창) · 청록 띠 · 금색 나팔
W.s(hw.tube("barrel", R_B, 0.0185, 0.12, 0.54, c=(0, BZ), verts=24, mat=M["gear"]))
W.s(hw.ycyl("shroud", R_B + 0.013, 0.12, 0.40, z=BZ, verts=24, bevel=0.004, seg=1, mat=M["hull"]))
for sx, fr in ((-1, ve.frame((-1, 0, 0))), (1, ve.frame((1, 0, 0)))):
    for i, y in enumerate((0.18, 0.25, 0.32)):
        W.s(ve.decal(f"sh_win{sx}{i}", hw.stadium(0.050, 0.016, 5), (sx * (R_B + 0.013), y, BZ + 0.004), fr,
                     lift=0.0006, mat=M["gear"]))
W.s(hw.tube("band_teal", R_B + 0.004, 0.0185, 0.44, 0.475, c=(0, BZ), verts=24, mat=M["teal"]))
W.s(ve.text("mk_less", "비살상", 0.020, (-(R_B + 0.0045), 0.4575, BZ), ve.frame((-1, 0, 0)), mat=M["steel"],
            lift=0.0008))
W.s(hw.tube("muzzle_bell", R_B + 0.003, 0.0195, 0.52, 0.58, c=(0, BZ), verts=24, r_out2=R_B + 0.011, r_in2=0.024,
            mat=M["gold"]))
W.s(hw.tube("muzzle_lip", R_B + 0.013, 0.024, 0.575, 0.585, c=(0, BZ), verts=24, mat=M["gold"]))
W.s(hw.ycyl("bore", 0.019, 0.20, 0.205, z=BZ, verts=16, mat=M["rubber"]))

# ------------------------------------------------------------------ 드럼 탄창 (바깥쪽 = -X), 창으로 청록 충격탄이 보인다
DX, DY, DZ = -0.135, -0.07, 0.085
W.s(hw.xcyl("drum", 0.105, DX - 0.045, DX + 0.045, y=DY, z=DZ, verts=28, bevel=0.010, seg=2, mat=M["hull"]))
W.s(hw.xcyl("drum_band", 0.108, DX - 0.012, DX + 0.012, y=DY, z=DZ, verts=28, mat=M["teal"]))
W.s(hw.xcyl("drum_hub", 0.032, DX - 0.052, DX - 0.040, y=DY, z=DZ, verts=16, mat=M["steel"]))
W.s(ve.rbox("drum_neck", DX + 0.03, -0.07, DY - 0.05, DY + 0.05, DZ - 0.04, DZ + 0.04, r=0.008, seg=2, mat=M["gear"]))
frx = ve.frame((-1, 0, 0))
W.s(ve.logo_disc("drum_", (DX - 0.046, DY, DZ), 0.075, frx, disc=M["hull_d"], rim=M["gold"], mark=M["gold"],
                 lift=0.0006))
for k in range(5):        # 둘레 창 (청록 탄두)
    a = math.radians(200 + k * 28)
    p = (DX - 0.020, DY + math.cos(a) * 0.106, DZ + math.sin(a) * 0.106)
    n = (0, math.cos(a), math.sin(a))
    W.s(ve.decal(f"drum_win{k}", hw.circle(0.012, 10), p, ve.frame(n, up=(-1, 0, 0)), lift=0.0008, mat=M["teal"]))
W.s(ve.text("mk_type", "MR-37A", 0.016, (-(REC_W / 2 + 0.001), -0.04, 0.035), frx, mat=M["steel"], lift=0.0006))
W.s(ve.text("mk_cal", "37", 0.030, (-(REC_W / 2 + 0.001), -0.20, 0.090), frx, mat=M["steel"], lift=0.0006))

# ------------------------------------------------------------------ 오른쪽: 배출구 + 장전 손잡이(움직임)
frR = ve.frame((1, 0, 0))
W.s(ve.decal("eject_port", hw.rrect(0.07, 0.035, 0.012, 3), (REC_W / 2 + 0.001, -0.02, 0.105), frR, lift=0.0006,
             mat=M["rubber"]))
for (y, z) in ((-0.20, 0.05), (0.08, 0.05), (-0.20, 0.13), (0.08, 0.13)):
    for sx, fr in ((1, frR), (-1, frx)):
        W.s(ve.decal(f"pin{sx}{y}{z}", hw.circle(0.006, 10), (sx * (REC_W / 2 + 0.001), y, z), fr, lift=0.0006,
                     mat=M["steel"]))
W.p("bolt", ve.rbox("ch_rail", REC_W / 2 - 0.005, REC_W / 2 + 0.012, -0.16, -0.06, 0.055, 0.075, r=0.004,
                    mat=M["gear"]),
    ve.bar("ch_knob", (REC_W / 2 + 0.010, -0.08, 0.065), (REC_W / 2 + 0.045, -0.08, 0.065), 0.012, verts=10,
           mat=M["teal"]))
W.pivot("bolt", (REC_W / 2, -0.10, 0.065), move=hw.mv(0, -0.06, 0))

W.anchor("muzzle", (0, 0.585, BZ))
W.anchor("eject", (REC_W / 2 + 0.005, -0.02, 0.105))
W.anchor("feed", (DX, DY, DZ))
W.finish("weapons/monatium/mount_mr37a.glb", outline=0.0035, budget=8000, props={
    "displayName": "MR-37A '자장자장' 자동 충격탄 발사기", "caliber": "37mm", "ammo": "beanbag"})
