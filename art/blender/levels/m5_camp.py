"""2막 M5 「수용소」 (+ M6 초반): 모나티엄 동쪽 공장 지대의 R41 수용소 (밤). 한 줄기 동선(레일슈터)으로 짠 레벨.

npm run model -- art/blender/levels/m5_camp.py   → public/models/levels/m5_camp.glb

원작: 엘레나·아멜리아·로네가 수용소에 갇혀 있다. 원래의 뮤트가 순찰 주기가 길어진 틈에 접근한다.
오리지널: 정전으로 수용소는 디젤 발전기(투광등·탐조등)와 유선 야전 전화로 돌아간다. 리타가 남서쪽 전화 분선함을 끊고
서쪽 발전기를 세우면 순찰이 걸어서 확인하러 나가야 한다(= 길어진 순찰 주기). 뮤트가 북서쪽 철조망 틈으로 들어가 엘레나와 아멜리아를
데리고 나오고, 로네가 돈까스 접시를 들고 뒤따른다. M6 초반은 같은 레벨에서 경보가 울린 수용소 북쪽 띠를 쓸고 북문을 뚫는다.
문서: docs/art/r41-camp.md, 미션: src/game/missions/m5.ts, m6.ts

동선 (한 줄기, 갈래는 짧게 갈라졌다 다시 합친다):
  감시 언덕(남쪽 공장 안마당) → 무너진 벽이 덮은 철조망 구멍 → 남쪽 순찰로(W1 탐조등, 순찰 A) → 남서 모서리 전화 분선함
  → 서쪽 순찰로(W2 탐조등, 순찰 B. 배관 밑 기기 / 철망 쪽 길) → 발전기 진지(W3 탐조등, 경비) → 북서 집합 지점(철망 틈)
  → (M6) 틈 → 수용소 북쪽 띠: 앞마당 → B동(둘레 두 길 + 안) → 식당 천막·보급 상자 → 북문
막는 것: 3겹 윤형 철조망(공장 벽 밑), 수용소 철망, 컨테이너 차단선, 막사·컨테이너로 이은 안쪽 담, 잠긴 안쪽 문, 무너진 공장.
좌표 (Blender, m): 원점 = 수용소 마당 가운데. 울타리 x −34..34, y −30..40. 남문 (0,−30), 북문 (20,40), 북서 틈 (−34, 27..31).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import monatium_ruins_kit as rk  # noqa: E402
import r41_camp_kit as ck  # noqa: E402
import battlefield_kit as bk  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
C = mk.City("m5_camp")
CARBINE = "r41_carbine"
SQ = {k: f"characters/squad_{k}.glb" for k in ("sabre", "rona", "jesty", "karen")}
# 이야기 인물 모델 (한곳에: 로네는 본편용 '로네(시장)' 모델로 바뀔 수 있다)
STORY_MODEL = {"elena": "characters/elena.glb", "amelia": "characters/amelia.glb", "rone": "characters/rone.glb", "mute": "characters/mute.glb"}

GAP_Y = 29.0          # 북서 철망 틈 가운데 (y 27..31)
WG = (-14.2, -10.4)   # 서쪽 쪽문 (수용소 서쪽 철망, y)
NG_X = 20.0           # 북문 가운데 (x 16.5..23.5)
BELT_X = -50.5        # 서쪽 철조망 띠 가운데 (공장 벽 밑)
BELT_Y = -45.8        # 남쪽 철조망 띠 가운데
BREACH = (-20.6, -15.4)   # 무너진 벽이 철조망을 덮은 구멍 (x)


# ================================================================== 레벨 전용 모듈

def coil_row(p0, p1, *, r=0.36, z=0.0, pitch=0.8, seed=0, stakes=True):
    """윤형 철조망 한 줄 (기운 다섯모 고리 + 위 두 가닥 + 말뚝). 충돌은 belt가 한꺼번에 넣는다."""
    rng = random.Random(seed)
    P0, P1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
    d = P1 - P0
    L = d.length
    t = d.normalized()
    s_ = Vector((-t.y, t.x, 0))
    b = C.bm("wire", "fine")
    n = max(2, int(L / pitch))
    for k in range(n + 1):
        q = P0 + d * (k / n)
        tilt = 0.35 if k % 2 else -0.35
        ring = []
        for i in range(5):
            a = 2 * math.pi * i / 5 + rng.uniform(-0.15, 0.15)
            u, v = math.cos(a) * r, math.sin(a) * r
            ring.append(q + s_ * u + t * (v * tilt) + Vector((0, 0, z + r + 0.02 + v)))
        for i in range(5):
            a_, c_ = ring[i], ring[(i + 1) % 5]
            w = t * 0.012
            vs = [b.verts.new(a_ - w), b.verts.new(c_ - w), b.verts.new(c_ + w), b.verts.new(a_ + w)]
            b.faces.new(vs)
    zz = z + 2 * r + 0.02
    for off in (-0.12, 0.12):
        qa, qb = P0 + s_ * off, P1 + s_ * off
        C.strip("wire", (qa.x, qa.y, zz), (qb.x, qb.y, zz), 0.014, normal=s_, lift=0.0)
    if stakes:
        m = max(1, int(L / 4.0))
        for k in range(m + 1):
            q = P0 + d * (k / m)
            C.beam("stake", (q.x, q.y, -0.1), (q.x, q.y, z + 2 * r + 0.15), 0.05, 0.05, kind="detail")


def belt(p0, p1, *, seed=0, sides=(1,)):
    """철조망 겹벽: 3겹 윤형 철조망(아래 두 줄 + 위 한 줄, 높이 약 1.35 m, 너비 1.56 m) + 걸을 수 있는 쪽 면에 낮은 철망(1.35 m).
    축 정렬. COL은 띠 모양 그대로 1.35 m 상자이고, 낮은 철망이 그 면에 서 있다 (막힌 자리가 보인다).
    sides: 낮은 철망을 세울 쪽 (+1 = p0→p1 진행 방향의 왼쪽)."""
    a, b = Vector((p0[0], p0[1])), Vector((p1[0], p1[1]))
    t = (b - a).normalized()
    s = Vector((-t.y, t.x))
    for sd in sides:
        o = s * (0.8 * sd)
        ck.fence_run(C, tuple(a + o), tuple(b + o), h=1.35, pitch=3.2, col=False, coil=False)
    for k, off in enumerate((-0.42, 0.42)):
        coil_row(tuple(a + s * off), tuple(b + s * off), seed=seed + k)
    coil_row(tuple(a), tuple(b), z=0.6, pitch=1.0, seed=seed + 5, stakes=False)
    x0, x1 = sorted((a.x, b.x))
    y0, y1 = sorted((a.y, b.y))
    if abs(t.x) > abs(t.y):
        C.col(x0, x1, y0 - 0.8, y1 + 0.8, 0, 1.35)
    else:
        C.col(x0 - 0.8, x1 + 0.8, y0, y1, 0, 1.35)


def ruin(x0, x1, y0, y1, *, h=6.0, seed=0, faces=(), teeth=4, chimney=False):
    """경계 공장 (톱니 지붕 통짜 블록, COL은 factory_shed). faces: 동선 쪽 면에 깨진 창 (그을음 데칼은 머티리얼 하나를 더 그려서 뺐다)."""
    mk.factory_shed(C, x0, x1, y0, y1, h=h, teeth=teeth, chimney=chimney, seed=seed)
    rng = random.Random(seed)
    for f in faces:
        N = mk.FRONT[f]
        horiz = f in ("-y", "+y")
        a0, a1 = (x0, x1) if horiz else (y0, y1)
        c = (y0 if f == "-y" else y1) if horiz else (x0 if f == "-x" else x1)
        k = a0 + 2.0
        while k < a1 - 1.5:
            # 남쪽(−y) 면은 factory_shed가 h×0.6 높이에 창을 낸다: 그 줄과 겹치지 않게 아래 줄만
            for z in ((2.0, 4.3) if h > 5 and f != "-y" else (2.0,)):
                p = Vector((k, c, z)) if horiz else Vector((c, k, z))
                C.rect("char" if rng.random() < 0.6 else "glass_d", tuple(p), tuple(N), 1.3, 0.9, lift=0.02)
            k += rng.uniform(2.8, 3.6)


def barrier_line(x0, y0, x1, y1, *, w=1.8):
    """R41 모따기 차단벽 줄 (높이 0.95 m, 끝과 끝을 붙여 세운다)."""
    a, b = Vector((x0, y0)), Vector((x1, y1))
    L = (b - a).length
    n = max(1, round(L / w))
    yaw = math.degrees(math.atan2(b.y - a.y, b.x - a.x))
    for i in range(n):
        p = a.lerp(b, (i + 0.5) / n)
        bk.r41_barrier(C, p.x, p.y, 0, yaw=yaw, w=L / n - 0.04)


def cable_reel(x, y, *, yaw=0.0):
    """나무 케이블 드럼 (누운 원통, 엄폐물 높이 1.2 m)."""
    a = math.radians(yaw)
    ax = Vector((math.cos(a), math.sin(a), 0)) * 0.45
    c = Vector((x, y, 0.6))
    C.cyl("wood_d", tuple(c - ax), tuple(c - ax * 0.8), 0.6, segs=14)
    C.cyl("wood_d", tuple(c + ax * 0.8), tuple(c + ax), 0.6, segs=14)
    C.cyl("cable", tuple(c - ax * 0.8), tuple(c + ax * 0.8), 0.46, segs=14)
    rk.col_cyl(C, tuple(c - ax), tuple(c + ax), 0.6, segs=14)


def pipe_rack(x0, x1, y):
    """공장 배관 다리: 굵은 관 둘(밑면 1.0 m) + H 받침 둘. 앉아서 기어 지나간다 (선 키 1.2 m는 걸림)."""
    for dy in (-0.3, 0.3):
        C.cyl("r41_light", (x0, y + dy, 1.24), (x1, y + dy, 1.24), 0.24, segs=12)
        for x in (x0 + 0.15, x1 - 0.15):
            C.cyl("rebar", (x - 0.06, y + dy, 1.24), (x + 0.06, y + dy, 1.24), 0.29, segs=12, kind="detail")
    C.col(x0, x1, y - 0.56, y + 0.56, 0.98, 1.5)
    for x in (x0 + 0.25, x1 - 0.25):
        for dy in (-0.62, 0.62):
            C.box("fence_post", x - 0.07, x + 0.07, y + dy - 0.07, y + dy + 0.07, 0, 1.62, col=True)
        C.box("fence_post", x - 0.07, x + 0.07, y - 0.7, y + 0.7, 1.5, 1.62)
    # 잘린 끝 (동쪽): 플랜지와 녹 자국
    C.cyl("rebar", (x1, y - 0.3, 1.24), (x1 + 0.04, y - 0.3, 1.24), 0.3, segs=12, kind="detail")
    C.cyl("rebar", (x1, y + 0.3, 1.24), (x1 + 0.04, y + 0.3, 1.24), 0.3, segs=12, kind="detail")
    C.cyl("char", (x1 + 0.041, y - 0.3, 1.24), (x1 + 0.05, y - 0.3, 1.24), 0.19, segs=12, kind="fine")
    C.cyl("char", (x1 + 0.041, y + 0.3, 1.24), (x1 + 0.05, y + 0.3, 1.24), 0.19, segs=12, kind="fine")
    ck.sign(C, x1 + 0.7, y - 1.4, "낮은 배관 · 머리 조심", "LOW PIPE · MIND YOUR HEAD", face=(0, -1), h=1.3)


def tarp_shelter(x0, x1, y0, y1, *, h=2.5):
    """발전기 위 차양 (기둥 넷 + 방수포 지붕)."""
    for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        C.cyl("fence_post", (x, y, 0), (x, y, h), 0.06, segs=6)
        C.col(x - 0.07, x + 0.07, y - 0.07, y + 0.07, 0, h)
    C.prism("tarp_o", [(x0 - 0.3, y0 - 0.3), (x1 + 0.3, y0 - 0.3), (x1 + 0.3, y1 + 0.3), (x0 - 0.3, y1 + 0.3)],
            h, h + 0.06, bottom=True)
    C.box("tarp_o", (x0 + x1) / 2 - 0.15, (x0 + x1) / 2 + 0.15, y0 - 0.3, y1 + 0.3, h + 0.06, h + 0.3)


def container(cx, cy, *, axis="x", z=0.0, door="+y", label="R41-07", seed=0):
    bk.r41_container(C, cx, cy, z, axis=axis, door=door, seed=seed, label=label)


# ================================================================== 바닥
C.group("ground")
C.box("ash", -90, 90, -95, 75, -0.6, 0.0)
C.col(-90, 90, -95, 75, -0.6, 0.0)
C.box("asphalt", -36, 36, -32, 42, 0.0, 0.02, kind="detail")        # 수용소 마당 (콘크리트 바닥 위 아스팔트)
# 순찰로: 남쪽(남문 앞 → 동쪽 길) · 서쪽(철조망 띠 안). 북쪽 길은 북문 밖 (M6 다음 레벨로)
for (x0, x1, y0, y1) in [(-46, 44, -42, -35), (-46, -39, -35, 44), (36, 44, -35, 52), (-24, 44, 44, 52)]:
    C.box("pave_d", x0, x1, y0, y1, 0.0, 0.015, kind="detail")

# ================================================================== 수용소 철망·문
C.group("fence")
corners = [(-34, -30), (34, -30), (34, 40), (-34, 40)]
gaps = [(0, (34 - 3) / 68, (34 + 3) / 68),
        (2, (34 - (NG_X + 3.5)) / 68, (34 - (NG_X - 3.5)) / 68),
        (3, (40 - (GAP_Y + 2)) / 70, (40 - (GAP_Y - 2)) / 70),
        (3, (40 - WG[1]) / 70, (40 - WG[0]) / 70)]
ck.fence_loop(C, corners, gaps=gaps)
ck.gate_posts(C, 0, -30, 6.4)
# 정문 간판 뒷면 (마당 안에서 본다): 앞면은 「외래종 수용소」
C.rect("r41_band", (0, -29.91, 3.2 - 0.62), (0, 1, 0), 6.4 - 0.3, 0.08, lift=0.01)
ck.paint_text(C, "white", "정문", 0.34, (0, -29.91, 3.2 - 0.32), (0, 1, 0), lift=0.012)
ck.paint_text(C, "r41_band", "MAIN GATE · 남쪽", 0.14, (0, -29.91, 3.2 - 0.5), (0, 1, 0), lift=0.012)
# 정문: 철창 미닫이 문 (안쪽에서 동쪽으로 열린다) + 바깥 차단기. 요란하게(M5)면 험비가 들이받아 날린다 (m5.ts)
def _gate_bars(b):
    for (x0, x1, z0, z1) in [(-3.0, 3.0, 0.05, 0.17), (-3.0, 3.0, 2.28, 2.4), (-3.0, -2.88, 0.05, 2.4), (2.88, 3.0, 0.05, 2.4),
                             (-3.0, 3.0, 1.15, 1.25)]:
        mk._bm_box(b, x0, x1, -29.8, -29.68, z0, z1)
    for k in range(1, 24):
        x = -3.0 + k * 0.25
        mk._bm_box(b, x - 0.025, x + 0.025, -29.77, -29.71, 0.17, 2.28)
C.special("DOOR_main_gate", _gate_bars, "r41_shell", {"move": "6.2,0,0"})
C.box("fence_post", 3.5, 3.72, -31.75, -31.53, 0, 1.15, col=True)
rk.door(C, "gate_arm", -2.9, 3.5, -31.7, -31.58, 0.98, 1.1, key="r41_band", move="0,1.6,0")     # 차단기 (올라간다)
ck.gate_posts(C, -34, (WG[0] + WG[1]) / 2, WG[1] - WG[0], axis="y", sign=None)
# 서쪽 쪽문: 남쪽 마당 → 서쪽 순찰로 (평소 잠김. 요란하게면 제스티가 폭약으로 연다)
rk.door(C, "west_gate", -33.82, -33.7, WG[0] + 0.1, WG[1] - 0.1, 0.05, 2.4, key="r41_grey", move=f"0,0,{-(WG[1] - WG[0])}")
# 문 표지 (2026-11-05 사용자: 어느 문인지 표기): 목표 「서쪽 쪽문」과 같은 이름. 기둥 사이 가로판(양면), 북쪽 기둥에서 마당 쪽으로
# 내민 판(북쪽 길 = 하차 자리에서 내려오는 길에서 읽힌다), 수용 구역 북서 모서리 길목의 방향 표지
WEST_GATE_SIGN = [("서쪽 쪽문", 0.42, "white"), ("WEST GATE", 0.15, "r41_band")]
ck.gate_label(C, -34, (WG[0] + WG[1]) / 2, WG[1] - WG[0], WEST_GATE_SIGN, axis="y")
ck.blade_label(C, -34, WG[1], 1.9, (1, 0), [("서쪽 쪽문", 0.32, "white"), ("WEST GATE", 0.12, "r41_band")])
ck.post_label(C, -28.4, 4.6, (1, 0), [("← 서쪽 쪽문", 0.3, "white"), ("WEST GATE", 0.12, "r41_band")], h=1.45)
ck.gate_posts(C, NG_X, 40, 7.4, h=4.0, sign=None)      # 문(2.8 m) 위에 표지판이 들어가게 높은 기둥 (m6_route 북문과 같다)
NORTH_GATE_SIGN = [("북문", 0.8, "white"), ("NORTH GATE", 0.17, "r41_band")]
ck.gate_label(C, NG_X, 40, 7.4, NORTH_GATE_SIGN, h=4.0)
rk.door(C, "north_gate", NG_X - 3.5, NG_X + 3.5, 39.85, 40.15, 0.05, 2.8, key="r41_grey", move="7.2,0,0")
# 북서 모서리: 철망이 무너진 공장 벽까지 이어진다 (철망 밖 북쪽 길로 새지 않게)
ck.fence_run(C, (-34, 40), (-34, 46.3))
# 찢긴 철망: 벗겨져 바닥에 늘어진 판
C.rbox("mesh_a", (-35.2, GAP_Y, 0.3), (1.2, 3.6, 0.04), (0, 18, 6))
C.rbox("steel", (-34.9, GAP_Y + 2.1, 1.3), (0.05, 0.05, 2.6), (0, -22, 0), kind="detail")
# 남문 초소: 안에 근무 책상(야전 전화 = 남쪽 전봇대 줄의 끝, 근무 일지, 남포등), 의자, 총가, 열쇠함, 기름통
R = ck.barrack(C, -11, -6.5, -28.5, -25, h=2.4, doors=[("+x", -26.8, 1.0)], windows=True, inner=True)
ck.door_label(C, -6.5, -26.8, "+x", [("정문 초소", 0.2, "r41_light")], roof_h=2.4)
top = ck.desk(R, "-x", -27.55, -25.95, d=0.6)
ck.field_phone(C, -10.62, -26.25, top.z, face=(1, 0))
C.box("paper", -10.75, -10.47, -27.0, -26.62, top.z, top.z + 0.012, kind="detail")          # 근무 일지
ck.lantern(C, "gatehut", -10.62, -27.3, z=top.z, light=0.32)
ck.chair(C, -10.12, -26.75, face=(-1, 0))
ck.rifle_rack(R, "+y", -9.75, -8.55, n=3)
R.wbox("olive_d", "-y", -10.25, -9.85, 0.0, 0.06, 1.15, 1.5, kind="detail")                 # 열쇠함
ck.notice(R, "+y", -10.35, 1.5, [("근무표", 0.05), ("DUTY ROSTER", 0.025)], w=0.36)
ck.jerrycans(R, "-y", -6.59 - 3 * 0.18, 3)
# 전화선: 천장 밑 북쪽 벽을 따라 서쪽 벽 모서리로, 책상 북쪽 끝에서 곧게 내려와 전화기로
for (a, b) in [((-6.62, -25.13, 2.3), (-10.87, -25.13, 2.3)), ((-10.87, -25.13, 2.3), (-10.87, -25.9, 2.3)),
               ((-10.87, -25.9, 2.3), (-10.87, -25.9, top.z + 0.05)), ((-10.87, -25.9, top.z + 0.05), (-10.72, -26.15, top.z + 0.08))]:
    ck.wire(C, a, b, sag=0.0, segs=1)
for (x, y, a) in [(-4.5, -29, 0), (4.5, -29, 0)]:
    mk.sandbag_wall(C, x, y, yaw=a, n=3, rows=3)

# ================================================================== 남쪽 마당 (M5 철망 너머로 보이는 곳. 플레이어는 들어가지 않는다)
C.group("yard")
# 수용 구역 (안쪽 철망 + 천막·침상). 철망은 모두 fence 묶음으로 (같은 머티리얼끼리 한 메시)
C.group("fence")
ck.fence_loop(C, [(-27, -17), (-13, -17), (-13, 3), (-27, 3)], gaps=[(0, 0.42, 0.58)], h=2.2)
ck.fence_run(C, (-33.8, 19), (-20.3, 19))
ck.fence_run(C, (26, 19), (33.8, 19))
C.group("yard")
for i, (x, y) in enumerate([(-23.5, -12.5), (-17, -12.5), (-23.5, -5.5), (-17, -5.5)]):
    ck.tent_open(C, x, y, yaw=0, w=2.6, d=3.2, h=1.9, key="canvas_r", seed=i)        # 앞자락을 걷은 천막: 서서 들어가 침상 둘
for (x, y) in [(-23.5, 0.6), (-17.5, 0.6)]:
    ck.bunk(C, x, y, yaw=0)
# 현장 지휘소 (장교): 서쪽 벽 배치도 + 작전 탁자(종이 지도, 매단 남포등), 장교 책상(죽은 무전기 「먹통」, 야전 전화), 서류함,
# 장교 야전 침대, 총가, 외투 걸이. 경비 in_b가 서는 자리(−6, −17.5)와 문 → 방 가운데 통로는 비운다
R = ck.barrack(C, -10, -2, -24, -16, h=2.6, doors=[("+x", -20, 1.2)], inner=True)
ck.sign(C, -1.2, -15.2, "현장 지휘소", "FIELD OFFICE", face=(1, 0))
ck.door_label(C, -2, -20, "+x", [("지휘소", 0.24, "r41_light"), ("동쪽 출입구", 0.15, "r41_band")])
ck.map_board(R, "-x", -20.0, w=2.3, h=1.15, z0=0.85, title="수용소 배치도 · CAMP R41-E", seed=3)
ck.table(C, -8.6, -7.2, -21.0, -19.0)
C.box("paper", -8.45, -7.35, -20.75, -19.25, 0.62, 0.626, kind="detail")                    # 탁자 위 지도
for (px, py) in [(-8.1, -20.3), (-7.7, -19.6), (-7.9, -20.55)]:
    C.cyl("pin", (px, py, 0.626), (px, py, 0.66), 0.012, segs=6, kind="detail")
C.strip("ink", (-8.35, -20.6, 0.627), (-7.45, -19.4, 0.627), 0.01, lift=0.001)
ck.lantern(C, "office", -7.9, -20.0, hang=2.6 - 0.04, light=0.5)
ck.stool(C, -7.9, -21.17)
ck.stool(C, -7.9, -18.83)
top = ck.desk(R, "-y", -5.2, -3.6, d=0.65)
ck.dead_radio(C, -4.82, -23.62, top.z, face=(0, 1))
ck.field_phone(C, -3.95, -23.58, top.z, face=(0, 1))
C.box("paper", -4.45, -4.15, -23.45, -23.25, top.z, top.z + 0.02, kind="detail")
ck.chair(C, -4.4, -23.07, face=(0, -1))
R.wbox("r41_metal", "-y", -9.91, -8.91, 0.0, 0.5, 0.0, 1.25, col=True)                     # 서류함 둘
for k in range(2):
    for j in range(3):
        R.wbox("steel", "-y", -9.66 + k * 0.5 - 0.08, -9.66 + k * 0.5 + 0.08, 0.5, 0.52, 0.3 + j * 0.38, 0.33 + j * 0.38,
               kind="detail")
ck.cot(C, -9.11, -16.39, yaw=90, L=1.6, W=0.6, h=0.4)
ck.rifle_rack(R, "+y", -3.95, -2.75, n=4)
ck.coat_hooks(R, "+y", -7.3, -5.9, seed=2)
ck.notice(R, "-y", -6.3, 1.5, [("점호 05:30 · 21:00", 0.045), ("ROLL CALL", 0.025)])
# 막사 C (동쪽): 2층 침상 여섯(남북 벽에 머리, 발치마다 관물 상자), 동쪽 벽 사물함, 난로, 탁자와 벤치, 총가, 방화 양동이
R = ck.barrack(C, 20, 32, -22, -12, h=2.6, doors=[("-x", -17, 1.2)], inner=True)
ck.door_label(C, 20, -17, "-x", [("C동 막사", 0.24, "r41_light"), ("서쪽 출입구", 0.15, "r41_band")])
for bx in (23.0, 26.0, 29.0):
    ck.bunk(C, bx, -12.09 - 0.82, yaw=-90, bedding=True)          # 머리(베개)는 벽 쪽
    ck.footlocker(C, bx, -13.73 - 0.18, face=(0, -1))
    ck.bunk(C, bx, -21.91 + 0.82, yaw=90, bedding=True)
    ck.footlocker(C, bx, -20.27 + 0.18, face=(0, 1))
ck.lockers(R, "+x", -18.4, 6, h=1.24, seed=4)
ck.stove(C, 27.2, -17.0, ceil=2.6 - 0.04)
ck.table(C, 28.7, 30.3, -17.45, -16.55)
ck.bench_pair(C, 28.7, 30.3, -17.45, -16.55, axis="x")
for (cx_, cy_) in [(29.0, -17.2), (29.9, -16.8)]:
    C.cyl("tin", (cx_, cy_, 0.62), (cx_, cy_, 0.7), 0.04, segs=8, kind="detail")              # 반합 컵
C.box("paper", 29.35, 29.6, -17.1, -16.9, 0.62, 0.625, kind="detail")                         # 카드 패
ck.lantern(C, "barrack_c", 26.2, -17.0, hang=2.6 - 0.04, light=0.55)
ck.rifle_rack(R, "-x", -15.6, -14.4, n=5)
ck.bucket(C, 20.09 + 0.16, -18.6, water=False, key="pin")
ck.coat_hooks(R, "-x", -21.8, -20.9, seed=5)
ck.notice(R, "-x", -15.0, 1.55, [("C동 내무 규칙", 0.045), ("소등 22:00", 0.035)])
for i, (x, y, st) in enumerate([(-4, 2, 2), (4, 6, 1), (13, 6.5, 1), (8, -10, 1), (16, -24, 2), (24, -2, 1), (-20, -24, 1)]):
    ck.r41_crate(C, x, y, s=0.75, yaw=(i * 37) % 90, stack=st)
for (x, y) in [(28, -26), (29, -24.8), (30, 8), (-8, -6)]:
    ck.drum(C, x, y)

# ================================================================== 수용소 북쪽 띠 (M6 전장): 남쪽 담 = 철망 + 막사 A + 컨테이너 + 보급창 + 안쪽 문
C.group("yard")
# 막사 A (문은 남쪽 마당으로): 2층 침상 넷(북쪽 벽 둘 + 양 끝 벽 하나씩), 관물 상자, 가운데 난로, 남쪽 벽 사물함, 탁자와 벤치, 총가.
# 요란하게(M5)의 마당 보충 병력이 진입점 ENTRY_loud_a_01(−14, 15.5)에서 나와 문으로 뛰어나간다: 문 ~ 진입점 ~ 난로 앞은 비운다
R = ck.barrack(C, -20, -8, 12, 19, h=2.6, doors=[("-y", -14, 1.2)], inner=True)
ck.door_label(C, -14, 12, "-y", [("A동 막사", 0.24, "r41_light"), ("남쪽 출입구", 0.15, "r41_band")])
ck.wall_paint(C, -14, 19, "+y", "A동", 0.7, 2.2)          # 북쪽 띠(M6)에서 보이는 뒷벽
for bx in (-17.0, -11.0):
    ck.bunk(C, bx, 18.91 - 0.82, yaw=-90, bedding=True)
    ck.footlocker(C, bx, 17.27 - 0.18, face=(0, -1))
ck.bunk(C, -19.91 + 0.37, 15.42, yaw=90, bedding=True)
ck.bunk(C, -8.09 - 0.37, 15.42, yaw=-90, bedding=True)
ck.stove(C, -14.0, 17.9, ceil=2.6 - 0.04)
ck.lockers(R, "-y", -19.91, 6, h=1.24, seed=1)
ck.table(C, -11.8, -10.2, 13.6, 14.5)
ck.bench_pair(C, -11.8, -10.2, 13.6, 14.5, axis="x")
C.cyl("tin", (-11.3, 14.1, 0.62), (-11.3, 14.1, 0.7), 0.04, segs=8, kind="detail")
C.box("r41_shell", -10.75, -10.45, 13.85, 14.05, 0.62, 0.66, kind="detail")                   # 탄창 주머니
ck.rifle_rack(R, "-y", -8.09 - 1.2, -8.09, n=4)
ck.lantern(C, "barrack_a", -14.0, 15.0, hang=2.6 - 0.04, light=0.5)
ck.notice(R, "+x", 12.7, 1.5, [("A동 내무 규칙", 0.045), ("소등 22:00", 0.035)])
container(-5.15, 18.0, door="-y", label="R41-11", seed=1)
container(0.45, 18.0, door="-y", label="R41-12", seed=2)
container(-5.15, 18.0, z=2.64, door=None, label="R41-14", seed=3)
# 보급창: 북쪽 벽·양 끝 벽 철제 선반(상자·자루·탄통), 깔판 위 상자 더미 둘과 자루 더미, 출납 책상(장부·남포등), 기름통 줄.
# 보충 병력 진입점 ENTRY_loud_a_02(9, 15.5)와 문 사이(x 8.4..9.6), 선반 사이 가운데 칸(x 8..10)은 비운다
R = ck.barrack(C, 3.3, 15, 12, 19, h=2.6, doors=[("-y", 9, 1.2)], inner=True)
ck.door_label(C, 9, 12, "-y", [("보급창", 0.24, "r41_light"), ("남쪽 출입구", 0.15, "r41_band")])
ck.wall_paint(C, 8, 19, "+y", "보급창", 0.6, 2.2)
ck.shelf_run(R, "+y", 3.39, 8.0, seed=11)
ck.shelf_run(R, "+y", 10.0, 14.91, seed=12)
ck.shelf_run(R, "-x", 14.3, 16.7, seed=13)
ck.shelf_run(R, "+x", 14.3, 16.7, seed=14)
ck.pallet_stack(C, 6.0, 15.4)
ck.pallet_stack(C, 12.0, 15.4, axis="y")
ck.pallet_stack(C, 6.0, 13.6, layers=1, sacks=True)
top = ck.desk(R, "-y", 10.6, 12.0, d=0.6)
C.box("paper", 11.0, 11.4, 12.25, 12.55, top.z, top.z + 0.03, kind="detail")                # 장부
ck.lantern(C, "depot_desk", 11.75, 12.4, z=top.z, light=0)
ck.chair(C, 11.3, 12.69 + 0.19, face=(0, -1))
ck.notice(R, "-y", 11.3, 1.05, [("출납 · ISSUE LOG", 0.04), ("서명 없이 반출 금지", 0.03)], w=0.46)
ck.jerrycans(R, "-y", 6.6, 5)
ck.lantern(C, "depot", 9.0, 15.8, hang=2.6 - 0.04, light=0.55)
container(17.8, 18.0, door="-y", label="R41-20", seed=4)
# 안쪽 문 (북쪽 띠 ↔ 남쪽 마당): 평소 잠김. M5 순찰 교대 때만 잠깐 열린다
ck.gate_posts(C, 23.3, 19, 5.4, sign=None)
rk.door(C, "yard_gate", 20.8, 25.8, 19.25, 19.45, 0.05, 2.4, key="r41_grey", move="5.0,0,0")
ck.sign(C, 27.0, 20.3, "안쪽 문 · 관계자 외 출입 금지", "INNER GATE · STAFF ONLY", face=(0, 1))
ck.gate_label(C, 23.3, 19, 5.4, [("안쪽 문", 0.42, "white"), ("INNER GATE", 0.13, "r41_band")])

# 앞마당 (틈 안쪽): 감시탑 W3, 드럼통 불, 포로 천막
for i, (x, y) in enumerate([(-28.0, 37.0), (-24.0, 37.3)]):
    ck.tent_open(C, x, y, yaw=0, w=2.6, d=3.2, h=1.9, key="canvas_r", seed=10 + i)
# B동 (엘레나·아멜리아·로네): 서쪽 뒷문(틈 쪽) + 동쪽 정문. 문짝은 미닫이(벽 안팎 면을 미끄러진다)라 문틀·창턱을 내지 않는다
R = ck.barrack(C, -17, -5, 25, 33, h=2.8, doors=[("-x", GAP_Y, 1.2), ("+x", GAP_Y, 1.2)], inner=True, trims=False)
rk.door(C, "hb_back", -17.13, -16.87, GAP_Y - 0.65, GAP_Y + 0.65, 0.0, 2.0, key="r41_grey", move="0,0,-1.3")
rk.door(C, "hb_front", -5.13, -4.87, GAP_Y - 0.65, GAP_Y + 0.65, 0.0, 2.0, key="r41_grey", move="0,0,1.3")
# B동 표지: 문마다 「B동 · ~쪽 출입구」, 북쪽 길·남쪽 골목 쪽 벽에 큰 「B동」 (M6에서 틈으로 들어오면 서쪽 출입구가 정면)
ck.door_label(C, -17, GAP_Y, "-x", [("B동", 0.34, "r41_light"), ("서쪽 출입구", 0.2, "r41_band")], roof_h=2.8)
ck.door_label(C, -5, GAP_Y, "+x", [("B동", 0.34, "r41_light"), ("동쪽 출입구", 0.2, "r41_band")], roof_h=2.8)
ck.wall_paint(C, -11, 33, "+y", "B동", 0.95, 2.3)
ck.wall_paint(C, -11, 25, "-y", "B동", 0.95, 2.3)
for (x, y) in [(-14.5, 31.9), (-8.0, 31.9), (-14.5, 26.1)]:
    ck.bunk(C, x, y, yaw=0, bedding=True)
# 탁자: 판 + 네 다리, COL은 바닥부터 (2026-11-03 floatcheck: 다리 없이 판만 0.55 m에 떠 있었다)
C.box("plywood", -9.6, -7.4, 26.0, 27.0, 0.55, 0.6)
for (lx, ly) in ((-9.48, 26.12), (-7.52, 26.12), (-9.48, 26.88), (-7.52, 26.88)):
    C.box("fence_post", lx - 0.04, lx + 0.04, ly - 0.04, ly + 0.04, 0, 0.55)
C.col(-9.6, -7.4, 26.0, 27.0, 0, 0.6)
# 갇힌 사람의 방: 탁자 위 남포등·양철 접시·물주전자, 걸상, 물 양동이, 요강 양동이, 벽에 긁은 날짜, 수칙 종이.
# 서쪽 문 ↔ 동쪽 문 통로(y 28.4..29.6), 탄약 보급함(−12.81, 30.87), 세 사람 자리는 비운다
ck.lantern(C, "hb", -7.85, 26.5, z=0.6, light=0.45)
C.cyl("tin", (-9.0, 26.45, 0.6), (-9.0, 26.45, 0.62), 0.12, segs=12, kind="detail")
C.cyl("tin", (-8.45, 26.7, 0.6), (-8.45, 26.7, 0.8), 0.07, r2=0.06, segs=10, kind="detail")
ck.stool(C, -8.5, 27.0 + 0.17)
ck.bucket(C, -5.09 - 0.16, 25.09 + 0.16)
ck.bucket(C, -16.91 + 0.16, 32.91 - 0.16, water=False, key="r41_metal")
ck.tally(R, "+y", -16.6, 0.95, n=19)
ck.notice(R, "+x", 25.9, 1.45, [("B동 수용 수칙", 0.045), ("HOLDING RULES", 0.025)])
ck.sign(C, -18.3, 31.8, "외래종 B동", "HOLDING B", face=(-1, 0))
# 식당 천막 (경비 저녁: 돈까스. 모나티엄 커틀릿 하우스에서 노획)
table = ck.mess_tent(C, 0.5, 6.5, 32, 37.5)
# 경비 초소 (북동 구석): 경보 뒤 잔당이 여기서 나온다
# 안: 동쪽 벽 교환대 책상(초소끼리 잇는 야전 전화가 모인다) + 의자, 경계 구역도, 비번 침상, 총가, 탄약 상자, 난로.
# 진입점 ENTRY_camp_a_03(30, 26.6)·camp_b_01(30, 25.2)과 문 사이는 비운다
R = ck.barrack(C, 26.5, 33.6, 22, 30, h=2.6, doors=[("-x", 26, 1.2)], inner=True)
ck.door_label(C, 26.5, 26, "-x", [("경비 초소", 0.24, "r41_light"), ("서쪽 출입구", 0.15, "r41_band")])
top = ck.desk(R, "+x", 25.0, 26.8, d=0.65)
ck.switchboard(C, 33.18, 26.25, top.z, face=(-1, 0))
ck.field_phone(C, 33.2, 25.35, top.z, face=(-1, 0))
ck.chair(C, 32.86 - 0.19, 25.9, face=(1, 0))
ck.wire(C, (33.47, 26.25, 2.5), (33.45, 26.25, top.z + 0.3), sag=0.0, segs=1)              # 교환대로 내려오는 선 묶음 (벽을 따라)
ck.map_board(R, "+y", 30.4, w=1.7, h=1.0, z0=0.9, title="경계 구역도", seed=7)
ck.bunk(C, 26.59 + 0.82, 29.91 - 0.37, yaw=0, bedding=True)
ck.rifle_rack(R, "-y", 28.8, 30.4, n=6)
ck.r41_crate(C, 26.59 + 0.366, 22.09 + 0.306, s=0.6, stack=2)
ck.stove(C, 32.5, 23.3, ceil=2.6 - 0.04)
ck.lantern(C, "guard", 31.4, 26.0, hang=2.6 - 0.04, light=0.5)
ck.notice(R, "-x", 22.9, 1.45, [("근무표", 0.05), ("DUTY ROSTER", 0.025)], w=0.36)
container(29.5, 35.5, axis="y", door="+x", label="R41-31", seed=5)
container(9.0, 22.6, door="+y", label="R41-09", seed=6)
# 북쪽 띠 엄폐 (M6): 상자·모래주머니. COVER_ 마커도 같은 자리
covers = [(-26.5, 27.0, 2), (-22.5, 32.0, 1), (-24.0, 24.2, 1), (-12.0, 21.8, 1), (-7.5, 34.4, 1), (3.5, 28.0, 2),
          (8.5, 35.0, 1), (12.5, 25.5, 2), (18.5, 31.0, 1), (25.0, 34.0, 2)]
for i, (x, y, st) in enumerate(covers):
    ck.r41_crate(C, x, y, s=0.75, yaw=(i * 37) % 90, stack=st)
sandbags = [(-11.0, 36.6, 0), (-1.2, 23.6, 90), (9.5, 29.5, 0), (15.5, 35.2, 0), (22.5, 27.0, 90), (14.5, 38.3, 0)]
for i, (x, y, a) in enumerate(sandbags):
    if i % 2:
        bk.r41_barrier(C, x, y, 0, yaw=a, w=2.4)
    else:
        mk.sandbag_wall(C, x, y, yaw=a, n=4, rows=3)
for (x, y) in [(-6.5, 21.2), (-6.0, 21.9), (31.5, 20.5)]:
    ck.drum(C, x, y)

# ================================================================== 감시탑·투광등 (발전기 전원). 탐조등 셋이 동선의 세 구간을 하나씩 쓴다
C.group("towers")
ck.watchtower(C, "w1", -30, -26, face=(-36, -46))       # 남쪽 순찰로·전화 분선함
ck.watchtower(C, "w2", -30, -6, face=(-48, -12.5))      # 서쪽 순찰로 (배관 다리)
ck.watchtower(C, "w3", -29.5, 21.5, face=(-46, 6))      # 발전기 진지
for i, (x, y, f) in enumerate([(-26, -21, (-38, -34)), (-26, -2.5, (-40, -6)), (-22, 30, (-30, 24)), (12, 37, (6, 28))],
                              start=1):
    ck.flood_pole(C, str(i), x, y, face=f)

# ================================================================== 바깥 동선 (M5): 남쪽·서쪽 순찰로
C.group("outside")
# 3겹 윤형 철조망 띠: 공장 벽 밑을 따라 (구멍 = 무너진 벽 판). 수용소 철망과 같은 묶음(머티리얼이 겹쳐 그리기 호출이 준다)
C.group("fence")
belt((BELT_X, BELT_Y), (BELT_X, 46.3), seed=1, sides=(-1,))
belt((BELT_X, BELT_Y), (BREACH[0], BELT_Y), seed=11, sides=(1,))
ck.fence_run(C, (-28.0, BELT_Y - 0.8), (BREACH[0], BELT_Y - 0.8), h=1.35, pitch=3.2, col=False, coil=False)   # 감시 언덕 쪽 면
belt((BREACH[1], BELT_Y), (-8.6, BELT_Y), seed=21, sides=(1, -1))
for x in (BREACH[0] - 0.06, BREACH[1] + 0.06):      # 끊긴 띠 끝: 낮은 철망으로 마감 (띠 COL 끝면, 말뚝과 겹치지 않게 6 cm 밖)
    ck.fence_run(C, (x, BELT_Y - 0.8), (x, BELT_Y + 0.8), h=1.35, col=False, coil=False)
# 구멍: 북쪽으로 쓰러진 벽 판이 철조망을 눌러 덮었다 (밟고 지나간다, 높이 0.22 m)
C.box("concrete_d", BREACH[0], BREACH[1], -50.0, -43.0, 0.0, 0.22, col=True)
for (x, y) in [(-20.2, -47.0), (-19.0, -44.2), (-16.4, -45.5), (-15.8, -48.6)]:
    C.beam("rebar", (x, y, 0.24), (x + 0.5, y + 0.4, 0.29), 0.035, 0.035, kind="detail")      # 판 위에 누운 철근
for (x, d) in [(BREACH[0], -1), (BREACH[1], 1)]:
    # 눌린 철조망 끝: 판 가장자리 밑으로 낮게 깔린 고리
    C.beam("wire", (x, BELT_Y - 0.5, 0.25), (x + d * 0.6, BELT_Y + 0.4, 0.55), 0.02, 0.02, kind="detail")
C.group("outside")
rk.rubble(C, -21.6, -49.6, r=0.9, h=0.6, seed=81)
rk.rubble(C, -14.2, -50.2, r=0.8, h=0.55, seed=82)

# 남쪽 차단선: 컨테이너 셋이 길을 막고 공장 벽에 박혀 있다 (그 너머 남문 앞은 경비만 다닌다)
container(-7.0, -33.0, axis="y", door=None, label="R41-02", seed=7)
container(-7.0, -38.75, axis="y", door=None, label="R41-03", seed=8)
container(-7.0, -44.4, axis="y", door=None, label="R41-05", seed=9)
container(-7.0, -38.75, axis="y", z=2.64, door=None, label="R41-06", seed=10)
# 동쪽 차단선: 남문 앞 길은 정문 · 남쪽 골목(공장 사이)으로만 이어진다
container(8.5, -33.0, axis="y", door=None, label="R41-21", seed=12)
container(8.5, -38.75, axis="y", door=None, label="R41-22", seed=13)
container(8.5, -44.4, axis="y", door=None, label="R41-23", seed=14)
container(8.5, -33.0, axis="y", z=2.64, door=None, label="R41-24", seed=15)
rk.burnt_car(C, -11.8, -41.4, yaw=55, seed=5)

# 야전 전화: 남문 초소 → 서쪽으로 전봇대 → 남서 모서리 분선함 (−40, −33.5)
poles = [(-4, -33.3), (-14, -33.3), (-24, -33.3), (-33, -33.3), (-40, -33.3)]
tops = [ck.phone_pole(C, x, y) for (x, y) in poles]
for a, b in zip(tops, tops[1:]):
    ck.wire(C, tuple(a), tuple(b), sag=0.35)
ck.junction_box(C, -40, -33.5, face=(0, -1))
ck.wire(C, tuple(tops[-1]), (-40, -33.5, 1.5), sag=0.05, segs=2)
ck.sign(C, -37.8, -35.4, "통신선 · 접근 금지", "FIELD TEL · KEEP OFF", face=(0, -1))
# 남쪽 순찰로 엄폐: 케이블 드럼, 배수관 토막, 상자, 모래주머니, 잔해
cable_reel(-19.0, -37.0, yaw=0)
cable_reel(-30.0, -42.6, yaw=90)
for dx in (0.0, 1.15):
    C.cyl("concrete", (-26.6, -42.4 + dx, 0.55), (-23.4, -42.4 + dx, 0.55), 0.55, segs=14)
    C.cyl("char", (-26.62, -42.4 + dx, 0.55), (-26.6, -42.4 + dx, 0.55), 0.42, segs=14, kind="fine")
    C.cyl("char", (-23.4, -42.4 + dx, 0.55), (-23.38, -42.4 + dx, 0.55), 0.42, segs=14, kind="fine")
    rk.col_cyl(C, (-26.6, -42.4 + dx, 0.55), (-23.4, -42.4 + dx, 0.55), 0.55, segs=14)
for i, (x, y, st) in enumerate([(-44.5, -42.6, 2), (-36.0, -43.4, 1), (-47.3, -33.5, 1), (-33.5, -38.4, 1)]):
    ck.r41_crate(C, x, y, s=0.75, yaw=(i * 29) % 90, stack=st)
mk.sandbag_wall(C, -40.5, -40.2, yaw=0, n=4, rows=3)
rk.rubble(C, -31.0, -36.6, r=1.0, h=0.8, seed=91)
for (x, y) in [(-27.0, -31.3), (-26.3, -31.9)]:
    ck.drum(C, x, y)

# 서쪽 순찰로: 컨테이너 + 배관 다리 칸막이 (배관 밑을 기거나 철망 쪽 밝은 길로)
container(-46.85, -19.0, door="-y", label="R41-17", seed=11)
pipe_rack(-44.05, -38.6, -19.0)
for i, (x, y, st) in enumerate([(-47.6, -24.5, 2), (-39.8, -6.5, 1), (-42.0, -14.0, 1)]):
    ck.r41_crate(C, x, y, s=0.75, yaw=(i * 41) % 90, stack=st)
for (x, y) in [(-46.6, -27.6), (-47.2, -28.2), (-48.6, -3.2), (-48.0, -2.5)]:
    ck.drum(C, x, y)
mk.sandbag_wall(C, -38.2, -25.0, yaw=0, n=3, rows=3)
rk.burnt_car(C, -45.6, -9.0, yaw=100, seed=6)
cable_reel(-40.0, -12.5, yaw=90)

# 발전기 진지: 차단벽 담 둘 (남쪽은 철망 쪽, 북쪽은 철조망 쪽이 트였다) + 차양.
# 북쪽 담은 남쪽 담의 트인 철망 쪽 줄(x −39.7 ~ −38.3)에 맞춰 차단벽 하나 폭(2.6 m)을 빼 둔다: 순찰로를 따라 북쪽 집합 지점으로
# 걸어서 곧게 지나간다 (넘기는 그대로 된다). 예전에는 남쪽 틈 → 발전기 북쪽을 서쪽으로 돌아 → 북쪽 담 서쪽 끝으로 S자로만 지나가서
# 넘지 않으면 북쪽 담 동쪽 끝에 막혔다 (2026-11-04 M5 점검: 넘지 않는 플레이어 312초 막힘, 아군이 플레이어에 붙어 밀었다)
barrier_line(-49.55, 0.5, -39.7, 0.5)
barrier_line(-44.45, 15.5, -40.9, 15.5)
barrier_line(-38.3, 15.5, -34.45, 15.5)
ck.generator(C, -43.0, 8.0, yaw=90)
C.box("concrete_d", -45.4, -40.6, 4.4, 11.6, 0.0, 0.08)
tarp_shelter(-45.0, -41.0, 4.6, 11.4)
for i, (x, y, st) in enumerate([(-48.6, 14.4, 2), (-37.2, 4.2, 1)]):
    ck.r41_crate(C, x, y, s=0.75, yaw=(i * 53) % 90, stack=st)
for (x, y) in [(-36.2, 13.4), (-36.8, 12.8)]:
    ck.drum(C, x, y)
# 발전기 → 철망 → 탑·투광등 케이블 (땅을 기는 굵은 선)
for (a, b) in [((-41.6, 8, 0.05), (-34, 8, 0.05)), ((-34, 8, 0.05), (-29.5, 21.5, 0.05)), ((-34, 8, 0.05), (-30, -6, 0.05)),
               ((-34, 8, 0.05), (-26, -2.5, 0.05)), ((-30, -6, 0.05), (-30, -26, 0.05)), ((-30, -26, 0.05), (-26, -21, 0.05)),
               ((-29.5, 21.5, 0.05), (-22, 30, 0.05))]:
    ck.wire(C, a, b, sag=0.0, segs=2, w=0.05)

# 북서 집합 지점: 무너진 벽 토막 (엘레나 일행이 웅크리는 곳)
C.box("concrete_d", -47.2, -46.2, 18.5, 23.5, 0, 1.1, col=True)
C.box("rubble", -47.25, -46.15, 20.0, 21.6, 1.1, 1.32)
for (x, y) in [(-47.0, 18.7), (-46.4, 23.3)]:
    C.beam("rebar", (x, y, 1.0), (x + 0.1, y + 0.2, 1.6), 0.035, 0.035, kind="detail")
rk.rubble(C, -48.2, 26.6, r=0.9, h=0.8, seed=71)
rk.rubble(C, -42.6, 17.6, r=0.9, h=0.75, seed=72)
ck.r41_crate(C, -38.0, 44.2, s=0.75, yaw=12, stack=1)
ck.drum(C, -47.6, 43.6)

# ================================================================== 남쪽 감시 언덕 (공장 안마당, 분대가 남는다)
C.group("outside")
C.prism("rubble_d", [(-26, -64), (-14, -64), (-14, -54), (-26, -54)], 0, 0.6, kind="main")
C.col(-26, -14, -64, -54, 0, 0.6)
# 북쪽 비탈: 0.1 m 단 6개, COL은 단 코를 잇는 경사판 하나 (27°)
for k in range(6):
    C.box("rubble", -26 + k * 0.1, -14 - k * 0.1, -54.0, -52.8 - 0.2 * k, 0, 0.1 * (k + 1), kind="detail")
C.ccol([(x, y, 0.0) for x in (-26.0, -14.0) for y in (-54.0, -52.6)]
       + [(x, y, 0.6) for x in (-25.3, -14.7) for y in (-54.0, -53.8)])
rk.rubble(C, -26.4, -49.2, r=1.2, h=0.85, seed=41)
rk.rubble(C, -9.6, -52.0, r=1.3, h=0.9, seed=42)
rk.rubble(C, -11.5, -62.5, r=1.1, h=0.85, seed=43)
rk.rubble(C, -27.0, -60.0, r=1.0, h=0.8, seed=44)

# ================================================================== 경계: 무너진 공장들 (동선을 둘러싼 벽, 바깥은 높은 담)
C.group("outside")
ruin(-78, -51.6, -84, -13, h=7.0, seed=11, faces=("+x",))
ruin(-76, -51.8, -14, 17, h=6.5, seed=12, faces=("+x",))
ruin(-74, -51.6, 16, 47, h=6.0, seed=13, faces=("+x",))
ruin(-76, -24, 46.3, 72, h=6.0, seed=14, faces=("-y",), teeth=6)
ruin(-82, -28, -86, -46.6, h=6.0, seed=15, faces=("+y", "+x"), teeth=6)
ruin(-30, 6, -88, -66.2, h=7.0, seed=16, faces=("+y",))
# 남쪽 골목 (x −5..5): 공장 사이로 남문 앞 길까지. 요란하게(M5) 험비가 여기서 정문으로 돌진한다. 남쪽 끝은 막힘
ruin(5, 48, -86, -46.6, h=6.0, seed=17, faces=("-x", "+y"), teeth=6)
ruin(-8, -5, -86, -46.6, h=6.0, seed=22, faces=("-x", "+x"), teeth=1)
C.group("ground")
C.box("asphalt", -4.6, 4.6, -66.2, -46.6, 0.0, 0.02, kind="detail")
C.group("outside")
# 철망 밖 동쪽·북쪽 (경비만 다니는 길 너머)
ruin(52, 88, -46, 40, h=7.0, seed=18, faces=("-x",), teeth=5)
ruin(50, 88, 56, 72, h=8.0, seed=19, faces=("-y",))
ruin(-20, 12, 58, 72, h=7.0, seed=20, faces=("-y",))
ruin(28, 48, 58, 72, h=6.0, seed=21, faces=("-y",))
# 맵 가장자리: 높은 공장 담
for (x0, x1, y0, y1) in [(-92, -88, -95, 75), (88, 92, -95, 75), (-92, 92, -95, -91), (-92, 92, 71, 75)]:
    C.box("concrete_d", x0, x1, y0, y1, 0, 9, col=True)
# 북문 너머 짧은 길 (M6: 다음 레벨 차고로 이어진다)
C.group("ground")
C.box("asphalt", NG_X - 4, NG_X + 4, 40, 66, 0.0, 0.02, kind="detail")
C.group("outside")
C.box("concrete_d", NG_X - 8, NG_X + 8, 66, 67, 0, 4.0, col=True)
ck.sign(C, NG_X + 4.6, 60, "↑ 구 기갑병기 보관고 · 0.3 mi", "OLD ARMOR DEPOT", face=(0, -1))

# 불 (발전기가 꺼져도 남는 빛)
rk.fire_barrel(C, 1, -5.5, -27.5)
rk.fire_barrel(C, 2, -21.0, 23.0)
rk.fire_barrel(C, 3, -12.2, -19.0, rust=True)
rk.fire_barrel(C, 4, 22.0, 4.2)
rk.fire_barrel(C, 5, -25.0, 34.0, rust=True)
rk.fire_barrel(C, 6, 6.8, 30.0)
C.group("skyline")
rk.dark_skyline(C, 0, -10, r=170, n=36, seed=12)
mk.smoke_column(C, -160, 120, h=70, r=7, seed=3, dark=0.6)
mk.sky_moons(C, (120, 280, 150), (-0.35, -0.85, -0.4), r=26)

# ================================================================== 마커
C.group("markers")
C.marker("SPAWN_player", (-20.0, -59.5, 0.6), face=(-24, -20))
C.marker("SPAWN_cycle", (-45.2, 17.2, 0), face=(-42, 26))
C.marker("SPAWN_rally", (-42.0, 22.5, 0), face=(-34, GAP_Y))
C.marker("SPAWN_m6", (-43.0, 27.0, 0), face=(-30, GAP_Y))
C.marker("SPAWN_gate", (NG_X, 32.0, 0), face=(NG_X, 60))
# 요란하게 (M5): 험비를 세워 둔 자리(감시 언덕 동쪽) → 골목 남쪽 끝에서 출발 → 정문을 들이받고 마당에 선다
C.marker("MARK_hv_park", (-13.0, -53.0, 0), face=(-22, -53))
C.marker("MARK_hv_start", (0.0, -63.5, 0), face=(0, -30))
C.marker("MARK_hv_stop", (0.0, -26.0, 0), face=(0, 0))
C.marker("SPAWN_yard", (-2.8, -27.0, 0), face=(-20, -18))
C.marker("SPAWN_push", (-37.5, (WG[0] + WG[1]) / 2, 0), face=(-41, 10))
C.marker("MARK_west_gate", (-31.5, (WG[0] + WG[1]) / 2, 0))
for who, (x, y), face in [("sabre", (-18.3, -58.2), (-24, -20)), ("rona", (-21.6, -57.6), (-28, -20)),
                          ("jesty", (-22.2, -60.6), (-24, -20)), ("karen", (-18.6, -61.2), (-20, -20))]:
    C.marker(f"ALLY_{who}", (x, y, 0.6), face=face, props={"who": who, "behavior": "hold", "model": SQ[who]})
# 상호작용 지점 (리타가 서는 곳)
C.marker("MARK_breach", (-18.0, -45.8, 0.22))
C.marker("MARK_phone", (-40.0, -34.8, 0), face=(-40, -33))
C.marker("MARK_generator", (-41.2, 8.0, 0), face=(-43, 8))
C.marker("MARK_rally", (-42.5, 25.5, 0))
C.marker("MARK_hide", (-48.4, 21.0, 0))                     # M6: 엘레나 일행이 벽 토막 뒤에 웅크린다
C.marker("MARK_fence_gap", (-35.5, GAP_Y, 0))
C.marker("MARK_hb", (-11.0, GAP_Y, 0))
C.marker("MARK_north_gate", (NG_X, 37.0, 0))
C.marker("MARK_mess", (table.x, table.y, 0))


def enemy(eid, xy, kind, group, behavior, face, z=0.0, path=None, spawn=None, weapon=CARBINE):
    p = {"kind": kind, "group": group, "behavior": behavior, "weapon": weapon}
    if path:
        p["path"] = path
    if spawn:
        p["spawn"] = spawn
    C.marker(f"ENEMY_{eid}", (xy[0], xy[1], z), face=face, props=p)


def wps(prefix, pts):
    for i, (x, y) in enumerate(pts, start=1):
        C.marker(f"WP_{prefix}_{i:02d}", (x, y, 0))


# 경비 (밤): 바깥 순찰 둘은 남쪽·서쪽 순찰로를 오간다
s_path = [(-17, -39.5), (-27, -39), (-37, -40.8), (-43, -36), (-43, -27), (-43, -36), (-37, -40.8), (-27, -39)]
w_path = [(-38.0, -3.5), (-44.0, -3.0), (-38.0, -3.5), (-36.6, -13), (-36.6, -24), (-36.6, -13)]
enemy("pat_a", s_path[0], "rifleman_a", "outer", "patrol", (-27, -39), path="patrol_s")
wps("patrol_s", s_path)
enemy("pat_b", w_path[0], "rifleman_b", "outer", "patrol", (-44, -3), path="patrol_w")
wps("patrol_w", w_path)
enemy("gate_a", (-2.4, -32.2), "rifleman_c", "gate", "hold", (-2.4, -50))
enemy("gate_b", (2.4, -32.2), "rifleman_a", "gate", "hold", (2.4, -50))
enemy("tower_w1", (-30, -26), "rifleman_c", "towers", "hold", (-36, -46), z=4.0)
enemy("tower_w2", (-30, -6), "rifleman_c", "towers", "hold", (-48, -12.5), z=4.0)
enemy("tower_w3", (-29.5, 21.5), "rifleman_c", "towers", "hold", (-46, 6), z=4.0)
g_path = [(-47.3, 3.4), (-47.3, 12.6), (-38.6, 12.8), (-38.6, 3.4)]
enemy("gen_a", g_path[0], "rifleman_b", "gen", "patrol", (-47, 12), path="patrol_gen")
wps("patrol_gen", g_path)
# B동 경비: B동 둘레를 돈다
i_path = [(-19.6, 23.0), (-3.0, 23.0), (-3.0, 35.4), (-19.6, 35.4)]
enemy("in_a", i_path[0], "rifleman_a", "inner", "patrol", (-3, 23), path="patrol_inner")
wps("patrol_inner", i_path)
enemy("officer", (-4, -14), "officer", "inner", "hold", (0, 0), weapon="r41_sidearm")
enemy("in_b", (-6, -17.5), "rifleman_c", "inner", "hold", (-4, -10))
# 순찰 교대 (M5_CYCLE): B동 경비는 안쪽 문 → 남쪽 마당 → 남문으로, 정문 둘과 함께 동쪽 길로 나간다
wps("cycle_in", [(-3, 23), (-0.5, 20.4), (16, 20.4), (23.3, 21.0), (23.3, 16.5), (18, 9), (3, -11), (1, -26), (0, -33)])
wps("cycle_street", [(1, -37), (0, -50), (0.5, -61)])
# 요란하게: 뮤트가 험비에서 내려 혼란 틈에 막사 A 쪽으로 사라진다
wps("mute_loud", [(1.6, -21.5), (0.5, -13.0), (-11.0, 4.5), (-14.0, 10.6)])
# 요란하게: 마당 (정문 → 서쪽 쪽문)에서 막사 A·보급창 쪽에서 몰려나오는 경비, 서쪽 순찰로 북쪽에서 내려오는 경비
for i, (x, y, kind) in enumerate([(-8, -10, "rifleman_a"), (-6, -3, "rifleman_b"), (-11, -20.5, "assault"),
                                  (-16, -21.5, "rifleman_c"), (-20, -24.5, "rifleman_a"), (-28, -18, "rifleman_b")], start=1):
    enemy(f"lda_{i}", (x, y), kind, "loud_a", "advance", (0, -25), spawn="manual")
for i, (x, y, kind) in enumerate([(-45, 6, "rifleman_a"), (-40, 10, "rifleman_b"), (-46, 18.5, "assault"),
                                  (-38, 20, "rifleman_c")], start=1):
    enemy(f"ldb_{i}", (x, y), kind, "loud_b", "advance", (-37, -12), spawn="manual")
for name, (x, y), grp in [("loud_a_01", (-14.0, 15.5), "loud_a"), ("loud_a_02", (9.0, 15.5), "loud_a"),
                          ("loud_b_01", (-44.5, 44.6), "loud_b"), ("loud_b_02", (-39.0, 44.6), "loud_b")]:
    C.marker(f"ENTRY_{name}", (x, y, 0), face=(0, -25), props={"group": grp})
# M6 (경보 뒤, 미션이 부른다): 북쪽 띠 동쪽 반에서 플레이어 쪽(서쪽)으로 밀고 온다
for i, (x, y, kind) in enumerate([(-3, 30.5, "rifleman_a"), (3, 25.5, "rifleman_b"), (8, 32.5, "assault"),
                                  (12.5, 27.6, "rifleman_c"), (-2, 37.4, "rifleman_a"), (17, 23.6, "rifleman_b")], start=1):
    enemy(f"m6a_{i}", (x, y), kind, "camp_a", "advance", (-40, GAP_Y), spawn="manual")
for i, (x, y, kind) in enumerate([(15, 33, "rifleman_c"), (20.5, 25, "assault"), (25, 31, "rifleman_a"),
                                  (19, 37.4, "riot")], start=1):
    enemy(f"m6b_{i}", (x, y), kind, "camp_b", "flank", (-30, GAP_Y), spawn="manual")
# 진입점 (docs/COMBAT.md 11장): 동선 앞쪽, 틈·앞마당에서 가려진 자리 (B동 동쪽 문 앞, 보급 컨테이너 뒤, 경비 초소 안, 북동 컨테이너 뒤)
for name, (x, y), grp in [("camp_a_01", (-3.6, GAP_Y + 2.6), "camp_a"), ("camp_a_02", (9.0, 20.3), "camp_a"),
                          ("camp_a_03", (30.0, 26.6), "camp_a"), ("camp_b_01", (30.0, 25.2), "camp_b"),
                          ("camp_b_02", (32.3, 35.5), "camp_b")]:
    C.marker(f"ENTRY_{name}", (x, y, 0), face=(-30, GAP_Y), props={"group": grp})
cover_pts = [(x, y, "high" if st > 1 else "low") for (x, y, st) in covers]
cover_pts += [(x, y, "low") for (x, y, _a) in sandbags]
cover_pts += [(9.0, 24.3, "high"), (-4.4, 26.0, "high"), (-4.4, 32.0, "high")]
for i, (x, y, h) in enumerate(cover_pts):
    C.marker(f"COVER_{i + 1:02d}", (x, y, 0), face=(-40, GAP_Y), props={"height": h})
# 이야기 인물 (B동 안, 뮤트는 집합 지점 북쪽 어둠)
C.npc("elena", (-12.0, 29.6, 0), STORY_MODEL["elena"], pose="sit_tired", name="엘레나", face=(-15, 29))
C.npc("amelia", (-9.6, 30.6, 0), STORY_MODEL["amelia"], pose="idle", name="아멜리아", face=(-12, 28))
C.npc("rone", (-13.2, 27.2, 0), STORY_MODEL["rone"], pose="idle", name="로네", face=(-11, 30))
C.npc("mute", (-45.0, 41.0, 0), STORY_MODEL["mute"], pose="cross_arms", name="뮤트", face=(-38, 30))
wps("mute_in", [(-44, 32), (-35.5, GAP_Y), (-26, GAP_Y + 0.5), (-17.8, GAP_Y)])
wps("escape", [(-17.8, GAP_Y), (-26, GAP_Y + 0.5), (-35.5, GAP_Y), (-41, 27.5), (-45.2, 25.5)])
# M6_GATE: 엘레나 일행이 틈 → 앞마당 → B동 북쪽 → 식당 천막 남쪽으로 북문까지 (NPC는 곧은 선으로 걷는다: 사이에 막힘 없음)
wps("escort", [(-48.2, 24.8), (-39, 28.5), (-31, 29.2), (-19.5, 34.6), (-3, 35.6), (-1, 30.5), (12, 31.5)])
wps("rone", [(table.x, table.y - 1.15), (-3, 38.2), (-18, 38.2), (-26, 31.5), (-35.6, 28.3), (-41.5, 26.4), (-44.6, 24.4)])
# 식탁 위 돈까스
for i, dx in enumerate((-0.9, 0.2, 1.1)):
    C.prop(f"plate_{i + 1}", (table.x + dx, table.y + (0.12 if i % 2 else -0.1), table.z), "props/act2_tonkatsu_plate.glb",
           yaw=i * 40, props={"collider": 0})
# 트리거
C.group("triggers")
rk.trig(C, "phone", -41.6, -38.4, -36.4, -33.6, 0, 2.5)
rk.trig(C, "generator", -42.2, -39.8, 6.0, 10.0, 0, 2.5)
rk.trig(C, "rally", -45.5, -38, 19, 31, 0, 3)
rk.trig(C, "north_gate", NG_X - 4, NG_X + 4, 34, 39.6, 0, 3)
rk.trig(C, "camp_inside", -34, 34, -30, 40, 0, 4)
rk.trig(C, "west_gate", -33.5, -29.0, WG[0] - 0.8, WG[1] + 0.8, 0, 3)

rk.blackout(C)
C.finish("levels/m5_camp.glb", root_props={
    "sky": "#0c1120", "fog": "18,160", "sun": "-0.4,0.8,0.35", "sunColor": "#9fb2e6", "sunIntensity": 0.75,
    "ambient": 1.05, "hemiSky": "#4a5a86", "hemiGround": "#2a2430", "timeOfDay": "night", "music": "act2_camp",
})
