"""모나티엄 진압반 MR-B2 '꿀밤' 고전압 전기충격봉 (근접).

[오리지널] 진압반 제식 전기충격봉. 손잡이 위 엄지 단추로 두 갈래 전극 사이에 방전한다. 충전 표시 4칸(모나티엄 HUD 연동).
[원작] 교주 차원 모나티엄은 주말농장 법칙 때문에 고무탄과 '고전압 전기충격기'를 쓴다.
       캐시는 모나티엄에서 지급받은 '전기 지짐이'(전기 충격기)를 들고 다니고, 알레트의 테이저건은 15000볼트다.
       칸나: "민중의 몽둥이~ 시민을 위한 봉사정신!"
형태 근거: 타이다가 든 두 갈래 무기(금색 안쪽 레일), 캐시 충격기의 번개 표식. 교주 차원 문법(금색 고리, 둥근 덩어리).

원점 = 오른손 파지점(손잡이 중심), +Y = 전극 쪽, +Z = 엄지 쪽(표시창·단추).
`arc` = 방전 불꽃(UNLIT, 기본으로 보임). 무기 시스템이 평소에는 숨기고 방전할 때만 켠다(커스텀 속성 fx="discharge").
`charge_1`~`charge_4` = 충전 표시 칸(UNLIT). 남은 충전량만큼 켠다.

npm run model -- art/blender/weapons/monatium/monatium_stun_baton.py
npm run shot -- weapons/monatium/monatium_stun_baton.glb --views side,34,top,muzzle --focus monatium_stun_baton
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402

cb.reset()
g = hw.Gun("monatium_stun_baton")

# ================================================================== 손잡이 끝 (금색 머리) + 끈 고리
g.s(hw.ycyl("pommel_neck", 0.0165, -0.072, -0.060, verts=24, r2=0.0158, mat="dark"))
pom = cb.sphere("pommel", radius=0.0195, loc=(0, -0.074, 0), scale=(1, 0.62, 1), segments=24, rings=12,
                material=hw.M("gold"))
g.s(pom)
g.s(hw.torus("lanyard_eye", 0.0058, 0.0016, loc=(0, -0.0865, 0), rot=(0, 90, 0), seg=14, rseg=6, mat="steel"))
g.s(hw.torus("lanyard", 0.0120, 0.0018, loc=(0, -0.096, -0.010), rot=(0, 90, 0), seg=18, rseg=6, ry=0.016,
             mat="teal"))

# ================================================================== 손잡이 (고무, 손가락 홈 3개)
g.s(hw.ycyl("grip_core", 0.0155, -0.062, 0.050, verts=24, mat="dark"))
for i, y in enumerate((-0.044, -0.014, 0.016)):   # 손가락 사이 둥근 마디
    g.s(hw.torus(f"grip_ring{i}", 0.0157, 0.0036, loc=(0, y, 0), rot=(90, 0, 0), seg=24, rseg=8, mat="dark"))
for i in range(6):   # 손잡이 위아래 미끄럼 방지 홈 (데칼)
    a = math.radians(90 + (i - 2.5) * 22)
    n = (math.cos(a), 0, math.sin(a))
    g.f(hw.decal(f"grip_line{i}", hw.rrect(0.0015, 0.024, 0.0006, 1), (n[0] * 0.0167, 0.032, n[2] * 0.0167),
                 right=(-math.sin(a), 0, math.cos(a)), up=(0, 1, 0), mat="metal"))

# ================================================================== 날밑 (손 보호 고리)
g.s(hw.ycyl("guard", 0.0200, 0.050, 0.064, verts=28, r2=0.0235, bevel=0.0024, seg=2, mat="dark"))
g.s(hw.muzzle_ring("guard_gold", 0.064, 0.069, 0.0205, mat="gold", verts=28))

# ================================================================== 몸통 (남보라, 살짝 가늘어짐) + 표시창 꼬투리
g.s(hw.ycyl("shaft", 0.0190, 0.069, 0.250, verts=28, r2=0.0170, bevel=0.0010, mat="violet"))
g.s(hw.tube("band_teal", 0.0185, 0.0160, 0.200, 0.214, c=(0, 0), verts=28, mat="teal"))
# 표시창 꼬투리 (위, 1인칭에서 보임)
pod = hw.sculpt("display_pod", [(0.070, 0.010), (0.140, 0.010), (0.150, 0.016), (0.146, 0.0235), (0.076, 0.0245),
                                (0.068, 0.019)], hw.rrect(0.024, 0.030, 0.008, n=3, cy=0.014), bevel=0.0015, seg=2,
                mat="metal")
g.s(pod)
g.f(hw.decal("display_win", hw.rrect(0.014, 0.052, 0.003, 2), (0, 0.106, 0.0246), mat="dark", **hw.TOP))
for k in range(4):   # 충전 칸 (손잡이 쪽이 1)
    y = 0.088 + k * 0.012
    bar = hw.decal(f"charge_bar{k}", hw.rrect(0.010, 0.0085, 0.0015, 1), (0, y, 0.0246), lift=0.0010, mat="glow",
                   **hw.TOP)
    g.p(f"charge_{k + 1}", bar)
    g.pivot(f"charge_{k + 1}", (0, y, 0.0256), noOutline=1)
# 엄지 단추 (방전) - 날밑 바로 앞 윗면
BTN = (0, 0.0590, 0.0230)
g.p("trigger", hw.zcyl("button", 0.0052, BTN[2] - 0.0030, BTN[2] + 0.0022, y=BTN[1], verts=18, bevel=0.0012,
                       mat="teal"))
g.pivot("trigger", BTN, move=hw.mv(0, 0, -0.0025), note="thumb button")
g.s(hw.zcyl("button_well", 0.0074, 0.0180, 0.0222, y=BTN[1], verts=20, bevel=0.0010, mat="dark"))

# ================================================================== 경고 표식 (번개 삼각형, 양옆) + 엘프 로고 + 각인
tri = [(-0.0080, -0.0058), (0.0080, -0.0058), (0.0, 0.0080)]
bolt = [(0.0006, 0.0050), (-0.0030, -0.0002), (-0.0002, -0.0002), (-0.0012, -0.0048), (0.0030, 0.0008),
        (0.0004, 0.0008)]
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    x = sx * 0.0176
    g.f(hw.decal(f"warn_tri{sx}", tri, (x, 0.232, 0.0), mat="hazard", **fr))
    g.f(hw.decal(f"warn_bolt{sx}", bolt, (x, 0.232, -0.0006), lift=0.0010, mat="dark", **fr))
g.f(hw.decal("logo_disc", hw.circle(0.0122, 24), (-0.0182, 0.165, 0.0), mat="dark", **hw.LEFT))
g.logo((-0.0182, 0.165, 0.0), 0.0150, mat="gold", **hw.LEFT)
g.f(hw.text("mk_type", "MR-B2", 0.0062, (-0.0188, 0.116, 0.0), mat="steel", **hw.LEFT))
g.f(hw.text("mk_volt", "고전압", 0.0050, (0.0188, 0.140, 0.0), mat="hazard", **hw.RIGHT))

# ================================================================== 머리 (전극 하우징) + 두 갈래 전극 (금색 안쪽 레일)
head = hw.sculpt("head", [(0.246, -0.017), (0.284, -0.019), (0.296, -0.014), (0.296, 0.014), (0.284, 0.019),
                          (0.246, 0.017)], hw.rrect(0.050, 0.038, 0.012, n=3), bevel=0.0022, seg=2, mat="metal")
g.s(head)
g.s(hw.boxr("insulator", -0.0085, 0.0085, 0.294, 0.318, -0.0100, 0.0100, bevel=0.0035, mat="dark"))
PX = 0.0155
for sx in (-1, 1):
    g.s(hw.ycyl(f"prong{sx}", 0.0058, 0.292, 0.356, x=sx * PX, verts=16, r2=0.0050, mat="steel"))
    g.s(cb.sphere(f"prong_tip{sx}", radius=0.0064, loc=(sx * PX, 0.357, 0), segments=16, rings=8,
                  material=hw.M("steel")))
    g.s(hw.ycyl(f"prong_collar{sx}", 0.0074, 0.292, 0.302, x=sx * PX, verts=16, bevel=0.0012, mat="dark"))
    # 금색 안쪽 레일 (타이다 무기의 금색 띠)
    g.s(hw.boxr(f"prong_rail{sx}", sx * PX - sx * 0.0058 - 0.0011, sx * PX - sx * 0.0058 + 0.0011, 0.304, 0.348,
                -0.0034, 0.0034, bevel=0.0007, mat="gold"))
# 하우징 앞면 통풍 구멍 줄
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    g.f(*hw.holes(f"head_hole{sx}", (sx * 0.0251, 0.271, 0.0), 3, 0.0085, 0.0026, along=(0, 1), mat="dark", **fr))

# ================================================================== 방전 불꽃 (UNLIT, 서로 직각인 두 지그재그 띠)
ARC_Y = 0.351
arc_objs = []
for k, (axis_u, wob) in enumerate((((1, 0, 0), (0, 0, 1)), ((1, 0, 0), (0, 1, 0)))):
    pts = []
    n = 7
    for i in range(n + 1):
        t = i / n
        x = -PX + 2 * PX * t
        w = (0.0072 if i % 2 else -0.0072) * math.sin(math.pi * t) * (1.0 if k == 0 else 0.8)
        if i in (0, n):
            w = 0.0
        pts.append((x, ARC_Y + (w if wob[1] else 0.0) + 0.0015 * k, w if wob[2] else 0.0))
    sec = [(-0.0013, -0.0013), (0.0013, -0.0013), (0.0013, 0.0013), (-0.0013, 0.0013)]
    arc_objs.append(hw.sweep(f"arc{k}", pts, sec, side_vec=(0, 0, 1) if k == 0 else (0, 1, 0), mat="glow",
                             smooth=0))
g.p("arc", *arc_objs)
g.pivot("arc", (0, ARC_Y, 0), noOutline=1, fx="discharge")

# ================================================================== 앵커
g.anchor("muzzle", (0, ARC_Y, 0))           # 방전 중심 (타격·이펙트 원점)
g.anchor("tip", (0, 0.364, 0))              # 전극 끝 (근접 판정 앞 끝)
g.anchor("grip_support", (0, -0.040, 0))    # 양손 밀치기 자세에서 왼손 (손잡이 뒤쪽)

g.finish("weapons/monatium/monatium_stun_baton.glb", outline=0.0018, fp="0.12,-0.16,-0.19", fprot="42,26,18")
