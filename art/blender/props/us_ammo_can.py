"""M2A1 탄약 상자 (노획 미군 물자 소품, 모나티엄 창고 보관분).

npm run model -- art/blender/props/us_ammo_can.py
npm run shot -- props/us_ammo_can.glb --views front,34,side,top

원점 = 바닥 중심, 긴 축 = X. 실측 ≈ 0.305 x 0.155 x 0.190 m.
움직이는 파츠: lid(뒤 긴 변 경첩, X축 회전), latch(앞 짧은 변 잠금 레버), handle(접이 손잡이).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402

cb.reset()
b = us.Build("us_ammo_can")

LX, LY, H = 0.305, 0.155, 0.168
HL = 0.026      # 뚜껑 높이
F_ = dict(right=(1, 0, 0), up=(0, 0, 1))      # -Y 면
B_ = dict(right=(-1, 0, 0), up=(0, 0, 1))     # +Y 면
S_ = dict(right=(0, -1, 0), up=(0, 0, 1))     # +X 면? (오른쪽 끝)

b.s(us.boxr("body", -LX / 2, LX / 2, -LY / 2, LY / 2, 0.0, H, bevel=0.008, seg=2, mat="od"))
# 옆면 보강 홈 (앞뒤 긴 면에 가로 리브)
for sy in (-1, 1):
    for z in (0.045, 0.110):
        b.s(us.boxr(f"rib{sy}{z}", -LX / 2 + 0.020, LX / 2 - 0.020, min(sy * LY / 2, sy * (LY / 2 + 0.003)),
                    max(sy * LY / 2, sy * (LY / 2 + 0.003)), z, z + 0.012, bevel=0.002, mat="od"))
# 위 테두리 (말린 가장자리)
b.s(us.boxr("rim", -LX / 2 - 0.003, LX / 2 + 0.003, -LY / 2 - 0.003, LY / 2 + 0.003, H - 0.008, H, bevel=0.003,
            mat="od"))
# 경첩 (뒤 긴 변)
b.s(us.xcyl("hinge", 0.0055, -LX / 2 + 0.030, LX / 2 - 0.030, y=LY / 2 + 0.004, z=H + 0.002, verts=12, mat="od"))
# 잠금 레버 받침 (앞 짧은 변, +X)
b.s(us.boxr("latch_base", LX / 2, LX / 2 + 0.010, -0.030, 0.030, H - 0.050, H - 0.010, bevel=0.003, mat="od"))

# 스텐실 (노랑)
b.f(us.text("st1", "CARTRIDGES 5.56 MM", 0.0170, (0, -LY / 2 - 0.0005, 0.139), mat="yellow", **F_))
b.f(us.text("st2", "LINKED  M855 / M856  4 & 1", 0.0115, (0, -LY / 2 - 0.0005, 0.090), mat="yellow", **F_))
b.f(us.text("st3", "800 CTGS   LOT WCC07-0412", 0.0105, (0, -LY / 2 - 0.0005, 0.035), mat="yellow", **F_))
b.f(us.text("st_b", "5.56 MM", 0.0240, (0, LY / 2 + 0.0005, 0.085), mat="yellow", **B_))
# 모나티엄 창고 페인트 + 스티커
b.f(us.boxr("mnt_band", -LX / 2 - 0.0006, -LX / 2 + 0.0, -LY / 2 + 0.006, LY / 2 - 0.006, 0.066, 0.104, mat="paint"))
b.f(us.text("mnt_no", "MNT-07", 0.024, (-LX / 2 - 0.0008, 0, 0.085), mat="paper", right=(0, -1, 0), up=(0, 0, 1)))
b.f(us.boxr("sticker", -0.135, -0.075, -LY / 2 - 0.0006, -LY / 2, 0.050, 0.080, mat="paper"))
b.f(us.text("sticker_t", "진압반 병기고", 0.0085, (-0.105, -LY / 2 - 0.0008, 0.0705), mat="od", font="kr", **F_))
b.f(us.text("sticker_n", "B-0412", 0.0080, (-0.105, -LY / 2 - 0.0008, 0.0585), mat="od", **F_))

# ================================================================== lid (경첩 = 뒤 긴 변)
b.p("lid", us.boxr("lid_plate", -LX / 2 - 0.004, LX / 2 + 0.004, -LY / 2 - 0.004, LY / 2 + 0.004, H, H + HL,
                   bevel=0.007, seg=2, mat="od"))
b.p("lid", us.boxr("lid_ridge", -LX / 2 + 0.030, LX / 2 - 0.030, -LY / 2 + 0.025, LY / 2 - 0.025, H + HL - 0.002,
                   H + HL + 0.004, bevel=0.003, mat="od"))
for sx in (-1, 1):
    b.p("lid", us.boxr(f"handle_mount{sx}", sx * 0.070 - 0.010, sx * 0.070 + 0.010, -0.010, 0.010, H + HL + 0.002,
                       H + HL + 0.012, bevel=0.003, mat="od"))
b.pivot("lid", (0, LY / 2 + 0.004, H + 0.002), rotAxis="x", rotDeg=-105)

# 손잡이 (접힌 상태, 뚜껑 위)
hp = [(-0.070, 0, H + HL + 0.009), (-0.064, 0.0, H + HL + 0.020), (0.064, 0.0, H + HL + 0.020),
      (0.070, 0, H + HL + 0.009)]
b.p("handle", us.sweep("handle_bar", hp, us.circle_pts(0.0045, 8), side_vec=(0, 1, 0), mat="od", smooth=50))
b.pivot("handle", (0, 0, H + HL + 0.009), rotAxis="z", rotDeg=90, note="rotate up around can long axis")
b.sub("handle", "lid")

# 잠금 레버 (앞 짧은 변)
lp = [(LX / 2 + 0.011, 0.0, H - 0.040), (LX / 2 + 0.014, 0.0, H + 0.010), (LX / 2 + 0.008, 0.0, H + HL + 0.004)]
b.p("latch", us.sweep("latch_arm", lp, us.rrect(0.040, 0.006, 0.002, n=1), side_vec=(0, 1, 0), mat="od", smooth=40))
b.pivot("latch", (LX / 2 + 0.011, 0.0, H - 0.040), rotAxis="z", rotDeg=-60)

# 창고 태그 (손잡이 고리에 묶어 뚜껑 위에 눕힘)
hole = (0.058, 0.030, H + HL + 0.0045)
tag_pts = [(-0.012, -0.019), (0.012, -0.019), (0.012, 0.013), (0.006, 0.019), (-0.006, 0.019), (-0.012, 0.013)]
tag = us.side("tag", [(0.0 + u, 0.0 + v) for (u, v) in tag_pts], 0.0009, mat="paper")
tfine = [us.text("tag_t", "MNT", 0.0085, (0.00046, 0.0, 0.006), mat="od", right=(0, 1, 0), up=(0, 0, 1)),
         us.boxr("tag_band", 0.00046, 0.00066, -0.012, 0.012, -0.004, 0.0, mat="paint"),
         us.text("tag_n", "B-0412", 0.0042, (0.00070, 0.0, -0.002), mat="paper", right=(0, 1, 0), up=(0, 0, 1))]
for o in [tag] + tfine:
    us.xform(o, rot=(0, -90, 20), loc=hole)
b.p("lid", tag)
b.pf("lid", *tfine)

b.anchor("socket_carry", (0, 0, H + HL + 0.020))

b.finish("props/us_ammo_can.glb", outline=0.003, fp="0,0,0")
