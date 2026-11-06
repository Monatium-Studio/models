"""모나티엄 진압반 MR-12 '토닥토닥' 고무탄 경기관총 (차량 거치).

[원작] 교주 차원 진압반은 고무탄을 쓴다(엘리아스 침공전: 흑뉴아가 진압반의 고무탄에 당황). 알레트의 진압 방패.
[오리지널] MR-7C '자장가' 카빈의 고무탄을 벨트로 먹이는 거치용 경기관총. MRV-3 '괭이잠' 사이드카 앞의 회전대에 단다.
           손 전체를 감싸는 D자 쌍손잡이(교주 차원 화기 문법)와 투명 진압 방패가 붙은 것이 특징이다.

규약: 원점 = 트러니언(상하 회전축, 좌우 회전축과 만나는 점), 총구 +Y, 위 +Z, 사수 오른쪽 +X.
      차량 쪽 mount_* 노드(같은 점)에 변환 없이 붙인다. 회전대 핀 바닥은 원점 아래 pivotDrop(0.09 m).
움직이는 파츠: yoke (counterPitch=1: 피치만큼 되돌려 받침이 서 있게), charging_handle (move), trigger (rotAxis x)
npm run model -- art/blender/weapons/monatium/mount_mr12.py
npm run shot -- weapons/monatium/mount_mr12.glb --views side,34,top,muzzle
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import vehicles_elf as ve  # noqa: E402

cb.reset()
W = ve.Mount("mount_mr12", "monatium")
M = W.M
BZ = 0.115                  # 총열 축
TZ = 0.090                  # 요크 축 (상하 회전 중심)
RW = 0.075                  # 리시버 폭

# ------------------------------------------------------------------ 요크 (U자 받침) + 회전 핀
# 요크는 좌우로만 돈다: 별도 파츠(counterPitch=1 → 런타임이 피치만큼 되돌림)
W.p("yoke", hw.zcyl("pin", 0.022, -0.06, 0.012, verts=14, mat=M["steel"]),
    hw.zcyl("yoke_base", 0.040, 0.0, 0.025, verts=18, bevel=0.005, seg=1, mat=M["gear"]))
for sx in (1, -1):
    x0, x1 = sorted((sx * (RW / 2 + 0.004), sx * (RW / 2 + 0.020)))
    W.p("yoke", ve.rbox("yoke_arm", x0, x1, -0.025, 0.025, 0.012, TZ + 0.02, r=0.004, mat=M["gear"]))
W.p("yoke", ve.rbox("yoke_floor", -(RW / 2 + 0.02), RW / 2 + 0.02, -0.025, 0.025, 0.012, 0.028, r=0.004,
                    mat=M["gear"]),
    hw.xcyl("trunnion", 0.012, -(RW / 2 + 0.026), RW / 2 + 0.026, z=TZ, verts=12, mat=M["steel"]))
W.pivot("yoke", (0, 0, TZ), counterPitch=1)

# ------------------------------------------------------------------ 리시버 (둥근 상자) + 덮개 + 운반 손잡이
rec_side = ve.round_poly([(-0.21, 0.065), (0.10, 0.065), (0.11, 0.15), (0.06, 0.165), (-0.18, 0.165), (-0.22, 0.13)],
                         [0.015, 0.015, 0.015, 0.02, 0.025, 0.02], 3)
W.s(ve.sculpt("receiver", rec_side, hw.rrect(RW, 0.10, 0.018, 3, cy=0.115), bevel=0.004, seg=2, mat=M["hull"]))
W.s(ve.rbox("cover", -0.032, 0.032, -0.17, 0.05, 0.160, 0.176, r=0.006, seg=2, mat=M["hull_d"]))
W.s(hw.sweep("carry", [(0, 0.05, 0.14), (0, 0.065, 0.172), (0, 0.155, 0.172), (0, 0.17, 0.14)],
             [(math.cos(2 * math.pi * k / 6) * 0.008, math.sin(2 * math.pi * k / 6) * 0.008) for k in range(6)],
             side_vec=(1, 0, 0), mat=M["gear"]))
# 왼쪽 원판 + 금색 로고, 각인
frL = ve.frame((-1, 0, 0))
frR = ve.frame((1, 0, 0))
W.s(ve.logo_disc("rec_", (-(RW / 2 + 0.0005), -0.07, 0.115), 0.045, frL, disc=M["hull_d"], rim=M["gold"],
                 mark=M["gold"], lift=0.0005))
W.s(ve.text("mk_type", "MR-12", 0.014, (-(RW / 2 + 0.0005), 0.03, 0.135), frL, mat=M["steel"], lift=0.0006))
W.s(ve.text("mk_less", "고무탄", 0.013, (-(RW / 2 + 0.0005), 0.03, 0.095), frL, mat=M["teal"], lift=0.0006))
W.s(ve.decal("eject_port", hw.rrect(0.055, 0.026, 0.008, 3), (RW / 2 + 0.0005, -0.03, 0.125), frR, lift=0.0006,
             mat=M["rubber"]))
for y in (-0.17, 0.07):
    for sx, fr in ((1, frR), (-1, frL)):
        W.s(ve.decal(f"pin{sx}{y}", hw.circle(0.005, 10), (sx * (RW / 2 + 0.0005), y, 0.08), fr, lift=0.0006,
                     mat=M["steel"]))

# ------------------------------------------------------------------ 총열 덮개(스타디움 창) · 청록 띠 · 금색 총구 고리
W.s(hw.ycyl("shroud", 0.027, 0.10, 0.40, z=BZ, verts=20, bevel=0.003, seg=1, mat=M["hull"]))
for sx, fr in ((1, frR), (-1, frL)):
    for i, y in enumerate((0.15, 0.21, 0.27, 0.33)):
        W.s(ve.decal(f"sh_win{sx}{i}", hw.stadium(0.040, 0.012, 4), (sx * 0.027, y, BZ + 0.002), fr, lift=0.0006,
                     mat=M["gear"]))
W.s(hw.ycyl("barrel", 0.014, 0.40, 0.50, z=BZ, verts=14, mat=M["gear"]))
W.s(hw.tube("band_teal", 0.0285, 0.014, 0.36, 0.385, c=(0, BZ), verts=20, mat=M["teal"]))
W.s(hw.tube("muzzle_ring", 0.020, 0.010, 0.485, 0.515, c=(0, BZ), verts=18, r_out2=0.024, mat=M["gold"]))
# 가늠쇠 (보호 귀 + 시안 점) / 고리 가늠자. 점과 고리 가운데는 총열 축과 나란한 한 선(SZ = sight_eye 높이) 위:
# 정조준하면 점이 화면 가운데(탄착점)에 온다 (예전에는 점이 0.02 m 낮아 1.5° 아래에 보였다)
SZ = 0.205
W.s(ve.rbox("fs_base", -0.012, 0.012, 0.37, 0.39, BZ + 0.025, BZ + 0.035, mat=M["gear"]))
for sx in (1, -1):
    W.s(ve.rbox("fs_ear", sx * 0.011 - 0.003, sx * 0.011 + 0.003, 0.372, 0.388, BZ + 0.035, SZ + 0.005, mat=M["gear"]))
W.s(ve.bar("fs_post", (0, 0.38, BZ + 0.035), (0, 0.38, SZ - 0.002), 0.0025, verts=6, mat=M["gear"]))
W.s(cb.sphere("fs_dot", radius=0.004, loc=(0, 0.38, SZ), segments=8, rings=4, material=M["glow"]))
W.s(hw.torus("rear_ring", 0.014, 0.003, loc=(0, -0.15, SZ), rot=(90, 0, 0), seg=14, rseg=5, mat=M["gear"]))
W.s(ve.bar("rear_ring_post", (0, -0.15, 0.176), (0, -0.15, SZ - 0.014), 0.004, verts=6, mat=M["gear"]))

# ------------------------------------------------------------------ 탄통 (왼쪽, 청록 띠) + 급탄 슈트
W.s(ve.rbox("ammo_box", -(RW / 2 + 0.11), -(RW / 2 + 0.005), -0.11, 0.04, 0.015, 0.12, r=0.010, seg=2,
            mat=M["hull_d"]))
W.s(ve.rbox("ammo_band", -(RW / 2 + 0.112), -(RW / 2 + 0.003), -0.11, 0.04, 0.085, 0.100, mat=M["teal"]))
W.s(ve.rbox("ammo_lid", -(RW / 2 + 0.105), -(RW / 2 + 0.010), -0.105, 0.035, 0.118, 0.128, r=0.004, mat=M["gear"]))
W.s(ve.text("ammo_mk", "비살상", 0.016, (-(RW / 2 + 0.112), -0.035, 0.055), frL, mat=M["steel"], lift=0.0006))

# ------------------------------------------------------------------ 투명 진압 방패 (총열 덮개 뒤쪽)
shield = ve.round_poly([(-0.17, 0.0), (0.17, 0.0), (0.17, 0.20), (0.10, 0.25), (-0.10, 0.25), (-0.17, 0.20)],
                       [0.03, 0.03, 0.04, 0.05, 0.05, 0.04], 2)
W.s(ve.slab("shield", shield, (0, 0.105, 0.02), (1, 0, 0), (0, 0, 1), 0.008, mat=M["glass"]))
W.s(ve.loop_frame("shield_rim", shield, (0, 0.105, 0.02), (1, 0, 0), (0, 0, 1), r=0.007, lift=-0.004, mat=M["gear"],
                  verts=4))
W.s(ve.rbox("shield_clamp", -0.03, 0.03, 0.095, 0.115, 0.07, 0.15, r=0.006, mat=M["gear"]))
W.s(ve.slab("shield_band", [(-0.165, 0.02), (0.165, 0.02), (0.165, 0.045), (-0.165, 0.045)], (0, 0.104, 0.02),
            (1, 0, 0), (0, 0, 1), 0.010, mat=M["teal"]))

# ------------------------------------------------------------------ 뒤 D자 쌍손잡이 (엘프 장갑 손 전체를 감싼다)
for sx in (1, -1):
    path = [(sx * 0.050, -0.20, 0.135)] + [(sx * 0.050, -0.20 - 0.07 * math.sin(math.radians(a)),
                                              0.095 + 0.04 * math.cos(math.radians(a))) for a in range(0, 181, 30)] \
        + [(sx * 0.050, -0.20, 0.055)]
    W.s(hw.sweep(f"d_grip{sx}", path, [(math.cos(2 * math.pi * k / 6) * 0.009, math.sin(2 * math.pi * k / 6) * 0.009)
                                        for k in range(6)], side_vec=(1, 0, 0), mat=M["gear"]))
    W.s(ve.bar(f"grip{sx}", (sx * 0.050, -0.27, 0.07), (sx * 0.050, -0.27, 0.12), 0.013, verts=10, mat=M["rubber"]))
W.s(ve.rbox("grip_bridge", -0.05, 0.05, -0.215, -0.195, 0.075, 0.115, r=0.005, mat=M["gear"]))
# 엄지 방아쇠 (나비형, 청록)
W.p("trigger", ve.rbox("trig", -0.022, 0.022, -0.232, -0.222, 0.082, 0.108, r=0.004, mat=M["teal"]))
W.pivot("trigger", (0, -0.222, 0.095), rotAxis="x", rotDeg=12)
# 장전 손잡이 (오른쪽)
W.p("charging_handle", ve.rbox("ch_slide", RW / 2 - 0.002, RW / 2 + 0.010, -0.12, -0.06, 0.135, 0.150, r=0.003,
                               mat=M["gear"]),
    ve.bar("ch_knob", (RW / 2 + 0.008, -0.075, 0.1425), (RW / 2 + 0.032, -0.075, 0.1425), 0.008, verts=8, mat=M["teal"]))
W.pivot("charging_handle", (RW / 2, -0.09, 0.1425), move=hw.mv(0, -0.06, 0))

W.anchor("muzzle", (0, 0.515, BZ))
W.anchor("eject", (RW / 2 + 0.004, -0.03, 0.125))
W.anchor("sight_eye", (0, -0.36, SZ))
W.anchor("grip_R", (0.050, -0.27, 0.095))
W.anchor("grip_support", (-0.050, -0.27, 0.095))
W.anchor("trunnion", (0, 0, TZ))
W.finish("weapons/monatium/mount_mr12.glb", outline=0.003, budget=8000, origin=(0, 0, TZ), props={
    "displayName": "MR-12 '토닥토닥' 고무탄 경기관총", "ammo": "rubber", "pivotDrop": TZ,
    # 사수 눈 (회전축 기준, three 카메라 공간: 회전축이 눈의 0.22 m 아래·0.48 m 앞). 투명 방패 테 위로 넘겨 보고,
    # 고리 가늠자가 지향 사격 조준점을 가리지 않는다 (좌석 노드 자리는 고리가 조준점에 겹쳤다)
    "fpOffset": "0,-0.22,-0.48"})
