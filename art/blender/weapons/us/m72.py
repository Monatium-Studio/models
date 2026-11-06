"""M72 LAW 66 mm 대전차 로켓 (노획 미군 화기, 드론·장갑 대응).

npm run model -- art/blender/weapons/us/m72.py
npm run shot -- weapons/us/m72.glb --views side,34,top,muzzle

원점 = 방아쇠 막대 아래 발사관 축(오른손 파지점), 발사 방향 +Y.
기본 자세 = **전개(발사 준비)**: 내관이 뒤로 0.25 m 빠지고, 가늠자·가늠쇠가 서고, 앞뒤 마개가 매달려 있다.
접은(휴대) 상태는 각 파츠의 커스텀 속성으로 되돌린다 (docs/art/weapons-us.md 참고):
  tube_inner   stowMove = "0,0,-0.25"  (three.js, 앞으로 0.25 m 밀어 넣음)
  sight_front / sight_rear  회전을 0 → stowRotXDeg 만큼 X축 회전(앞으로 눕힘)
  cover_front / cover_rear  회전을 0으로 두면 닫힌 마개 (기본은 열려 매달린 각도)
실측: 접은 길이 0.63 m, 전개 길이 0.88 m, 외관 지름 ≈ 77 mm.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402

cb.reset()
b = us.Build("m72")

RO = 0.0385           # 외관 반지름 (유리섬유)
RI = 0.0345           # 내관 반지름 (알루미늄)
OY0, OY1 = -0.200, 0.430
EXT = 0.250
IY0 = OY0 - EXT       # 전개 시 내관 뒤끝
SZ = 0.066            # 조준선 높이
L_ = dict(right=(0, -1, 0), up=(0, 0, 1))
R_ = dict(right=(0, 1, 0), up=(0, 0, 1))

# ================================================================== outer tube (정지)
b.s(us.ytube("outer_tube", RO, RI + 0.001, OY0, OY1, verts=28, mat="od"))
b.s(us.ytube("front_band", RO + 0.0022, RI + 0.001, OY1 - 0.016, OY1, verts=28, mat="black"))
b.s(us.ytube("rear_band", RO + 0.0022, RI + 0.001, OY0, OY0 + 0.016, verts=28, mat="black"))
b.s(us.ycyl("mid_band", RO + 0.0015, 0.130, 0.148, verts=28, mat="black"))
b.s(us.ycyl("heat_band", RO + 0.0004, 0.350, 0.364, verts=28, mat="yellow"))
# 발사관 안 로켓 머리 (앞에서 보임)
b.s(us.ycyl("rocket_nose", 0.020, OY1 - 0.060, OY1 - 0.030, r2=0.006, verts=16, mat="od"))
b.s(us.ycyl("tube_dark", RI + 0.001, OY1 - 0.062, OY1 - 0.061, verts=20, mat="black"))
# 슬링 고리 (중간 띠 아래, 앞 띠 아래)
for y in (0.139, OY1 - 0.008):
    b.s(us.torus(f"sling_eye{y}", 0.0055, 0.0014, loc=(0, y, -RO - 0.006), rot=(0, 90, 0), seg=10, rseg=5,
                 mat="black"))

# 방아쇠 뭉치 (위, 원점)
b.s(us.boxr("trig_housing", -0.017, 0.017, -0.045, 0.078, RO - 0.010, RO + 0.020, bevel=0.006, seg=2, mat="od"))
b.s(us.boxr("trig_housing_base", -0.021, 0.021, -0.050, 0.083, RO - 0.012, RO + 0.004, bevel=0.003, mat="black"))
# 가늠자/가늠쇠 받침
b.s(us.boxr("rs_mount", -0.016, 0.016, -0.170, -0.130, RO - 0.006, RO + 0.006, bevel=0.003, mat="black"))
b.s(us.boxr("fs_mount", -0.020, 0.020, 0.372, 0.402, RO - 0.006, RO + 0.006, bevel=0.003, mat="black"))

# 표기: 왼쪽 (검정 스텐실), 오른쪽
b.f(us.text("mk_l1", "ROCKET, 66 MM: HEAT, M72A3", 0.0095, (-RO - 0.0004, 0.220, 0.012), mat="black", **L_))
b.f(us.text("mk_l2", "U.S.   LOT MNT-07", 0.0075, (-RO - 0.0004, 0.220, -0.004), mat="black", **L_))
b.f(us.text("mk_r1", "FRONT", 0.0110, (RO + 0.0004, 0.330, 0.004), mat="black", **R_))
b.f(us.text("mk_bb", "BACKBLAST AREA", 0.0080, (RO + 0.0004, -0.110, 0.004), mat="black", **R_))

# 엘프식: 흰 테이프 + 한글 낙서 (뒤쪽), 청록 페인트 번호
b.s(us.ycyl("tape", RO + 0.0012, -0.112, -0.078, verts=28, mat="paper"))
b.f(us.text("tape_kr", "후폭풍 주의!", 0.0110, (-RO - 0.0016, -0.095, 0.0), mat="black", font="kr", **L_))
b.f(us.text("paint_no", "MNT-L12", 0.0130, (-RO - 0.0004, 0.060, -0.020), mat="paint", **L_))

# ================================================================== moving parts
# 내관 (전개 위치)
b.p("tube_inner", us.ytube("inner_tube", RI, RI - 0.0025, IY0, OY0 + 0.040, verts=28, mat="steel"))
b.p("tube_inner", us.ytube("inner_rear_ring", RI + 0.0020, RI - 0.0025, IY0, IY0 + 0.012, verts=28, mat="black"))
b.p("tube_inner", us.ycyl("rocket_fins", RI - 0.0026, IY0 + 0.060, IY0 + 0.061, verts=20, mat="black"))
b.p("tube_inner", us.ycyl("rocket_motor", 0.012, IY0 + 0.061, IY0 + 0.080, verts=14, mat="steel"))
b.p("tube_inner", us.boxr("detent_lug", -0.006, 0.006, IY0 + 0.020, IY0 + 0.040, RI - 0.001, RI + 0.004,
                          bevel=0.0015, mat="black"))
b.pivot("tube_inner", (0, IY0, 0), stowMove=f"0,0,-{EXT}")

# 가늠쇠 (투명 레티클 틀 → 검정 틀 + 십자선)
FY = 0.388
fs = []
fs.append(us.boxr("fs_hinge", -0.016, 0.016, FY - 0.006, FY + 0.006, RO + 0.004, RO + 0.010, bevel=0.002, mat="black"))
for sx in (-1, 1):
    fs.append(us.boxr(f"fs_side{sx}", min(sx * 0.0165, sx * 0.0130), max(sx * 0.0165, sx * 0.0130), FY - 0.0015,
                      FY + 0.0015, RO + 0.008, SZ + 0.016, bevel=0.0008, mat="black"))
fs.append(us.boxr("fs_top", -0.0165, 0.0165, FY - 0.0015, FY + 0.0015, SZ + 0.013, SZ + 0.016, bevel=0.0008,
                  mat="black"))
fs.append(us.boxr("fs_cross_v", -0.0005, 0.0005, FY - 0.0004, FY + 0.0004, RO + 0.010, SZ + 0.013, mat="black"))
fs.append(us.boxr("fs_cross_h", -0.013, 0.013, FY - 0.0004, FY + 0.0004, SZ - 0.0005, SZ + 0.0005, mat="black"))
for i, z in enumerate((SZ - 0.006, SZ - 0.012, SZ - 0.018)):
    fs.append(us.boxr(f"fs_tick{i}", -0.0045 + i * 0.001, 0.0045 - i * 0.001, FY - 0.0004, FY + 0.0004, z - 0.0004,
                      z + 0.0004, mat="black"))
b.p("sight_front", *fs)
b.pivot("sight_front", (0, FY, RO + 0.007), stowRotXDeg=-90)

# 가늠자 (핍)
RY = -0.150
AP = 0.0065   # 핍 구멍 반폭 (게임용으로 실물보다 크게)
rs = [us.boxr("rs_hinge", -0.013, 0.013, RY - 0.006, RY + 0.006, RO + 0.004, RO + 0.010, bevel=0.002, mat="black")]
for sx in (-1, 1):
    rs.append(us.boxr(f"rs_side{sx}", min(sx * 0.0125, sx * AP), max(sx * 0.0125, sx * AP), RY - 0.0018,
                      RY + 0.0018, RO + 0.008, SZ + 0.012, bevel=0.0008, mat="black"))
rs.append(us.boxr("rs_low", -AP, AP, RY - 0.0018, RY + 0.0018, RO + 0.008, SZ - AP, mat="black"))
rs.append(us.boxr("rs_high", -AP, AP, RY - 0.0018, RY + 0.0018, SZ + AP, SZ + 0.012, mat="black"))
b.p("sight_rear", *rs)
b.pivot("sight_rear", (0, RY, RO + 0.007), stowRotXDeg=-90)

# 방아쇠 막대 (고무)
b.p("trigger", us.boxr("trigger_bar", -0.008, 0.008, -0.012, 0.040, RO + 0.019, RO + 0.027, bevel=0.003, seg=2,
                       mat="black"))
b.pivot("trigger", (0, 0.014, RO + 0.020), move="0,-0.004,0")

# 안전(장전) 손잡이
AH = (0, 0.072, RO + 0.020)
b.p("arming_handle", us.boxr("ah_stem", -0.003, 0.003, AH[1] - 0.003, AH[1] + 0.003, AH[2], AH[2] + 0.016,
                             bevel=0.001, mat="black"))
b.p("arming_handle", us.boxr("ah_grip", -0.011, 0.011, AH[1] - 0.004, AH[1] + 0.004, AH[2] + 0.012, AH[2] + 0.019,
                             bevel=0.0025, mat="black"))
b.pivot("arming_handle", AH, rotAxis="x", rotDeg=-75, note="SAFE upright, rotate forward to ARM")

# 앞 마개 (열려 앞 아래로 매달림)
FC = (0, OY1, -RO - 0.002)
b.p("cover_front", us.ycyl("fc_cup", RO + 0.0035, OY1, OY1 + 0.024, verts=24, bevel=0.003, seg=1, mat="black"))
b.p("cover_front", us.boxr("fc_strap", -0.006, 0.006, OY1 - 0.010, OY1 + 0.004, -RO - 0.004, -RO + 0.002,
                           mat="black"))
b.pivot("cover_front", FC, rest_rot=(-105, 0, 0), stowRotXDeg=0)

# 뒤 마개 (아래로 열림)
RC = (0, IY0, -RI - 0.003)
b.p("cover_rear", us.ycyl("rc_cup", RI + 0.0045, IY0 - 0.026, IY0, verts=24, bevel=0.003, seg=1, mat="black"))
b.p("cover_rear", us.boxr("rc_hinge", -0.008, 0.008, IY0 - 0.004, IY0 + 0.006, -RI - 0.006, -RI + 0.001,
                          bevel=0.0015, mat="black"))
b.pivot("cover_rear", RC, rest_rot=(100, 0, 0), stowRotXDeg=0)

# ================================================================== anchors
b.anchor("muzzle", (0, OY1, 0))
b.anchor("backblast", (0, IY0, 0), parent="tube_inner")
b.anchor("grip_support", (0, 0.215, 0))
b.anchor("sight_eye", (0, -0.300, SZ))
b.anchor("shoulder", (0, -0.090, -RO))

b.finish("weapons/us/m72.glb", outline=0.002, fp="0.17,-0.15,-0.3")
