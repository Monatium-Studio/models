"""M67 세열수류탄 (노획 미군 화기, 투척).

npm run model -- art/blender/weapons/us/m67.py
npm run shot -- weapons/us/m67.glb --views side,34,top,muzzle

원점 = 몸통 중심(오른손이 감싸 쥐는 점). 위 +Z = 신관, 안전손잡이(spoon)는 +X 쪽(오른손 손바닥),
안전핀 고리(pin)는 -X 쪽(왼손으로 뽑음), 총구 규칙 대신 +Y = 던지는 방향.
실측: 몸통 지름 63.5 mm, 신관 포함 높이 ≈ 90 mm.
움직이는 파츠: spoon(경첩 축 Y로 회전해 튀어나감), pin(고리+핀, -X로 뽑힘), clip(안전 클립).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402

cb.reset()
b = us.Build("m67")

R = 0.03175
F0 = R - 0.004          # 신관 목 시작 높이
FZ = 0.040              # 핀 높이
L_ = dict(right=(0, -1, 0), up=(0, 0, 1))
F_ = dict(right=(-1, 0, 0), up=(0, 0, 1))   # -Y 면(앞에서 보이는 면)

# ================================================================== body
body = cb.sphere("body", radius=R, segments=28, rings=16, material=us.M("od"))
b.s(body)
# 아래 이음매 링
b.s(us.zcyl("seam", R * 0.62, -R * 0.80, -R * 0.76, verts=28, mat="od"))
# 노랑 고폭 띠 (몸통 윗부분)
zb0, zb1 = 0.0185, 0.0230
r0 = math.sqrt(R * R - zb0 * zb0) + 0.0005
r1 = math.sqrt(R * R - zb1 * zb1) + 0.0005
b.s(us.zcyl("yellow_band", r0, zb0, zb1, r2=r1, verts=28, mat="yellow"))
# 신관 목 + 신관 몸체 (M213)
b.s(us.zcyl("fuze_neck", 0.0105, F0, F0 + 0.007, verts=18, mat="od"))
b.s(us.zcyl("fuze_body", 0.0098, F0 + 0.007, 0.047, verts=18, bevel=0.0012, seg=1, mat="od"))
b.s(us.zcyl("fuze_top", 0.0080, 0.047, 0.0505, r2=0.0066, verts=18, mat="od"))
# 핀 구멍 귀 (양쪽)
for sx in (-1, 1):
    b.s(us.boxr(f"pin_ear{sx}", min(sx * 0.0085, sx * 0.0125), max(sx * 0.0085, sx * 0.0125), -0.0045, 0.0045,
                FZ - 0.005, FZ + 0.005, bevel=0.0012, mat="od"))
# 표기 (앞면 -Y, 노랑 스텐실) + 모나티엄 표식
b.f(us.text("mk_m67", "M67", 0.0105, (0, -R - 0.0012, 0.002), mat="yellow", right=(1, 0, 0), up=(0, 0, 1)))
b.f(us.text("mk_lot", "LOT 07", 0.0050, (0, -R + 0.0006, -0.011), mat="yellow", right=(1, 0, 0), up=(0, 0, 1)))
b.f(us.text("mk_mnt", "MNT", 0.0080, (0, R + 0.0012, 0.0), mat="paint", right=(-1, 0, 0), up=(0, 0, 1)))
b.f(us.zcyl("paint_dot", 0.0045, 0.0505, 0.0510, verts=14, mat="paint"))

# ================================================================== spoon (안전손잡이, +X)
sp = [(-0.0040, 0.0525), (0.0030, 0.0545), (0.0095, 0.0525), (0.0122, 0.0470), (0.0128, 0.0380),
      (0.0150, 0.0300)]
for a in range(60, -31, -15):
    ar = math.radians(a)
    sp.append(((R + 0.0022) * math.cos(ar), (R + 0.0022) * math.sin(ar)))
path = [(x, 0.0, z) for (x, z) in sp]
w = [(0.65, 1.0)] + [(1.0, 1.0)] * (len(path) - 3) + [(0.80, 1.0), (0.65, 1.0)]
b.p("spoon", us.sweep("spoon_strip", path, [(-0.0072, -0.0010), (0.0072, -0.0010), (0.0072, 0.0010),
                                            (-0.0072, 0.0010)], side_vec=(0, 1, 0), mat="od", smooth=40, scales=w))
b.pivot("spoon", (0.0090, 0.0, 0.0510), rotAxis="z", rotDeg=120, note="flies off around hinge on release")
# 스푼 위 테이프 (엘프식 보강: 청록 페인트 줄)
b.pf("spoon", us.text("spoon_no", "07", 0.0055, (R + 0.0034, 0, 0.012), mat="paint", right=(0, 1, 0),
                      up=(0, 0, 1)))

# ================================================================== pin + pull ring (-X)
b.p("pin", us.xcyl("pin_wire", 0.0011, -0.0160, 0.0140, y=0.0, z=FZ, verts=8, mat="bright"))
b.p("pin", us.torus("pull_ring", 0.0115, 0.0016, loc=(-0.0275, 0.0, FZ - 0.003), rot=(90, 0, 0), seg=20, rseg=6,
                    mat="bright"))
b.p("pin", us.torus("pin_loop", 0.0030, 0.0009, loc=(-0.0162, 0.0, FZ - 0.0005), rot=(90, 0, 0), seg=10, rseg=5,
                    mat="bright"))
b.pivot("pin", (-0.0160, 0.0, FZ), move="-0.05,0,0")

# ================================================================== safety clip
cl = []
for a in range(-150, 151, 25):
    ar = math.radians(a)
    cl.append((0.0105 * math.cos(ar) + 0.0012, 0.0105 * math.sin(ar), 0.0335))
cl.append((0.0150, -0.0040, 0.0320))
cl.append((0.0172, 0.0, 0.0300))
b.p("clip", us.sweep("clip_wire", cl, us.circle_pts(0.0008, 5), side_vec=(0, 0, 1), mat="bright"))
b.pivot("clip", (0.012, 0.0, 0.0335), move="0.03,0,0")

# ================================================================== anchors
b.anchor("grip_support", (-0.0275, 0.0, FZ - 0.003), parent="pin")   # 왼손이 당기는 고리 중심
b.anchor("throw_release", (0.0, 0.0, 0.0))

b.finish("weapons/us/m67.glb", outline=0.0016, fp="0.1,-0.09,-0.24")
