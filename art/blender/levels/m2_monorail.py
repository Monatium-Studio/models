"""1막 M2 「방어선」 2부: 모노레일 선로 전투 → 시청 중앙역 → 시청 앞 방어선 (D-DAY 10:00 무렵).

npm run model -- art/blender/levels/m2_monorail.py   → public/models/levels/m2_monorail.glb

[원작] 도시 중앙부를 순환하는 모노레일과 중앙역, 모나티엄 시청과 시청 앞 광장, 진압반장 칸나.
       흑뉴아가 칸나를 제압한다(M2). 흑뉴아는 이길 수 없는 존재다. 주말농장 법칙: 아무도 죽지 않는다.
[오리지널] 병기창고 정비 계단 → 궤도 점검 통로 → 멈춘 열차 → 중앙역 → 광장 남쪽 방어선. 칸나의 현장 지휘소는
       시청 포르티코(계단 위 기둥 안쪽). 리타는 방어선 뒤 방호벽에 숨어 흑뉴아가 칸나를 제압하는 것을 본다.
계약 노드: 스크래치패드 act1_level_contract.md "M2 「방어선」 part 2". 실행하면 [m2] 줄에 노드 좌표를 찍는다.

좌표 (Blender, m): 원점 = 광장 가운데, +Y = 북쪽(시청), 중앙로·궤도 y = -20.8, 궤도 보 윗면 z = 8.15,
중앙역 승강장 z = 8.2, 지면 z = 0, 차도 z = -0.15, 시청 포르티코 바닥 z = 0.9.
  - 정비 계단탑 x -235..-225.4 (남쪽 보도) → 다리 → 남쪽 점검 통로. 서쪽 끝 x -237.4에 통행 금지 문.
  - 점검 통로 x -237.6..-33 (보 1.0 m + 양쪽 1.2 m, 난간), 멈춘 열차 x -149.4..-130.6 (2량, 안을 지나간다).
  - 중앙역 x -33..-5, 북쪽 계단탑 x -29.4..-19.8 → 광장 남서 모서리 (-28, -11)로 내려간다.
  - 방어선: 중심 (0, 18), 반지름 26 호 (θ -42..42°, 꼭짓점 (0, -8)), 건설 자리 4곳. 적은 남쪽 큰길과 동쪽 옆길
    (x 42..48, 화면 건물 동쪽)에서 온다. 칸나 지휘소 (-6, 16.5, 0.9), 목격 엄폐 (-5.5, -4.0).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import monatium_defense_kit as dk  # noqa: E402
import monatium_subway_kit as sk  # noqa: E402

cb.reset()
C = mk.City("m2_monorail")
AV = mk.AVENUE_Y
TOP = dk.TRACK_TOP                      # 8.15
PZ = 0.9                                # 시청 포르티코 바닥
WIND = (-0.32, 0.12)                    # 연기가 기우는 쪽 (위성 브리핑 WAR_d0과 같은 바람)
SQ = {k: f"characters/squad_{k}.glb" for k in ("sabre", "rona", "jesty", "karen")}
SQ_W = {"sabre": "m4a1", "rona": "m4a1", "jesty": "m870", "karen": "m249"}
RIOT = "characters/_kit_elfinia_soldier.glb"
NODES = []                              # 보고용 (이름, 좌표)


def M(name, loc, **kw):
    C.marker(name, loc, **kw)
    NODES.append((name, tuple(round(v, 2) for v in loc), kw.get("props", {})))


# ================================================================== 도심 (시청 광장 + 중앙로 서쪽 연장)
A = mk.downtown(C, variant="day", training=False, train=False, highway_on=True, skyline=False, screens=True)
C.group("avenue")
dk.avenue_ext(C, -340.0, -96.0, lamp_pitch=48.0, median_gaps=[(-212.0, -154.0)])   # 기동차가 화단을 건너는 구간
# 상가 옥상 홀로 광고의 뒷면 글자(남쪽, 아무도 못 본다)는 뺀다
dk.drop_text(C, "south", lambda N: N.y < -0.9)
# 도심 COL 보수 (배경 판석, 판석 없는 땅, 중앙 화단, 코어 탑, 표지 문형) + 맵 경계 (서쪽은 중앙로 연장이 닫는다)
dk.downtown_cols(C, A)
dk.downtown_bounds(C, A, west=False)

# 빈 땅 메우기 (downtown 바닥판 사이 틈: 광장 동·서 가장자리, 화면 건물 앞)
C.group("plaza")
# (-48, -28, 12, 14): 훈련장 판석(y 12까지)과 EBI 본부(y 14부터) 사이 2 m 도랑, (-48, -28, 30, 36): EBI 본부 뒤
# (북쪽 보도 y 36까지). 판석이 없으면 바닥이 -0.32라 내려서면 자동 오르기(0.28)로 못 나온다 (M3 f5bd4ed와 같은 자리)
for box in ((24, 42, -11, -9), (24, 26, -9, 22), (26, 42, 9, 11), (40, 42, 11, 22), (-48, -24, -11, -9),
            (-26, -24, -9, 12), (-48, -28, 12, 14), (-48, -28, 30, 36)):
    mk.paving(C, *box, grout=None, tile=1.6)

# 동쪽 옆길 (x 42..48, 화면 건물과 북동 건물 사이): 동쪽에서 오는 적의 길
C.group("avenue")
C.box("asphalt", 43.0, 47.0, -11.0, 38.0, -0.02, 0.02, kind="detail")
for x in (42.0, 47.0):
    C.box("pave_d", x, x + 1.0, -11.0, 38.0, -0.02, 0.06, kind="detail")
C.strip("line_y", (45.0, -10.0, 0.02), (45.0, 37.0, 0.02), 0.1, lift=0.006)
C.col(42.0, 48.0, -11.0, 38.0, -0.4, 0.0)
mk.street_sign(C, 47.6, -10.4, "시청 동로", "CITY HALL E. ST", yaw=0)

# 궤도 기둥 COL (도심 궤도 monorail()은 COL이 없다)
C.group("track")
for k in range(17):
    dk.pillar(C, -120.0 + 16 * k, visual=False)

# ================================================================== 궤도 서쪽 연장 + 점검 통로
CAT_X0, CAT_X1 = -237.6, -33.0
MT_X0, MT_Y0, MT_Y1 = -235.0, -33.6, -29.2            # 정비 계단탑
BR_X0, BR_X1 = -234.85, -232.55                        # 다리 (계단탑 윗참 폭)
dk.track_beam(C, -330.0, -120.0, pillars=[-136.0 - 16 * k for k in range(13)])
dk.catwalks(C, CAT_X0, CAT_X1, openings=[(-1, BR_X0, BR_X1)], low=True)   # 낮은 난간: 너머로 쏜다 (1.1 m 안전 띠)
dk.track_gate(C, -237.4, face=1)
# 문 너머: 찢긴 점검 통로 조각 + 보 위에 추락한 드론, 불
C.rbox("grate", (-241.0, AV - 1.1, TOP - 0.6), (2.6, 1.2, 0.08), rot=(28, 0, 8), kind="detail")
C.rbox("rail_y", (-241.2, AV - 1.7, TOP - 0.1), (2.4, 0.06, 0.06), rot=(30, 10, 4), kind="detail")
dk.crashed_drone(C, -246.0, AV, z=TOP, s=0.9, seed=31, col=False)
dk.fire(C, -245.5, AV - 0.2, TOP + 0.2, s=0.8, seed=3)
dk.smoke_plume(C, -246.0, AV, z=TOP + 1.0, h=34.0, r=1.4, drift=WIND, seed=19, dark=0.7, segs=6)

# 정비 계단탑 (남쪽 보도) + 다리
# 맨 아래 참(서쪽 끝, 남쪽 줄) 남벽에 출입구: 병기창고 정비 계단실(아래 '정비 계단실')이 지상 1층에서 이어진다
MT = dk.stair_tower(C, MT_X0, MT_Y0, MT_Y1, TOP, z0=0.0, top_lane=1, top_end=-1, style="steel",
                    top_open=("+y", BR_X0, BR_X1), bottom_open=("-y", -234.65, -233.05))
# 받침 기둥(y -27.7)은 남쪽 보도(연석 y -27.4 너머, 윗면 0) 위에 선다
dk.bridge(C, BR_X0, BR_X1, MT_Y1, AV - dk.EDGE, top=TOP, posts=(-27.7,), low=True, post_floor=0.0)
# 판석은 계단실 자리(x -235.35..-229.35, y < -33.6)를 비운다
mk.paving(C, MT_X0 - 1.5, MT["x1"] + 1.9, MT_Y0, -30.6, grout=None)
mk.paving(C, MT_X0 - 1.5, -235.35, -34.6, MT_Y0, grout=None)
mk.paving(C, -229.35, MT["x1"] + 1.9, -34.6, MT_Y0, grout=None)
C.text("white", "궤도 정비 계단 · TRACK STAIRS 7", 0.22, (MT_X0 + 4.8, MT_Y1 + 0.02, 3.0), (0, 1, 0), lift=0.02)

# ================================================================== 정비 계단실 (병기창고 → 계단탑, m2_subway와 한 좌표)
# m2_subway.glb는 루트를 SUB만큼 옮겨 내보낸다 (m2_subway.py SHARED): 두 레벨이 한 월드에 함께 붙는다. 계단실은 이 레벨이
# 가진다 (지하를 떼어도 남는다). 창고 서벽 문(x 66..67, 지하 레벨) → B3 → B2 → B1 → 중간참 → 지상 1층 → 북벽 출입구 →
# 계단탑 맨 아래 참. 지하 쪽 좌표(옮기기 전)로 적고 s*()로 옮긴다. 지상으로 나온 부분(1층 + 천장)이 계단탑 남쪽 콘크리트 계단실이다.
SUB = (-296.35, -2.6, -8.83)


def sx(v):
    return v + SUB[0]


def sy(v):
    return v + SUB[1]


def sz(v):
    return v + SUB[2]


# ------------------------------------------------------------------ 정비 계단실 꾸밈
# 층마다(B3 · B2 · B1 · 1F) 열리지 않는 강철 방화문(문틀, 손잡이, 망입 유리, 도어 클로저, 옆에 층 판, 위에 비상구 유도등).
# 문은 벽에 붙은 장식이라 벽 COL이 그대로 막는다. 벽 아래 칠(바닥·디딤 선 위 1 m, 청록 띠), 큰 층 스텐실, 철망 벽등
# (B3 꺼짐 → B2 깜빡임 → B1 · 중간참 · 1층 켜짐: 위로 갈수록 밝다), 배관·전선관, 소화전함 · 소화기(B2), 분전반(B1),
# 환기 그릴, 물때, 전투 뒤 떨어진 것(헬멧, 탄약통, 종이), 계단 안쪽(가운데 벽) 손잡이. 걷는 길과 계단 폭은 그대로다:
# 벽에서 6 cm 넘게 나온 것(소화전함, 분전반, 배관, 손잡이)만 벽에 붙인 COL(끝을 깎은 볼록)을 두고 나머지는 COL이 없다.
from mathutils import Matrix, Vector  # noqa: E402
import home_weapons as hw  # noqa: E402

# 철망 벽등 (흰빛): 발광 키, 켜진 색, 번짐, 꺼진 렌즈. lamp_w · exit_g(유도등)는 방어 키트 팔레트 그대로
sk.EMERG["w"] = ("lamp_w", "#fff4dc", "halo_w", "lamp_dead")
mk.ALPHA.update({"halo_w": ("#fff2d2", 0.12)})
mk.PAL.update({"grime": "#d4cdc6"})             # 물때 (벽 콘크리트 #dcd8d4보다 조금 어둡게)


def _wall(P, N):
    """벽면 좌표 f(u, v, d) = P + R u + U v + N d (R = 벽을 볼 때 오른쪽, U = 위, N = 벽에서 나오는 쪽)."""
    R, U, Nv = mk.frame(N)
    P = Vector(P)
    return (lambda u, v, d=0.0: tuple(P + R * u + U * v + Nv * d)), tuple(Nv)


def exit_sign(C, f, N, u, v):
    """비상구 유도등: 남색 갑 + 녹색 발광 판 + 흰 '비상구 EXIT', 문으로 달리는 사람."""
    C.plate("navy", hw.rrect(0.52, 0.21, 0.03, 2), f(u, v), N, 0.07, kind="detail", back=0.005)
    C.rect("exit_g", f(u, v, 0.065), N, 0.47, 0.165, lift=0.002)
    C.text("lamp_w", "비상구", 0.075, f(u + 0.075, v + 0.028, 0.065), N, lift=0.012)
    C.text("lamp_w", "EXIT", 0.042, f(u + 0.075, v - 0.047, 0.065), N, lift=0.012)
    pu, pv, d = u - 0.165, v - 0.005, 0.077
    C.decal("lamp_w", hw.circle(0.013, 8), f(pu + 0.012, pv + 0.052, 0.065), N, lift=0.012)
    for (a, b, w) in (((0.007, 0.034), (-0.008, -0.004), 0.017),
                      ((-0.008, -0.004), (-0.03, -0.03), 0.012), ((-0.03, -0.03), (-0.044, -0.06), 0.011),
                      ((-0.008, -0.004), (0.017, -0.026), 0.012), ((0.017, -0.026), (0.01, -0.06), 0.011),
                      ((0.004, 0.026), (0.03, 0.01), 0.01), ((0.004, 0.026), (-0.022, 0.012), 0.01)):
        C.strip("lamp_w", f(pu + a[0], pv + a[1], d), f(pu + b[0], pv + b[1], d), w, N, lift=0.0)
    C.ring("lamp_w", hw.rrect(0.05, 0.12, 0.004, 1), hw.rrect(0.034, 0.104, 0.003, 1), f(pu + 0.075, pv, 0.065), N,
           lift=0.012)


def fire_door(C, P, N, *, w=0.95, h=2.0, hinge=1, staff=False, sign=True):
    """열리지 않는 강철 방화문. P = 벽면 · 바닥 위 문 가운데, N = 문이 보이는 쪽. hinge = 경첩 쪽(+1 = 벽을 볼 때 오른쪽).
    문틀 앞면은 벽에서 6 cm, 문짝 앞면 3 cm (COL 없음: 벽 COL이 막는다). 반환: 벽면 좌표 f, N."""
    f, N = _wall(P, N)
    fw = 0.07
    C.plate("navy", [(-w / 2 - fw, 0), (-w / 2, 0), (-w / 2, h), (w / 2, h), (w / 2, 0), (w / 2 + fw, 0),
                     (w / 2 + fw, h + fw), (-w / 2 - fw, h + fw)], f(0, 0), N, 0.065, kind="detail", back=0.005)
    C.plate("violet", [(-w / 2 + 0.003, 0.004), (w / 2 - 0.003, 0.004), (w / 2 - 0.003, h - 0.004),
                       (-w / 2 + 0.003, h - 0.004)], f(0, 0), N, 0.035, kind="detail", back=0.005)
    lf = 0.03                                                            # 문짝 앞면
    C.rect("steel", f(0, 0.13, lf), N, w - 0.07, 0.2, lift=0.003)        # 발판
    # 망입 유리 (어두운 유리 + 철사 격자 + 테)
    C.rect("dark", f(0, 1.22, lf), N, 0.2, 0.32, lift=0.003)
    for i in range(1, 4):
        C.strip("steel", f(-0.1 + 0.05 * i, 1.06, lf + 0.008), f(-0.1 + 0.05 * i, 1.38, lf + 0.008), 0.004, N, lift=0.0)
    for i in range(1, 6):
        C.strip("steel", f(-0.1, 1.06 + 0.32 * i / 6, lf + 0.008), f(0.1, 1.06 + 0.32 * i / 6, lf + 0.008), 0.004, N,
                lift=0.0)
    C.ring("steel", hw.rrect(0.25, 0.37, 0.02, 2), hw.rrect(0.2, 0.32, 0.008, 2), f(0, 1.22, lf), N, lift=0.006)
    # 손잡이 (레버 + 판 + 열쇠 구멍)
    ul = -hinge * (w / 2 - 0.1)
    C.plate("steel", hw.rrect(0.05, 0.2, 0.02, 2), f(ul, 0.78, lf), N, 0.008, kind="detail")
    C.cyl("steel", f(ul, 0.82, lf + 0.008), f(ul, 0.82, lf + 0.05), 0.014, segs=8, kind="detail")
    C.beam("steel", f(ul, 0.82, lf + 0.056), f(ul + hinge * 0.13, 0.815, lf + 0.056), 0.022, 0.02, kind="detail")
    C.decal("dark", hw.circle(0.009, 8), f(ul, 0.72, lf + 0.008), N, lift=0.002)
    # 경첩 셋
    for v in (0.25, 1.0, 1.75):
        C.cyl("steel", f(hinge * (w / 2 + 0.002), v - 0.06, 0.036), f(hinge * (w / 2 + 0.002), v + 0.06, 0.036), 0.013,
              segs=8, kind="detail")
    # 도어 클로저 (경첩 쪽 위: 몸통 + 팔 + 문틀 받침)
    ub = hinge * (w / 2 - 0.07)
    C.beam("navy", f(ub, h - 0.085, lf + 0.034), f(ub - hinge * 0.3, h - 0.085, lf + 0.034), 0.062, 0.07, kind="detail")
    C.beam("steel", f(ub - hinge * 0.27, h - 0.06, lf + 0.072), f(ub - hinge * 0.03, h + 0.03, 0.09), 0.018, 0.012,
           kind="detail")
    C.plate("steel", hw.rrect(0.09, 0.045, 0.008, 2), f(ub - hinge * 0.03, h + 0.035, 0.06), N, 0.02, kind="detail")
    # 문턱 (1.2 cm, COL 없음). 벽면에서 시작해 문틀 바깥 끝보다 6 mm 짧고 바닥에서 1.5 mm 뜬다 (문틀 · 문짝 면과 같은 평면에 겹치지 않게)
    a, b = f(-w / 2 - fw + 0.006, 0, 0.0), f(w / 2 + fw - 0.006, 0, 0.1)
    C.box("steel", min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1]), a[2] + 0.0015, a[2] + 0.012,
          kind="detail")
    if staff:
        C.plate("red", hw.rrect(0.44, 0.15, 0.02, 2), f(0, 1.6, lf), N, 0.006, kind="detail")
        C.text("white", "관계자 외 출입금지", 0.04, f(0, 1.622, lf + 0.006), N, lift=0.005)
        C.text("white", "STAFF ONLY", 0.028, f(0, 1.565, lf + 0.006), N, lift=0.005)
    else:
        C.text("white", "방화문 · 항상 닫아 두십시오", 0.03, f(0, 1.6, lf), N, lift=0.005)
        C.text("white", "FIRE DOOR · KEEP CLOSED", 0.022, f(0, 1.56, lf), N, lift=0.005)
    if sign:
        exit_sign(C, f, N, 0.0, h + 0.25)
    return f, N


def floor_plate(C, f, N, u, num, ko, en):
    """문 옆 층 판 (남색 + 남보라 테): 큰 층 번호, 한글, 영문."""
    sk.sign(C, f(u, 1.38), N, 0.36, 0.42, [(num, 0.16, "white", 0.065, 0.0), (ko, 0.052, "white", -0.07, 0.0),
                                          (en, 0.03, "glow", -0.14, 0.0)], rim="violet", depth=0.03)


def bulkhead(C, ls, P, N, *, top=None):
    """철망 벽등: 남색 받침 + 꺼진 렌즈(늘 보임) + 켜진 렌즈(ls, None이면 꺼진 등) + 철망. top: 위로 전선관 끝 높이."""
    f, N = _wall(P, N)
    C.plate("navy", hw.stadium(0.34, 0.2, 4), f(0, 0), N, 0.035, kind="detail", back=0.004)
    C.plate("lamp_dead", hw.stadium(0.26, 0.13, 4), f(0, 0, 0.031), N, 0.045, kind="fine")
    if ls is not None:
        pts = hw.stadium(0.27, 0.14, 4)
        Rv, Uv, Nv = mk.frame(N)
        c = Vector(f(0, 0, 0.092))

        def fn(b, c=c, R=Rv, U=Uv, Nn=Nv):
            vs = [b.verts.new(c + R * u + U * v) for u, v in pts]
            fc = b.faces.new(vs)
            fc.normal_update()
            if fc.normal.dot(Nn) < 0:
                fc.normal_flip()
        ls.add(fn)
        ls.add_halo(f(0, 0, 0.022), N, 0.6)
    for v in (-0.04, 0.0, 0.04):
        q = [(-0.165, v, 0.03), (-0.13, v, 0.1), (0.13, v, 0.1), (0.165, v, 0.03)]
        for a, b in zip(q, q[1:]):
            C.beam("steel", f(*a), f(*b), 0.011, 0.011, kind="detail")
    for u in (-0.075, 0.075):
        q = [(u, -0.1, 0.03), (u, -0.068, 0.1), (u, 0.068, 0.1), (u, 0.1, 0.03)]
        for a, b in zip(q, q[1:]):
            C.beam("steel", f(*a), f(*b), 0.011, 0.011, kind="detail")
    if top is not None:
        p0 = f(0, 0.1, 0.02)
        C.cyl("steel", p0, (p0[0], p0[1], top), 0.014, segs=6, kind="detail")


def riser(C, key, x, y, z0, z1, r, wall, *, collars=()):
    """세운 배관 + 벽 걸쇠(1.6 m마다, wall = 벽 쪽 (dx, dy)) + 바닥 관통 칼라(collars = 칼라 아래 높이들)."""
    C.cyl(key, (x, y, z0), (x, y, z1), r, segs=10, kind="detail", cap=False)
    z = z0 + 0.9
    while z < z1 - 0.3:
        C.cyl("steel", (x, y, z - 0.02), (x, y, z + 0.02), r + 0.012, segs=10, kind="detail")
        C.beam("steel", (x, y, z), (x + wall[0] * (r + 0.13), y + wall[1] * (r + 0.13), z), 0.03, 0.035, kind="detail")
        z += 1.6
    for zc in collars:
        C.cyl("steel", (x, y, zc), (x, y, zc + 0.035), r + 0.03, segs=10, kind="detail")


def hose_cabinet(C, ls, P, N, *, w=0.7, h=0.9, z0=0.32):
    """옥내 소화전함 (적색 함 + 창 너머 감긴 호스 + 표시등: 적색 비상등 묶음 ls에 넣는다). P = 벽면 · 바닥."""
    f, N = _wall(P, N)
    d = 0.155
    C.plate("red", hw.rrect(w, h, 0.02, 2), f(0, z0 + h / 2), N, d, kind="detail", back=0.005)
    fr = d - 0.005
    C.ring("steel", hw.rrect(w - 0.04, h - 0.04, 0.015, 2), hw.rrect(w - 0.07, h - 0.07, 0.01, 2), f(0, z0 + h / 2, fr),
           N, lift=0.003)
    wc = f(0, z0 + h * 0.4, fr)
    C.rect("dark", wc, N, w - 0.2, h * 0.42, lift=0.004)
    C.ring("white", hw.circle(0.15, 16), hw.circle(0.085, 16), wc, N, lift=0.012)
    C.decal("steel", hw.circle(0.035, 10), wc, N, lift=0.012)
    C.text("white", "소화전", 0.08, f(0, z0 + h * 0.8, fr), N, lift=0.006)
    C.text("white", "FIRE HOSE", 0.034, f(0, z0 + h * 0.69, fr), N, lift=0.006)
    C.beam("steel", f(w / 2 - 0.05, z0 + h * 0.34, fr + 0.012), f(w / 2 - 0.05, z0 + h * 0.5, fr + 0.012), 0.02, 0.02,
           kind="detail")
    lu, lv = 0.17, z0 + h + 0.09
    C.cyl("steel", f(lu, lv, 0.0), f(lu, lv, 0.04), 0.05, segs=12, kind="detail")
    C.cyl(ls.off_key, f(lu, lv, 0.04), f(lu, lv, 0.07), 0.04, segs=12, kind="detail")
    p0, p1 = Vector(f(lu, lv, 0.039)), Vector(f(lu, lv, 0.075))
    ls.add(lambda b, p0=p0, p1=p1: mk._bm_cyl(b, p0, p1, 0.044, segs=12))
    ls.add_halo(f(lu, lv, 0.02), N, 0.3)


def extinguisher(C, x, y, z):
    """바닥에 선 소화기 (엘프 크기, 높이 0.47 m)."""
    C.cyl("red", (x, y, z), (x, y, z + 0.36), 0.07, segs=12, kind="detail")
    C.cyl("red", (x, y, z + 0.36), (x, y, z + 0.4), 0.07, r2=0.035, segs=12, kind="detail")
    C.cyl("steel", (x, y, z + 0.4), (x, y, z + 0.45), 0.022, segs=8, kind="detail")
    C.beam("steel", (x - 0.01, y, z + 0.465), (x + 0.075, y, z + 0.475), 0.022, 0.012, kind="detail")
    C.cyl("navy", (x + 0.025, y + 0.02, z + 0.43), (x + 0.06, y + 0.07, z + 0.2), 0.012, segs=6, kind="detail")


def vent(C, P, N, w, h):
    """환기 그릴 (남색 테 + 어두운 구멍 + 가로 날개). P = 그릴 가운데 (벽면)."""
    f, N = _wall(P, N)
    C.plate("navy", hw.rrect(w + 0.07, h + 0.07, 0.015, 2), f(0, 0), N, 0.022, kind="detail", back=0.004)
    C.rect("dark", f(0, 0, 0.018), N, w, h, lift=0.002)
    n = max(3, int(h / 0.055))
    for i in range(n):
        vv = -h / 2 + (i + 0.5) * h / n
        C.beam("steel", f(-w / 2, vv, 0.032), f(w / 2, vv, 0.032), 0.03, 0.009, kind="fine")


def elec_panel(C, P, N, *, w=0.62, h=0.95, z0=0.5, top=None):
    """분전반 (강철 함 + 가운데 틈 + 손잡이 + 고압 위험 표지 + 이름 판, 위로 전선관 셋). P = 벽면 · 바닥."""
    f, N = _wall(P, N)
    d = 0.13
    C.plate("steel", hw.rrect(w, h, 0.015, 2), f(0, z0 + h / 2), N, d, kind="detail", back=0.005)
    fr = d - 0.005
    C.strip("dark", f(0, z0 + 0.03, fr), f(0, z0 + h - 0.03, fr), 0.006, N, lift=0.003)
    for s in (-1, 1):
        C.beam("navy", f(s * 0.045, z0 + h * 0.45, fr + 0.012), f(s * 0.045, z0 + h * 0.58, fr + 0.012), 0.02, 0.02,
               kind="detail")
    tc = f(-w / 4, z0 + h * 0.78, fr)
    C.decal("hazard", [(-0.075, -0.06), (0.075, -0.06), (0.0, 0.07)], tc, N, lift=0.003)
    C.decal("dark", [(0.004, 0.05), (-0.018, 0.0), (-0.002, 0.0), (-0.01, -0.05), (0.018, 0.008), (0.002, 0.008)],
            tc, N, lift=0.008)
    C.text("dark", "고압 위험", 0.034, f(-w / 4, z0 + h * 0.64, fr), N, lift=0.004)
    C.plate("navy", hw.rrect(0.22, 0.1, 0.012, 2), f(w / 4, z0 + h * 0.78, fr), N, 0.004, kind="detail")
    C.text("white", "분전반", 0.042, f(w / 4, z0 + h * 0.79, fr + 0.004), N, lift=0.004)
    C.text("glow", "EPS B1", 0.022, f(w / 4, z0 + h * 0.745, fr + 0.004), N, lift=0.004)
    if top is not None:
        for k in range(3):
            p0 = f(-w / 2 + 0.12 + k * 0.14, z0 + h - 0.01, 0.045)
            C.cyl("steel", p0, (p0[0], p0[1], top), 0.02, segs=6, kind="detail")


def platform_sign(C, P, N, arrow):
    """'모노레일 승강장 · MONORAIL PLATFORM' 안내판: 화살표(arrow +1 = 벽을 볼 때 오른쪽) + 반대쪽 엘프 로고."""
    f, N = _wall(P, N)
    w = 1.5
    sk.sign(C, f(0, 0), N, w, 0.46, [("모노레일 승강장", 0.105, "white", 0.06, 0.0),
                                    ("MONORAIL PLATFORM", 0.045, "glow", -0.06, 0.0),
                                    ("선로 계단탑 7 · 1층", 0.035, "white", -0.14, 0.0)], rim="gold", depth=0.03)
    au = arrow * (w / 2 - 0.2)
    pts = [(-0.13, 0.03), (0.02, 0.03), (0.02, 0.08), (0.14, 0.0), (0.02, -0.08), (0.02, -0.03), (-0.13, -0.03)]
    C.decal("white", [(au + arrow * px, py) for px, py in pts], f(0, 0, 0.03), N, lift=0.01)
    C.logo(f(-au, 0, 0.03), 0.28, N, key="gold", lift=0.01)


def streak(C, P, N, w, L, seed):
    """물때: 윗 끝(P, 벽면 가운데)에서 폭 w로 번지고 아래 끝은 길이가 다른 줄기 몇 개로 흘러내린다 (최대 L)."""
    f, N = _wall(P, N)
    rng = random.Random(seed)
    m = max(2, int(w / 0.18))
    fw = w / m
    pts = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, -0.35 * L)]
    for k in reversed(range(m)):
        uc = -w / 2 + fw * (k + 0.5)
        lk = L * rng.uniform(0.55, 1.0)
        pts += [(uc + fw * 0.48, -0.45 * L), (uc + fw * 0.3, -lk), (uc - fw * 0.3, -lk), (uc - fw * 0.48, -0.45 * L)]
    pts.append((-w / 2, -0.35 * L))
    C.decal("grime", pts, f(0, 0), N, lift=0.015)


def puddle(C, x, y, z, r, seed, *, key="grime"):
    """바닥 물 얼룩 (어두운 바닥 B3 · B2는 key="floor_ar_d")."""
    rng = random.Random(seed)
    pts = [(math.cos(a) * r * rng.uniform(0.7, 1.15), math.sin(a) * r * rng.uniform(0.5, 0.9))
           for a in (2 * math.pi * i / 12 for i in range(12))]
    C.decal(key, pts, (x, y, z), (0, 0, 1), up=(0, 1, 0), lift=0.016)


def papers(C, x, y, z, n, seed):
    """흩어진 서류 (흰 종이 + 인쇄 줄)."""
    rng = random.Random(seed)
    for i in range(n):
        a = rng.uniform(0, math.pi)
        ca, sa = math.cos(a), math.sin(a)
        cx, cy = x + rng.uniform(-0.35, 0.35), y + rng.uniform(-0.3, 0.3)
        lift = 0.02 + 0.003 * i

        def rot(q):
            return [(ca * u - sa * v, sa * u + ca * v) for u, v in q]
        C.decal("white", rot([(-0.105, -0.15), (0.105, -0.15), (0.105, 0.15), (-0.105, 0.15)]), (cx, cy, z), (0, 0, 1),
                up=(0, 1, 0), lift=lift)
        for k in range(4):
            vv = 0.1 - k * 0.045
            C.decal("dark", rot([(-0.075, vv - 0.006), (0.075 - 0.03 * (k % 2), vv - 0.006), (0.075 - 0.03 * (k % 2), vv + 0.006),
                                 (-0.075, vv + 0.006)]), (cx, cy, z), (0, 0, 1), up=(0, 1, 0), lift=lift + 0.0015)


def helmet(C, x, y, z, yaw, tilt=8.0):
    """떨어진 헬멧 (노획 미군 PASGT형, 엘프 머리 크기). COL 없음."""
    b = C.bm("od", "detail")
    Mx = (Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
          @ Matrix.Rotation(math.radians(tilt), 4, "Y"))
    segs, rings, rx, ry, hh = 16, 5, 0.25, 0.28, 0.2
    rows = []
    for i in range(rings):
        t = (math.pi / 2) * i / rings
        k = math.cos(t)
        rows.append([b.verts.new(Mx @ Vector((rx * k * math.cos(2 * math.pi * j / segs), ry * k * math.sin(2 * math.pi * j / segs),
                                              0.03 + hh * math.sin(t)))) for j in range(segs)])
    top = b.verts.new(Mx @ Vector((0, 0, 0.03 + hh)))
    for i in range(rings - 1):
        for j in range(segs):
            jn = (j + 1) % segs
            b.faces.new((rows[i][j], rows[i][jn], rows[i + 1][jn], rows[i + 1][j]))
    for j in range(segs):
        b.faces.new((rows[-1][j], rows[-1][(j + 1) % segs], top))
    out = [b.verts.new(Mx @ Vector((rx * 1.12 * math.cos(2 * math.pi * j / segs), ry * 1.12 * math.sin(2 * math.pi * j / segs),
                                    0.004))) for j in range(segs)]
    for j in range(segs):
        jn = (j + 1) % segs
        b.faces.new((out[j], out[jn], rows[0][jn], rows[0][j]))
    C.strip("dark", (x + 0.12, y - 0.2, z + 0.004), (x + 0.32, y - 0.32, z + 0.004), 0.025, lift=0.01)   # 턱끈


def ammo_can(C, x, y, z, *, along_x=True):
    """노획 미군 탄약통 (올리브 + 손잡이 + 노랑 스텐실). COL 없음."""
    lx, ly = (0.3, 0.15) if along_x else (0.15, 0.3)
    C.box("od", x - lx / 2, x + lx / 2, y - ly / 2, y + ly / 2, z, z + 0.19, kind="detail")
    C.box("od", x - lx / 2 + 0.01, x + lx / 2 - 0.01, y - ly / 2 + 0.01, y + ly / 2 - 0.01, z + 0.19, z + 0.205, kind="detail")
    a = (x - lx / 2 + 0.07, y, z + 0.215) if along_x else (x, y - ly / 2 + 0.07, z + 0.215)
    b = (x + lx / 2 - 0.07, y, z + 0.215) if along_x else (x, y + ly / 2 - 0.07, z + 0.215)
    C.beam("steel", a, b, 0.025, 0.012, kind="detail")
    if along_x:
        C.text("hazard", "CTG 5.56MM", 0.024, (x, y - ly / 2, z + 0.11), (0, -1, 0), lift=0.004)
    else:
        C.text("hazard", "CTG 5.56MM", 0.024, (x + lx / 2, y, z + 0.11), (1, 0, 0), lift=0.004)


BAND_H = 1.0


def band(C, axis, c, s, a0, a1, z_a, z_b, *, zf=None):
    """벽 아래 칠 (concrete_d, 기준선 위 1 m) + 청록 띠 5 cm. axis 'x': 벽 x = c(면 쪽 s = ±1), a = y. 'y': 벽 y = c, a = x.
    z_a · z_b = 두 끝의 기준(바닥, 계단 옆은 아래 참 바닥 → 위 참 바닥을 잇는 선). zf: 계단 옆이면 계단 덩어리 밑면 (칠 아래
    끝을 기준선 0.35 m 밑으로 내려 디딤판 속에 숨기되 덩어리 밑으로는 내리지 않는다: 아래 계단에서 올려다보인다)."""
    def P(a, z, lift=0.012):
        return (c + s * lift, a, z) if axis == "x" else (a, c + s * lift, z)
    N = (s, 0, 0) if axis == "x" else (0, s, 0)
    if zf is None:
        lo = [(a0, z_a + 0.002), (a1, z_b + 0.002)]
    else:
        lo = [(a0, max(z_a - 0.35, zf))]
        if (z_a - 0.35 - zf) * (z_b - 0.35 - zf) < 0:
            lo.append((a0 + (a1 - a0) * (zf - (z_a - 0.35)) / (z_b - z_a), zf))
        lo.append((a1, max(z_b - 0.35, zf)))
    C.poly("concrete_d", [P(a, z) for a, z in lo + [(a1, z_b + BAND_H), (a0, z_a + BAND_H)]], normal=N, kind="under")
    C.poly("teal", [P(a, z, 0.013) for a, z in ((a0, z_a + BAND_H), (a1, z_b + BAND_H), (a1, z_b + BAND_H + 0.05),
                                                (a0, z_a + BAND_H + 0.05))], normal=N, kind="fine")


def dress_stairwell(ls):
    """정비 계단실 꾸밈 (위 설명). ls = 계단실 적색 비상등 묶음 (소화전 표시등을 더한다)."""
    zw, zm, zt, zu, z1 = sz(-0.75), sz(1.65), sz(4.05), sz(6.45), sz(8.85)
    zs = z1 + 3.0
    xw, xe, ys, yn = sx(61.5), sx(66.0), sy(-47.0), sy(-31.5)
    ex = sx(65.98) + 0.005              # 동벽 면 (지하 창고 앞 얇은 벽 -230.37, 그 위 두꺼운 벽 -230.365)
    spw, spe = sx(63.5), sx(64.0)       # 가운데 벽 서·동 면
    yan, yas = sy(-35.5), sy(-41.5)     # 북쪽 참 남쪽 끝(-38.1) · 남쪽 참 북쪽 끝(-44.1) = 계단 양 끝
    lw = sk.LampSet("stair_w", "w", group="stair")
    lf = sk.LampSet("stair_flk", "w", group="stair", blink=0.19)

    # ---- 벽 아래 칠: 참 둘레 + 계단 옆 (바깥 벽, 가운데 벽)
    for z in (zw, zt, z1):                                               # 북쪽 참 (B3, B1, 1F)
        band(C, "x", xw, 1, yan, yn, z, z)
        if z != zw:                                                      # B3 동벽은 아래 (병기창고 문 구멍)
            band(C, "x", ex, -1, yan, yn, z, z)
        if z == z1:
            band(C, "y", yn, -1, xw, -234.65, z, z)
            band(C, "y", yn, -1, -233.05, ex, z, z)
        else:
            band(C, "y", yn, -1, xw, ex, z, z)
        band(C, "y", yan, 1, xw if z == zw else spw, spe, z, z)          # B3은 서쪽 줄 계단 덩어리 앞면까지
    band(C, "x", ex, -1, yan, sy(-34.43), zw, zw)                        # B3 동벽: 병기창고 문 구멍 양옆
    band(C, "x", ex, -1, sy(-32.37), yn, zw, zw)
    for z in (zm, zu):                                                   # 남쪽 참 (B2, 중간참)
        band(C, "x", xw, 1, ys, yas, z, z)
        band(C, "x", ex, -1, ys, yas, z, z)
        band(C, "y", ys, 1, xw, ex, z, z)
        band(C, "y", yas, -1, spw, spe, z, z)
    for (z_lo, z_hi, zf) in ((zw, zm, zw), (zt, zu, zt)):                # 동쪽 줄 (남으로 오른다)
        band(C, "x", ex, -1, yan, yas, z_lo, z_hi, zf=zf)
        band(C, "x", spe, 1, yan, yas, z_lo, z_hi, zf=zf)
    for (z_lo, z_hi, zf) in ((zm, zt, zw), (zu, z1, zu)):                # 서쪽 줄 (북으로 오른다)
        band(C, "x", xw, 1, yas, yan, z_lo, z_hi, zf=zf)
        band(C, "x", spw, -1, yas, yan, z_lo, z_hi, zf=zf)

    # ---- 계단 손잡이: 가운데 벽에도 (바깥 손잡이와 같은 선, 끝은 가운데 벽 모서리에서 0.25 m 안), 걸쇠는 양쪽 모두
    rails = ((xe, -1, sy(-35.3), zw, yas, zm), (xw, 1, yas, zm, sy(-35.3), zt),
             (xe, -1, sy(-35.3), zt, yas, zu), (xw, 1, yas, zu, sy(-35.3), z1))
    for (wx, s, ya, za, yb, zb) in rails:
        def zr(y, ya=ya, za=za, yb=yb, zb=zb):
            return za + (y - ya) / (yb - ya) * (zb - za) + 0.85
        face = spe if s < 0 else spw                                     # 바깥 벽 손잡이의 맞은편 = 가운데 벽 면
        xc = face - s * 0.08
        y0, y1 = (yan - 0.25, yas + 0.25) if ya > yb else (yas + 0.25, yan - 0.25)
        C.cyl("hazard", (xc, y0, zr(y0)), (xc, y1, zr(y1)), 0.03, segs=6, kind="detail")
        C.ccol([(xx, yy, zr(yy) + dz) for xx in (face, face - s * 0.12) for yy in (y0, y1) for dz in (-0.05, 0.05)])
        for (wf, xr) in ((face, xc), (wx, wx + s * 0.08)):
            for t in (0.12, 0.5, 0.88):
                y = y0 + (y1 - y0) * t
                C.beam("steel", (wf, y, zr(y) - 0.07), (xr, y, zr(y) - 0.07), 0.025, 0.02, kind="detail")
                C.beam("steel", (xr, y, zr(y) - 0.075), (xr, y, zr(y) - 0.025), 0.02, 0.02, kind="detail")

    # ---- 배관: 북동 모서리(B3 → 천장, 강철 급수관 + 남색 전선관), 남동 모서리(B2 → 천장, 적색 소화 배관 + 강철 배수관)
    riser(C, "steel", xe - 0.15, yn - 0.12, zw, zs, 0.06, (0, 1), collars=(zt, zt - 0.335, z1, z1 - 0.335))
    riser(C, "navy", xe - 0.36, yn - 0.09, zw, zs, 0.035, (0, 1), collars=(zt, z1))
    C.col(xe - 0.45, xe, yn - 0.24, yn, zw, zs)
    riser(C, "red", xe - 0.15, ys + 0.1, zm, zs, 0.055, (0, -1), collars=(zu, zu - 0.335))
    riser(C, "steel", xe - 0.35, ys + 0.1, zm, zs, 0.04, (0, -1), collars=(zu,))
    C.col(xe - 0.45, xe, ys, ys + 0.22, zm, zs)

    # ---- B3 (병기창고 층): 북벽 기계실 문 (관계자 외 출입금지), 서벽 비상계단 표지, 꺼진 벽등, 낮은 그릴, 탄약통·종이
    f, N = fire_door(C, (-233.85, yn, zw), (0, -1, 0), staff=True)
    floor_plate(C, f, N, 0.85, "B3", "지하 3층", "BASEMENT 3 · 기계실")
    C.text("white", "B3", 0.5, f(0.0, 2.85), N, lift=0.018)
    sk.sign(C, (xw + 0.01, sy(-33.5), zw + 2.32), (1, 0, 0), 1.7, 0.5,
            [("비상계단", 0.13, "white", 0.07, -0.16), ("EMERGENCY STAIRS", 0.055, "glow", -0.1, -0.16)], rim="gold",
            depth=0.03)
    C.logo((xw + 0.04, sy(-33.5) + 0.6, zw + 2.32), 0.31, (1, 0, 0), key="gold", lift=0.01)
    bulkhead(C, None, (-231.45, yn, zw + 2.55), (0, -1, 0), top=zt - 0.3)
    vent(C, (xw, sy(-32.15), zw + 0.32), (1, 0, 0), 0.55, 0.28)
    ammo_can(C, xw + 0.12, yan + 0.17, zw, along_x=False)
    ammo_can(C, xw + 0.45, yan + 0.1, zw)
    papers(C, -233.9, -37.2, zw, 3, 31)
    puddle(C, xe - 0.5, yn - 0.55, zw, 0.4, 3, key="floor_ar_d")
    streak(C, (-232.2, yn, zt - 0.3), (0, -1, 0), 0.5, 1.4, 5)
    streak(C, (xw, sy(-32.9), zt - 0.3), (1, 0, 0), 0.4, 1.0, 6)

    # ---- B2: 남벽 문 + 층 판, 소화전함 · 소화기, 깜빡이는 벽등, 그릴, 헬멧
    f, N = fire_door(C, (-233.35, ys, zm), (0, 1, 0))
    floor_plate(C, f, N, -0.85, "B2", "지하 2층", "BASEMENT 2")
    C.text("white", "B2", 0.5, f(0.0, 2.85), N, lift=0.018)
    hose_cabinet(C, ls, (-231.25, ys, zm), (0, 1, 0))
    extinguisher(C, -231.88, ys + 0.13, zm)
    sk.sign(C, (-231.88, ys + 0.01, zm + 0.95), (0, 1, 0), 0.3, 0.13,
            [("소화기", 0.06, "white", 0.012, 0.0), ("EXTINGUISHER", 0.022, "white", -0.042, 0.0)], key="red", rim=None,
            depth=0.02)
    C.cyl("red", (xe - 0.15, ys + 0.1, zm + 1.4), (-231.0, ys + 0.1, zm + 1.4), 0.032, segs=8, kind="detail")
    C.cyl("red", (-231.0, ys + 0.1, zm + 1.432), (-231.0, ys + 0.1, zm + 1.215), 0.032, segs=8, kind="detail")
    C.cyl("steel", (-231.0, ys + 0.1, zm + 1.25), (-231.0, ys + 0.1, zm + 1.29), 0.045, segs=8, kind="detail")   # 밸브
    # 소화전함 + 소화기 COL: 서쪽 끝을 깎는다 (남벽을 따라 걸어도 모서리에 서지 않고 비켜 간다)
    C.ccol([(x, y, z) for (x, y) in ((-232.0, ys), (xe - 0.45, ys), (xe - 0.45, ys + 0.21), (-231.84, ys + 0.21))
            for z in (zm, zm + 1.35)])
    bulkhead(C, lf, (-231.25, ys, zm + 2.45), (0, 1, 0), top=zu - 0.3)
    vent(C, (-234.35, ys, zm + 0.4), (0, 1, 0), 0.5, 0.28)
    helmet(C, -234.2, -48.6, zm, 40.0)
    papers(C, -233.8, -47.6, zm, 2, 32)
    puddle(C, xe - 0.6, ys + 0.5, zm, 0.45, 4, key="floor_ar_d")
    streak(C, (-230.95, ys, zu - 0.3), (0, 1, 0), 0.4, 1.6, 7)
    streak(C, (-234.5, ys, zu - 0.3), (0, 1, 0), 0.45, 1.1, 8)

    # ---- B1: 북벽 문 + 층 판, 분전반, 켜진 벽등 하나 · 꺼진 벽등 하나
    f, N = fire_door(C, (-233.85, yn, zt), (0, -1, 0))
    floor_plate(C, f, N, 0.85, "B1", "지하 1층", "BASEMENT 1")
    C.text("white", "B1", 0.5, f(0.0, 2.85), N, lift=0.018)
    elec_panel(C, (-231.75, yn, zt), (0, -1, 0), top=z1 - 0.3)
    C.ccol([(x, y, z) for (x, y) in ((-232.08, yn), (-231.42, yn), (-231.5, yn - 0.135), (-232.0, yn - 0.135))
            for z in (zt, zt + 1.5)])
    bulkhead(C, lw, (-231.15, yn, zt + 2.45), (0, -1, 0), top=z1 - 0.3)
    bulkhead(C, None, (xw, sy(-35.0), zt + 2.5), (1, 0, 0), top=z1 - 0.3)
    papers(C, -234.25, -35.0, zt, 2, 33)
    streak(C, (-234.6, yn, z1 - 0.3), (0, -1, 0), 0.4, 1.2, 9)

    # ---- 중간참 (B1M): 남벽 모노레일 승강장 안내(화살표 → 서쪽 줄), 높은 그릴과 물때, 켜진 벽등, 넘어진 탄약통
    platform_sign(C, (-233.55, ys, zu + 1.62), (0, 1, 0), 1)
    vent(C, (-231.5, ys, zu + 2.1), (0, 1, 0), 0.8, 0.45)
    streak(C, (-231.5, ys, zu + 1.86), (0, 1, 0), 0.75, 0.9, 10)
    puddle(C, -231.45, ys + 0.45, zu, 0.32, 5)
    bulkhead(C, lw, (-232.55, ys, zu + 2.55), (0, 1, 0), top=zs)
    ammo_can(C, xw + 0.25, ys + 0.12, zu)
    papers(C, -234.2, -48.9, zu, 2, 34)

    # ---- 1층: 동벽 지상 출입문(밖 문짝은 계단실 동쪽 바깥 벽) + 층 판 + 스텐실, 북벽 모노레일 승강장 안내(← 탑 출입구),
    # 켜진 벽등 둘
    f, N = fire_door(C, (ex, sy(-32.7), z1), (-1, 0, 0))
    floor_plate(C, f, N, 0.85, "1F", "지상 1층", "GROUND FLOOR")
    C.text("white", "1F", 0.5, f(2.15, 1.4), N, lift=0.018)
    platform_sign(C, (-231.75, yn, z1 + 1.62), (0, -1, 0), -1)
    bulkhead(C, lw, (ex, sy(-34.95), z1 + 2.45), (-1, 0, 0), top=zs)
    bulkhead(C, lw, (xw, sy(-32.9), z1 + 2.45), (1, 0, 0), top=zs)
    # 바깥: 계단실 동쪽 바깥 벽의 같은 문 (판석 없는 낮은 땅 -0.32 위 콘크리트 디딤, 맵 밖이라 COL 없음)
    xo = sx(67.0)
    C.box("concrete_d", xo, xo + 0.8, sy(-33.35), sy(-32.05), -0.32, 0.0, kind="detail")
    f, N = fire_door(C, (xo, sy(-32.7), 0.0), (1, 0, 0), staff=True, sign=False)
    sk.sign(C, f(0.0, 2.3), N, 0.9, 0.24, [("비상계단", 0.075, "white", 0.03, 0.0), ("EMERGENCY STAIRS", 0.036, "glow", -0.06, 0.0)],
            rim="gold", depth=0.03)
    lw.emit(C)
    lf.emit(C)


def stairwell():
    C.group("connector")
    ls = sk.LampSet("emerg_09", "r")
    zw, zm, zt, zu, z1 = sz(-0.75), sz(1.65), sz(4.05), sz(6.45), sz(8.85)   # B3, B2, B1, 중간참, 지상 1층 (z1 = 탑 바닥 0.02)
    zs = z1 + 3.0                                                             # 천장
    za_c = sz(4.75)                                                           # 창고 천장(지하)
    xw, xe, ys, yn = sx(61.5), sx(66.0), sy(-47.0), sy(-31.5)
    wt = 0.5
    lw = (xw, sx(63.5))
    le = (sx(64.0), xe)
    mk.paving(C, xw, xe, ys, yn, z=zw, key="concrete_d", grout="floor_ar_d", tile=1.5, t=0.3)
    sk.wall_y(C, "concrete", xw - wt, xw, ys - wt, yn + wt, zw - 0.3, zs + 0.3)
    # 북벽: 지상 1층 출입구 (계단탑 남벽 출입구와 같은 폭·높이)
    sk.wall_x(C, "concrete", xw - wt, xe, yn, yn + wt, zw - 0.3, zs + 0.3, openings=[(-234.65, -233.05, z1, z1 + 2.25)])
    sk.wall_x(C, "concrete", xw - wt, xe, ys - wt, ys, zw - 0.3, zs + 0.3)
    # 동벽 = 지하 병기창고 서벽(x 66..67). 지하를 뗐을 때를 위해 2 cm 앞에 얇은 벽(문 구멍은 지하 문보다 3 cm 넓게:
    # 가장자리 면이 지하 문틀 면과 같은 평면에 오지 않게), 창고 천장 위로는 예전처럼 두꺼운 벽
    sk.wall_y(C, "concrete", sx(65.98), xe, ys, yn, zw - 0.3, za_c,
              openings=[(sy(-34.43), sy(-32.37), zw - 0.3, sz(-0.75 + 2.33))])
    xe2 = xe - 0.015
    C.box("concrete", xe2, sx(67.0), ys - wt, yn + wt, za_c, zs + 0.3, col=True)
    # 창고 문: 지하가 붙어 있는 동안 열림(창고 벽 속으로 밀려 들어간다), 지하를 떼면 닫힘 (?step=TRACK처럼 선로만 읽었을 때도)
    dz0, dz1 = zw, sz(-0.75 + 2.29)
    sk.door(C, "armory_stair", (sx(66.32), sx(66.5), sy(-34.39), sy(-32.41), dz0, dz1), "0,0,-2.02", key="steel",
            parts=[("hazard", lambda b: mk._bm_box(b, sx(66.31), sx(66.33), sy(-34.2), sy(-32.6), dz0 + 0.12, dz0 + 0.3))])
    # 문틀 안쪽 판 (지하 문틀 면보다 1 cm 안): 지하를 떼면 문과 얇은 벽 사이 30 cm 틈이 비어 보인다
    for (a0, a1) in ((sy(-34.45), sy(-34.39)), (sy(-32.41), sy(-32.35))):
        C.box("concrete", sx(66.0), sx(66.32), a0, a1, zw, dz1 + 0.04, kind="detail")
    C.box("concrete", sx(66.0), sx(66.32), sy(-34.45), sy(-32.35), dz1, dz1 + 0.06, kind="detail")
    C.box("concrete_d", sx(66.0), sx(66.32), sy(-34.41), sy(-32.39), zw - 0.3, zw - 0.005, kind="detail")
    sk.ceil_box(C, "tunnel_d", xw, xe2, ys, yn, zs, zs + 0.3)
    # 지붕 덮개 (계단탑 남쪽에서 보이는 지상 부분의 윗면)
    C.box("concrete_d", xw - wt - 0.03, sx(67.0) + 0.03, ys - wt - 0.03, yn + wt, zs + 0.3, zs + 0.42, kind="detail")
    # 계단: 동쪽 줄은 남으로, 서쪽 줄은 북으로 오른다 (B3→B2, B2→B1, B1→중간참, 중간참→1층)
    sk.stair_flight(C, "y", le[0], le[1], sy(-35.5), -1, zw, zm, 16, tread=0.4, z_floor=zw)
    C.box("concrete_d", xw, xe, ys, sy(-41.5), zw, zm, col=True)
    sk.stair_flight(C, "y", lw[0], lw[1], sy(-41.5), 1, zm, zt, 16, tread=0.4, z_floor=zw)
    # 위 두 구간은 아래 구간 위에 얹는다: 채움 밑면을 아래 단보다 2.2 m 이상 높게 (머리 공간)
    sk.stair_flight(C, "y", le[0], le[1], sy(-35.5), -1, zt, zu, 16, tread=0.4, z_floor=zt)
    sk.stair_flight(C, "y", lw[0], lw[1], sy(-41.5), 1, zu, z1, 16, tread=0.4, z_floor=zu)
    C.box("concrete", sx(63.5), sx(64.0), sy(-41.5), sy(-35.5), zw, zs, col=True)
    # 참: 어두운 판 위에 밝은 윗면 2 cm (판이 참 높이까지 올라오면 윗면·앞면이 겹친다). COL은 참 높이까지
    for (y0_, y1_, z_) in ((sy(-35.5), yn, zt), (ys, sy(-41.5), zu), (sy(-35.5), yn, z1)):
        C.box("concrete_d", xw, xe, y0_, y1_, z_ - 0.3, z_ - 0.02)
        C.box("concrete", xw, xe, y0_, y1_, z_ - 0.02, z_, kind="detail")
        C.col(xw, xe, y0_, y1_, z_ - 0.3, z_)
    # 1층 참 남쪽 끝(동쪽 줄): 아래로 B1→중간참 구간이 뚫려 있다
    sk.railing(C, (le[0] + 0.05, sy(-35.45), z1), (le[1] - 0.05, sy(-35.45), z1), h=0.95)
    # 벽 손잡이 (경사) + COL (기운 막대, 벽에서 0.12 m): 계단 벽에 붙어 오를 때 몸이 손잡이에 묻혔다
    for (xw_, xi, ya_, za, yb_, zb_) in ((xe, xe - 0.12, sy(-35.3), zw, sy(-41.5), zm), (xw, xw + 0.12, sy(-41.5), zm, sy(-35.3), zt),
                                         (xe, xe - 0.12, sy(-35.3), zt, sy(-41.5), zu), (xw, xw + 0.12, sy(-41.5), zu, sy(-35.3), z1)):
        xc = xw_ - 0.08 if xw_ == xe else xw_ + 0.08
        C.cyl("hazard", (xc, ya_, za + 0.85), (xc, yb_, zb_ + 0.85), 0.03, segs=6, kind="detail")
        C.ccol([(xx, yy, zz + dz) for xx in (xw_, xi) for (yy, zz) in ((ya_, za + 0.85), (yb_, zb_ + 0.85)) for dz in (-0.05, 0.05)])
    # 층 표시
    for (p, n_, t) in (((xw + 0.01, sy(-33.5), zw + 1.6), (1, 0, 0), "B3 · 병기창고"),
                       ((xw + 0.01, sy(-44.2), zm + 1.6), (1, 0, 0), "B2"),
                       ((xe - 0.03, sy(-33.5), zt + 1.6), (-1, 0, 0), "B1"),
                       ((xw + 0.01, sy(-44.2), zu + 1.6), (1, 0, 0), "B1M")):
        sk.sign(C, p, n_, 1.6, 0.4, [(t, 0.16, "white", 0.0, 0.0)], depth=0.03, rim="violet")
    sk.sign(C, (-233.85, yn - 0.01, z1 + 2.65), (0, -1, 0), 2.4, 0.5,
            [("모노레일 선로 ↑", 0.15, "white", 0.07, 0.0), ("TRACK STAIRS 7", 0.08, "glow", -0.13, 0.0)], depth=0.03)
    for (p, n_) in (((xe - 0.02, sy(-33.0), zw + 2.2), (-1, 0, 0)), ((xw, sy(-44.2), zm + 2.4), (1, 0, 0)),
                    ((xe - 0.02, sy(-44.2), zm + 2.4), (-1, 0, 0)), ((xw, sy(-34.0), zt + 2.3), (1, 0, 0)),
                    ((xw, sy(-44.2), zu + 2.4), (1, 0, 0)), ((xe - 0.015, sy(-44.2), zu + 2.4), (-1, 0, 0)),
                    ((xe - 0.015, sy(-34.2), z1 + 2.3), (-1, 0, 0))):
        sk.emerg_lamp(C, ls, p, n_)
    dress_stairwell(ls)
    ls.emit(C)
    # 계단탑 출입구 위 표지 (탑 안쪽에서 보인다)
    C.text("white", "지하 연결 · 병기창고", 0.12, (-233.85, MT_Y0 + 0.17, 2.55), (0, 1, 0), lift=0.01)


stairwell()
C.group("track")


def carve(box, keep=("connector",)):
    """다른 묶음의 면·COL에서 상자 안을 비운다 (계단실 자리: 도심 큰 바닥판·판석이 계단실을 가로지르지 않게).
    상자 면으로 자른 뒤 가운데가 상자 안인 면을 지운다. 자른 끝은 계단실 벽 두께 안에 숨는다."""
    import bmesh
    x0, x1, y0, y1, z0, z1 = box

    def touches(f):
        xs = [v.co.x for v in f.verts]
        ys = [v.co.y for v in f.verts]
        zs = [v.co.z for v in f.verts]
        return max(xs) > x0 and min(xs) < x1 and max(ys) > y0 and min(ys) < y1 and max(zs) > z0 and min(zs) < z1

    gone = 0
    for (g, key, kind), b in C.acc.items():
        if g in keep:
            continue
        for co, no in (((x0, 0, 0), (1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, 1, 0)), ((0, y1, 0), (0, 1, 0)),
                       ((0, 0, z0), (0, 0, 1)), ((0, 0, z1), (0, 0, 1))):
            fs = [f for f in b.faces if touches(f)]
            if not fs:
                break
            geom = list({v for f in fs for v in f.verts}) + list({e for f in fs for e in f.edges}) + fs
            bmesh.ops.bisect_plane(b, geom=geom, plane_co=co, plane_no=no)
        dead = []
        for f in b.faces:
            c = f.calc_center_median()
            if x0 < c.x < x1 and y0 < c.y < y1 and z0 < c.z < z1:
                dead.append(f)
        if dead:
            bmesh.ops.delete(b, geom=dead, context="FACES")
            gone += len(dead)
    out, split = [], 0
    for c in C.cols:
        nm, a0, a1, b0, b1, c0, c1 = c
        if a1 <= x0 or a0 >= x1 or b1 <= y0 or b0 >= y1 or c1 <= z0 or c0 >= z1 or nm.startswith("COL_connector"):
            out.append(c)
            continue
        split += 1
        xa, xb, ya, yb = max(a0, x0), min(a1, x1), max(b0, y0), min(b1, y1)
        pieces = [(a0, x0, b0, b1, c0, c1), (x1, a1, b0, b1, c0, c1), (xa, xb, b0, y0, c0, c1), (xa, xb, y1, b1, c0, c1),
                  (xa, xb, ya, yb, c0, z0), (xa, xb, ya, yb, z1, c1)]
        for k, (p0, p1, q0, q1, r0, r1) in enumerate(pieces):
            if p1 - p0 > 1e-3 and q1 - q0 > 1e-3 and r1 - r0 > 1e-3:
                out.append((f"{nm}_c{k}", p0, p1, q0, q1, r0, r1))
    C.cols[:] = out
    print(f"[m2] carve {box}: faces {gone}, cols split {split}")


# 선로 위 엄폐물과 보급 (COVER_track_..)
COVERS_T = []


def tcover(x, y, h, face_x=None):
    COVERS_T.append(((x, y, TOP), h, (face_x if face_x is not None else x + 10, y)))


dk.supply_stack(C, -224.0, AV + 1.05, TOP, 0, n=3, seed=1)
tcover(-225.2, AV + 1.0, "high")
dk.cable_drum(C, -212.0, AV - 1.05, TOP, 0)
tcover(-213.0, AV - 1.0, "low")
dk.maint_cart(C, -198.0)
tcover(-199.7, AV + 0.3, "high")
dk.spilled_sandbags(C, -184.0, AV + 0.7, z=TOP, n=6, r=0.7, seed=4)
tcover(-185.2, AV + 0.6, "low")
dk.crashed_drone(C, -167.0, AV + 0.95, z=TOP, s=0.7, seed=12)
tcover(-168.4, AV + 0.9, "low")
AMMO_T = dk.ammo_crate(C, -158.0, AV - 1.05, TOP, 0, text="진압반 보급 · AMMO")
dk.supply_stack(C, -160.2, AV - 1.05, TOP, 0, n=2, seed=5)
tcover(-161.6, AV - 1.0, "low")
dk.supply_stack(C, -121.0, AV + 1.05, TOP, 0, n=3, seed=6)
tcover(-122.2, AV + 1.0, "high")
dk.cable_drum(C, -108.0, AV - 1.05, TOP, 0)
tcover(-109.0, AV - 1.0, "low")
dk.r41_barrier(C, -95.0, AV, yaw=90, z=TOP)
tcover(-96.0, AV + 0.0, "low")
dk.supply_stack(C, -79.0, AV - 1.05, TOP, 0, n=2, seed=8)
tcover(-80.4, AV - 1.0, "low")
dk.cable_drum(C, -64.0, AV + 1.05, TOP, 0)
# 윗줄 주머니 COL이 남쪽 난간 띠에서 0.6 m 넘게 떨어지게 (예전 AV - 0.6: 0.47 m 틈에 주머니 위에서 내려서다 발이 뜬 채
# 박혔다, scripts/wedgecheck.mjs m2_track)
dk.spilled_sandbags(C, -52.0, AV - 0.4, z=TOP, n=6, r=0.7, seed=9)
tcover(-53.2, AV - 0.4, "low")
dk.supply_stack(C, -41.0, AV + 1.05, TOP, 0, n=3, seed=10)
tcover(-42.2, AV + 1.0, "high")

# ================================================================== 멈춘 열차
C.group("train")
TR = dk.walk_train(C, -140.0, broken={(0, 1, 1), (0, -1, 3), (1, 1, 2), (1, -1, 0), (1, -1, 1)}, seed=7)
ZF = TR["floor"]
# 차체 옆과 난간 띠 사이 0.32 m 틈(못 지나가게 둔 틈)을 COL로 채운다: 끝 기둥(0.35 m 튀어나옴)과 난간 띠 사이 구석에 뛰어들면
# 캡슐이 기둥 모서리와 띠 사이에 박혔다 (wedgecheck m2_track). 차체 양 끝 기둥 바깥면까지, 난간 띠 윗면(1.1 m) 높이로
for s_ in (-1, 1):
    C.col(TR["cars"][0][0] - 0.35, TR["cars"][-1][1] + 0.35, *sorted((AV + s_ * 1.3, AV + s_ * (dk.EDGE - 0.08))),
          TOP, TOP + dk.RAIL_SAFE[1], props=dk.NO_CLIMB)
for k, (x, s) in enumerate(((-146.0, 1), (-136.5, -1), (-133.0, 1))):
    C.decal("soot", [(math.cos(a) * 0.7, math.sin(a) * 0.3) for a in [i * 0.785 for i in range(8)]],
            (x, AV + s * 1.3, ZF + 0.42), (0, s, 0), lift=0.03)

# ================================================================== 중앙역 + 계단탑 (광장으로)
C.group("station")
ST_A0, ST_A1 = -33.0, -5.0
SS_X0, SS_Y0, SS_Y1 = -29.4, -15.9, -11.5
ST = dk.central_station(C, ST_A0, ST_A1, north_open=(SS_X0 + 0.1, SS_X0 + 2.45), low=True)
SS = dk.stair_tower(C, SS_X0, SS_Y0, SS_Y1, ST["top"], z0=0.0, top_lane=-1, top_end=-1, style="glass",
                    top_open=("-y", SS_X0 + 0.1, SS_X0 + 2.45), bottom_open=("+y", SS_X0 + 0.1, SS_X0 + 2.45))
for sgn in (1, -1):
    c = (SS_X0 + 1.2, SS_Y1 + 0.16 if sgn > 0 else SS_Y0 - 0.02, 2.75 if sgn > 0 else ST["top"] + 2.75)
    N = (0, 1, 0) if sgn > 0 else (0, -1, 0)
    C.plate("navy", [(-1.0, -0.22), (1.0, -0.22), (1.0, 0.22), (-1.0, 0.22)], c, N, 0.04, kind="detail")
    C.text("white", "시청 앞 광장 출구" if sgn < 0 else "모노레일 중앙역", 0.15, (c[0], c[1] + 0.05 * sgn, c[2] + 0.05),
           N, lift=0.004)
    C.text("glow", "EXIT · CITY HALL" if sgn < 0 else "MONORAIL · CENTRAL", 0.08,
           (c[0], c[1] + 0.05 * sgn, c[2] - 0.13), N, lift=0.004)

# ================================================================== 중앙로 서쪽 블록 (양쪽 상가·사무실, 북쪽은 궤도 높이 옥상)
C.group("blocks")
rng = random.Random(202)
N_STYLES = ["brick", "office", "apartment", "brick", "office"]
SHOPS = [("모나티엄 25", "MONATIUM 25 · 서부점", "mint"), ("커틀릿 하우스", "공기커틀릿 아님", "coral"),
         ("엘프 약국", "PHARMACY", "teal"), ("세탁소 뽀송", "LAUNDRY", "mint"), ("분식 귀쟁이", "SNACK", "coral"),
         ("모나티엄 철물", "HARDWARE", "teal")]
NORTH, SOUTH = [], []
x, i = -250.0, 0
while x < -70.0:
    w = [15, 13, 17, 14, 16, 12][i % 6]
    if x + w > -66.0:
        w = -66.0 - x
    if w < 7:
        break
    cxb = x + w / 2
    roof = -214.0 < cxb < -92.0
    floors = 2 if roof else [4, 5, 3, 6][i % 4]
    shop = None if roof or i % 3 else SHOPS[i % len(SHOPS)]
    sh = dict(zip(("name", "sub", "awning"), shop)) if shop else None
    b = dk.street_block(C, x, x + w, -11.0, 1.0, floors=floors, style=N_STYLES[i % 5], front="-y", shop=sh,
                        seed=300 + i, roof_units=0 if roof else 1)
    NORTH.append((x, x + w, b["top"], roof))
    x += w + (1.6 if i % 3 == 2 else 0.4)
    i += 1
x, i = -250.0, 0
while x < -84.0:
    w = [14, 16, 13, 17, 15][i % 5]
    if -236.5 < x + w and x < -223.5:          # 정비 계단탑 자리
        x = -223.5
        continue
    if x + w > -80.6:
        w = -80.6 - x
    if w < 7:
        break
    shop = SHOPS[(i + 2) % len(SHOPS)] if i % 3 == 0 else None
    sh = dict(zip(("name", "sub", "awning"), shop)) if shop else None
    b = dk.street_block(C, x, x + w, -43.6, -30.6, floors=[5, 4, 6, 3, 7][i % 5], style=N_STYLES[(i + 2) % 5],
                        front="+y", shop=sh, seed=400 + i)
    SOUTH.append((x, x + w, b["top"]))
    x += w + (1.8 if i % 3 == 1 else 0.4)
    i += 1

# 맵 경계: 중앙로 연장은 양쪽 보도 바깥 끝(블록 앞면 줄)으로 닫는다 (블록 사이 골목·원경 블록 틈으로 나가면 판석 없는
# 낮은 땅에서 다시 오르지 못하고 맵 끝 x -360에서 떨어진다). 정비 계단탑 자리는 탑 벽이 막는다.
dk.bounds(C, [(-340.3, -95.5, -11.0, -10.7),                              # 북쪽 보도 끝
              (-340.3, MT_X0 + 0.05, -30.9, -30.6), (MT["x1"] - 0.05, -97.5, -30.9, -30.6),   # 남쪽 보도 끝
              (-340.3, -340.0, -31.0, -10.7),                             # 서쪽 도로 끝
              (-96.3, -96.0, 0.0, 60.3), (-96.3, -96.0, -60.3, -43.0)])   # 도심 서쪽 (블록 뒤)

# ================================================================== 원경 (뒷줄 블록, 고층 고리, 바닥판, 지평선 연기)
C.group("far")
x = -252.0
k = 0
while x < -70:
    w = rng.uniform(16, 24)
    dk.far_block(C, x, x + w, 8.0, 22.0, rng.uniform(18, 32), key=("far", "concrete_d")[k % 2], sides="-y")
    if x < -82:
        dk.far_block(C, x, x + w, -64.0, -50.0, rng.uniform(16, 30), key=("concrete_d", "far")[k % 2], sides="+y")
    x += w + rng.uniform(2, 5)
    k += 1
for (bx0, bx1) in ((-336, -316), (-310, -290), (-284, -262)):
    for (by0, by1) in ((-11.0, 2.0), (-43.6, -30.6)):
        dk.far_block(C, bx0, bx1, by0, by1, rng.uniform(12, 24), key="concrete_d", sides="-y" if by0 > AV else "+y")
dk.far_ring(C, -70.0, -10.0, radius=300.0, n=30, seed=77, rx=1.25,
            skip=lambda sx, sy: abs(sy - AV) < 22 or (sx > 60 and abs(sy - AV) < 30))
C.box("pave_d", -360, 160, -150, 120, -0.6, -0.32, kind="fine")
C.col(-360, 160, -150, 120, -0.9, -0.32)
dk.horizon_smoke(C, [(-280, 150, 120, 10, 0.5), (-400, -140, 100, 11, 0.6), (190, 170, 130, 12, 0.45),
                     (140, -210, 95, 9, 0.6), (-120, 240, 115, 10, 0.5), (320, -30, 110, 10, 0.55)],
                 drift=WIND, seed=40)

# ================================================================== 중앙로 전쟁 피해 (광장은 아직 멀쩡)
C.group("war")
for j, (x, y, yaw) in enumerate(((-189.0, -24.6, 80), (-117.0, -16.8, 100), (-73.0, -25.3, 70), (33.0, -24.8, 95))):
    dk.burning_wreck(C, x, y, yaw, seed=60 + j, drift=WIND)
    dk.scorch_mark(C, x + 1.5, y + 0.8, 2.6, z=-0.15, seed=70 + j)
    M(f"FX_smoke_{j + 1:02d}", (x, y, 1.2), props={"dir": "0,1,0", "strength": 0.8})
for j, (x, y, yaw, col) in enumerate(((-205.0, -16.6, 95, "car_y"), (-160.0, -24.9, 84, "car_b"),
                                      (-142.5, -16.2, 263, "car_w"), (-96.0, -17.1, 101, "car_r"),
                                      (-58.0, -24.6, 75, "car_w"), (-226.0, -24.6, 92, "car_b"))):
    dk.car(C, x, y, yaw, color=col, seed=80 + j)
for j, (x, y, yaw) in enumerate(((-176.0, -26.4, 8), (-130.0, -15.4, 172), (-102.0, -25.6, -6), (-214.0, -15.8, 185))):
    dk.r41_barrier(C, x, y, yaw)
for j, (x, y, r) in enumerate(((-150.0, -20.0, 3.0), (-200.0, -23.0, 2.2), (-86.0, -19.0, 2.4))):
    dk.scorch_mark(C, x, y, r, z=-0.15, seed=90 + j)

# ================================================================== 시청 방어선 (광장 남쪽 반)
C.group("line")
ARC_C, ARC_R = (0.0, 18.0), 26.0
PLAN = ["S", "B", "s", "S", "B", "b", "S", "b", "B", "S", "s", "B", "S"]
ARC = dk.defense_arc(C, ARC_C, ARC_R, PLAN, start=-42.0, step=7.0)
# 목격 엄폐: 방호벽 두 개 (엎드리면 숨고 서면 너머로 포르티코가 보인다)
WIT = (-5.5, -4.0)
dk.jersey_barrier(C, WIT[0] - 1.02, WIT[1], 0.0, 0)
dk.jersey_barrier(C, WIT[0] + 1.02, WIT[1], 0.0, 0)
# 방어선 뒤 보급: 탄약 상자, M72 상자, 들것, 상자 더미
AMMO_L = dk.ammo_crate(C, 3.6, -4.4, 0.0, 0, key="violet", text="진압반 · 탄약")
M72_L = dk.weapon_crate(C, -0.8, -4.5, 0.0, 0, text="U.S. ARMY · M72 LAW")
dk.ammo_crate(C, 4.5, -3.6, 0.0, 15)
dk.supply_stack(C, 12.0, -2.4, 0.0, 30, n=3, seed=21)
dk.supply_stack(C, -13.0, -1.6, 0.0, -30, n=2, seed=22)
dk.stretcher(C, -16.5, 4.5, yaw=10)
dk.stretcher(C, -15.4, 4.4, yaw=-5)
# 서쪽 정비 구역 (옛 훈련장 자리): 천막, 상자
mk.tent(C, -38.0, 4.0, yaw=90, w=3.0, d=3.6)
mk.tent(C, -38.0, -3.0, yaw=90, w=3.0, d=3.6, key="tarp")
for j, (x, y) in enumerate(((-31.0, 6.5), (-31.5, 2.0), (-42.5, 9.0), (-44.0, -6.0))):
    dk.supply_stack(C, x, y, 0.0, 90 * (j % 2), n=3, seed=30 + j)
dk.sandbags(C, -30.5, -6.5, yaw=90, n=4, rows=3)

# 칸나 현장 지휘소 (포르티코 위 서쪽 기둥 사이 안쪽)
CP = dk.command_post(C, -6.0, 16.6, z=PZ, yaw=0.0)

# 시청 정문 (흑뉴아가 들어간다) + 안쪽 복도
# M2에서는 대피소를 아직 열지 않았다 (M3에서 엘레나가 연다): 정문만 열고 대피소 표지는 두지 않는다
DOOR = dk.cityhall_doorway(C, lit=True, shelter=False)

# 경보등 (미션이 켬, on=0)
C.group("ALERTS")
n = 0
for (x, y) in ((-6.5, -9.5), (6.5, -9.5), (-22.5, 14.5), (22.5, 14.5), (-22.8, -10.2), (22.8, -10.2)):
    n += 1
    mk.alert_beacon(C, f"alert_{n:02d}", (x, y, 4.75 if abs(x) < 10 else 4.45), blink=0.6 + 0.07 * n)
    M(f"FX_siren_{n:02d}", (x, y, 4.2), props={"sound": "siren", "group": "alert"})
for (x, y, z) in ((-15.0, 19.6, 12.4), (15.0, 19.6, 12.4), (0.0, 13.6, 9.6)):
    n += 1
    mk.alert_beacon(C, f"alert_{n:02d}", (x, y, z), blink=0.55 + 0.05 * n, siren=False)

# ================================================================== 마커
C.group("markers")
YC = AV
# 시작: 정비 계단 위 (궤도 위, 동쪽을 본다)
M("SPAWN_player", (-231.3, YC - 0.9, TOP), face=(-200.0, YC - 0.9))
M("SPAWN_train", (-153.5, YC, TOP), face=(-140.0, YC))
# 계단실에서 걸어 올라온 플레이어가 선로에 닿는 자리 (다리 북쪽 절반 + 점검 통로 이음): m2.ts TO_TRACK → TRACK
sk.trig(C, "track_in", BR_X0 - 0.4, BR_X1 + 0.4, -27.0, YC + 0.6, TOP - 0.5, TOP + 3.0)
M("SPAWN_station", (-25.0, YC + 3.0, ST["top"]), face=(-10.0, YC + 3.0))
M("SPAWN_plaza", (-3.0, -3.0, 0.0), face=(0.0, -20.0))
M("SPAWN_witness", (WIT[0], WIT[1] - 0.8, 0.0), face=(-3.0, 16.0))
for who, (x, y) in (("sabre", (-229.6, YC + 0.1)), ("rona", (-230.0, YC + 1.1)), ("jesty", (-233.7, YC - 3.6)),
                    ("karen", (-232.6, YC - 1.2))):
    M(f"ALLY_{who}", (x, y, TOP), face=(-200.0, y),
      props={"who": who, "behavior": "follow", "model": SQ[who], "weapon": SQ_W[who]})

M("MARK_track_end", (CAT_X1 - 0.6, YC, TOP))
M("MARK_train", (TR["west_door"][0] - 0.6, YC, TOP + 0.1))
M("MARK_station", (-19.0, YC + 3.2, ST["top"]))
M("MARK_plaza_stairs", (SS_X0 + 1.2, SS_Y0 + 1.0, ST["top"]))
M("MARK_kanna_cp", (CP["stand"].x, CP["stand"].y, PZ), face=(CP["stand"].x, 0.0))
M("MARK_line", (0.0, -6.8, 0.0), face=(0.0, -20.0))
M("MARK_witness", (WIT[0], WIT[1] - 0.8, 0.0), face=(-3.0, 16.0))
NYUA = (-2.9, 16.0, PZ)
M("MARK_nyua_land", NYUA, face=(-2.9, 0.0))
M("MARK_cityhall_door", (DOOR["door"][0], DOOR["door"][1] - 0.1, PZ), face=(0.0, 0.0))

# 분대 대기 자리
for sec, center, spots, face in (
        ("track", (-201.5, YC), {"sabre": (-200.2, YC + 1.1), "rona": (-200.6, YC - 1.1), "jesty": (-203.2, YC + 0.3),
                                 "karen": (-204.2, YC - 1.0)}, (-150.0, YC)),
        ("train", (-155.5, YC), {"sabre": (-154.6, YC + 1.1), "rona": (-155.0, YC - 1.1), "jesty": (-156.8, YC + 0.3),
                                 "karen": (-157.8, YC - 1.0)}, (-140.0, YC)),
):
    for who, p in dk.hold_marks(C, sec, center, spots, z=TOP, face=face).items():
        NODES.append((f"MARK_hold_{sec}_{who}", p, {}))
    NODES.append((f"MARK_hold_{sec}", (*center, TOP), {}))
for sec, center, spots, z, face in (
        ("station", (-20.0, YC + 3.0), {"sabre": (-22.0, YC + 2.4), "rona": (-18.0, YC + 2.4),
                                         "jesty": (-21.0, YC + 3.9), "karen": (-17.4, YC + 3.6)}, ST["top"],
         (-20.0, -11.0)),
        ("line", (0.0, -5.4), {"sabre": (-3.2, -6.0), "rona": (3.2, -6.0), "jesty": (-10.8, -4.4),
                               "karen": (10.8, -4.4)}, 0.0, (0.0, -30.0)),
        ("witness", (WIT[0], WIT[1] - 1.0), {"sabre": (WIT[0] - 2.4, WIT[1] - 0.9), "rona": (WIT[0] + 2.2, WIT[1] - 0.9),
                                             "jesty": (WIT[0] - 1.2, WIT[1] - 1.6), "karen": (WIT[0] + 1.0, WIT[1] - 1.7)},
         0.0, (-3.0, 16.0)),
):
    for who, p in dk.hold_marks(C, sec, center, spots, z=z, face=face).items():
        NODES.append((f"MARK_hold_{sec}_{who}", p, {}))
    NODES.append((f"MARK_hold_{sec}", (*center, z), {}))

# 건설 자리 (빈 자리, -Y = 적 쪽)
nb = 0
for e in ARC:
    if e["kind"] in ("s", "b"):
        nb += 1
        p = e["pos"]
        M(f"MARK_build_{nb}", (p.x, p.y, 0.0), yaw=e["yaw"],
          props={"prop": "sandbags" if e["kind"] == "s" else "barricade"})
# 방어선 엄폐점 (기존 바리케이드·모래주머니 안쪽, 정면 = 바깥) + 목격 엄폐 + 화단 두 곳
nc = 0
for e in ARC:
    if e["kind"] in ("S", "B"):
        nc += 1
        p = e["pos"] - e["normal"] * 0.75
        M(f"COVER_line_{nc:02d}", (p.x, p.y, 0.0), yaw=e["yaw"], props={"height": "low"})
for (x, y, face, h) in ((WIT[0], WIT[1] - 0.75, (-3.0, 16.0), "low"), (-9.5, -3.25, (-9.5, -20.0), "low"),
                        (9.5, -3.25, (9.5, -20.0), "low")):
    nc += 1
    M(f"COVER_line_{nc:02d}", (x, y, 0.0), face=face, props={"height": h})
for j, (p, h, face) in enumerate(COVERS_T, start=1):
    M(f"COVER_track_{j:02d}", p, face=face, props={"height": h})

# 트리거
TRIGS = [
    ("train", (TR["west_door"][0] + 0.1, TR["west_door"][0] + 2.8, YC - 1.2, YC + 1.2, TOP - 0.4, TOP + 2.6)),
    ("train_out", (TR["east_door"][0] + 0.3, TR["east_door"][0] + 3.6, YC - dk.EDGE, YC + dk.EDGE, TOP - 0.5,
                   TOP + 2.6)),
    ("station", (ST_A0, ST_A1, YC - ST["edge"], YC + ST["edge"], TOP - 0.5, TOP + 3.0)),
    ("plaza", (SS_X0 - 0.6, SS_X0 + 3.0, SS_Y1 - 0.1, SS_Y1 + 2.4, -0.5, 3.0)),
    ("line", (-20.0, 20.0, -10.0, 0.0, -0.5, 3.0)),
]
for tid, box in TRIGS:
    dk.trig(C, tid, *box)
    NODES.append((f"TRIG_{tid}", tuple(round(v, 2) for v in box), {}))

# 아군: 칸나 + 진압반 6
M("ALLY_kanna", (CP["stand"].x, CP["stand"].y, PZ), face=(CP["stand"].x, 0.0),
  props={"who": "kanna", "behavior": "hold", "model": "characters/kanna.glb", "weapon": "monatium_riot_carbine"})
for j, idx in enumerate((1, 3, 4, 8, 9, 11), start=1):
    e = ARC[idx]
    p = e["pos"] - e["normal"] * 0.8 + mk.Vector((-e["normal"].y, e["normal"].x, 0)) * 0.5
    M(f"ALLY_riot_{j:02d}", (p.x, p.y, 0.0), yaw=e["yaw"],
      props={"who": "riot", "behavior": "hold", "model": RIOT, "weapon": "monatium_riot_carbine"})

# 흑뉴아 (숨김) + 강하·퇴장 경로
M("NPC_black_renewa", NYUA, face=(NYUA[0], 0.0),
  props={"model": "characters/black_renewa.glb", "name": "흑뉴아", "pose": "idle", "hidden": 1, "look": "none"})
for name, pts in (("nyua_in", [(-1.0, -24.0, 26.0), (-2.0, -4.0, 14.0), (-2.6, 8.5, 5.2), (-2.8, 13.0, 1.6), NYUA]),
                  ("nyua_exit", [NYUA, (-0.8, 18.0, PZ), (0.0, 19.6, PZ), (0.0, 22.5, PZ)])):
    for j, p in enumerate(pts, start=1):
        M(f"WP_{name}_{j:02d}", p)

# 집기
M("PICKUP_ammo_track", (-158.0, AV - 1.05, AMMO_T + 0.04), yaw=90, props={"weapon": "ammo"})
M("PICKUP_ammo_line", (3.6, -4.4, AMMO_L + 0.04), yaw=90, props={"weapon": "ammo"})
M("PICKUP_m72_line", (-0.8, -4.55, M72_L + 0.04), yaw=90, props={"weapon": "m72", "lay": "side"})

# ---------------------------------------------------------------- 적 (전부 spawn=manual)


def E(eid, loc, kind, group, behavior, face=None, yaw=None, path=None):
    dk.enemy(C, eid, loc, kind, group, behavior, face=face, yaw=yaw, path=path)
    NODES.append((f"ENEMY_{eid}", tuple(round(v, 2) for v in loc), {"kind": kind, "group": group}))


RIF = ("rifleman_a", "rifleman_b", "rifleman_c")
# 선로 아래 큰길 6
for j, (x, y) in enumerate(((-211.0, -25.4), (-195.5, -16.0), (-180.0, -25.8), (-149.0, -16.5), (-111.0, -25.1),
                            (-89.0, -16.8)), start=1):
    E(f"rail_street_{j:02d}", (x, y, -0.15), RIF[j % 3], "rail_street", "hold" if j % 2 else "advance", face=(x + 6, AV))
# 북쪽 옥상 4 (궤도 높이 지붕)
roofs = [b for b in NORTH if b[3]]
want = (-192.0, -170.0, -118.0, -102.0)
for j, wx in enumerate(want, start=1):
    b = min(roofs, key=lambda r: abs((r[0] + r[1]) / 2 - wx))
    x = min(max(wx, b[0] + 1.5), b[1] - 1.5)
    E(f"rail_roof_{j:02d}", (x, -9.8, b[2]), RIF[(j + 1) % 3], "rail_roof", "hold", face=(x + 3, AV))
    # 연출된 도착 (docs/COMBAT.md 17.2): 뒷벽(+y, 선로에서 안 보임) 사다리로 옥상에 기어오른다. 옥상은 섬이라 내비로 이어진
    # 가려진 자리가 없고 앞 파라펫(0.7 m)은 선 몸을 못 가린다. 마커는 뒤 가장자리 0.3 m 안쪽 옥상 바닥 (ENTRY_ arrive=ladder)
    sk.ladder(C, x, 1.0, -0.15, b[2] + 0.9, normal=(0, 1, 0))
    M(f"ENTRY_rail_roof_up_{j:02d}", (x, 0.7, b[2]), face=(x, -9.8), props={"group": "rail_roof", "arrive": "ladder"})
# 드론 3 + 순찰 경로
for j, (x, y, z) in enumerate(((-196.0, -13.5, 12.0), (-160.0, -28.0, 13.0), (-118.0, -13.5, 14.0)), start=1):
    E(f"rail_drone_{j:02d}", (x, y, z), "drone", "rail_drone", "patrol", face=(x + 10, y), path="rail_drone")
for j, p in enumerate(((-215.0, -13.0, 12.0), (-150.0, -13.0, 13.0), (-80.0, -13.0, 13.5), (-55.0, -28.5, 12.0),
                       (-130.0, -28.5, 13.0), (-205.0, -28.5, 12.5)), start=1):
    M(f"WP_rail_drone_{j:02d}", p)
# 멈춘 열차 위·안 (소총 4 + 돌격 1)
E("rail_train_01", (-133.0, AV + 0.4, ZF), "rifleman_a", "rail_train", "hold", face=(-150.0, AV))
E("rail_train_02", (-136.9, AV - 0.4, ZF), "rifleman_b", "rail_train", "hold", face=(-150.0, AV))
E("rail_train_03", (-133.6, AV, TR["roof"]), "rifleman_c", "rail_train", "hold", face=(-160.0, AV))
E("rail_train_04", (-127.2, AV + 1.0, TOP), "rifleman_a", "rail_train", "advance", face=(-150.0, AV + 1.0))
E("rail_train_05", (-141.6, AV, ZF), "assault", "rail_train", "rush", face=(-150.0, AV))
# 큰길의 R41 기동차
M("VEH_rail_raider", (-62.0, -24.6, -0.15), face=(-90.0, -24.6),
  props={"vehicle": "r41_raider", "faction": "enemy", "state": "ready", "driver": "ai", "path": "rail_raider",
         "group": "rail_raider", "spawn": "manual"})
for j, p in enumerate(((-62.0, -24.6), (-110.0, -24.6), (-160.0, -24.2), (-206.0, -17.2), (-226.0, -17.2),
                       (-165.0, -17.2), (-100.0, -17.4)), start=1):
    M(f"WP_rail_raider_{j:02d}", (p[0], p[1], -0.15))

# 방어전: 1파 (큰길 남쪽에서 8), 2파 (동쪽 옆길 6 + 진압 방패 3), 드론 3, 장갑차, 3파 10
for j, (x, y) in enumerate(((-20.0, -29.4), (-12.0, -28.8), (-4.0, -29.7), (4.0, -29.0), (12.0, -29.5),
                            (20.0, -28.9), (-8.0, -25.3), (8.0, -25.0)), start=1):
    E(f"def_w1_{j:02d}", (x, y, 0.0 if y < -27.4 else -0.15), RIF[j % 3], "def_w1", "advance", face=(x * 0.7, 0.0))
for j, (x, y) in enumerate(((44.0, 6.0), (46.0, 10.5), (44.5, 15.0), (46.5, 20.0), (44.0, 25.0), (46.0, 30.0)),
                           start=1):
    E(f"def_w2_{j:02d}", (x, y, 0.0), RIF[j % 3], "def_w2", "flank" if j % 3 == 0 else "advance", face=(30.0, -12.0))
for j, (x, y) in enumerate(((45.0, -0.5), (43.8, 1.8), (46.3, 2.4)), start=1):
    E(f"def_w2_riot_{j:02d}", (x, y, 0.0), "riot", "def_w2", "advance", face=(30.0, -12.0))
for j, (x, y, z) in enumerate(((-10.0, -24.0, 13.0), (6.0, -30.0, 14.0), (22.0, -22.0, 12.0)), start=1):
    E(f"def_drone_{j:02d}", (x, y, z), "drone", "def_drone", "patrol", face=(x, 0.0), path="def_drone")
for j, p in enumerate(((-18.0, -24.0, 13.0), (18.0, -26.0, 13.5), (22.0, -6.0, 12.5), (-20.0, -6.0, 12.5)), start=1):
    M(f"WP_def_drone_{j:02d}", p)
M("VEH_def_apc", (62.0, -24.6, -0.15), face=(30.0, -24.6),
  props={"vehicle": "r41_apc", "faction": "enemy", "state": "ready", "driver": "ai", "path": "def_apc",
         "group": "def_apc", "spawn": "manual"})
for j, p in enumerate(((62.0, -24.6), (40.0, -24.6), (16.0, -23.8)), start=1):
    M(f"WP_def_apc_{j:02d}", (p[0], p[1], -0.15))
W3 = [((-34.0, -28.0), "rifleman_a", "advance"), ((-28.0, -24.8), "assault", "rush"),
      ((-40.0, -17.0), "rifleman_b", "flank"), ((-2.0, -30.0), "riot", "advance"), ((6.0, -30.4), "officer", "hold"),
      ((14.0, -25.4), "assault", "rush"), ((45.0, 6.0), "rifleman_c", "advance"), ((46.0, 12.0), "riot", "advance"),
      ((44.5, 18.0), "rifleman_a", "flank"), ((34.0, -28.4), "rifleman_b", "advance")]
for j, ((x, y), kind, beh) in enumerate(W3, start=1):
    z = 0.0 if (y > -14.2 or y < -27.4) else -0.15
    E(f"def_w3_{j:02d}", (x, y, z), kind, "def_w3", beh, face=(0.0, -6.0))

# ================================================================== 보고 + 내보내기
for nm, p, pr in NODES:
    extra = " ".join(f"{k}={v}" for k, v in pr.items() if k in ("kind", "group", "prop", "weapon", "height", "who"))
    print(f"[m2] {nm:28s} {p} {extra}")
print(f"[m2] north roofs (track height): {[(round(a), round(b), round(t, 2)) for a, b, t, r in NORTH if r]}")
ROOT = {
    "sky": "#adc4d6",            # 연기 낀 오전 하늘
    "fog": "80,470",
    "sun": "0.55,0.72,0.42",     # 동남동, 고도 약 45° (10시)
    "sunColor": "#fff1da",
    "sunIntensity": 2.0,
    "ambient": 1.15,
    "hemiSky": "#d3e2ef",
    "hemiGround": "#7a7068",
    "near": 0.1,
    "far": 900,
    "music": "m2_combat",
    "timeOfDay": "morning_war",
}
carve((sx(61.25), sx(66.75), sy(-47.25), sy(-31.25), sz(-1.4), sz(8.85) + 3.29))
C.finish("levels/m2_monorail.glb", root_props=ROOT, outline=0.025)
