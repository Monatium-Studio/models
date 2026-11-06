"""R41 M-4 '호박벌' 거치 경기관총 (차량 거치).

[원작] R41 병사는 실탄 돌격소총을 쓰고(PV 3:00~3:03), 효율적 전투용 장비를 갖췄다(엘리아스 침공전).
[오리지널] K-7 '쐐기벌'과 같은 소구경 탄을 벨트로 먹이는 차량 거치 경기관총. V-7 '나나니' 습격차의 회전대에 달고,
           V-21 '쌍살벌' 보병전투차 포탑의 공축 기관총(mount_coax) 무기 정의로도 쓴다.
           PV 소총의 도장(회백 + 앰버 띠·줄 + 어두운 탄통·손잡이), 45° 모따기, 가운데 조준 홈이 난 낮은 방탄판.

1인칭 (2026-11-02 사수 시야 개정): 사수는 방탄판 위로 넘겨 본다(fpOffset: 회전축 0.27 m 위·0.55 m 뒤). 방탄판은 눈보다
      낮고 가운데에 조준 홈을 파서, 정조준(sight_eye)은 홈 사이로 링 가늠쇠를 본다. 링 조준기(앞 링 + 십자 + 점,
      뒤 큰 고리 가늠자: 정조준에서 앞 링 바깥을 두르는 가는 원)는 총열 축과 나란한 한 선(SZ) 위에 있어 링 가운데가 곧 탄착점이다.

규약: 원점 = 트러니언(상하 회전축, 좌우 회전축과 만나는 점), 총구 +Y, 위 +Z, 사수 오른쪽 +X.
      차량 쪽 mount_* 노드(같은 점)에 변환 없이 붙인다. 회전대 핀 바닥은 원점 아래 pivotDrop(0.09 m).
움직이는 파츠: yoke (counterPitch=1), charging_handle (move), trigger (rotAxis x), feed_cover (rotAxis x)
npm run model -- art/blender/weapons/r41/mount_r41_lmg.py
npm run shot -- weapons/r41/mount_r41_lmg.glb --views side,34,top,muzzle
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import r41  # noqa: E402
import vehicles_elf as ve  # noqa: E402

cb.reset()
W = ve.Mount("mount_r41_lmg", "r41")
M = W.M
BZ = 0.120
TZ = 0.090
RW = 0.072
SZ = 0.250                  # 조준선 높이 (총열 축과 나란함: 가늠자 구멍 가운데 = 링 가운데 = sight_eye)

# ------------------------------------------------------------------ 요크 + 핀
W.p("yoke", r41.cyl_z("pin", 0.022, 0.07, (0, 0, -0.025), verts=6, mat=M["steel"]),
    r41.ngon_prism("yoke_base", 6, 0.045, 0.026, (0, 0, 0.013), axis="Z", rot_deg=30, mat=M["shell"], ch=0.004))
for sx in (1, -1):
    x0, x1 = sorted((sx * (RW / 2 + 0.004), sx * (RW / 2 + 0.020)))
    W.p("yoke", ve.rbox("yoke_arm", x0, x1, -0.026, 0.026, 0.012, TZ + 0.022, r=0.004, mat=M["shell"]))
W.p("yoke", ve.rbox("yoke_floor", -(RW / 2 + 0.02), RW / 2 + 0.02, -0.026, 0.026, 0.012, 0.028, r=0.003, mat=M["shell"]),
    r41.cyl_x("trunnion", 0.011, RW + 0.054, (0, 0, TZ), verts=6, mat=M["steel"]))
W.pivot("yoke", (0, 0, TZ), counterPitch=1)

# ------------------------------------------------------------------ 리시버 (모따기 덩어리, 회백) + 앰버 줄
rec_side = [(-0.23, 0.070), (0.10, 0.070), (0.10, 0.168), (-0.20, 0.168), (-0.23, 0.140)]
rec_sec = [(-RW / 2, 0.070), (RW / 2, 0.070), (RW / 2, 0.150), (RW / 2 - 0.016, 0.168), (-RW / 2 + 0.016, 0.168),
           (-RW / 2, 0.150)]
W.s(ve.facet("receiver", rec_side, rec_sec, ch=0.003, mat=M["light"]))
W.s(ve.rbox("lower", -RW / 2 + 0.006, RW / 2 - 0.006, -0.17, 0.06, 0.055, 0.072, r=0.003, mat=M["shell"]))
frL, frR = ve.frame((-1, 0, 0)), ve.frame((1, 0, 0))
for sx, fr in ((1, frR), (-1, frL)):
    W.s(ve.decal(f"amber_line{sx}", [(-0.15, -0.0025), (0.09, -0.0025), (0.09, 0.0025), (-0.15, 0.0025)],
                 (sx * RW / 2, -0.02, 0.085), fr, lift=0.0006, mat=M["amber"]))
    for i, y in enumerate((-0.19, 0.07)):
        W.s(r41.screw(f"rscrew{sx}{i}", (sx * (RW / 2 + 0.0008), y, 0.150), axis="X", r=0.004, h=0.002, mat=M["steel"]))
# 왼쪽: 엘프 로고(제국 흑) + 막대 부호 / 오른쪽: 배출구
W.s(r41.elf_logo("rec_", (-(RW / 2 + 0.0006), -0.11, 0.120), 0.030, axis="X", sign=-1, mat=M["shell"]))
W.s(r41.stencil_bars("rec_", (-(RW / 2 + 0.0006), -0.02, 0.140), axis="X", sign=-1, h=0.008, mat=M["shell"],
                     pattern=(1, 0, 1, 1, 0, 1, 0, 1)))
W.s(ve.decal("eject_port", [(-0.03, -0.012), (0.03, -0.012), (0.03, 0.012), (-0.03, 0.012)],
             (RW / 2 + 0.0006, -0.04, 0.128), frR, lift=0.0, mat=M["shell"]))
# 급탄 덮개 (위, 움직임)
W.p("feed_cover", ve.facet("cover", [(-0.16, 0.166), (0.04, 0.166), (0.04, 0.184), (-0.14, 0.188)],
                           [(-RW / 2 + 0.010, 0.166), (RW / 2 - 0.010, 0.166), (RW / 2 - 0.016, 0.188),
                            (-RW / 2 + 0.016, 0.188)], ch=0.002, mat=M["light"]),
    ve.rbox("cover_latch", -0.012, 0.012, -0.165, -0.150, 0.170, 0.190, mat=M["amber"]))
W.pivot("feed_cover", (0, 0.04, 0.176), rotAxis="x", rotDeg=70)
# 가늠자: 리시버 뒤 기둥 위의 큰 구멍 (정조준에서 링 가늠쇠를 두르는 바깥 원)
W.s(ve.rbox("rs_base", -0.010, 0.010, -0.20, -0.17, 0.166, 0.176, mat=M["shell"]))
W.s(ve.rbox("rs_post", -0.003, 0.003, -0.188, -0.182, 0.174, SZ - 0.0245, mat=M["shell"]))
W.s(r41.tube("rs_ring", 0.0265, 0.0245, 0.004, (0, -0.185, SZ), axis="Y", verts=28, mat=M["shell"]))

# ------------------------------------------------------------------ 팔각 총열 덮개 · 앰버 띠 · 슬롯 소염기 · 높은 가늠쇠
W.s(r41.ngon_prism("handguard", 8, 0.030, 0.25, (0, 0.225, BZ), axis="Y", rot_deg=22.5, mat=M["light"], ch=0.002))
W.s(r41.ngon_prism("band", 8, 0.0315, 0.018, (0, 0.108, BZ), axis="Y", rot_deg=22.5, mat=M["amber"]))
for sx, fr in ((1, frR), (-1, frL)):
    for i, y in enumerate((0.16, 0.20, 0.24, 0.28)):
        W.s(ve.decal(f"hg_slot{sx}{i}", [(-0.012, -0.003), (0.012, -0.003), (0.012, 0.003), (-0.012, 0.003)],
                     (sx * 0.0288, y, BZ), fr, lift=0.0006, mat=M["shell"]))
W.s(r41.cyl_y("barrel", 0.012, 0.15, (0, 0.415, BZ), verts=10, mat=M["metal"]))
W.s(r41.cyl_y("hider", 0.017, 0.07, (0, 0.525, BZ), verts=8, mat=M["metal"]))
for k in range(4):
    a = math.radians(45 + 90 * k)
    W.s(ve.decal(f"hider_slot{k}", [(-0.018, -0.0025), (0.018, -0.0025), (0.018, 0.0025), (-0.018, 0.0025)],
                 (math.cos(a) * 0.0172, 0.53, BZ + math.sin(a) * 0.0172), ve.frame((math.cos(a), 0, math.sin(a)), up=(0, 1, 0)),
                 lift=0.0004, mat=M["shell"]))
W.s(r41.cyl_y("hider_ring", 0.0185, 0.008, (0, 0.493, BZ), verts=8, mat=M["amber"]))
# 링 가늠쇠 (대공 링 조준기 꼴): 기둥 위 링 + 가운데가 빈 십자 + 앰버 점. 링 가운데 = 조준선
FS_Y, FR = 0.310, 0.050
W.s(ve.rbox("fs_block", -0.010, 0.010, FS_Y - 0.010, FS_Y + 0.010, BZ + 0.025, BZ + 0.040, mat=M["shell"]))
W.s(ve.rbox("fs_post", -0.004, 0.004, FS_Y - 0.004, FS_Y + 0.004, BZ + 0.040, SZ - FR + 0.002, mat=M["shell"]))
W.s(r41.tube("fs_ring", FR, FR - 0.005, 0.005, (0, FS_Y, SZ), axis="Y", verts=28, mat=M["shell"]))
for a, b in ((0.008, FR - 0.003), (-FR + 0.003, -0.008)):
    W.s(ve.rbox("fs_cross_h", a, b, FS_Y - 0.0012, FS_Y + 0.0012, SZ - 0.0012, SZ + 0.0012, mat=M["shell"]))
    W.s(ve.rbox("fs_cross_v", -0.0012, 0.0012, FS_Y - 0.0012, FS_Y + 0.0012, SZ + a, SZ + b, mat=M["shell"]))
W.s(cb.sphere("fs_dot", radius=0.0028, loc=(0, FS_Y, SZ), segments=8, rings=4, material=M["glow_amber"]))
# 아래 양각대 접힘 (모듈 자리, 앰버 줄)
W.s(ve.rbox("bipod_fold", -0.012, 0.012, 0.13, 0.32, BZ - 0.048, BZ - 0.032, mat=M["shell"]))
W.s(ve.rbox("bipod_line", -0.0125, 0.0125, 0.14, 0.31, BZ - 0.042, BZ - 0.038, mat=M["amber"]))

# ------------------------------------------------------------------ 탄통 (왼쪽, 제국 흑 + 가로 골 + 앰버 줄) + 급탄 슈트
W.s(ve.rbox("belt_box", -(RW / 2 + 0.12), -(RW / 2 + 0.006), -0.12, 0.05, 0.010, 0.130, r=0.006, mat=M["shell"]))
for k in range(4):
    W.s(ve.rbox("box_rib", -(RW / 2 + 0.123), -(RW / 2 + 0.003), -0.12, 0.05, 0.030 + k * 0.025, 0.036 + k * 0.025,
                mat=M["metal"]))
W.s(ve.rbox("box_line", -(RW / 2 + 0.1235), -(RW / 2 + 0.0025), -0.06, -0.05, 0.010, 0.130, mat=M["amber"]))
W.s(ve.rbox("chute", -(RW / 2 + 0.01), -(RW / 2 - 0.004), -0.07, -0.01, 0.10, 0.155, mat=M["metal"]))

# ------------------------------------------------------------------ 방탄판 (낮은 모따기 판 + 가운데 조준 홈 + 앰버 위 띠 + 엘프 로고)
# 위 모서리(z 0.235)는 정조준 눈높이(SZ)보다 조금 낮고 지향 사격 눈(회전축 위 0.27 m)보다 한참 아래: 사수는 판 너머로 본다.
# 가운데 홈(바닥 z 0.205, 폭 ±0.06)으로 정조준 선이 링 가늠쇠까지 트인다
SH_Y = 0.075
shield = [(-0.20, 0.00), (0.20, 0.00), (0.23, 0.05), (0.23, 0.18), (0.19, 0.22), (0.09, 0.22), (0.06, 0.19),
          (-0.06, 0.19), (-0.09, 0.22), (-0.19, 0.22), (-0.23, 0.18), (-0.23, 0.05)]
W.s(ve.slab("shield", shield, (0, SH_Y, 0.015), (-1, 0, 0), (0, 0, 1), 0.010, mat=M["light"]))
for sx in (1, -1):
    top = [(sx * 0.095, 0.205), (sx * 0.185, 0.205), (sx * 0.19, 0.216), (sx * 0.09, 0.216)]
    W.s(ve.slab(f"shield_top{sx}", top, (0, SH_Y + 0.011, 0.015), (-1, 0, 0), (0, 0, 1), 0.003, mat=M["amber"]))
W.s(r41.elf_logo("shield_", (-0.13, SH_Y + 0.0108, 0.095), 0.070, axis="Y", sign=1, mat=M["shell"]))
W.s(r41.stencil_bars("shield_", (0.13, SH_Y + 0.0108, 0.06), axis="Y", sign=1, h=0.012, mat=M["shell"],
                     pattern=(1, 1, 0, 1, 0, 1, 1), unit=0.006))
W.s(ve.rbox("shield_clamp", -0.03, 0.03, 0.06, 0.085, 0.08, 0.16, r=0.004, mat=M["shell"]))

# ------------------------------------------------------------------ 뒤 쌍손잡이 (제국 흑, 엘프 손: 손가락 홈 3) + 방아쇠
for sx in (1, -1):
    W.s(ve.bar(f"spade_arm{sx}", (sx * 0.03, -0.22, 0.10), (sx * 0.055, -0.27, 0.10), 0.008, verts=6, mat=M["shell"]))
    W.s(r41.ngon_prism(f"spade{sx}", 6, 0.014, 0.065, (sx * 0.055, -0.27, 0.10), axis="Z", rot_deg=30, mat=M["shell"]))
    for k in range(3):
        W.s(ve.rbox(f"spade_ridge{sx}{k}", sx * 0.055 - 0.0145, sx * 0.055 + 0.0145, -0.2845, -0.2805,
                    0.079 + k * 0.018, 0.084 + k * 0.018, mat=M["metal"]))
W.p("trigger", ve.rbox("trig", -0.018, 0.018, -0.252, -0.242, 0.086, 0.112, mat=M["amber"]))
W.pivot("trigger", (0, -0.242, 0.099), rotAxis="x", rotDeg=12)
W.p("charging_handle", ve.rbox("ch_slide", RW / 2 - 0.002, RW / 2 + 0.010, -0.11, -0.05, 0.138, 0.152, mat=M["shell"]),
    ve.rbox("ch_knob", RW / 2 + 0.008, RW / 2 + 0.030, -0.075, -0.06, 0.137, 0.153, mat=M["amber"]))
W.pivot("charging_handle", (RW / 2, -0.08, 0.145), move=hw.mv(0, -0.06, 0))

W.anchor("muzzle", (0, 0.56, BZ))
W.anchor("eject", (RW / 2 + 0.004, -0.04, 0.128))
W.anchor("sight_eye", (0, -0.33, SZ))               # 가늠자 구멍 0.145 m 뒤, 링과 같은 높이
W.anchor("grip_R", (0.055, -0.27, 0.10))
W.anchor("grip_support", (-0.055, -0.27, 0.10))
W.anchor("trunnion", (0, 0, TZ))
W.finish("weapons/r41/mount_r41_lmg.glb", outline=0.003, budget=8000, origin=(0, 0, TZ), props={
    "displayName": "M-4 '호박벌' 거치 경기관총", "ammo": "live", "pivotDrop": TZ,
    # 사수 눈 (회전축 기준, three 카메라 공간: 회전축이 눈의 0.27 m 아래·0.55 m 앞). 좌석 노드보다 우선
    "fpOffset": "0,-0.27,-0.55"})
