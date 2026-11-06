"""엘피니아 7식 소총 '톱니' (엘피니아 군 제식 화기).

[오리지널] 지구 침공 당시 엘피니아 정규군의 제식 소총. 화약식 실탄, 30발 탄창, 불펍 배치.
[원작] 엘프는 화약식 총기와 광선총을 섞어 쓴다. 침공군의 광자 무기는 출력이 낮아 지구군에 먹히지 않았다.
→ 실탄을 쏘는 소총이지만 조준기와 잔탄 표시창은 광자 시대의 시안 발광을 쓴다.

형태 근거 (원작 엘프 화기의 형태 언어, docs/art/weapons-home.md 2장)
  - 레이지의 'XG-레이저' 소총: 불펍, 긴 총열, 개머리 옆 둥근 구멍 줄, 표시창
  - 칸나의 발사기: 금색 총구 고리, 위 운반 손잡이, 손을 감싸는 D자 고리
  - 시온의 저격총 메모: 팔이 짧은 엘프용으로 방아쇠를 개머리 쪽으로 당겨 붙인다

npm run model -- art/blender/weapons/elfinia/elfinia_rifle.py
npm run shot -- weapons/elfinia/elfinia_rifle.glb --views side,34,top,muzzle --focus elfinia_rifle
npm run shot -- weapons/elfinia/elfinia_rifle.glb --mode fp
npm run shot -- weapons/elfinia/elfinia_rifle.glb --mode fp --ads 1
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402

cb.reset()
g = hw.Gun("elfinia_rifle")

BZ = 0.070          # 총열 축 높이
SZ = 0.150          # 조준선 높이 (광점 조준기 중심)
W_LOW = 0.036       # 아래 몸통(회녹) 폭
W_UP = 0.030        # 위 리시버(건메탈) 폭

# ================================================================== 아래 몸통 + 개머리 (회녹)
low_pts = [
    (-0.200, -0.016), (-0.150, -0.010), (-0.118, -0.002), (-0.112, 0.010), (-0.046, 0.010), (-0.040, 0.020),
    (0.012, 0.022), (0.096, 0.028), (0.108, 0.036), (0.110, 0.062), (-0.150, 0.062), (-0.168, 0.068),
    (-0.178, 0.090), (-0.190, 0.099), (-0.200, 0.097), (-0.206, 0.086), (-0.207, 0.000),
]
g.s(hw.side("low_shell", low_pts, W_LOW, bevel=0.0055, seg=3, mat="olive"))
# 개머리 패드 (고무)
pad_pts = [(-0.214, -0.012), (-0.204, -0.017), (-0.204, 0.096), (-0.214, 0.090)]
g.s(hw.side("butt_pad", pad_pts, W_LOW + 0.002, bevel=0.003, seg=2, mat="dark"))
# 개머리 옆 둥근 구멍 줄 (레이지 소총의 구멍 줄) + 분리선
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    x = sx * W_LOW / 2
    g.f(*hw.holes(f"butt_hole{sx}", (x, -0.150, 0.026), 4, 0.0135, 0.0036, along=(sx * -1, 0), mat="dark", **fr))
    g.f(hw.decal(f"seam{sx}", [(-0.0006, -0.030), (0.0006, -0.030), (0.0006, 0.030), (-0.0006, 0.030)],
                 (x, -0.120, 0.034), mat="dark", **fr))
    # 핀
    for (y, z) in ((-0.135, 0.050), (0.075, 0.046), (-0.030, 0.046)):
        g.f(hw.decal(f"pin{sx}{y}", hw.circle(0.0022, 10), (x, y, z), mat="steel", **fr))
        g.f(hw.decal(f"pinc{sx}{y}", hw.circle(0.0009, 8), (x, y, z), lift=0.0008, mat="dark", **fr))

# ================================================================== 위 리시버 (자줏빛 건메탈, 둥근 단면)
up_side = [(-0.184, 0.056), (0.200, 0.056), (0.208, 0.062), (0.208, 0.094), (0.198, 0.102), (-0.168, 0.102),
           (-0.184, 0.092)]
up_sec = hw.rrect(W_UP, 0.050, 0.013, n=4, cy=0.079)
g.s(hw.sculpt("upper", up_side, up_sec, bevel=0.0025, seg=2, mat="metal"))
# 앞쪽 통풍 창 (스타디움, 양쪽)
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    x = sx * W_UP / 2 + sx * 0.0004
    for i, y in enumerate((0.128, 0.153, 0.178)):
        g.f(hw.decal(f"vent{sx}{i}", hw.stadium(0.019, 0.0075, 5), (x, y, 0.083), mat="dark", **fr))
    # 윗면 홈 줄 (손 미끄럼 방지)
for i in range(6):
    g.f(hw.decal(f"top_rib{i}", hw.rrect(0.016, 0.0018, 0.0008, 1), (0, 0.120 + i * 0.012, 0.1024),
                 mat="dark", **hw.TOP))
# 배출구 (오른쪽, 손잡이 뒤 = 불펍 약실)
g.f(hw.decal("eject_port", hw.rrect(0.036, 0.014, 0.004, 2), (W_UP / 2 + 0.0004, -0.070, 0.079),
             mat="dark", **hw.RIGHT))
g.s(hw.boxr("eject_lip", W_UP / 2 - 0.001, W_UP / 2 + 0.0025, -0.090, -0.050, 0.0700, 0.0718, bevel=0.0008,
            mat="metal"))

# 왼쪽 배출구 덮개 (불펍: 왼손잡이 전환용 막힌 배출구) + 나사, 형식 각인
g.s(hw.side("port_cover", hw.rrect(0.050, 0.020, 0.006, 3, cx=-0.072, cy=0.079), 0.002, x=-W_UP / 2 - 0.0002,
            bevel=0.0007, seg=1, mat="olive_d"))
for y in (-0.092, -0.052):
    g.f(hw.decal(f"cover_screw{y}", hw.circle(0.0018, 8), (-W_UP / 2 - 0.0013, y, 0.079), mat="steel", **hw.LEFT))
g.f(hw.text("mk_army", "엘피니아 육군", 0.0058, (-W_UP / 2 - 0.0004, 0.010, 0.064), mat="steel", **hw.LEFT))

# ================================================================== 앞 손받침 (회녹)
hg_side = [(0.104, 0.060), (0.104, 0.034), (0.116, 0.026), (0.186, 0.026), (0.196, 0.020), (0.202, 0.024),
           (0.200, 0.060)]
g.s(hw.sculpt("handguard", hg_side, hw.rrect(0.034, 0.060, 0.012, n=3, cy=0.042), bevel=0.003, seg=2,
              mat="olive"))
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    for i in range(4):
        g.f(hw.decal(f"hg_grip{sx}{i}", hw.stadium(0.012, 0.0028, 3, angle=90),
                     (sx * 0.0171, 0.134 + i * 0.013, 0.040), mat="olive_d", **fr))

# ================================================================== 총열 · 가스 블록 · 소염기 · 금색 총구 고리
g.s(hw.ycyl("barrel", 0.0085, 0.200, 0.300, z=BZ, verts=16, mat="dark"))
g.s(hw.ycyl("gas_block", 0.0102, 0.236, 0.252, z=BZ, verts=16, bevel=0.0012, mat="metal"))
g.s(hw.ycyl("gas_tube", 0.0036, 0.205, 0.240, z=BZ + 0.012, verts=10, mat="metal"))
g.s(hw.muzzle_ring("ring_rear", 0.205, 0.213, 0.0118, z=BZ, mat="gold"))
g.s(hw.ycyl("flash_hider", 0.0104, 0.296, 0.330, z=BZ, verts=18, r2=0.0108, mat="metal"))
for k in range(4):
    a = math.radians(45 + 90 * k)
    cx, cz = math.cos(a) * 0.0109, math.sin(a) * 0.0109
    n = (math.cos(a), 0, math.sin(a))
    rt = (0, 1, 0)
    up = (-math.sin(a), 0, math.cos(a))
    g.f(hw.decal(f"fh_slot{k}", hw.stadium(0.016, 0.0034, 3), (cx, 0.311, BZ + cz), right=rt, up=up,
                 mat="dark"))
g.s(hw.tube("muzzle_crown", 0.0118, 0.0058, 0.329, 0.338, c=(0, BZ), verts=20, r_out2=0.0122, mat="gold"))
g.s(hw.ycyl("bore", 0.0060, 0.322, 0.333, z=BZ, verts=12, mat="dark"))

# ================================================================== 운반 손잡이 + 광점 조준기 (위)
# 손잡이 윗면은 앞으로 갈수록 낮아진다: 광점 창의 시야 원뿔(반각 약 7°) 밖에 두어 정조준 시 가리지 않게
handle_path = [(-0.058, 0.099), (-0.058, 0.113)] + hw.arc_pts(-0.046, 0.113, 0.012, 180, 90, 3)[1:] + \
    [(0.040, 0.1150)] + hw.arc_pts(0.040, 0.1030, 0.012, 90, 30, 2)[1:] + [(0.066, 0.100)]
g.s(hw.side("carry_handle", hw.strip(handle_path, 0.011), 0.016, bevel=0.0032, seg=2, mat="metal"))
g.s(hw.boxr("sight_post", -0.0075, 0.0075, -0.070, -0.046, 0.100, 0.1335, bevel=0.003, mat="metal"))
# 손잡이 아래 손가락 홈 (금색 아님, 어두운 줄)
for i in range(3):
    g.f(hw.decal(f"handle_rib{i}", hw.rrect(0.010, 0.0016, 0.0007, 1), (0, -0.020 + i * 0.016, 0.1290 - i * 0.0042),
                 mat="dark", right=(1, 0, 0), up=(0, 1, 0)))
# 광점 조준기 후드 (둥근 관) + 받침
g.s(hw.tube("sight_hood", 0.0172, 0.0146, -0.082, -0.034, c=(0, SZ), verts=24, mat="metal"))
g.s(hw.tube("sight_ring", 0.0182, 0.0146, -0.038, -0.033, c=(0, SZ), verts=24, mat="gold"))
g.s(hw.tube("sight_eyecup", 0.0180, 0.0146, -0.084, -0.079, c=(0, SZ), verts=24, mat="dark"))
# 조준기 조절 다이얼 (오른쪽)
g.s(hw.xcyl("sight_knob", 0.0050, 0.0160, 0.0215, y=-0.058, z=SZ, verts=14, bevel=0.0008, mat="dark"))
# 광점 레티클 (시안 고리 + 점, 앞 창 안쪽에 떠 있는 투영)
g.f(hw.ring_decal("reticle_ring", (0, -0.036, SZ), 0.0034, 0.0027, **hw.BACK, mat="glow", seg=20))
g.f(hw.decal("reticle_dot", hw.circle(0.0008, 10), (0, -0.036, SZ), **hw.BACK, mat="glow"))
for k in range(4):   # 고리 바깥 짧은 눈금 4개
    a = math.radians(90 * k)
    u, v = math.cos(a) * 0.0050, math.sin(a) * 0.0050
    g.f(hw.decal(f"reticle_tick{k}", hw.rrect(0.0008 if k % 2 else 0.0022, 0.0022 if k % 2 else 0.0008, 0.0003, 1,
                                              u, v), (0, -0.036, SZ), **hw.BACK, mat="glow"))

# ================================================================== 손잡이 · D자 고리 · 방아쇠
grip = hw.side("grip", hw.rrect(0.029, 0.084, 0.011, n=3, cy=-0.016), 0.025, bevel=0.004, seg=2, mat="dark")
hw.xform(grip, rot=(-13, 0, 0), pivot=(0, 0, 0.02))
g.s(grip)
for sx in (-1, 1):   # 손잡이 판 (회녹)
    p = hw.side(f"grip_panel{sx}", hw.rrect(0.020, 0.058, 0.008, n=2, cy=-0.018), 0.003, x=sx * 0.0128,
                bevel=0.0010, seg=1, mat="olive_d")
    hw.xform(p, rot=(-13, 0, 0), pivot=(0, 0, 0.02))
    g.s(p)
# D자 고리: 손잡이 밑에서 앞으로 나와 손 전체를 감싸고 몸통 앞에 붙는다
loop_path = [(-0.012, -0.056), (0.050, -0.056)] + hw.arc_pts(0.050, -0.034, 0.022, 270, 360, 5)[1:] + \
    [(0.072, 0.000), (0.080, 0.026)]
g.s(hw.side("d_loop", hw.strip(loop_path, 0.0085), 0.015, bevel=0.0028, seg=2, mat="olive"))
TRIG = (0, 0.030, 0.021)
trig_pts = [(-0.0022, 0.0), (0.0030, 0.0), (0.0038, -0.010), (0.0072, -0.020), (0.0040, -0.025),
            (-0.0010, -0.022), (-0.0020, -0.010)]
trig = hw.side("trigger_blade", trig_pts, 0.006, bevel=0.0012, seg=2, mat="steel")
trig.location = TRIG
g.p("trigger", trig)
g.pivot("trigger", TRIG, rotAxis="x", rotDeg=-14)

# ================================================================== 잔탄 표시창 (왼쪽, 시안) + 엘프 로고
g.f(hw.decal("counter_bg", hw.rrect(0.026, 0.011, 0.003, 2), (-W_LOW / 2, -0.076, 0.044), mat="navy",
             **hw.LEFT))
for i in range(5):
    g.f(hw.decal(f"counter_bar{i}", hw.rrect(0.0032, 0.0062, 0.0006, 1), (-W_LOW / 2, -0.086 + i * 0.0048, 0.044),
                 lift=0.0009, mat="glow", **hw.LEFT))
# 엘프 로고: 엘피니아 남색 원판 + 금색 로고 (왼쪽, 1인칭에서 보이는 면)
g.f(hw.decal("logo_disc", hw.circle(0.0165, 24), (-W_LOW / 2, 0.050, 0.042), mat="navy", **hw.LEFT))
g.f(hw.ring_decal("logo_rim", (-W_LOW / 2, 0.050, 0.042), 0.0165, 0.0150, mat="gold", lift=0.0008, **hw.LEFT))
g.logo((-W_LOW / 2, 0.050, 0.042), 0.020, mat="gold", **hw.LEFT)
# 스텐실: 형식명과 일련번호 (왼쪽 개머리)
g.f(hw.text("mk_type", "7식", 0.0105, (-W_LOW / 2, -0.150, 0.050), mat="steel", **hw.LEFT))
g.f(hw.text("mk_serial", "No.0412", 0.0050, (-W_LOW / 2, -0.150, 0.039), mat="steel", **hw.LEFT))
g.f(hw.text("mk_type_r", "7식", 0.0105, (W_LOW / 2, -0.150, 0.050), mat="steel", **hw.RIGHT))

# ================================================================== 조정간 (왼쪽, 손잡이 위)
SEL = (-W_LOW / 2 - 0.0012, 0.000, 0.046)
sel = [hw.xcyl("sel_hub", 0.0042, -0.0010, 0.0014, y=0, z=0, verts=14, mat="dark"),
       hw.side("sel_lever", hw.stadium(0.016, 0.0042, 3, cx=0.006, angle=0), 0.0022, x=-0.0004, bevel=0.0006,
               seg=1, mat="dark")]
for o in sel:
    o.location = (o.location.x + SEL[0], o.location.y + SEL[1], o.location.z + SEL[2])
g.p("selector", *sel)
g.pivot("selector", SEL, rotAxis="x", rotDeg="0,45,90", note="SAFE/SEMI/AUTO")
for i, (txt, ang) in enumerate((("S", 180), ("1", 135), ("A", 90))):
    a = math.radians(ang)
    g.f(hw.text(f"sel_mk{i}", txt, 0.0040, (-W_LOW / 2, 0.0115 * math.cos(a) * -1, 0.046 + 0.0115 * math.sin(a)),
                mat="steel", **hw.LEFT))

# ================================================================== 장전 손잡이 (왼쪽 앞, 앞으로 뺀 엘프식 위치)
CH = (-W_UP / 2, 0.098, 0.084)
ch = [hw.xcyl("ch_stem", 0.0030, -0.012, 0.0, y=0, z=0, verts=10, mat="steel"),
      cb.sphere("ch_knob", radius=0.0052, loc=(-0.013, 0, 0), segments=12, rings=8, material=hw.M("dark"))]
for o in ch:
    o.location = (o.location.x + CH[0], o.location.y + CH[1], o.location.z + CH[2])
g.p("charging_handle", *ch)
g.pivot("charging_handle", CH, move=hw.mv(0, -0.070, 0))
g.f(hw.decal("ch_slot", hw.stadium(0.090, 0.0042, 3), (-W_UP / 2 - 0.0002, 0.062, 0.084), mat="dark", **hw.LEFT))

# ================================================================== 노리쇠 (배출구 안)
bolt = [hw.boxr("bolt_body", W_UP / 2 - 0.004, W_UP / 2 + 0.0009, -0.082, -0.058, 0.0748, 0.0836, bevel=0.0010,
                mat="steel")]
g.p("bolt", *bolt)
g.pivot("bolt", (W_UP / 2, -0.070, 0.079), move=hw.mv(0, -0.040, 0))
g.pf("bolt", hw.decal("bolt_groove", hw.rrect(0.018, 0.0016, 0.0006, 1), (W_UP / 2 + 0.0009, -0.070, 0.0792),
                      mat="metal", **hw.RIGHT))

# ================================================================== 탄창 (손잡이 뒤, 불펍)
MAGY = -0.079
mag_path = [(0, MAGY, 0.040), (0, MAGY, 0.000), (0, MAGY + 0.002, -0.030), (0, MAGY + 0.008, -0.056),
            (0, MAGY + 0.016, -0.076)]
mag = [hw.sweep("mag_body", mag_path, hw.rrect(0.020, 0.052, 0.005, 2), side_vec=(1, 0, 0), mat="dark", smooth=40)]
base = hw.side("mag_base", hw.rrect(0.058, 0.010, 0.004, 2), 0.024, bevel=0.0018, seg=2, mat="olive_d")
hw.xform(base, rot=(22, 0, 0), loc=(0, MAGY + 0.017, -0.078))
mag.append(base)
for sx in (-1, 1):
    for i, z in enumerate((-0.018, -0.040)):
        r = hw.boxr(f"mag_rib{sx}{i}", -0.0002, 0.0012, -0.020, 0.020, -0.0012, 0.0012, bevel=0.0004, mat="dark")
        hw.xform(r, rot=(-8 - i * 7, 0, 0), loc=(sx * 0.0100 - (0.0005 if sx < 0 else 0), MAGY + 0.004 + i * 0.006, z))
        mag.append(r)
g.p("mag", *mag)
g.pivot("mag", (0, MAGY, 0.010), move=hw.mv(0, 0, -0.15))
# 탄창 왼쪽 확인 창 3개 (놋쇠 탄이 보임 = 구멍 줄)
for i in range(3):
    z = -0.006 - i * 0.012
    g.pf("mag", hw.decal(f"mag_win{i}", hw.circle(0.0032, 12), (-0.0101, MAGY + 0.001 + i * 0.0025, z),
                         mat="gold", **hw.LEFT))
g.pf("mag", hw.text("mag_no", "30", 0.0060, (-0.0101, MAGY + 0.010, -0.050), mat="steel", **hw.LEFT))

# ================================================================== 멜빵 고리 · 탄창 멈치
g.s(hw.torus("sling_rear", 0.0060, 0.0013, loc=(0, -0.186, -0.020), rot=(0, 90, 0), seg=14, rseg=6, mat="steel"))
g.s(hw.torus("sling_front", 0.0060, 0.0013, loc=(-0.020, 0.190, 0.040), rot=(90, 0, 90), seg=14, rseg=6,
             mat="steel"))
g.s(hw.boxr("mag_release", -0.008, 0.008, -0.118, -0.110, -0.004, 0.006, bevel=0.0015, mat="dark"))

# ================================================================== 앵커
g.anchor("muzzle", (0, 0.338, BZ))
g.anchor("grip_support", (0, 0.150, 0.040))
g.anchor("sight_eye", (0, -0.150, SZ))
g.anchor("eject", (W_UP / 2 + 0.006, -0.070, 0.079))
g.anchor("mag_well", (0, MAGY, 0.010))

g.finish("weapons/elfinia/elfinia_rifle.glb", outline=0.0019, fp="0.16,-0.215,-0.37", fprot="0,6,0")
