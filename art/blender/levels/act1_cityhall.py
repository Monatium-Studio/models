"""1막 시청 방어선 시네마틱 세트: 해 질 녘 D-day의 시청 앞 광장 (로딩 영상 3 「종군기자 하이디」, 1막 종료 「정전」).

npm run model -- art/blender/levels/act1_cityhall.py   → public/models/levels/act1_cityhall.glb
npm run shot -- levels/act1_cityhall.glb --views top,34

보는 세트다(루트 physics=0). 배치는 도시 키트 downtown(variant="dusk")을 그대로 쓰고(인터루드 6·7, 1막 M1·M2와 같은 장소),
그 위에 전쟁 피해(그을음, 잔해, 부서진 민간 차량, 연기 기둥)와 시청 계단 앞 방어선(바리케이드·모래주머니 호)을 얹었다.
인물·차량·드론은 마커뿐이다. 1막 연출 코드가 띄우고 움직인다.
  NPC_riot_*   진압반원 (쓰러지는 중, 쓰러짐, 엄폐)           scene heidi,blackout
  NPC_rita, NPC_sabre/rona/jesty/karen  분대 (리타 눈 = 1인칭)  scene blackout
  NPC_r41_*    중앙로에서 밀고 들어오는 R41 보병              scene heidi,blackout
  PROP_veh_1..3 + WP_veh_<n>_nn    R41 차량 돌입 경로 (마지막 점 = 멈춰 서는 자리, veh_1은 방어선을 들이받는다)
  PROP_drone_1..8 + WP_drone_<n>_nn 남쪽 지붕 너머로 날아 들어오는 드론 (마지막 점 = 떠 있는 자리, floor = 떨어질 바닥)
정전용 발광 묶음: GLOW_<구역> 노드 아래에는 발광(UNLIT) 메시만 있다. 노드를 숨기면 그 구역이 꺼지고 아래의 꺼진 창·등갓이 남는다.
  순서(루트 blackout, blackoutDelay): cityhall → core → plaza → screens → monorail(+monorail_train) → d1 → d2 → d3
문서: docs/art/monatium-city.md 11장
"""
import math
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bmesh  # noqa: E402
import bpy  # noqa: E402
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

cb.reset()

# 이 세트만 쓰는 색 (키트 파일은 건드리지 않고 실행 중에 사전에 더한다)
mk.PAL.update({
    "a1_lamp_dead": "#77706b",    # 꺼진 가로등 갓
    "a1_rubble": "#b7ada2",       # 잔해 (석재·콘크리트)
    "a1_rubble_d": "#8c837c",
    "a1_car_red": "#9c4a42",      # 그을린 민간 차량 도색
    "a1_car_blue": "#5b6f8f",
    "a1_car_cream": "#c9bda6",
    "a1_tire": "#2c2830",
    "a1_smoke_d": "#5a5866",      # 검은 연기 (기름·차량 화재). 붉은 해 질 녘 빛에서 회색으로 보이게 푸른 기를 섞었다
    "a1_smoke_m": "#8e8c9a",
    "a1_smoke_l": "#b9b8c4",      # 위로 퍼진 옅은 연기
})
mk.GLOW.update({
    "a1_win_cool": "#d6e6ff",     # 사무실 형광등 창
    "a1_win_amber": "#f2b66e",    # 주거 백열등 창
    "a1_gold_lit": "#ffe6a2",     # 조명 받은 시청 이름 띠
    "a1_lamp_lit": "#fff2cf",     # 포르티코 등·초상 조명등 렌즈
    "a1_screen_on": "#4d84c4",    # 켜진 도시 화면 (몽타주가 텍스처를 씌운다)
    "a1_fountain": "#aef4ff",     # 분수 수중등
    "a1_vend_lit": "#f3fbff",     # 자판기 진열창 조명
})
mk.ALPHA.update({
    "a1_pool": ("#ffd79c", 0.17),    # 가로등 아래 빛 웅덩이
    "a1_flood": ("#ffe3b0", 0.16),   # 초상 투광 조명
})

C = mk.City("act1_cityhall")
A = mk.downtown(C, variant="dusk", training=False, train=True, highway_on=True, skyline=True, screens=True,
                train_x=-36.0)

Y = mk.AVENUE_Y
RD = A["road"]
Z_ROAD = RD.get("z_road", -0.15)
RIOT = "characters/_kit_elfinia_soldier.glb"
CARBINE = "weapons/monatium/monatium_riot_carbine.glb"
M4 = "weapons/us/m4a1.glb"
K7 = "weapons/r41/r41_carbine.glb"
SQ = {k: f"characters/squad_{k}.glb" for k in ("rona", "sabre", "jesty", "karen")}
NAMES = {"rita": "리타", "rona": "로나", "sabre": "사브르", "jesty": "제스티", "karen": "케이트"}
rng = random.Random(41)


# ================================================================== 도우미

def kit_xform(M, fn, *args, **kw):
    """키트 함수 하나가 쌓은 지오메트리를 행렬 M으로 옮긴다 (넘어진 바리케이드, 뒤집힌 차). 충돌 박스는 버린다(보는 세트)."""
    # 빈 누적기에 따로 쌓은 뒤 옮겨서 합친다 (bmesh 원뿔·구 연산이 지운 자리를 재사용해 '뒤에 붙은 정점'으로는 가를 수 없다)
    real, C.acc = C.acc, {}
    n_obj, n_col = len(C.objs), len(C.cols)
    try:
        fn(*args, **kw)
    finally:
        tmp, C.acc = C.acc, real
    for k, b in tmp.items():
        for v in b.verts:
            v.co = M @ v.co
        me = bpy.data.meshes.new("a1_xform_tmp")
        b.to_mesh(me)
        b.free()
        dst = C.acc.get(k)
        if dst is None:
            dst = C.acc[k] = bmesh.new()
        dst.from_mesh(me)
        bpy.data.meshes.remove(me)
    for i in range(n_obj, len(C.objs)):
        o = C.objs[i][3]
        o.matrix_world = M @ o.matrix_world
    del C.cols[n_col:]


def TRS(loc=(0, 0, 0), rz=0.0, ry=0.0, rx=0.0):
    return (Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(rz), 4, "Z")
            @ Matrix.Rotation(math.radians(ry), 4, "Y") @ Matrix.Rotation(math.radians(rx), 4, "X"))


def ground_z(x, y):
    """바닥 높이 (Blender z): 차도는 보도보다 0.15 m 낮다."""
    return Z_ROAD if RD["road_lo"] < y < RD["road_hi"] else 0.0


def jag(r, n, seed, amp=0.25):
    rr = random.Random(seed)
    return [(math.cos(2 * math.pi * i / n) * r * rr.uniform(1 - amp, 1 + amp),
             math.sin(2 * math.pi * i / n) * r * rr.uniform(1 - amp, 1 + amp)) for i in range(n)]


# ================================================================== 방어선 (시청 계단 앞 호, 정면 남쪽)
# 호: y = 9 - 4.5 (x/20)^2. 가운데는 분수 뒤(시청 계단 바로 앞), 양 날개는 앞으로 나와 광장 가운데를 겨눈다.

def arc_y(x):
    return 9.0 - 4.5 * (x / 20.0) ** 2


def arc_yaw(x):
    """호의 바깥(남쪽) 법선을 정면(-Y)으로 하는 yaw(도)."""
    return math.degrees(math.atan(-0.0225 * x))


def arc_n(x):
    d = -0.0225 * x
    v = Vector((d, -1.0, 0.0)).normalized()
    return v


def fallen_barricade(x, y, yaw, *, tip=84.0, seed=0):
    """앞으로 넘어진 바리케이드 (판이 바닥에 눕고 다리가 하늘로)."""
    M = TRS((x, y, 0.05), rz=yaw) @ TRS((0, -0.05, 0), rx=tip)
    kit_xform(M, mk.barricade, C, 0, 0, yaw=0)


C.group("line")
LINE = [
    # (x, 종류)  sand = 모래주머니 벽, bar = 바리케이드, gap = 넘어진 바리케이드(틈), crash = IFV가 들이받은 자리
    (-20.6, "sand"), (-18.3, "bar"), (-16.1, "gap"), (-13.9, "sand"), (-11.6, "bar"), (-9.9, "bar"),
    (-7.8, "sand"), (-5.4, "sand"), (-3.0, "bar"), (-1.2, "gap"), (0.9, "sand"), (3.2, "bar"), (5.0, "bar"),
    (7.1, "sand"), (9.4, "bar"), (11.1, "bar"), (13.0, "crash"), (15.6, "sand"), (17.9, "bar"), (20.3, "sand"),
]
for i, (x, kind) in enumerate(LINE):
    y = arc_y(x)
    yaw = arc_yaw(x)
    if kind == "sand":
        mk.sandbag_wall(C, x, y, yaw=yaw, n=4, rows=3)
    elif kind == "bar":
        jitter = rng.uniform(-6, 6)
        mk.barricade(C, x, y, yaw=yaw + jitter)
    elif kind == "gap":
        # 넘어진 바리케이드 + 흩어진 모래주머니 (틈)
        n = arc_n(x)
        fallen_barricade(x + n.x * 0.9, y + n.y * 0.9, yaw + rng.uniform(-25, 25), seed=i)
        for k in range(4):
            p = Vector((x, y, 0)) + n * rng.uniform(-0.3, 1.6) + Vector((rng.uniform(-1.1, 1.1), 0, 0))
            C.blob("sand", (p.x, p.y, 0.12), 0.34, (1, 0.6, 0.42), segs=8, rings=4, rot_z=rng.uniform(0, 3))
    elif kind == "crash":
        # IFV(veh_1) 코에 밀려 뒤로 넘어간 바리케이드 + 흩어진 모래주머니
        fallen_barricade(x - 0.6, y + 1.3, yaw + 160, tip=80)
        for k in range(6):
            p = (x + rng.uniform(-1.6, 1.8), y + rng.uniform(0.4, 2.2), 0.12)
            C.blob("sand", p, 0.34, (1, 0.6, 0.42), segs=8, rings=4, rot_z=rng.uniform(0, 3))
# 방어선 뒤 탄약 상자·구급 상자 (진압반 남보라)
for (x, y, s) in ((-6.6, 10.4, 0.5), (-12.6, 9.0, 0.45), (2.3, 10.6, 0.5), (8.4, 9.9, 0.45), (-19.4, 6.4, 0.45)):
    mk.crate(C, x, y, s=s, yaw=rng.uniform(-30, 30), key="violet")


# ================================================================== 전쟁 피해
C.group("damage")


def scorch(x, y, r, seed, z=0.0):
    C.decal("soot", jag(r * 0.62, 16, seed, 0.35), (x, y, z), (0, 0, 1), up=(0, 1, 0), lift=0.032)
    C.decal("a1_rubble_d", jag(r * 1.25, 18, seed + 7, 0.35), (x, y, z), (0, 0, 1), up=(0, 1, 0), lift=0.026)


def rubble(x, y, r, n, seed, z=0.0, keys=("a1_rubble", "a1_rubble_d", "concrete_d"), rebar=True):
    rr = random.Random(seed)
    for k in range(n):
        a = rr.uniform(0, 2 * math.pi)
        d = rr.uniform(0, r)
        s = rr.uniform(0.12, 0.42) * (1.0 if d < r * 0.5 else 0.7)
        C.blob(rr.choice(keys), (x + math.cos(a) * d, y + math.sin(a) * d, z + s * 0.35), s,
               (rr.uniform(0.8, 1.4), rr.uniform(0.7, 1.2), rr.uniform(0.45, 0.8)), segs=6, rings=3,
               rot_z=rr.uniform(0, 3), kind="detail")
    if rebar:
        for k in range(2):
            p = Vector((x + rr.uniform(-r, r) * 0.5, y + rr.uniform(-r, r) * 0.5, z + 0.1))
            d = Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(0.3, 0.9))).normalized()
            C.beam("metal", p, p + d * rr.uniform(0.6, 1.2), 0.03, 0.03, kind="detail")


def car(x, y, yaw, color, *, state="burnt", seed=0, z=None):
    """모나티엄 민간 소형차 (엘프 체격, 1.5 x 3.4 m). state: burnt(제자리 그을림) / roof(뒤집힘) / side(옆으로 누움)."""
    z = ground_z(x, y) if z is None else z
    body = "soot" if state == "burnt" else color

    def build():
        C.rbox(body, (0, 0, 0.58), (1.5, 3.4, 0.56))
        C.rbox(body, (0, 0.2, 1.06), (1.32, 1.9, 0.44))
        C.rbox("dark", (0, -0.78, 1.06), (1.2, 0.08, 0.36))       # 앞 유리 (깨져 검은 구멍)
        C.rbox("dark", (0, 1.16, 1.06), (1.2, 0.08, 0.34))
        for sx in (-1, 1):
            C.rbox("dark", (sx * 0.665, 0.2, 1.08), (0.04, 1.6, 0.3))
            for sy in (-1, 1):
                C.cyl("a1_tire", (sx * 0.62, sy * 1.12, 0.3), (sx * 0.8, sy * 1.12, 0.3), 0.3, segs=10)
        if state == "burnt":
            C.rbox(color, (0, 0, 0.3), (1.52, 3.42, 0.12))          # 아래쪽에 남은 도색 띠
            C.blob("smoke_d", (0, -1.2, 0.95), 0.5, (1.4, 1, 0.5), segs=6, rings=3)

    if state == "roof":
        M = TRS((x, y, z + 1.36), rz=yaw, ry=180 + rng.uniform(-6, 6))
    elif state == "side":
        M = TRS((x, y, z + 0.76), rz=yaw, ry=90)
    else:
        M = TRS((x, y, z), rz=yaw, rx=rng.uniform(-3, 3))
    kit_xform(M, build)


# 그을음 (포격·폭발 자국)
for i, (x, y, r) in enumerate([(-3.0, -5.0, 1.8), (4.8, -5.6, 1.4), (-12.0, -3.0, 1.6), (-2.2, -9.4, 1.2), (13.4, -4.2, 1.5),
                               (-16.0, 4.0, 1.9), (-1.0, 6.8, 1.3), (12.6, 6.6, 1.6), (19.5, -2.0, 1.1), (-20.5, -8.4, 1.2),
                               (7.5, 2.4, 0.9), (-8.0, 4.6, 1.0)]):
    scorch(x, y, r, 300 + i)
for i, (x, y, r) in enumerate([(-8.0, -17.0, 2.2), (12.0, -24.0, 2.6), (-30.0, -18.5, 2.0), (26.0, -16.5, 1.8),
                               (-44.0, -23.5, 2.4), (40.0, -24.0, 2.0)]):
    scorch(x, y, r, 340 + i, z=Z_ROAD)
# 잔해 더미 (틈, 충돌 자리, 상가 앞)
for i, (x, y, r, n) in enumerate([(-16.4, 5.6, 1.4, 9), (-1.4, 7.6, 1.2, 8), (12.4, 8.6, 1.6, 10), (-4.0, -4.4, 1.0, 5),
                                  (6.0, -7.4, 1.0, 5), (-12.6, 1.0, 0.8, 4), (16.6, -7.8, 1.0, 5)]):
    rubble(x, y, r, n, 400 + i)
for i, x in enumerate((-18.0, -45.5, 20.4, 3.4, 33.0)):
    rubble(x, RD["walk_lo"] + 0.6 - 0.2, 1.6, 10, 450 + i)     # 상가 정면에서 떨어진 외벽 조각
# 부서진 화단 (광장 앞 화단 두 개: 흙이 쏟아지고 테두리가 깨짐)
for i, (x, y) in enumerate(((-9.5, -2.2), (9.5, -2.2))):
    C.decal("soil", jag(1.5, 14, 500 + i, 0.35), (x + 0.4, y - 1.0, 0), (0, 0, 1), up=(0, 1, 0), lift=0.028)
    rubble(x, y - 0.9, 1.3, 7, 510 + i, keys=("stone_d", "a1_rubble", "soil"), rebar=False)
# 쓰러진 가로수 (광장 남서 화단)
C.cyl("trunk", (-16.4, -6.5, 0.45), (-13.2, -8.6, 0.3), 0.16, r2=0.1, segs=8)
C.blob("leaf_d", (-12.4, -9.2, 0.9), 1.4, (1.3, 1.0, 0.7), segs=8, rings=5)
C.blob("leaf", (-13.4, -8.4, 1.1), 1.1, (1.1, 1.0, 0.8), segs=8, rings=5)

# 부서진 민간 차량
CARS = [
    ("car_1", 21.4, -12.7, 70, "a1_car_red", "burnt"),       # 광장 남동 모퉁이 보도 (불타는 중)
    ("car_2", -19.0, -25.2, 200, "a1_car_blue", "roof"),     # 중앙로 남쪽 차로, 뒤집힘
    ("car_3", 10.6, -25.0, -24, "a1_car_cream", "side"),     # 남쪽 차로, 옆으로 누움
    ("car_4", -21.8, -6.2, 104, "a1_car_cream", "burnt"),    # 광장 서쪽 가장자리
    ("car_5", 5.4, -19.0, 96, "a1_car_red", "burnt"),         # 모노레일 기둥(x=8)에 박힘
]
for i, (cid, x, y, yaw, col, st) in enumerate(CARS):
    car(x, y, yaw, col, state=st, seed=i)

# 연기 기둥 (정지한 회색 덩어리 더미: 중앙로 너머 상가 뒤, 광장 가장자리)
C.group("smoke")
SMOKE = [
    # (x, y, 높이, 반지름, 검은 비율)
    (-58.0, -60.0, 70.0, 5.5, 0.3), (-24.0, -66.0, 84.0, 6.0, 0.3), (18.0, -62.0, 60.0, 5.0, 0.35),
    (50.0, -68.0, 76.0, 6.0, 0.25), (86.0, -40.0, 56.0, 5.0, 0.3), (-42.0, 64.0, 62.0, 5.0, 0.25),
    (32.0, 68.0, 50.0, 4.5, 0.3),
    (21.4, -12.7, 22.0, 1.5, 0.35), (-21.8, -6.2, 18.0, 1.4, 0.35), (5.4, -19.0, 18.0, 1.3, 0.35),
]


def smoke(x, y, z, h, r, seed, dark, fire):
    """정지한 연기 기둥: 아웃라인 없는(fine) 덩어리를 위로 갈수록 크고 옅게, 바람 쪽으로 기울여 쌓는다.
    키트 smoke_column(위성 시점용, 아웃라인 있는 불투명 덩어리)은 지상에서 보면 바위처럼 보여 따로 만든다."""
    sr = random.Random(seed)
    n = max(5, int(h / (r * 1.1)))
    wind = Vector((0.3, 0.12, 0.0))
    if fire:
        C.blob("fire", (x, y, z + r * 0.2), r * 0.42, (1, 1, 0.55), segs=7, rings=4)
        C.blob("fire_c", (x, y, z + r * 0.16), r * 0.24, (1, 1, 0.6), segs=6, rings=3)
    for k in range(n):
        t = k / (n - 1)
        zz = z + r * 0.45 + t * h
        rr = r * (0.6 + 0.95 * t ** 1.2) * sr.uniform(0.85, 1.15)
        c = Vector((x, y, zz)) + wind * (zz - z) * (0.4 + 0.6 * t)
        key = "a1_smoke_d" if t < dark else ("a1_smoke_m" if t < dark + 0.3 else "a1_smoke_l")
        for j in range(2 if t > 0.5 else 1):
            o = Vector((sr.uniform(-0.45, 0.45) * rr, sr.uniform(-0.45, 0.45) * rr, sr.uniform(-0.2, 0.2) * rr))
            C.blob(key, tuple(c + o), rr * (1.0 if j == 0 else 0.75), (1.0, 1.0, 0.72), segs=9, rings=5,
                   rot_z=sr.uniform(0, 3), kind="fine")


for i, (x, y, h, r, dark) in enumerate(SMOKE):
    smoke(x, y, ground_z(x, y), h, r, 60 + i, dark, fire=r < 4.0 or i in (1, 3))

# 상가 외벽 포탄 자국 (정면 +Y, 보도 쪽 벽)
C.group("damage")
yb1 = RD["walk_lo"] - 0.4
for i, (x, z, r) in enumerate([(-16.0, 9.0, 1.6), (21.0, 12.5, 1.8), (-44.0, 6.5, 1.4), (5.0, 15.5, 1.2), (36.0, 8.0, 1.5)]):
    C.decal("soot", jag(r, 14, 600 + i, 0.4), (x, yb1, z), (0, 1, 0), lift=0.05)
    C.decal("dark", jag(r * 0.45, 10, 620 + i, 0.4), (x, yb1, z), (0, 1, 0), lift=0.056)


# ================================================================== 인물 (마커만)
C.group("npc")
HB = "heidi,blackout"


def riot(i, x, y, pose, face, *, carbine=True, note=None, look=None):
    p = {"scene": HB}
    if carbine:
        p["hold_R"] = CARBINE
    if note:
        p["note"] = note
    C.npc(f"riot_{i:02d}", (x, y, 0.0), RIOT, pose=pose, face=face, name="진압반원", look=look, props=p)


def behind(x, d=0.6):
    """호 뒤(북쪽) d m 지점."""
    n = arc_n(x)
    return (x - n.x * d, arc_y(x) - n.y * d)


def front(x, d):
    n = arc_n(x)
    return (x + n.x * d, arc_y(x) + n.y * d)


def aim(x, dist=30.0):
    n = arc_n(x)
    return (x + n.x * dist, arc_y(x) + n.y * dist)


# 진압반원 15명: 엄폐, 겨눔, 쓰러짐, 부상 (방어선 12 + 앞쪽 화단 전초 3)
riot(1, *behind(-18.3, 0.62), "train_drill", aim(-18.3), note="바리케이드 위로 겨눔")
riot(2, *front(-16.1, 1.9), "lie_sprawl", front(-16.1, 6.0), note="틈에서 앞으로 쓰러짐")
riot(3, *behind(-12.7, 0.62), "hold_rifle_ready", aim(-12.7))
riot(4, *behind(-11.5, 1.9), "sit_dazed", (-11.0, 4.0), note="방어선 뒤 부상")
riot(5, -7.4, 11.7, "lie_sprawl", (-9.4, 13.2), note="케이트가 곁에 무릎 꿇음")
riot(6, *front(-1.2, 1.2), "lie_sprawl", front(-1.2, 6.0), note="가운데 틈에서 쓰러짐")
riot(7, *behind(0.9, 0.62), "kneel_head_down", aim(0.9))
riot(8, *behind(5.0, 0.62), "hold_rifle_ready", aim(5.0))
riot(9, *behind(8.6, 1.4), "cower", (13.0, 5.0), carbine=False, note="IFV 돌입에 웅크림")
riot(10, 15.6, 10.1, "help_up", (16.3, 10.9), carbine=False, look="riot_11", note="riot_11을 일으킴")
riot(11, 16.3, 10.9, "sit_dazed", (15.0, 9.0))
riot(12, *behind(19.0, 0.62), "train_drill", aim(19.0))
# 앞쪽 화단(전초) 뒤: 버티다 쓰러지는 중
riot(13, -10.3, -1.1, "kneel", (-10.0, -20.0), note="서쪽 화단 뒤 전초")
riot(14, -8.1, -0.4, "lie_sprawl", (-7.6, 3.5), note="화단에서 뒤로 쓰러짐")
riot(15, 10.4, -1.0, "hold_rifle_ready", (10.0, -20.0), note="동쪽 화단 뒤 전초")

# 분대 (정전 컷: 리타의 눈이 1인칭 시점)
RITA = behind(-5.4, 0.55)
C.npc("rita", (RITA[0], RITA[1], 0.0), "characters/rita.glb", pose="hold_rifle_ready", face=aim(-5.4), name="리타",
      props={"scene": "blackout", "hold_R": M4, "note": "pov_rita 카메라 = 이 자리 눈높이 0.92 m"})
SQUAD = [
    ("sabre", behind(-3.0, 0.62), "train_drill", aim(-3.0)),
    ("rona", behind(-7.8, 0.6), "kneel", aim(-7.8)),
    ("jesty", behind(-9.9, 0.62), "hold_rifle_ready", aim(-9.9)),
    ("karen", (-6.6, 11.1), "kneel", (-7.4, 11.7)),
]
for nid, (x, y), pose, face in SQUAD:
    C.npc(nid, (x, y, 0.0), SQ[nid], pose=pose, face=face, name=NAMES[nid],
          props={"scene": "blackout", "hold_R": M4})

# R41 보병 12명: 중앙로에서 광장으로
R41 = {"a": "enemies/r41_rifleman_a.glb", "b": "enemies/r41_rifleman_b.glb", "x": "enemies/r41_assault.glb"}
R41_LIST = [
    ("a", -6.3, -12.5, "kneel", (-5.0, 8.0), "가로등 뒤 엄폐"),
    ("b", -5.7, -14.8, "hold_rifle_ready", (-3.0, 8.0), "veh_3 앞"),
    ("x", 2.6, -12.4, "run", (1.0, 4.0), "광장으로 돌진"),
    ("a", 8.6, -8.4, "run", (6.0, 2.0), "광장 안"),
    ("x", -12.4, -10.0, "hold_rifle_ready", (-9.0, 8.0), "veh_2 옆"),
    ("b", -18.8, -14.4, "kneel", (-12.0, 6.0), "veh_2 뒤 엄폐"),
    ("a", 16.4, -13.4, "hold_rifle_ready", (13.0, 4.0), "veh_1 뒤를 따름"),
    ("x", 18.6, -9.6, "run", (15.0, 4.0), "광장 동쪽으로"),
    ("b", -21.0, -25.4, "run", (-18.0, -12.0), "남쪽 차로를 건넘"),
    ("a", 0.6, -32.4, "run", (0.0, -18.0), "가운데 골목에서 나옴"),
    ("b", 9.2, -24.2, "kneel", (5.0, 0.0), "남쪽 차로"),
]
for i, (m, x, y, pose, face, note) in enumerate(R41_LIST, start=1):
    C.npc(f"r41_{i:02d}", (x, y, ground_z(x, y)), R41[m], pose=pose, face=face, name="R41",
          props={"scene": HB, "hold_R": K7, "note": note, "faction": "enemy"})


# ================================================================== R41 차량 (돌입 경로 → 멈춘 자리)

def ramp_z(x):
    """알프토반 진입로 높이 (downtown의 highway: x 66 → 136에서 -0.15 → 9.0, smoothstep)."""
    x0, x1, z0, z1 = 66.0, 136.0, Z_ROAD, 9.0
    t = min(1.0, max(0.0, (x - x0) / (x1 - x0)))
    return z0 + (z1 - z0) * t * t * (3 - 2 * t)


def path_markers(prefix, pts, speed, *, slow_last=0.5, extra=None):
    """WP_<prefix>_nn. 속성 t = 출발 뒤 그 점에 닿는 시각(초, 제안값). 마지막 구간은 속도를 줄인다."""
    t = 0.0
    out = []
    for i, p in enumerate(pts):
        if i:
            d = (Vector(p) - Vector(pts[i - 1])).length
            v = speed * (slow_last if i == len(pts) - 1 else 1.0)
            t += d / v
        nxt = pts[i + 1] if i + 1 < len(pts) else None
        prv = pts[i - 1] if i else None
        face = (nxt[0], nxt[1]) if nxt else (2 * p[0] - prv[0], 2 * p[1] - prv[1])
        props = {"t": round(t, 2)}
        props.update(extra or {})
        C.marker(f"WP_{prefix}_{i + 1:02d}", p, face=face, props=props)
        out.append(round(t, 2))
    return out


C.group("vehicles")
IFV = "vehicles/r41/r41_ifv.glb"
RAIDER = "vehicles/r41/r41_raider.glb"
VEH = {
    # veh_1: 알프토반에서 내려와 중앙로 북쪽 차로 → 광장으로 꺾어 방어선 동쪽(x 13)을 들이받는다
    1: (IFV, [(122.0, -18.4), (70.0, -17.8), (34.0, -16.0), (19.5, -14.6), (14.2, -10.6), (13.1, -3.0), (12.9, 4.4)],
        (12.3, 12.0), 13.0, "crash"),
    # veh_2: 서쪽 끝에서 고속 습격차가 달려와 광장 남서 보도에 비스듬히 멈춘다
    2: (RAIDER, [(-100.0, -16.4), (-50.0, -16.6), (-25.0, -16.2), (-17.8, -14.4), (-15.4, -12.7)],
        (-9.0, -6.0), 18.0, "stall"),
    # veh_3: 알프토반에서 내려와 중앙로 북쪽 차로를 따라 서쪽으로, 시청 축(x 0) 앞에서 멈춘다
    3: (IFV, [(128.0, -22.0), (74.0, -18.4), (30.0, -17.6), (8.0, -16.8), (-1.5, -16.5)],
        (-12.0, -16.2), 12.0, "stall"),
}
for n, (model, pts2, face, speed, mode) in VEH.items():
    pts = [(x, y, ramp_z(x) if x > 66 else ground_z(x, y)) for (x, y) in pts2]
    ts = path_markers(f"veh_{n}", pts, speed, extra={"scene": HB})
    last = pts[-1]
    C.prop(f"veh_{n}", last, model, face=face,
           props={"collider": 0, "scene": HB, "path": f"veh_{n}", "arrive": ts[-1], "stall": 1,
                  "crash": 1 if mode == "crash" else 0, "faction": "enemy"})
# 충돌 불꽃·연기 지점 (IFV 코가 방어선에 박힌 자리)
C.fx("spark_1", (12.9, 7.6, 0.9), delay=0.0, dir="0,0.5,-0.5", strength=0.8, scene=HB)
C.fx("smoke_1", (12.9, 6.8, 1.6), delay=0.2, dir="0,1,0", strength=0.6, scene=HB)
for i, (cid, x, y, yaw, col, st) in enumerate([c for c in CARS if c[5] == "burnt"], start=2):
    C.fx(f"smoke_{i}", (x, y, ground_z(x, y) + 1.2), delay=0.0, dir="0,1,0", strength=0.5, scene=HB, car=cid)


# ================================================================== R41 드론 (남쪽 지붕 너머로 날아 들어와 떠 있음)
C.group("drones")
DRONES = {
    # n: (모델, 떠 있는 자리, 들어오는 경로(먼 남쪽 → 지붕 위 → 자리 앞), 정면이 볼 곳)
    1: ("drone_gunship", (-3.0, -15.0, 14.0), [(-24.0, -150.0, 58.0), (-10.0, -62.0, 38.0), (-4.0, -30.0, 20.0)], (-4.0, 9.0)),
    2: ("drone_gunship", (9.0, -5.0, 17.0), [(30.0, -160.0, 62.0), (18.0, -66.0, 40.0), (11.0, -24.0, 24.0)], (6.0, 10.0)),
    3: ("drone_gunship", (-14.0, -23.4, 23.0), [(-60.0, -150.0, 66.0), (-30.0, -70.0, 44.0), (-17.0, -38.0, 30.0)], (-10.0, 8.0)),
    4: ("drone_gunship", (16.0, -27.0, 31.0), [(56.0, -150.0, 70.0), (30.0, -72.0, 48.0), (19.0, -42.0, 36.0)], (10.0, 8.0)),
    5: ("drone_recon", (-8.0, 1.5, 12.0), [(-14.0, -140.0, 52.0), (-10.0, -60.0, 34.0), (-8.5, -18.0, 16.0)], (-6.0, 12.0)),
    6: ("drone_recon", (0.6, -29.0, 38.0), [(8.0, -160.0, 74.0), (4.0, -80.0, 52.0), (1.2, -48.0, 43.0)], (0.0, 0.0)),
    7: ("drone_swarm", (2.0, -8.0, 13.0), [(4.0, -130.0, 48.0), (3.0, -58.0, 32.0), (2.4, -24.0, 18.0)], (1.0, 10.0)),
    8: ("drone_swarm", (-5.0, -11.0, 16.5), [(-8.0, -136.0, 52.0), (-6.0, -60.0, 34.0), (-5.2, -28.0, 21.0)], (-4.0, 10.0)),
}
for n, (model, hover, inbound, face) in DRONES.items():
    pts = inbound + [hover]
    speed = {"drone_gunship": 20.0, "drone_recon": 16.0, "drone_swarm": 24.0}[model]
    ts = path_markers(f"drone_{n}", pts, speed, slow_last=0.45, extra={"scene": HB})
    floor = ground_z(hover[0], hover[1])
    C.prop(f"drone_{n}", hover, f"drones/{model}.glb", face=face,
           props={"collider": 0, "scene": HB, "path": f"drone_{n}", "arrive": ts[-1], "hover": 1,
                  "floor": round(floor, 3), "faction": "enemy"})


# ================================================================== 카메라
C.group("cams")
RX, RY = RITA
C.cam("heidi_a", [   # 바리케이드 뒤에 웅크린 하이디: 중앙로로 R41이 밀려오고 진압반원이 쓰러진다
    (0.0, (-14.6, 8.75, 1.1), (-7.0, -20.0, 1.2), 52),
    (3.0, (-14.4, 8.65, 1.15), (-5.0, -20.0, 1.6), 50),
    (6.0, (-14.2, 8.6, 1.12), (-3.0, -19.0, 1.5), 48),
])
C.cam("heidi_b", [   # 핸드헬드로 하늘을 휙: 남쪽 지붕 너머로 쓸고 들어오는 드론
    (0.0, (-8.8, 10.7, 1.1), (-5.0, -20.0, 3.0), 50),
    (0.7, (-8.8, 10.65, 1.12), (-3.0, -24.0, 9.0), 52),
    (1.6, (-8.7, 10.6, 1.15), (1.0, -30.0, 24.0), 56),
    (5.0, (-8.5, 10.5, 1.18), (3.0, -32.0, 26.0), 56),
])
C.cam("heidi_c", [   # 방어선을 들이받는 IFV, 하이디가 물러선다
    (0.0, (10.4, 10.6, 1.1), (13.2, 3.6, 1.6), 54),
    (2.5, (9.0, 11.8, 1.25), (13.0, 4.2, 1.5), 58),
    (5.0, (7.4, 12.8, 1.35), (12.8, 4.8, 1.4), 60),
])
C.cam("pov_rita", [  # 리타 눈높이: 모래주머니 너머 중앙로
    (0.0, (RX, RY - 0.06, 0.92), (-6.4, -21.0, 2.2), 55),
    (4.0, (RX + 0.02, RY - 0.08, 0.93), (-6.0, -21.0, 2.5), 55),
])
C.cam("drones_fall", [  # 방어선 뒤 낮은 광각: 중앙로 위 하늘의 드론들이 떨어진다
    (0.0, (2.3, 11.7, 0.45), (1.0, -22.0, 17.0), 66),
    (6.0, (2.4, 11.4, 0.5), (1.0, -22.0, 12.0), 64),
])
C.cam("vehicles_stall", [  # 중앙로 노면 높이: 멈춰 선 R41 차량
    (0.0, (-27.0, -16.2, 0.9), (-14.0, -12.6, 1.2), 44),
    (5.0, (-23.0, -18.4, 1.1), (2.0, -14.5, 1.6), 50),
])
C.cam("blackout_hall", [  # (추가) 방어선 뒤에서 올려다본 시청: 가장 먼저 꺼진다
    (0.0, (-10.0, -1.2, 1.3), (-3.0, 22.0, 10.0), 58),
    (3.0, (-9.6, -0.6, 1.45), (-2.6, 22.0, 11.5), 56),
])
C.cam("blackout_wide", [  # 시청 탑 앞 높이에서 광장 너머 도심: 구역별로 꺼진다
    (0.0, (-3.0, 17.2, 19.0), (0.0, -60.0, 6.0), 58),
    (7.0, (2.5, 16.6, 21.5), (0.0, -70.0, 9.0), 54),
])
# 하이디 자리 (보이지 않음: 카메라를 든 사람의 발밑)
C.marker("MARK_heidi_a", (-14.6, 8.75, 0.0), face=(-7.0, -20.0), props={"scene": "heidi"})
C.marker("MARK_heidi_b", (-8.8, 10.7, 0.0), face=(-5.0, -20.0), props={"scene": "heidi"})
C.marker("MARK_heidi_c", (10.4, 10.6, 0.0), face=(13.2, 3.6), props={"scene": "heidi"})
C.marker("SPAWN_player", (RX, RY, 0.0), face=aim(-5.4))


# ================================================================== 정전 발광 묶음 (GLOW_<구역>)
# 1) 시청 전용 발광 (포르티코 등, 이름 띠, 초상 조명) 2) 창에 켜진 불 3) 키트가 만든 발광 메시를 구역별로 나눈다
#    (가로등 갓·시안 띠는 아래에 꺼진 복사본을 남긴다) 4) 도시 화면 SCREEN_*은 GLOW_screens로 옮겨 켜진 머티리얼

LIT_KEYS = {"glow", "lamp", "holo", "holo_l", "cyan_hot", "win_lit"}
GROUP_DISTRICT = {"cityhall": "cityhall", "core": "core", "plaza": "plaza", "east": "d1", "west": "d1", "north": "d1",
                  "south": "d2", "avenue": "d2", "skyline": "d3", "MONORAIL_train": "monorail_train"}
ORDER = [("cityhall", 0.0), ("core", 0.35), ("plaza", 0.9), ("screens", 1.1), ("monorail", 1.6),
         ("monorail_train", 1.6), ("d1", 2.2), ("d2", 3.0), ("d3", 4.0)]
WIN_P = {"cityhall": 0.9, "d1": 0.62, "d2": 0.58, "d3": 0.45, "monorail_train": 1.0}


def G(d):
    return f"GLOW_{d}"


def district_of(g, c):
    if g == "avenue" and abs(c.y - Y) < 0.8 and 7.6 < c.z < 8.8:
        return "monorail"
    d = GROUP_DISTRICT.get(g)
    if d:
        return d
    if math.hypot(c.x / 1.25, c.y) > 80:
        return "d3"
    return "d2" if c.y < RD["walk_hi"] else "d1"


def bm_into(dst, pts, smooth=False):
    vs = [dst.verts.new(p) for p in pts]
    try:
        f = dst.faces.new(vs)
        f.smooth = smooth
    except ValueError:
        pass


def face_frame(f):
    """세운 면의 (법선, 가로축, u 범위, z 범위, 중심)."""
    N = f.normal.copy()
    R = Vector((0, 0, 1)).cross(N)
    if R.length < 1e-4:
        return None
    R.normalize()
    us = [v.co.dot(R) for v in f.verts]
    zs = [v.co.z for v in f.verts]
    return N, R, (min(us), max(us)), (min(zs), max(zs)), f.calc_center_median()


WIN_KEYS = ("win_lit", "a1_win_cool", "a1_win_amber")


def light_windows():
    """창 유리 면(키트의 glass 데칼, 유리탑 몸체, 원경 창 띠)에 켜진 창을 덧붙인다 (UNLIT, GLOW_<구역>)."""
    wr = random.Random(77)
    adds = []
    for (g, key, kind), b in list(C.acc.items()):
        if g.startswith("GLOW_"):
            continue
        d = GROUP_DISTRICT.get(g)
        if d not in WIN_P:
            continue
        mode = None
        if key == "glass" and g != "skyline":
            mode = "win"
        elif key == "glass_t" and g != "skyline":
            mode = "tower"
        elif key in ("glass_d", "far_d") and g == "skyline":
            mode = "far"
        elif key == "glass_d" and g == "cityhall":
            mode = "slit"
        if not mode:
            continue
        b.normal_update()
        for f in b.faces:
            if abs(f.normal.z) > 0.3:
                continue
            fr = face_frame(f)
            if fr is None:
                continue
            N, R, (u0, u1), (z0, z1), cen = fr
            W, H = u1 - u0, z1 - z0
            base = cen - R * (cen.dot(R)) - Vector((0, 0, cen.z))   # 면 위 u=0, z=0 기준점
            off = N * (0.08 if mode == "far" else (0.012 if mode == "tower" else 0.01))
            p = WIN_P[d]
            if g == "cityhall" and N.y > 0.5:
                p = 0.55                                   # 시청 뒷면

            def cell(ua, ub, za, zb, k):
                adds.append((d, k, [base + R * ua + Vector((0, 0, za)) + off, base + R * ub + Vector((0, 0, za)) + off,
                                    base + R * ub + Vector((0, 0, zb)) + off, base + R * ua + Vector((0, 0, zb)) + off]))

            if mode == "slit":
                if H > 2.0:                                # 탑 옆 세로창, 정문 유리
                    adds.append((d, "a1_win_cool" if H > 4 else "win_lit", [v.co + off * 0.6 for v in f.verts]))
                continue
            if mode == "far":
                if W < 3.0 or H < 0.6:
                    continue
                n = max(2, int(W / 2.6))
                cw = W / n
                for k in range(n):
                    if wr.random() < p:
                        cell(u0 + k * cw + 0.25, u0 + (k + 1) * cw - 0.25, z0 + 0.1, z1 - 0.1,
                             wr.choice(("win_lit", "win_lit", "a1_win_cool", "a1_win_amber")))
                continue
            if mode == "tower":
                if W < 1.5 or H < 4.0:
                    continue
                n_v = max(2, int(W / 1.5))
                floors = int(round(H / 2.7))
                fh = H / max(1, floors)
                cw = W / n_v
                for i in range(floors):
                    for k in range(n_v):
                        if wr.random() < p * 0.8:
                            cell(u0 + k * cw + 0.1, u0 + (k + 1) * cw - 0.1, z0 + i * fh + 0.35, z0 + (i + 1) * fh - 0.25,
                                 wr.choice(("a1_win_cool", "a1_win_cool", "win_lit")))
                continue
            # mode == "win": 키트 창 데칼
            if W < 0.5 or H < 0.45:
                continue
            if W > 2.2:
                shop = H > 1.6                             # 상가 진열창 (높이 1.9) / 사무 띠창 (1.24)
                n = max(2, int(W / 1.8)) if shop else max(1, int(W / 1.4))
                cw = W / n
                for k in range(n):
                    if wr.random() < (0.85 if shop else p):
                        cell(u0 + k * cw + 0.07, u0 + (k + 1) * cw - 0.07, z0 + 0.06, z1 - 0.06,
                             "win_lit" if shop else wr.choice(("a1_win_cool", "a1_win_cool", "win_lit", "a1_win_amber")))
            elif wr.random() < p:
                k = "a1_win_amber" if d in ("d1", "d2") and wr.random() < 0.45 else "win_lit"
                if g == "MONORAIL_train":
                    k = "a1_win_cool"
                adds.append((d, k, [v.co + off for v in f.verts]))
    for d, k, pts in adds:
        bm_into(acc((G(d), k, "fine")), pts)


def islands(b):
    b.verts.index_update()
    parent = list(range(len(b.verts)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for f in b.faces:
        r0 = find(f.verts[0].index)
        for v in f.verts[1:]:
            r = find(v.index)
            if r != r0:
                parent[r] = r0
    out = defaultdict(list)
    for f in b.faces:
        out[find(f.verts[0].index)].append(f)
    return list(out.values())


def copy_faces(dst, faces, xf=None):
    vmap = {}
    for f in faces:
        vs = []
        for v in f.verts:
            nv = vmap.get(v)
            if nv is None:
                nv = vmap[v] = dst.verts.new(xf(v.co) if xf else v.co)
            vs.append(nv)
        try:
            nf = dst.faces.new(vs)
            nf.smooth = f.smooth
        except ValueError:
            pass


def acc(key3):
    b = C.acc.get(key3)
    if b is None:
        b = C.acc[key3] = bmesh.new()
    return b


POOLS = []


def split_glow():
    """키트 발광 메시를 섬(이어진 면) 단위로 구역 GLOW_<d> 그룹에 옮긴다."""
    for (g, key, kind), b in list(C.acc.items()):
        if g.startswith("GLOW_") or key not in LIT_KEYS:
            continue
        kept = bmesh.new()
        b.normal_update()
        for isl in islands(b):
            c = sum((f.calc_center_median() for f in isl), Vector()) / len(isl)
            d = district_of(g, c)
            if d is None:
                copy_faces(kept, isl)
                continue
            copy_faces(acc((G(d), key, "fine")), isl)
            n0 = isl[0].normal
            flat = all(f.normal.dot(n0) > 0.98 for f in isl)
            if key == "lamp":
                # 꺼진 등갓 (안쪽으로 조금 작게) + 가로등 빛 웅덩이
                copy_faces(acc((g, "a1_lamp_dead", "fine")), isl,
                           lambda co, c=c: Vector((c.x + (co.x - c.x) * 0.93, c.y + (co.y - c.y) * 0.93, co.z)))
                POOLS.append((d, c.x, c.y))
            elif key == "glow" and d in ("core", "monorail", "monorail_train"):
                if flat:
                    # 꺼진 복사본은 약한 편향 층(under): 켜진 발광(fine)이 거리와 상관없이 이긴다 (표준 깊이 버퍼에서 4 mm는
                    # 45 m부터 깜빡임)
                    copy_faces(acc((g, "glow_off", "under")), isl, lambda co, n=n0.copy(): co - n * 0.004)
                else:
                    copy_faces(acc((g, "glow_off", "under")), isl,
                               lambda co, c=c: Vector((c.x + (co.x - c.x) * 0.99, c.y + (co.y - c.y) * 0.99, co.z)))
        b.free()
        C.acc[(g, key, kind)] = kept
    # 글자 오브젝트 (간판·표지의 발광 글자)
    for i, (g, key, kind, o) in enumerate(C.objs):
        if g.startswith("GLOW_") or key not in LIT_KEYS:
            continue
        d = district_of(g, o.matrix_world.translation)
        if d:
            C.objs[i] = (G(d), key, "fine", o)


def screens_on():
    """SCREEN_*: 켜진 머티리얼로 GLOW_screens 아래에, 원래 자리에는 꺼진 화면 판을 남긴다."""
    for i, (g, o) in enumerate(C.specials):
        if not o.name.startswith("SCREEN_"):
            continue
        me = o.data
        me.calc_loop_triangles()
        nrm = me.polygons[0].normal.copy() if len(me.polygons) else Vector((0, -1, 0))
        dead = acc((g, "screen", "fine"))
        for poly in me.polygons:
            bm_into(dead, [o.location + me.vertices[vi].co - nrm * 0.01 for vi in poly.vertices])
        o.data.materials.clear()
        cb.assign(o, mk.M("a1_screen_on"))
        o["lit"] = 1
        C.specials[i] = (G("screens"), o)


def cityhall_lights():
    """시청: 포르티코 천장등·처마 띠, 조명 받은 이름 띠, 정문 벽등, 초상 투광 조명."""
    yf = A["cityhall_y_front"]            # 날개 정면 (19)
    PY0 = yf - 5.0                        # 포르티코 기둥 줄
    PH = 8.2                              # 포르티코 천장
    pfront = PY0 + 2.6 - 2.8              # 포르티코 지붕 앞면 (13.8)
    C.group(G("cityhall"))
    nc = Vector((0.0, pfront - 0.01, PH + 0.45))
    C.text("a1_gold_lit", "모나티엄 시청", 0.62, nc + Vector((0, 0, 0.05)), (0, -1, 0), lift=0.042)
    C.rect("a1_lamp_lit", (0.0, pfront - 0.01, PH + 0.08), (0, -1, 0), 15.6, 0.07, lift=0.03)
    for k in range(5):
        x = -7.5 + (k + 0.5) * 3.0
        for yy in (PY0 + 1.6, PY0 + 3.8):
            C.decal("a1_lamp_lit", hw.circle(0.3, 12), (x, yy, PH - 0.01), (0, 0, -1), up=(0, 1, 0), lift=0.0)
    # 정문 양옆 벽등
    for sx in (-1, 1):
        C.decal("a1_lamp_lit", hw.stadium(0.5, 0.22, 4, angle=90), (sx * 2.9, yf - 0.16, 3.2), (0, -1, 0), lift=0.0)
    C.group("cityhall")
    for sx in (-1, 1):
        C.rbox("metal", (sx * 2.9, yf - 0.08, 3.2), (0.34, 0.14, 0.62), kind="detail")
    # 초상 투광 조명: 액자 아래 조명등 셋 (등은 시청 그룹, 렌즈와 빛은 GLOW_cityhall)
    pc = Vector(A["cityhall_portrait_center"])
    zb = pc.z - 9.6 / 2 - 0.75
    for k in (-1, 0, 1):
        x = pc.x + k * 2.2
        C.beam("metal", (x, pc.y, zb + 0.15), (x, pc.y - 0.7, zb + 0.15), 0.08, 0.08, kind="detail")
        C.rbox("dark", (x, pc.y - 0.82, zb + 0.22), (0.42, 0.3, 0.26), rot=(-35, 0, 0), kind="detail")
    C.group(G("cityhall"))
    for k in (-1, 0, 1):
        x = pc.x + k * 2.2
        C.rect("a1_lamp_lit", (x, pc.y - 0.89, zb + 0.33), (0, -0.57, 0.82), 0.34, 0.2, lift=0.02)
    # 반투명 빛 자락: 초상 맨 위 층(판에서 약 39 cm)보다 3 cm 앞 (반투명은 깊이 편향을 받지 않으므로 간격으로만 가른다)
    C.rect("a1_flood", (pc.x, pc.y - 0.42, pc.z), (0, -1, 0), 6.5, 10.1, lift=0.0)
    # 날개 정면 투광: 바닥 투광등(시청 그룹) + 위로 옅어지는 빛 자락 (GLOW_cityhall)
    for sx in (-1, 1):
        for k in range(4):
            x = sx * (7.3 + k * 2.6)
            C.group("cityhall")
            C.rbox("dark", (x, yf - 0.55, 1.05), (0.5, 0.36, 0.28), rot=(28, 0, 0), kind="detail")
            C.group(G("cityhall"))
            C.rect("a1_lamp_lit", (x, yf - 0.73, 1.12), (0, -0.88, 0.47), 0.42, 0.18, lift=0.02)
            for j, (h0, h1, w) in enumerate(((1.0, 4.6, 2.2), (4.6, 8.0, 2.6), (8.0, 11.0, 2.9))):
                C.rect("a1_flood", (x, yf - 0.04 - j * 0.004, (h0 + h1) / 2), (0, -1, 0), w, h1 - h0, lift=0.0)
    # 탑 정면 위쪽 투광 (로고 원판 둘레)
    tz = A["cityhall_tower_top"]
    C.rect("a1_flood", (0.0, pc.y - 0.07, tz - 2.6), (0, -1, 0), 8.0, 5.6, lift=0.0)   # 로고(탑 면에서 4.8 cm)보다 2.2 cm 앞


def plaza_lights():
    """분수 수중등·자판기 진열창 (GLOW_plaza)."""
    fx, fy = A["fountain"].x, A["fountain"].y
    C.group(G("plaza"))
    C.ring("a1_fountain", hw.circle(3.55, 40), hw.circle(3.3, 40), (fx, fy, 0.52), (0, 0, 1), up=(0, 1, 0), lift=0.012)
    for i in range(10):
        a = 2 * math.pi * (i + 0.5) / 10
        C.decal("a1_fountain", hw.circle(0.16, 8), (fx + math.cos(a) * 1.1, fy + math.sin(a) * 1.1, 0.52), (0, 0, 1),
                up=(0, 1, 0), lift=0.014)
    for vy in (9.2, 10.2):
        C.rect("a1_vend_lit", (21.5 - 0.3, vy, 1.0), (-1, 0, 0), 0.66, 0.66, lift=0.034)   # 진열창 유리(0.022)보다 1.2 cm 앞


def lamp_pools():
    for d, x, y in POOLS:
        C.group(G(d))
        z = ground_z(x, y)
        C.decal("a1_pool", hw.circle(2.7, 18), (x, y, z), (0, 0, 1), up=(0, 1, 0), lift=0.045)


cityhall_lights()
plaza_lights()
light_windows()
split_glow()
lamp_pools()
screens_on()
for i, (d, delay) in enumerate(ORDER):
    C.group_props[G(d)] = {"glow": 1, "district": d, "order": i, "delay": delay}

# GLOW_monorail_train은 열차와 함께 움직여야 하므로 MONORAIL_train 노드 아래로 옮긴다 (finish 안의 export 직전)
_export = cb.export


def _export_nested(rel_path, *, props=None, root=None):
    t, p = bpy.data.objects.get(G("monorail_train")), bpy.data.objects.get("MONORAIL_train")
    if t and p:
        t.parent = p
    return _export(rel_path, props=props, root=root)


cb.export = _export_nested

C.group("city")
ROOT = {
    "sky": "#c9a08a",           # 전장의 연기 낀 붉은 해 질 녘
    "fog": "70,560",
    "sun": "-0.85,0.3,0.25",    # 서남서의 낮은 해 (three.js 기준 빛이 오는 방향)
    "sunColor": "#ffb890",
    "sunIntensity": 1.05,
    "ambient": 0.78,
    "hemiSky": "#c4abae",
    "hemiGround": "#463a44",
    "near": 0.1,
    "far": 900,
    "physics": 0,
    "timeOfDay": "dusk_dday",
    "scene": "ACT1_CITYHALL",
    "shots": "heidi_a,heidi_b,heidi_c,pov_rita,drones_fall,vehicles_stall,blackout_hall,blackout_wide",
    "scenes": "heidi,blackout",
    "blackout": ",".join(G(d) for d, _ in ORDER),            # 「정전」에서 끄는 순서 (act1_overview와 같은 키)
    "blackoutDelay": ",".join(f"{t:g}" for _, t in ORDER),   # 제안 시각(초): 같은 순서의 노드를 숨기는 때
}
C.finish("levels/act1_cityhall.glb", root_props=ROOT, outline=0.025)
