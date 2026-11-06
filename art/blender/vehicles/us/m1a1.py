"""노획 M1A1 에이브럼스 주력전차.

npm run model -- art/blender/vehicles/us/m1a1.py
npm run shot -- vehicles/us/m1a1.glb --views front,34,side,top

규약: docs/art/VEHICLES.md. 정면 -Y, 왼쪽 +X, 원점 = 차체 중심 아래 지면.
실측 기준: 차체 길이 7.92 m, 포 포함 9.77 m, 폭 3.66 m(스커트), 포탑 지붕 2.44 m, 궤도 중심 간격 2.87 m,
슈 폭 0.635 m, 보기륜 지름 0.635 m × 7. 키 1.2 m 엘프에게는 차체 갑판(1.5 m)부터 머리 위다.
노드: turret(요) > gun_pitch(피치, -10~+20) > gun_main(포방패+포신), muzzle_main, mount_coax(weapons/us/m240_coax.glb)
      turret > mount_m2_cdr(전차장 큐폴라 앞 피벗, weapons/us/m2.glb), hatch_cdr, hatch_loader, seat_*
      track_L/R(빈 노드, 슈 track_L_s00.. 경로 순서로 자식), roadwheel_L_01..07 / R, idler_L/R, sprocket_L/R (원점 = 바퀴 중심, radius)
엘프식 흔적: 왼쪽 앞 펜더의 밧줄 사다리(나무 발판), 큐폴라 테두리에 묶은 분홍 방석, 바구니 속 분홍 침낭,
포탑 옆 청록 관리번호와 한글 '포탑 회전 주의', 바구니의 창고 태그.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402
import vehicles_us as vu  # noqa: E402
from vehicles_us import boxr, side, text, xcyl, ycyl, ytube, zcyl  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
b = vu.VBuild("m1a1")

# ================================================================== 치수
TX = 1.435                # 궤도 중심 x
SW = 0.635                # 슈 폭
RWR = 0.3175              # 보기륜 반지름
RWZ = 0.42                # 보기륜 중심 높이
RW_Y = [-2.30 + i * (4.60 / 6) for i in range(7)]
IDL = (-3.32, 0.62, 0.33)     # 유도륜 (앞)
SPR = (3.42, 0.74, 0.33)      # 기동륜 (뒤)
DECK = 1.52
ZT0, ZT1 = 1.56, 2.42         # 포탑 바닥 / 지붕
YT = -0.25                    # 포탑 링 중심 y
GP = (0.0, -1.55, 2.00)       # 포 트러니언 (gun_pitch)
MUZ_Y = -5.83
CUP = (-0.70, 0.35)           # 전차장 큐폴라 (오른쪽)
LDR = (0.70, 0.35)            # 탄약수 해치 (왼쪽)
CUP_TOP = 2.64
PZ_CDR = 2.83                 # 전차장 M2 고각 핀
PY_CDR = CUP[1] - 0.40
LS = dict(right=(0, 1, 0), up=(0, 0, 1))
RS = dict(right=(0, -1, 0), up=(0, 0, 1))
FR = dict(right=(1, 0, 0), up=(0, 0, 1))
BK = dict(right=(-1, 0, 0), up=(0, 0, 1))

# ================================================================== 차체 (가운데 + 스폰슨)
hull = [(-3.45, 0.48), (3.70, 0.48), (3.96, 0.72), (3.96, 1.46), (3.86, DECK), (-2.10, DECK), (-3.96, 1.10),
        (-3.98, 1.02)]
hull_obj = b.s(side("hull", hull, 2.20, bevel=0.025, seg=1, mat="tan"))
for sx in (-1, 1):
    sp = [(-3.78, 1.18), (3.94, 1.18), (3.94, 1.46), (3.86, DECK), (-2.10, DECK), (-3.80, 1.14)]
    b.s(side(f"sponson{sx}", sp, 0.72, x=sx * (1.10 + 0.36), bevel=0.02, seg=1, mat="tan"))
    # 앞 펜더 끝 흙받이 + 전조등 가드
    b.s(boxr(f"mudflap{sx}", min(sx * 1.12, sx * 1.80), max(sx * 1.12, sx * 1.80), -3.86, -3.78, 0.80, 1.16,
             bevel=0.01, mat="rubber"))
    hx = sx * 1.52
    b.s(boxr(f"hl_box{sx}", hx - 0.14, hx + 0.14, -3.70, -3.46, 1.18, 1.36, bevel=0.02, mat="tan"))
    b.t(vu.tube(f"hl_guard{sx}", [(hx - 0.17, -3.48, 1.18), (hx - 0.17, -3.80, 1.30), (hx + 0.17, -3.80, 1.30),
                                  (hx + 0.17, -3.48, 1.18)], 0.018, mat="tan_dk", verts=6))
    b.s(boxr(f"hl_house{sx}", hx - 0.10, hx + 0.10, -3.72, -3.69, 1.22, 1.32, bevel=0.006, mat="black"))
    # 뒤 펜더 후미등 하우징 + 짐 상자
    b.s(boxr(f"tl_house{sx}", min(sx * 1.48, sx * 1.74), max(sx * 1.48, sx * 1.74), 3.94, 3.98, 1.28, 1.44,
             bevel=0.008, mat="black"))
    b.s(boxr(f"rear_box{sx}", min(sx * 1.20, sx * 1.76), max(sx * 1.20, sx * 1.76), 2.60, 3.70, DECK, DECK + 0.18,
             bevel=0.02, mat="tan"))
    for yy in (3.00, 3.30):
        b.t(boxr(f"rear_box_latch{sx}{yy}", min(sx * 1.76, sx * 1.775), max(sx * 1.76, sx * 1.775), yy, yy + 0.10,
                 1.58, 1.65, mat="black"))
    # 견인 고리 (앞 코)
    b.t(us.torus(f"tow_f{sx}", 0.07, 0.022, loc=(sx * 0.70, -4.00, 0.86), rot=(0, 90, 0), seg=8, rseg=5, arc=200,
                 mat="tan_dk"))
    b.t(boxr(f"tow_f_tab{sx}", sx * 0.70 - 0.05, sx * 0.70 + 0.05, -4.00, -3.92, 0.80, 0.98, bevel=0.01,
             mat="tan_dk"))
    # 견인 케이블 (뒤 갑판 옆)
    cab = [(sx * 1.00, 2.40, DECK + 0.03), (sx * 1.04, 3.70, DECK + 0.03), (sx * 0.90, 3.82, DECK + 0.03),
           (sx * 0.80, 3.70, DECK + 0.03), (sx * 0.84, 2.30, DECK + 0.03)]
    b.t(vu.tube(f"tow_cable{sx}", vu.rounded_path(cab, 0.1, 2), 0.022, mat="black", verts=6))
# 앞 상부 경사판 (조종수 해치 주변) 패널선 + 잠망경 블록
for (y0, y1) in ((-3.30, -3.28), (-2.95, -2.93)):
    zz = DECK - (-(y0) - 2.10) * (DECK - 1.10) / 1.86
    b.f(boxr(f"glacis_seam{y0}", -1.05, 1.05, y0, y1, zz - 0.004, zz + 0.006, mat="tan_dk"))
for i, x in enumerate((-0.22, 0.0, 0.22)):
    b.s(boxr(f"periscope{i}", x - 0.07, x + 0.07, -2.86, -2.76, 1.42, 1.50, bevel=0.01, mat="black"))
    b.f(boxr(f"periscope_gl{i}", x - 0.055, x + 0.055, -2.862, -2.858, 1.435, 1.49, mat="glass"))
# 뒤판: 배기 그릴, 견인 핀틀
b.s(boxr("exhaust_grille", -1.00, 1.00, 3.96, 4.00, 0.86, 1.40, bevel=0.012, mat="black"))
for i in range(9):
    z = 0.90 + i * 0.056
    b.t(boxr(f"ex_louver{i}", -0.97, 0.97, 3.995, 4.03, z, z + 0.026, mat="tan_dk"))
b.t(us.torus("tow_pintle", 0.07, 0.024, loc=(0, 4.04, 0.66), rot=(0, 90, 0), seg=8, rseg=5, arc=260, mat="black"))
b.s(boxr("tow_pintle_base", -0.12, 0.12, 3.92, 4.02, 0.58, 0.76, bevel=0.01, mat="tan_dk"))
b.s(boxr("phone_box", -1.48, -1.26, 3.96, 4.04, 1.20, 1.38, bevel=0.01, mat="od"))
# 엔진 갑판 그릴 + 정비 문 손잡이
for sx in (-1, 1):
    for i in range(6):
        y = 2.25 + i * 0.12
        b.f(boxr(f"deck_grille{sx}{i}", min(sx * 0.15, sx * 0.95), max(sx * 0.15, sx * 0.95), y, y + 0.05, DECK,
                 DECK + 0.004, mat="black"))
b.f(boxr("deck_seam", -1.05, 1.05, 2.00, 2.012, DECK, DECK + 0.004, mat="tan_dk"))
b.f(boxr("deck_seam2", -0.006, 0.006, 2.00, 3.86, DECK, DECK + 0.004, mat="tan_dk"))
for (x, y) in ((-0.55, 3.20), (0.55, 3.20), (-0.55, 2.10), (0.55, 2.10)):
    b.t(vu.tube(f"deck_handle{x}{y}", [(x - 0.08, y, DECK), (x - 0.08, y, DECK + 0.05), (x + 0.08, y, DECK + 0.05),
                                       (x + 0.08, y, DECK)], 0.012, mat="tan_dk", verts=5))
# 포탑 링 (갑판 위 고정부)
b.s(vu.lathe("hull_ring", [(DECK, 1.08), (DECK, 1.18), (DECK + 0.05, 1.18), (DECK + 0.05, 1.08)], segs=32, axis="z",
             loc=(0, YT, 0), closed=True, smooth=30, mat="tan_dk"))

# ================================================================== 사이드스커트 (앞 3장 두꺼운 장갑, 뒤는 얇은 판)
SKY = [-3.62, -2.88, -2.14, -1.40, -0.66, 0.08, 0.82, 1.56, 2.30, 3.04, 3.70]
for sx in (-1, 1):
    for i in range(len(SKY) - 1):
        y0, y1 = SKY[i] + 0.012, SKY[i + 1] - 0.012
        heavy = i < 3
        t = 0.09 if heavy else 0.035
        xo = sx * (1.84 if heavy else 1.80)
        x0, x1 = sorted((xo, xo - sx * t))
        if i == 0:
            pts = [(y0 + 0.16, 0.60), (y1, 0.58), (y1, 1.20), (y0, 1.18), (y0 - 0.02, 0.98)]
            b.s(side(f"skirt{sx}{i}", pts, t, x=(x0 + x1) / 2, bevel=0.012, seg=1, mat="tan"))
        else:
            b.s(boxr(f"skirt{sx}{i}", x0, x1, y0, y1, 0.58 if heavy else 0.62, 1.20, bevel=0.012 if heavy else 0.008,
                     mat="tan"))
        for yy in (y0 + 0.08, (y0 + y1) / 2, y1 - 0.08):
            b.f(vu.radial_disc(f"sk_bolt{sx}{i}{yy:.2f}", (xo + sx * 0.002, yy, 1.13), (sx, 0, 0), 0.016, 0.008,
                               verts=6, mat="tan_dk"))
    # 레일 바깥 면은 차체 옆면(±1.82)보다 6 mm 밖 (같은 평면 깜빡임)
    b.s(boxr(f"skirt_rail{sx}", min(sx * 1.74, sx * 1.826), max(sx * 1.74, sx * 1.826), -3.70, 3.72, 1.16, 1.22,
             mat="tan_dk"))
    b.f(text(f"skirt_no{sx}", "MNT-T01", 0.16, (sx * 1.846, -2.50, 0.90), mat="paint", **(LS if sx > 0 else RS)))
    b.f(text(f"skirt_kr{sx}", "모나티엄 창고", 0.10, (sx * 1.806, 1.90, 0.88), mat="paint", font="kr",
             **(LS if sx > 0 else RS)))

# ================================================================== 주행부: 보기륜, 유도륜, 기동륜, 상부 롤러, 궤도
RWP = [(0.0, 0.0), (0.0, 0.07), (0.035, 0.085), (0.05, 0.24), (0.06, 0.285), (0.10, 0.29), (0.10, 0.0)]
for side_nm, sx in (("L", 1), ("R", -1)):
    for i, y in enumerate(RW_Y):
        nm = f"roadwheel_{side_nm}_{i + 1:02d}"
        xo = sx * (TX + 0.24)     # 바깥 원판 바깥면
        prof = [(sx * (TX + 0.24 - a), r) for (a, r) in RWP]
        disc = vu.lathe(nm + "_disc", prof, segs=14, axis="x", loc=(0, y, RWZ), smooth=40, mat="tan_dk")
        tire = vu.lathe(nm + "_tire", [(sx * (TX + 0.235), 0.285), (sx * (TX + 0.235), RWR),
                                       (sx * (TX + 0.10), RWR), (sx * (TX + 0.10), 0.285)],
                        segs=14, axis="x", loc=(0, y, RWZ), closed=True, smooth=40, mat="rubber")
        b.p(nm, disc, tire)
        b.part(nm, (sx * TX, y, RWZ), radius=RWR)
        # 안쪽 원판은 바깥 원판 뒤에 가려지므로 축과 고무 띠만
        b.s(vu.lathe(nm + "_inner", [(sx * (TX - 0.10), 0.285), (sx * (TX - 0.10), RWR), (sx * (TX - 0.235), RWR),
                                     (sx * (TX - 0.235), 0.285)], segs=12, axis="x", loc=(0, y, RWZ), closed=True,
                     smooth=40, mat="rubber"))
        b.s(xcyl(f"arm{side_nm}{i}", 0.06, sx * 1.08, sx * (TX - 0.20), y=y, z=RWZ, verts=8, mat="tan_dk"))
    # 유도륜 (앞)
    nm = f"idler_{side_nm}"
    b.p(nm, vu.lathe(nm + "_disc", [(sx * (TX + 0.22), 0.0), (sx * (TX + 0.22), 0.09), (sx * (TX + 0.18), 0.12),
                                     (sx * (TX + 0.17), 0.30), (sx * (TX + 0.10), 0.31), (sx * (TX + 0.10), 0.0)],
                     segs=16, axis="x", loc=(0, IDL[0], IDL[1]), smooth=40, mat="tan_dk"))
    b.p(nm, vu.lathe(nm + "_rim", [(sx * (TX + 0.20), 0.30), (sx * (TX + 0.20), IDL[2]), (sx * (TX - 0.20), IDL[2]),
                                    (sx * (TX - 0.20), 0.30)], segs=16, axis="x", loc=(0, IDL[0], IDL[1]),
                     closed=True, smooth=40, mat="rubber"))
    b.part(nm, (sx * TX, IDL[0], IDL[1]), radius=IDL[2])
    b.s(vu.beam(f"idler_arm{side_nm}", (sx * 1.08, IDL[0] + 0.35, IDL[1] + 0.05), (sx * (TX - 0.10), IDL[0], IDL[1]),
                0.10, 0.08, mat="tan_dk"))
    # 기동륜 (뒤, 이빨 11개 × 2열)
    nm = f"sprocket_{side_nm}"
    b.p(nm, vu.lathe(nm + "_hub", [(sx * (TX + 0.24), 0.0), (sx * (TX + 0.24), 0.10), (sx * (TX + 0.18), 0.14),
                                    (sx * (TX + 0.17), 0.26), (sx * (TX - 0.17), 0.26), (sx * (TX - 0.20), 0.0)],
                     segs=16, axis="x", loc=(0, SPR[0], SPR[1]), smooth=40, mat="tan_dk"))
    teeth = []
    for row in (1, -1):
        for k in range(11):
            a = 2 * math.pi * (k + 0.5 * (row < 0)) / 11
            c = (sx * (TX + row * 0.13), SPR[0] + 0.29 * math.cos(a), SPR[1] + 0.29 * math.sin(a))
            teeth.append((c, (1, 0, 0), (0, -math.sin(a), math.cos(a)), (0, math.cos(a), math.sin(a)),
                          (0.07, 0.07, 0.11)))
    b.p(nm, vu.oboxes(nm + "_teeth", teeth, mat="black"))
    b.part(nm, (sx * TX, SPR[0], SPR[1]), radius=SPR[2], drive=1)
    b.s(xcyl(f"final_drive{side_nm}", 0.20, sx * 1.08, sx * (TX - 0.20), y=SPR[0], z=SPR[1], verts=14, mat="tan_dk"))
    # 상부 지지 롤러 (스커트 뒤)
    for y in (-1.20, 0.80):
        b.s(xcyl(f"ret_roller{side_nm}{y}", 0.10, sx * (TX - 0.18), sx * (TX + 0.18), y=y, z=1.00, verts=10,
                 mat="tan_dk"))
    # 궤도
    circles = [(IDL[0], IDL[1], IDL[2] + 0.05)] + [(y, RWZ, RWR + 0.05) for y in RW_Y] + \
              [(SPR[0], SPR[1], SPR[2] + 0.05)]
    loop = vu.track_path(circles, n=40)
    samples, pitch = vu.resample(loop, 0.193)
    trk = f"track_{side_nm}"
    # 슈 하나가 노드 하나 (track_L_s00.., 경로 순서, 원점 = 경로 위 슈 가운데): 게임이 달린 거리만큼 각 슈를 다음 슈 자리 쪽으로
    # 옮기고 돌려 궤도가 돈다 (vehicles/Vehicle.ts tracks, 2026-11-03 사용자 지적 "M9에서 전차들 궤도가 안움직이는데")
    for i, (p, tg) in enumerate(samples):
        T = Vector((0, tg[0], tg[1]))
        N = Vector((0, tg[1], -tg[0]))       # 반시계 경로의 바깥 법선
        C = Vector((sx * TX, p[0], p[1]))
        X = Vector((1, 0, 0))
        nm = f"{trk}_s{i:02d}"
        b.p(nm, vu.oboxes(nm + "_pad", [(C + N * 0.035, X, T, N, (SW - 0.08, pitch * 0.80, 0.03))], mat="rubber"),
            vu.oboxes(nm + "_body", [(C - N * 0.005, X, T, N, (SW, pitch * 0.62, 0.05)),
                                     (C - N * 0.075, X, T, N, (0.05, pitch * 0.45, 0.09))], mat="black"))   # 가운데 유도 돌기
        b.part(nm, tuple(C), parent=trk)
    b.part(trk, (sx * TX, 0, RWZ), roadWheels=7, pitch=round(pitch, 4), width=SW, shoes=len(samples))

# ================================================================== 포탑
TB = [(0.55, -1.98), (1.62, -1.74), (1.84, -1.42), (1.80, 0.95), (1.58, 1.75), (1.22, 1.95)]
TT = [(0.55, -1.80), (1.50, -1.56), (1.71, -1.28), (1.68, 0.92), (1.47, 1.70), (1.15, 1.86)]


def plan(half, y_off=YT * 0):
    right = [(x, y) for (x, y) in half]
    left = [(-x, y) for (x, y) in reversed(half)]
    return right + left


T = "turret"
tur = vu.loft("turret_shell", [(ZT0, plan(TB)), (ZT1 - 0.06, plan([(x - 0.008, y) for (x, y) in TT])),
                               (ZT1, plan([(x - 0.05 * (x / abs(x)), y + (0.04 if y < 0 else -0.03))
                                           for (x, y) in TT]))], axis="z", bevel=0.02, seg=1, mat="tan")
b.p(T, tur)
# 뺨 장갑 볼트, 버슬 지붕 블로아웃 패널, 옆 손잡이
for sx in (-1, 1):
    for (u, z) in ((0.30, 1.80), (0.65, 1.80), (0.30, 2.18), (0.65, 2.18)):
        x = sx * (0.55 + u * (1.62 - 0.55))
        y = -1.98 + u * (-1.74 + 1.98) + (z - ZT0) / (ZT1 - ZT0) * 0.18 - 0.005
        b.pf(T, vu.radial_disc(f"cheek_bolt{sx}{u}{z}", (x, y, z), (sx * 0.22, -1, 0), 0.035, 0.012, verts=6,
                               mat="tan_dk"))
    b.pf(T, boxr(f"blowout{sx}", min(sx * 0.15, sx * 1.15), max(sx * 0.15, sx * 1.15), 0.95, 1.65, ZT1,
                 ZT1 + 0.004, mat="tan_dk"))
    b.pf(T, boxr(f"blowout_in{sx}", min(sx * 0.17, sx * 1.13), max(sx * 0.17, sx * 1.13), 0.97, 1.63, ZT1 + 0.004,
                 ZT1 + 0.006, mat="tan"))
    b.pt(T, vu.tube(f"grab{sx}", [(sx * 1.73, -0.70, 2.30), (sx * 1.79, -0.66, 2.30), (sx * 1.79, -0.05, 2.30),
                                  (sx * 1.73, 0.0, 2.30)], 0.016, mat="tan_dk", verts=6))
# 지붕 패널선, 인양 고리
for (x0, x1, y0, y1) in ((-1.5, 1.5, -0.60, -0.588), (-1.4, 1.4, 1.20, 1.212), (-0.006, 0.006, -1.45, -0.60)):
    b.pf(T, boxr(f"roof_seam{y0}{x0}", x0, x1, y0, y1, ZT1, ZT1 + 0.004, mat="tan_dk"))
for (x, y) in ((1.35, -1.20), (-1.35, -1.20), (1.25, 1.55), (-1.25, 1.55)):
    b.pt(T, us.torus(f"lift{x}{y}", 0.05, 0.014, loc=(x, y, ZT1 + 0.04), rot=(90, 0, 0), seg=8, rseg=5, arc=200,
                     mat="tan_dk"))
# 포수 조준경 상자 (오른쪽 앞)
b.p(T, side("gps_box", [(-1.55, ZT1 - 0.01), (-0.95, ZT1 - 0.01), (-0.95, 2.80), (-1.40, 2.80), (-1.50, 2.72)],
            0.56, x=-0.70, bevel=0.015, seg=1, mat="tan"))
b.pt(T, boxr("gps_door_L", -0.98, -0.83, -1.56, -1.53, 2.54, 2.72, bevel=0.006, mat="tan_dk"))
b.pt(T, boxr("gps_door_R", -0.57, -0.42, -1.56, -1.53, 2.54, 2.72, bevel=0.006, mat="tan_dk"))
b.pt(T, boxr("gps_glass", -0.82, -0.58, -1.565, -1.552, 2.56, 2.70, mat="glass"))
# 전차장 큐폴라 (오른쪽 뒤): 받침 링 + 잠망경 6 + 피벗 받침
b.p(T, vu.lathe("cupola", [(ZT1 - 0.01, 0.50), (CUP_TOP - 0.05, 0.47), (CUP_TOP, 0.44), (CUP_TOP, 0.36),
                           (ZT1 - 0.01, 0.36)], segs=24, axis="z", loc=(CUP[0], CUP[1], 0), closed=True, smooth=30,
                mat="tan"))
for k in range(6):
    a = math.radians(-90 + 60 * k)
    if k == 0:
        continue   # 앞은 피벗 받침
    c = (CUP[0] + 0.486 * math.cos(a), CUP[1] + 0.486 * math.sin(a), ZT1 + 0.12)
    gl = vu.oboxes(f"vb{k}", [(c, (-math.sin(a), math.cos(a), 0), (0, 0, 1), (math.cos(a), math.sin(a), 0),
                               (0.12, 0.06, 0.02))], mat="glass")
    b.p(T, gl)
b.p(T, boxr("cdr_pintle_base", CUP[0] - 0.08, CUP[0] + 0.08, PY_CDR - 0.08, PY_CDR + 0.10, CUP_TOP - 0.02,
            CUP_TOP + 0.04, bevel=0.01, mat="tan_dk"))
# 엘프 흔적: 큐폴라 뒤 테두리에 묶은 분홍 방석
cc, ct = vu.cushion("cdr_cushion", (0, 0, 0), 0.34, 0.24, 0.08, tufts=False)
us.xform(cc, rot=(-70, 0, 0), loc=(CUP[0], CUP[1] + 0.47, CUP_TOP - 0.02))
b.p(T, cc)
b.pt(T, boxr("cdr_cushion_strap", CUP[0] - 0.012, CUP[0] + 0.012, CUP[1] + 0.40, CUP[1] + 0.56, CUP_TOP - 0.14,
             CUP_TOP + 0.02, mat="od"))
# 탄약수 해치 링 + 스케이트 링
b.p(T, vu.lathe("ldr_ring", [(ZT1 - 0.01, 0.46), (ZT1 + 0.08, 0.44), (ZT1 + 0.08, 0.38), (ZT1 - 0.01, 0.38)],
                segs=24, axis="z", loc=(LDR[0], LDR[1], 0), closed=True, smooth=30, mat="tan"))
b.pt(T, us.torus("skate_ring", 0.56, 0.022, loc=(LDR[0], LDR[1], ZT1 + 0.16), seg=24, rseg=5, mat="tan_dk"))
for k in range(4):
    a = math.radians(45 + 90 * k)
    b.pt(T, vu.beam(f"skate_post{k}", (LDR[0] + 0.44 * math.cos(a), LDR[1] + 0.44 * math.sin(a), ZT1 + 0.06),
                    (LDR[0] + 0.56 * math.cos(a), LDR[1] + 0.56 * math.sin(a), ZT1 + 0.16), 0.03, 0.03,
                    mat="tan_dk"))
# 연막탄 발사기 (앞 양옆, 6관씩)
for sx in (-1, 1):
    base = Vector((sx * 1.33, -1.30, ZT1 + 0.06))
    b.p(T, boxr(f"smoke_base{sx}", base.x - 0.16, base.x + 0.16, base.y - 0.06, base.y + 0.10, base.z - 0.06,
                base.z + 0.04, bevel=0.01, mat="tan_dk"))
    tubes = []
    for r in range(2):
        for c in range(3):
            p = base + Vector((sx * (c - 1) * 0.10, -0.02, 0.06 + r * 0.09))
            tubes.append(ycyl(f"smk{sx}{r}{c}", 0.04, p.y - 0.18, p.y, x=p.x, z=p.z, verts=8, mat="tan_dk"))
            b.pf(T, ycyl(f"smk_cap{sx}{r}{c}", 0.032, p.y - 0.185, p.y - 0.178, x=p.x, z=p.z, verts=8, mat="black"))
    for o in tubes:
        us.xform(o, rot=(25, 0, sx * -20), pivot=tuple(base))
    b.p(T, *tubes)
# 옆 짐 상자 + 표식 (청록 관리번호, 한글 '포탑 회전 주의')
for sx in (-1, 1):
    kw = LS if sx > 0 else RS
    x0, x1 = sorted((sx * 1.70, sx * 1.90))
    b.p(T, boxr(f"side_box{sx}", x0, x1, 0.15, 1.30, 1.80, 2.22, bevel=0.025, mat="tan"))
    b.pf(T, text(f"tur_no{sx}", "MNT-T01", 0.17, (sx * 1.902, 0.72, 2.06), mat="paint", **kw))
    b.pf(T, text(f"tur_kr{sx}", "포탑 회전 주의!", 0.085, (sx * 1.902, 0.72, 1.88), mat="paint", font="kr", **kw))
    for yy in (0.30, 1.15):
        b.pt(T, boxr(f"side_box_latch{sx}{yy}", min(sx * 1.90, sx * 1.915), max(sx * 1.90, sx * 1.915), yy - 0.04,
                     yy + 0.04, 2.10, 2.18, mat="black"))
# 바람 센서 기둥, 안테나 둘
b.pt(T, vu.tube("wind_mast", [(0, 1.55, ZT1), (0, 1.55, ZT1 + 0.55)], 0.015, mat="black", verts=6))
b.pt(T, vu.beam("wind_head", (-0.10, 1.55, ZT1 + 0.56), (0.10, 1.55, ZT1 + 0.56), 0.03, 0.03, mat="black"))
for sx in (-1, 1):
    b.p(T, zcyl(f"ant_base{sx}", 0.05, ZT1, ZT1 + 0.14, x=sx * 1.20, y=1.50, verts=10, mat="black"))
    b.pt(T, vu.tube(f"ant{sx}", vu.rounded_path([(sx * 1.20, 1.50, ZT1 + 0.12), (sx * 1.20, 1.55, ZT1 + 1.4),
                                                 (sx * 1.18, 2.00, ZT1 + 2.0)], 0.4, 2), 0.008, mat="black",
                    verts=5))

# 뒤 짐 바구니 (관 + 바닥) + 내용물
RK0, RK1 = 1.92, 2.62
RKX = 1.42
rk = []
for z in (1.78, 2.28):
    rk.append([(-RKX, RK0, z), (-RKX, RK1, z), (RKX, RK1, z), (RKX, RK0, z)])
for k, pts in enumerate(rk):
    b.pt(T, vu.tube(f"rack_rail{k}", vu.rounded_path(pts, 0.08, 2), 0.022, mat="tan_dk", verts=6))
for (x, y) in ((-RKX, RK1), (RKX, RK1), (-RKX, RK0 + 0.30), (RKX, RK0 + 0.30), (-0.70, RK1), (0.0, RK1),
               (0.70, RK1)):
    b.pt(T, vu.tube(f"rack_post{x}{y}", [(x, y, 1.78), (x, y, 2.28)], 0.018, mat="tan_dk", verts=6))
b.p(T, boxr("rack_floor", -RKX, RKX, RK0 - 0.05, RK1, 1.74, 1.78, mat="tan_dk"))
b.p(T, boxr("bag1", -1.30, -0.62, 2.00, 2.55, 1.78, 2.16, bevel=0.07, seg=2, mat="od"))
b.p(T, boxr("bag2", 0.62, 1.30, 2.05, 2.55, 1.78, 2.10, bevel=0.06, seg=2, mat="tan_dk"))
b.p(T, boxr("crate_r", -0.55, -0.05, 2.00, 2.50, 1.78, 2.12, bevel=0.01, mat="od"))
b.p(T, boxr("box_c", 0.02, 0.55, 2.02, 2.48, 1.78, 2.20, bevel=0.01, mat="coyote"))
b.p(T, ycyl("bedroll", 0.13, 2.05, 2.55, x=0.95, z=2.23, verts=12, mat="cushion"))   # 분홍 침낭
b.pt(T, ycyl("bedroll_strap", 0.135, 2.20, 2.24, x=0.95, z=2.23, verts=12, mat="od"))
b.pt(T, ycyl("bedroll_strap2", 0.135, 2.38, 2.42, x=0.95, z=2.23, verts=12, mat="od"))
b.pf(T, text("crate_t", "MNT", 0.08, (-0.30, 2.502, 1.95), mat="paper", **BK))
vu.tag(b, (-1.42, 2.62 + 0.02, 2.17), scale=4.0, lines=("MNT", "T-0001", "모나티엄 창고"), yaw=90,
       cord_top=(-1.42, 2.63, 2.265), f_add=lambda *o: b.pt(T, *o), fine_add=lambda *o: b.pf(T, *o))
b.part(T, (0, YT, DECK), yawMin=-180, yawMax=180)

# ================================================================== 주포 (gun_pitch > gun_main)
G = "gun_main"
b.p(G, boxr("mantlet", -0.46, 0.46, -2.12, -1.86, 1.72, 2.30, bevel=0.03, mat="tan"))
b.p(G, ycyl("gun_boss", 0.17, -2.22, -2.10, z=GP[2], verts=18, mat="tan"))
gy = [-2.22, -2.90, -3.58, -4.10, -4.62, -5.20, MUZ_Y]
gr = [0.098, 0.094, 0.090, 0.087, 0.084, 0.081, 0.079]
for i in range(len(gy) - 1):
    b.p(G, ycyl(f"tube{i}", gr[i], gy[i], gy[i + 1], z=GP[2], verts=16, r2=gr[i + 1], mat="tan"))
for i, y in enumerate((-2.90, -3.58, -4.62, -5.20)):   # 열 차폐 덮개 띠
    b.pt(G, ycyl(f"sleeve_band{i}", gr[min(i + 1, 5)] + 0.010, y - 0.03, y + 0.03, z=GP[2], verts=16, mat="tan_dk"))
b.p(G, ycyl("evacuator", 0.118, -4.10, -4.60, z=GP[2], verts=18, mat="tan"))
b.p(G, ycyl("evac_taper_f", 0.118, -4.60, -4.66, z=GP[2], verts=18, r2=0.088, mat="tan"))
b.p(G, ycyl("evac_taper_r", 0.088, -4.04, -4.10, z=GP[2], verts=18, r2=0.118, mat="tan"))
b.p(G, ytube("muzzle_ring", 0.085, 0.060, MUZ_Y + 0.05, MUZ_Y, z=GP[2], verts=16, mat="tan"))
b.p(G, boxr("mrs", -0.035, 0.035, -5.74, -5.62, GP[2] + 0.075, GP[2] + 0.13, bevel=0.008, mat="tan_dk"))
b.pf(G, ycyl("bore", 0.060, MUZ_Y - 0.002, MUZ_Y + 0.004, z=GP[2], verts=16, mat="black"))
b.pf(G, ycyl("coax_port", 0.035, -2.125, -2.118, x=-0.36, z=1.98, verts=10, mat="black"))
b.pf(G, ycyl("gas_port", 0.030, -2.125, -2.118, x=0.32, z=2.18, verts=10, mat="black"))
for (x, z) in ((-0.40, 1.78), (0.40, 1.78), (-0.40, 2.24), (0.40, 2.24)):
    b.pf(G, vu.radial_disc(f"mant_bolt{x}{z}", (x, -2.122, z), (0, -1, 0), 0.02, 0.008, verts=6, mat="tan_dk"))
b.part(G, GP, parent="gun_pitch")
b.empty("gun_pitch", GP, parent=T, pitchMin=-10, pitchMax=20, weapon="m256")
b.empty("muzzle_main", (0, MUZ_Y, GP[2]), parent="gun_pitch")
b.empty("mount_coax", (-0.36, -1.45, 1.93), parent="gun_pitch", rot=(0, 0, 180), weapon="m240_coax", yawMin=0,
        yawMax=0, pitchMin=0, pitchMax=0, restYawDeg=180)

# ================================================================== 전차장 M2 (피벗 마운트) + 해치들
b.empty("mount_m2_cdr", (CUP[0], PY_CDR, PZ_CDR), parent=T, rot=(0, 0, 180), weapon="m2", yawMin=-180, yawMax=180,
        pitchMin=-10, pitchMax=60, restYawDeg=180)
pin = vu.pintle("cdr_pintle", (CUP[0], PY_CDR, PZ_CDR), post_h=PZ_CDR - (CUP_TOP + 0.02))
b.p("cdr_pintle", *pin["main"])
b.pf("cdr_pintle", *pin["fine"])
b.part("cdr_pintle", (CUP[0], PY_CDR, PZ_CDR), parent="mount_m2_cdr")
hc = vu.lathe("hatch_cdr_plate", [(CUP_TOP, 0.0), (CUP_TOP, 0.37), (CUP_TOP + 0.05, 0.35), (CUP_TOP + 0.07, 0.20),
                                  (CUP_TOP + 0.07, 0.0)], segs=20, axis="z", loc=(CUP[0], CUP[1], 0), smooth=35,
              mat="tan")
b.p("hatch_cdr", hc)
b.pt("hatch_cdr", vu.tube("hatch_cdr_handle", [(CUP[0] - 0.10, CUP[1] - 0.18, CUP_TOP + 0.06),
                                               (CUP[0] - 0.10, CUP[1] - 0.18, CUP_TOP + 0.11),
                                               (CUP[0] + 0.10, CUP[1] - 0.18, CUP_TOP + 0.11),
                                               (CUP[0] + 0.10, CUP[1] - 0.18, CUP_TOP + 0.06)], 0.012,
                          mat="tan_dk", verts=5))
b.part("hatch_cdr", (CUP[0], CUP[1] + 0.38, CUP_TOP + 0.03), parent=T, rotAxis="x", rotDeg=-105)
hl_ = vu.lathe("hatch_ldr_plate", [(ZT1 + 0.08, 0.0), (ZT1 + 0.08, 0.40), (ZT1 + 0.12, 0.38), (ZT1 + 0.13, 0.0)],
               segs=20, axis="z", loc=(LDR[0], LDR[1], 0), smooth=35, mat="tan")
b.p("hatch_loader", hl_)
b.pt("hatch_loader", boxr("hatch_ldr_handle", LDR[0] - 0.10, LDR[0] + 0.10, LDR[1] - 0.22, LDR[1] - 0.18,
                          ZT1 + 0.13, ZT1 + 0.17, bevel=0.008, mat="tan_dk"))
b.part("hatch_loader", (LDR[0], LDR[1] + 0.40, ZT1 + 0.11), parent=T, rotAxis="x", rotDeg=-105)
# 조종수 해치 (앞 경사판 가운데, 들어 올려 오른쪽으로 돌림)
SLOPE = math.degrees(math.atan2(DECK - 1.10, 1.86))
# 해치 구멍: 경사판에 판 검은 우물 (속이 찬 차체라 바닥이 있다). AI 조종수(crew_driver)가 이 구멍으로 머리와 어깨를 내밀고,
# 몸은 우물 바닥 아래 차체 속으로 이어진다. 뚜껑을 열면 검은 구멍이 보인다 (예전에는 구멍 없이 판 위로 몸이 솟았다).
# 앞 잠망경(y -2.76) 바로 뒤까지. 테(턱)는 경사판 위 2.4 cm로 닫은 뚜껑 밑면에 닿는다
DH_X, DH_Y0, DH_Y1, DH_FLOOR = 0.27, -2.75, -2.37, 1.30
GLACIS_Z = lambda y: DECK - (-y - 2.10) * (DECK - 1.10) / 1.86   # noqa: E731
hole = boxr("drv_hole", -DH_X, DH_X, DH_Y0, DH_Y1, DH_FLOOR, 1.70, bevel=0.04, mat="black")
us.cut(hull_obj, hole)
for mod in hull_obj.modifiers:
    if mod.type == "BOOLEAN" and mod.object == hole:
        mod.material_mode = "TRANSFER"      # 구멍 벽·바닥은 검게 (커터 머티리얼)
coam = boxr("drv_coaming", -DH_X - 0.05, DH_X + 0.05, DH_Y0 - 0.04, DH_Y1 + 0.05, 1.380, 1.44, bevel=0.012,
            mat="tan_dk")
us.xform(coam, rot=(SLOPE, 0, 0), pivot=(0, -2.56, 1.416))
us.cut(coam, boxr("drv_coaming_hole", -DH_X, DH_X, DH_Y0, DH_Y1, 1.0, 1.8, bevel=0.04))
b.s(coam)
hd = boxr("hatch_drv_plate", -0.34, 0.34, -2.82, -2.30, 1.44, 1.50, bevel=0.03, mat="tan")
us.xform(hd, rot=(SLOPE, 0, 0), pivot=(0, -2.56, 1.47))
b.p("hatch_driver", hd)
hh = vu.tube("hatch_drv_handle", [(-0.10, -2.40, 1.50), (-0.10, -2.40, 1.55), (0.10, -2.40, 1.55),
                                  (0.10, -2.40, 1.50)], 0.012, mat="tan_dk", verts=5)
us.xform(hh, rot=(SLOPE, 0, 0), pivot=(0, -2.56, 1.47))
b.pt("hatch_driver", hh)
b.part("hatch_driver", (-0.34, -2.56, 1.50), rotAxis="y", rotDeg=-110, lift=0.05)

# ================================================================== 엘프 흔적: 왼쪽 앞 펜더 밧줄 사다리
LX, LY = 1.865, -3.05
for dy in (-0.16, 0.16):
    b.t(vu.tube(f"ladder_rope{dy}", [(LX - 0.10, LY + dy, 1.31), (LX, LY + dy, 1.22), (LX + 0.01, LY + dy * 0.95, 0.70),
                                     (LX + 0.012, LY + dy * 0.9, 0.18)], 0.012, mat="paper", verts=6))
for k, z in enumerate((0.26, 0.50, 0.74, 0.98)):
    b.t(boxr(f"ladder_rung{k}", LX - 0.025, LX + 0.045, LY - 0.19, LY + 0.19, z - 0.025, z + 0.025, bevel=0.008,
             mat="coyote"))
b.t(boxr("ladder_hook", LX - 0.16, LX - 0.06, LY - 0.22, LY + 0.22, 1.29, 1.33, bevel=0.01, mat="black"))

# ================================================================== 자리, 탑승 위치, 등, 배기
b.empty("seat_driver", (0, -2.62, 1.66), controls="drive")
b.empty("seat_gunner", (-0.70, -1.62, 2.66), parent=T, controls="turret,gun_pitch,mount_coax")
b.empty("seat_commander", (CUP[0], PY_CDR + 0.68, PZ_CDR + 0.26), parent=T, controls="mount_m2_cdr")
b.empty("seat_loader", (LDR[0], LDR[1] + 0.05, ZT1 + 0.42), parent=T)
# 해치에 선 승무원 (AI 아군이 몰 때만: M9 성전군 전차, combat/crew.ts). 해치 구멍 가운데, 테 윗면 높이, -Y가 정면.
# 전차장은 큐폴라에 상반신을 내밀고(M2 뒤), 조종수는 앞 해치로 머리를 내민다. 플레이어가 타는 M6 전차에는 쓰지 않는다
b.empty("crew_commander", (CUP[0], CUP[1], CUP_TOP), parent=T)
b.empty("crew_driver", (0.0, -2.56, GLACIS_Z(-2.56) + 0.024))   # 해치 턱 윗면 가운데
b.empty("enter_driver", (2.30, -3.05, 0))
b.empty("enter_gunner", (-2.30, -1.0, 0))
b.empty("enter_commander", (-2.30, 0.3, 0))
b.empty("enter_loader", (2.30, 0.3, 0))
b.empty("exhaust_1", (0, 4.02, 1.13), dir="0,0,-1")
for sx, nm in ((1, "L"), (-1, "R")):
    hx = sx * 1.52
    b.p(f"light_head_{nm}", boxr(f"hl_lens{sx}", hx - 0.08, hx + 0.08, -3.725, -3.718, 1.24, 1.30, mat="lamp"))
    b.part(f"light_head_{nm}", (hx, -3.72, 1.27))
    tl = boxr(f"tl_lens{sx}", min(sx * 1.52, sx * 1.70), max(sx * 1.52, sx * 1.70), 3.978, 3.986, 1.31, 1.41,
              mat="tail")
    b.p(f"light_tail_{nm}", tl)
    b.part(f"light_tail_{nm}", (sx * 1.61, 3.98, 1.36))

# ================================================================== 충돌체
b.col("COL_hull", boxr("c1", -1.84, 1.84, -3.98, 3.98, 0.10, DECK))
b.col("COL_glacis", boxr("c2", -1.10, 1.10, -3.98, -2.10, DECK - 0.20, DECK))
b.col("COL_turret", boxr("c3", -1.80, 1.80, -1.98, 1.95, ZT0, ZT1 + 0.30), parent=T)
b.col("COL_rack", boxr("c4", -1.45, 1.45, 1.95, 2.64, 1.74, 2.30), parent=T)
b.col("COL_gun", boxr("c5", -0.12, 0.12, MUZ_Y, -1.86, GP[2] - 0.12, GP[2] + 0.12), parent="gun_pitch")

b.finish("vehicles/us/m1a1.glb", outline=0.012, thin=0.005, props={
    "vehicleClass": "tracked", "mass": 57000, "maxSpeed": 18.6, "wheelbase": 4.60, "track": 2.87, "armor": "heavy",
    "seats": "driver,gunner,commander,loader",
})
