"""2막 시네마틱 「수용소 해방」 세트 (levels/cine_camp.glb, physics:false 디오라마). 장면: src/game/missions/cine/a2Camp.ts

npm run model -- art/blender/levels/cine_camp.py

[원작] 엘레나·아멜리아·로네가 R41의 외래종 수용소에 갇혀 있고, 원래의 뮤트가 길어진 순찰 주기의 틈으로 접근한다.
[오리지널] 수용소의 위치·생김새(원작에 서술 없음): 모나티엄 동쪽 공장 지대의 공장 마당에 R41이 세운 수용소.
  M5·M6 레벨(levels/m5_camp.glb, art/blender/levels/m5_camp.py)과 같은 곳이다. 이 세트는 그 북서쪽 철망 틈 일대
  (틈, 앞마당의 천막·드럼통 불, B동, 감시탑 W3)를 컷에 맞게 줄여 다시 놓았다. 철망·막사·감시탑·상자·표지판은
  r41_camp_kit 모양을 그대로 쓰고, 둘레는 톱니 지붕 공장(mk.factory_shed)이다.
  정전 뒤라 모나티엄 망의 조명은 없고, 리타가 M5에서 발전기를 세워 투광등과 탐조등도 꺼졌다. 마당은 드럼통 불과
  R41 휴대등(마젠타, 배터리)으로만 밝다. 뮤트가 드나드는 곳은 북서쪽 철망의 찢긴 틈이고, 리타와 분대가 그 앞에 몸을 낮추고 있다.

좌표 (Blender, -Y 정면): 철망 y=0 (남쪽 y<0이 바깥, 북쪽이 마당), 틈 x=-0.75..0.75. 감방 동 y=18..24, 가운데 동(B동)의 문 (0, 18).
감방 내부는 따로 떨어진 CELL 그룹 (x=68..72, y=-41..-38.8, on=0): 장면 camp_c에서만 켠다 (그 그룹 NPC도 함께).
컷 (CAM_<shot>):
  camp_a  리타 어깨 너머로 틈과 마당 (순찰이 멀어진다, 뮤트가 옆에 온다)
  camp_b  분대 뒤 높은 와이드: 뮤트가 틈을 지나 마당을 가로질러 감방 동 문으로
  camp_c  감방 창살 밖에서 안으로: 뮤트의 거래 (CELL)
  camp_d  틈 앞 낮은 망원: 문이 열리고 뮤트·엘레나·아멜리아, 뒤로 돈까스 접시를 든 로네가 달려 나온다
  camp_e  틈 옆에서 리타와 엘레나 두 사람 (옆모습)
  camp_f  경보: 틈 위 높은 와이드, 깜빡이는 경보등
노드: CELLDOOR(미션이 x로 밀어 연다), CELL(감방 내부, on=0), LIGHT_alarm_01..(group alarm, on 0, 깜빡임), FX_fire_*
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import cine_kit as ck  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
# 게임 속 수용소와 같은 철망·막사·감시탑. 팔레트(r41_grey, r41_band, fence_post, mesh_a …)를 import 때 더하므로
# ck.night()보다 먼저 불러 다른 색과 같이 밤빛으로 누른다
import r41_camp_kit as rck  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
NIGHT = {"t": 0.42, "k": 0.8}
ck.night(**NIGHT)
mk.PAL.update({
    "r41_mag_d": "#5c2a58",      # 꺼진 마젠타 띠 (감방 복도)
    "tarp_n": ck.shade("#4f5a48"),
    "bench_n": ck.shade("#8a6a52"),
    "mattress_n": ck.shade("#b8b2a2"),
    "blanket_n": ck.shade("#6e7a8d"),
    "cable": "#2f2d34",
    "tray_n": ck.shade("#b7bcc1"),
    # R41 앰버 띠 (막사 띠, 철망 기둥 고리, 탑 고리, 상자 띠, 표지 글자): 밤빛을 덜 눌러 게임처럼 앰버로 읽히게
    "r41_band": ck.shade("#d88a3a", t=0.25, k=0.9),
})
# 철망(mesh_a)은 키트 값(색·불투명도)을 쓰되 UNLIT 반투명이라 ck.night()가 누르지 않는다: 같은 밤빛으로 직접 누른다
# (게임은 밤에도 키트 색 그대로. 이 세트는 팔레트 전체를 누르고 조명을 올리므로 그대로 두면 철망만 떠 보인다)
_mesh_c, _mesh_a = mk.ALPHA["mesh_a"]
mk.ALPHA.update({"magpool": ("#ff4fd8", 0.13), "mesh_a": (ck.shade(_mesh_c, **NIGHT), _mesh_a),
                 "smoke": ("#2c2e3c", 0.6)})      # 공장 굴뚝 연기 (밤: 어두운 연기)
mk._R41.update({"r41_mag_d"})

C = mk.City("cine_camp")

# ================================================================== 바닥 (공장 마당: 수용소 안 아스팔트, 철망 밖 재 덮인 공장 바닥)
C.group("ground")
mk.paving(C, -40, 40, 0.2, 40, key="asphalt", grout=None, tile=2.0, col=False)
mk.paving(C, -40, 40, -48, 0.2, key="ash", grout=None, tile=2.0, col=False)
C.box("pave_d", -400, 400, -400, 400, -0.6, -0.31, kind="fine")
# 바깥: 잔해 더미 (분대의 엄폐), 그을린 자국
ck.rubble(C, -3.0, -3.0, 1.4, seed=1, h=0.5)
ck.rubble(C, 3.3, -3.4, 1.2, seed=2, h=0.45)
ck.rubble(C, -7.5, -2.0, 1.8, seed=3, h=0.7)
ck.rubble(C, 7.8, -2.6, 1.6, seed=4, h=0.6)
ck.debris(C, -10, 10, -8, -0.6, n=50, seed=5)
ck.scorch(C, -5, -5, 1.6, seed=6)
ck.debris(C, -14, 14, 1.5, 17, n=40, seed=8)   # 7은 한 조각이 드럼통 불빛 원판(z 0.03)과 같은 높이였다
# 마당 바퀴 자국 (어두운 줄)
for x in (-3.6, -2.4):
    C.strip("char", (x, 2.5, 0), (x - 1.0, 17.0, 0), 0.3, lift=0.012)

# ================================================================== 바깥 철망 (y=0, rck.fence_run 모양) + 북서쪽 철망의 찢긴 틈
# 수용소 세트(철망·막사·탑·마당·경보등)는 한 묶음: 같은 머티리얼이 한 메시가 되어 그리기 호출이 준다
C.group("camp")
GAP = (-0.75, 0.75)
H = 2.6              # 키트 철망 높이 (게임과 같다)
P = 2.4              # 기둥 간격: 경보등이 ±9.6 기둥 위에 선다
X_END = 28.8
# 틈 양옆 첫 기둥(±2.4)부터 바깥은 키트 철망 그대로 (모따기 기둥 + 앰버 띠 + 가로대 둘 + 반투명 철망 + 윤형 철조망)
for s in (-1, 1):
    rck.fence_run(C, (s * P, 0), (s * X_END, 0), h=H, pitch=P, col=False)
# 첫 기둥 → 틈: 철망과 아래 가로대가 찢겨 끝난다. 위 가로대는 틈 위로 이어진다 (기둥에서 기둥까지)
C.beam("fence_post", (-P, 0, H - 0.12), (P, 0, H - 0.12), 0.05, 0.05, kind="detail")
_coil_step = (X_END - P) / int((X_END - P) / 0.45)      # 키트 철조망과 같은 마디 (첫 기둥에서 이어진다)
for s in (-1, 1):
    x_cut = s * GAP[1]
    a = Vector((s * P, 0, 0))
    pts = [a + Vector((0, 0, 0.12)), Vector((x_cut, 0, 0.12)), Vector((x_cut, 0, H - 0.1)), a + Vector((0, 0, H - 0.1))]
    for dy in (-0.01, 0.01):
        C.poly("mesh_a", [tuple(p + Vector((0, dy, 0))) for p in pts])
    # 아래 가로대: 틈 0.2 m 앞에서 끊겨 바깥으로 휜 끝
    xb = s * (GAP[1] + 0.2)
    C.beam("fence_post", (s * P, 0, 0.15), (xb, 0, 0.15), 0.05, 0.05, kind="detail")
    C.beam("fence_post", (xb, 0, 0.15), (xb - s * 0.12, -0.22, 0.08), 0.05, 0.05, kind="detail")
    # 윤형 철조망: 첫 기둥에서 틈 0.35 m 앞까지 같은 나선으로 이어지다가 끊겨 바깥으로 늘어진다
    u = Vector((s, 0, 0))
    side = Vector((-u.y, u.x, 0))
    prev = None
    i = 0
    while True:
        p = a + u * (i * _coil_step)
        if s * p.x < GAP[1] + 0.35:
            break
        ang = i * 1.9
        q = p + Vector((0, 0, H + 0.22)) + side * math.cos(ang) * 0.2 + Vector((0, 0, math.sin(ang) * 0.2))
        if prev is not None:
            C.beam("steel", tuple(prev), tuple(q), 0.018, 0.018, kind="detail")
        prev = q
        i -= 1
    C.beam("steel", tuple(prev), tuple(prev + Vector((-s * 0.25, -0.3, -0.8))), 0.018, 0.018, kind="detail")
# 찢겨 바깥으로 젖혀진 판 (틈 양옆) + 그 윗변 가로대 토막
C.rbox("mesh_a", (GAP[0] - 0.42, -0.2, 0.75), (0.5, 0.03, 1.4), rot=(0, 0, 62), kind="fine")
C.rbox("fence_post", (GAP[0] - 0.42, -0.2, 1.46), (0.52, 0.04, 0.04), rot=(0, 0, 62), kind="detail")
C.rbox("mesh_a", (GAP[1] + 0.42, -0.2, 0.7), (0.5, 0.03, 1.3), rot=(0, 0, -62), kind="fine")
C.rbox("fence_post", (GAP[1] + 0.42, -0.2, 1.36), (0.52, 0.04, 0.04), rot=(0, 0, -62), kind="detail")
# 위 가로대에 걸려 남은 철망 조각 (머리 위 1.9 m부터), 벗겨져 바닥에 늘어진 판 (틈 왼쪽 바깥)
C.rbox("mesh_a", (0.1, -0.03, H - 0.42), (0.9, 0.02, 0.5), rot=(7, 0, 3), kind="fine")
C.rbox("mesh_a", (-1.8, -0.55, 0.06), (0.95, 0.55, 0.02), rot=(4, -3, 9), kind="fine")
# 철망 경고판 (R41 글자 대신 앰버 삼각판), 철망 바깥 면에서 1.5 cm 띄워 건다
for x in (-6.0, 6.0):
    C.plate("r41_band", [(-0.16, -0.14), (0.16, -0.14), (0, 0.15)], (x, -0.025, 1.5), (0, -1, 0), 0.02, kind="detail")
    C.text("char", "!", 0.16, (x, -0.045, 1.45), (0, -1, 0), lift=0.006)

# ================================================================== 감방 동 (rck.barrack 모양: 밝은 회색 벽, 아래 앰버 띠, 어두운 박공 지붕)
BLOCKS = [(-14.0, -5.0), (-4.0, 4.0), (5.0, 14.0)]      # 바깥 면 (벽 두께는 안으로)
BY0, BY1, BH = 18.0, 24.0, 3.0
FZ = 0.02            # 막사 바닥판 윗면 (마당 바닥 z=0과 같은 평면에 두지 않는다)
WALL = 0.18
w2 = WALL / 2
for i, (x0, x1) in enumerate(BLOCKS):
    cx = (x0 + x1) / 2
    if i != 1:
        # A동·C동: 키트 막사 그대로 (창 포함) + 닫힌 문 판
        rck.barrack(C, x0 + w2, x1 - w2, BY0 + w2, BY1 - w2, h=BH, floor_z=FZ, windows=True)
        C.box("r41_trim", cx - 0.6, cx + 0.6, BY0 - 0.05, BY0, FZ, FZ + 2.0, kind="detail")
        C.box("r41_shell", cx + 0.38, cx + 0.48, BY0 - 0.08, BY0 - 0.05, FZ + 0.9, FZ + 1.1, kind="detail")
        continue
    # B동 (외래종 수용, 문 (0, 18)): 키트 barrack과 같은 모양을 문간과 함께 짓는다.
    # 키트 barrack은 앰버 띠가 문간을 가로지른다 (사람이 달려 나오는 문이라 띠를 문 양옆에서 끊는다)
    ix0, ix1, iy0, iy1 = x0 + w2, x1 - w2, BY0 + w2, BY1 - w2      # 벽 중심선
    e = w2 + 0.01
    C.box("concrete_d", ix0 - 0.2, ix1 + 0.2, iy0 - 0.2, iy1 + 0.2, FZ - 0.3, FZ)
    # 앞·뒷벽은 바깥 모서리까지, 옆벽은 그 사이 (키트처럼 모서리가 9 cm 파이지 않게)
    C.box("r41_grey", x0, -0.6, iy0 - w2, iy0 + w2, FZ, FZ + BH)
    C.box("r41_grey", 0.6, x1, iy0 - w2, iy0 + w2, FZ, FZ + BH)
    C.box("r41_grey", -0.6, 0.6, iy0 - w2, iy0 + w2, FZ + 2.0, FZ + BH)
    C.box("r41_grey", x0, x1, iy1 - w2, iy1 + w2, FZ, FZ + BH)
    for xx in (ix0, ix1):
        C.box("r41_grey", xx - w2, xx + w2, iy0 + w2, iy1 - w2, FZ, FZ + BH)
    bz = (FZ + 0.25, FZ + 0.33)
    C.box("r41_band", ix0 - e, -0.61, iy0 - e, iy0 + e, *bz, kind="detail")
    C.box("r41_band", 0.61, ix1 + e, iy0 - e, iy0 + e, *bz, kind="detail")
    C.box("r41_band", ix0 - e, ix1 + e, iy1 - e, iy1 + e, *bz, kind="detail")
    for xx in (ix0, ix1):
        C.box("r41_band", xx - e, xx + e, iy0 - e, iy1 + e, *bz, kind="detail")
    C.prism("r41_shell", [(ix0 - 0.3, iy0 - 0.3), (ix1 + 0.3, iy0 - 0.3), (ix1 + 0.3, iy1 + 0.3), (ix0 - 0.3, iy1 + 0.3)],
            FZ + BH, FZ + BH + 0.18, bottom=True)
    C.prism("r41_shell", [(ix0 - 0.3, iy0 - 0.3), (ix1 + 0.3, iy0 - 0.3), (cx, (iy0 + iy1) / 2)], FZ + BH + 0.18,
            FZ + BH + 0.2)
    C.box("r41_shell", ix0 - 0.3, ix1 + 0.3, (iy0 + iy1) / 2 - 0.3, (iy0 + iy1) / 2 + 0.3, FZ + BH + 0.18, FZ + BH + 0.7)
    # 문간 안쪽 어둠 (벽 안쪽 면 2 cm 뒤). 문 뒤에서 기다리는 사람들은 이 판을 지나며 나타난다
    C.box("char", -0.75, 0.75, iy0 + w2 + 0.02, iy0 + w2 + 0.05, FZ, FZ + 2.05)
    # 문틀
    C.box("r41_trim", -0.72, 0.72, BY0 - 0.04, BY0 + 0.02, 2.0, 2.14, kind="detail")
    for sx in (-1, 1):
        C.box("r41_trim", sx * 0.66 - 0.06, sx * 0.66 + 0.06, BY0 - 0.04, BY0 + 0.02, 0.0, 2.0, kind="detail")
    # 수용 동의 높은 창 (어두운 창 + 쇠창살)
    for wx in (-2.6, 2.6):
        C.box("char", wx - 0.42, wx + 0.42, BY0 - 0.03, BY0, 2.1, 2.55, kind="fine")
        for b in range(4):
            bx = wx - 0.3 + b * 0.2
            C.box("steel", bx - 0.02, bx + 0.02, BY0 - 0.06, BY0 - 0.02, 2.1, 2.55, kind="detail")
# B동 표지판 (게임 속 B동 뒷문 옆과 같은 판): 문 왼쪽, 마당 쪽
rck.sign(C, -1.45, BY0 - 0.65, "외래종 B동", "HOLDING B", face=(0, -1))
# 미는 문 (가운데 동). 미션이 x+로 1.25 m 민다. 띠는 닫혔을 때 벽의 앰버 띠와 이어진다
C.group("CELLDOOR", slide="1.25,0,0")
C.box("r41_light", -0.6, 0.6, BY0 - 0.12, BY0 - 0.04, 0.0, 2.0)
C.box("r41_band", -0.6, 0.6, BY0 - 0.14, BY0 - 0.12, FZ + 0.25, FZ + 0.33, kind="detail")
C.box("r41_metal", 0.32, 0.46, BY0 - 0.18, BY0 - 0.12, 0.85, 1.15, kind="detail")
C.group("camp")
# 문 위 레일
C.box("r41_metal", -0.7, 2.0, BY0 - 0.16, BY0 - 0.04, 2.0, 2.12, kind="detail")

# ================================================================== 감시탑 (게임의 W3: rck.watchtower), 리타가 발전기를 세워 탐조등이 꺼졌다
TX, TY = 8.5, 4.5
TH = 4.0
rck.watchtower(C, "w3", TX, TY, h=TH, search=False)
# 꺼진 탐조등 (키트 searchlight 몸통, 렌즈는 꺼진 색. 받침은 발판에 선다)
SL = Vector((TX, TY, TH + 1.15))
_yaw = math.atan2(-10.0, -6.0)                       # 틈 바깥 쪽을 비추던 자리
_d = Vector((math.cos(_yaw), math.sin(_yaw), -0.18)).normalized()
C.cyl("r41_shell", (TX, TY, TH - 0.01), tuple(SL - Vector((0, 0, 0.05))), 0.08, segs=8)
C.cyl("r41_shell", tuple(SL - _d * 0.25), tuple(SL + _d * 0.18), 0.24, r2=0.28, segs=12)
C.cyl("lamp_off", tuple(SL + _d * 0.17), tuple(SL + _d * 0.2), 0.24, segs=12, kind="detail")
# 끊긴 전원선: 발판 밑에서 늘어진 끝 + 바닥을 기어 오다 끊긴 끝 (그을린 자국)
C.beam("cable", (TX + 0.9, TY - 1.42, TH - 0.15), (TX + 1.0, TY - 1.55, 2.3), 0.03, 0.03, kind="detail")
C.beam("cable", (TX + 0.3, TY - 3.4, 0.03), (TX + 0.95, TY - 1.85, 0.03), 0.03, 0.03, kind="detail")
C.beam("cable", (TX + 0.95, TY - 1.85, 0.03), (TX + 1.05, TY - 1.68, 0.4), 0.03, 0.03, kind="detail")
C.blob("char", (TX + 1.0, TY - 1.75, 0.04), 0.25, scale=(1, 1, 0.15), segs=8, rings=4, kind="fine")


# ================================================================== 마당: 천막, 드럼통 불, R41 휴대등, 짐
# 포로 천막 (게임 속 틈 안쪽 앞마당과 같은 R41 천막). 뮤트·순찰·달려 나오는 길에서 비켜 둔다
mk.tent(C, -7.4, 14.4, yaw=8, w=2.6, d=3.2, h=1.9, key="canvas_r")
mk.tent(C, 12.4, 14.0, yaw=-6, w=2.6, d=3.2, h=1.9, key="canvas_r")
for i, (x, y) in enumerate(((-3.6, 6.4), (4.6, 9.2), (-2.2, 13.6), (6.4, 15.6), (-9.0, 10.5), (2.3, 16.2))):
    ck.fire_barrel(C, x, y, fid=f"{i + 1:02d}")
for (x, y) in ((-6.6, 11.2), (9.2, 13.4), (-2.3, 16.9)):
    for a in (0, 120, 240):
        r = math.radians(a)
        C.beam("r41_metal", (x + math.cos(r) * 0.35, y + math.sin(r) * 0.35, 0), (x, y, 1.55), 0.04, 0.04, kind="detail")
    C.box("r41_shell", x - 0.16, x + 0.16, y - 0.12, y + 0.12, 1.5, 1.82)
    C.blob("r41_lamp", (x, y - 0.13, 1.66), 0.11, scale=(1.3, 0.5, 1.0), segs=10, rings=6)
    C.cyl("magpool", (x, y, 0.03), (x, y, 0.04), 2.6, segs=24, kind="fine")
    C.box("r41_shell", x - 0.2, x + 0.2, y - 0.2, y + 0.2, 0, 0.26, kind="detail")   # 배터리 상자
# 보급 상자 더미 (게임과 같은 R41 상자: 흑 + 앰버 띠)
for i, (x, y, s) in enumerate(((-11.5, 15.5, 0.8), (-10.6, 15.8, 0.6), (-11.0, 14.6, 0.7), (11.8, 9.5, 0.75), (12.6, 9.9, 0.55))):
    rck.r41_crate(C, x, y, s=s, yaw=i * 17)
# 경보등 (미션이 켠다): 감방 지붕, 탑 지붕, 철망 기둥 위
n = 0
for x in (-9.5, 0.0, 9.5):
    n += 1
    mk.alert_beacon(C, f"alarm_{n:02d}", (x, BY0 + 0.15, FZ + BH + 0.2), color="#ff3a7a", blink=0.55 + n * 0.05,
                    group="alarm", siren=False)
n += 1
mk.alert_beacon(C, f"alarm_{n:02d}", (TX + 0.8, TY + 0.8, TH + 2.4), color="#ff3a7a", blink=0.5, group="alarm", siren=True)
for x in (-9.6, 9.6):
    n += 1
    # 윤형 철조망(기둥 위 0.02~0.42 m) 위로 올린 짧은 받침대
    C.cyl("fence_post", (x, 0, H - 0.01), (x, 0, H + 0.46), 0.04, segs=6, kind="detail")
    mk.alert_beacon(C, f"alarm_{n:02d}", (x, 0.0, H + 0.45), color="#ff3a7a", blink=0.62, group="alarm", siren=False)


# ================================================================== 배경: 무너진 공장 (톱니 지붕) + 원경 + 달
def shed(x0, x1, y0, y1, *, h, seed, teeth=4, chimney=False, yard_face=False):
    """둘레 공장 (mk.factory_shed, 게임의 경계 공장과 같은 모듈). yard_face: 북쪽(+y, 마당 쪽) 면에도 창 줄."""
    mk.factory_shed(C, x0, x1, y0, y1, h=h, teeth=teeth, chimney=chimney, seed=seed)
    if not yard_face:
        return
    rng = random.Random(seed)
    k = x0 + 2.0
    while k < x1 - 1.5:
        for z in ((2.0, 4.3) if h > 5 else (2.0,)):
            C.rect("char" if rng.random() < 0.45 else "glass_d", (k, y1, z), (0, 1, 0), 1.3, 0.9, lift=0.02)
        k += rng.uniform(2.8, 3.6)


C.group("bg")
shed(-38, -16, 40.5, 58, h=7.0, seed=11, teeth=5)
shed(-13, 7, 44, 62, h=8.0, seed=12, chimney=True)
shed(10, 32, 41, 57, h=6.5, seed=13, teeth=5)
shed(-30, -8, -40, -22.4, h=6.0, seed=14, yard_face=True)
shed(6, 27, -42, -24.4, h=7.0, seed=15, teeth=5, yard_face=True)
mk.paving(C, -60, 60, 40, 70, key="rubble_d", grout=None, tile=4.0, col=False, t=0.25)   # 마당(~40) 뒤부터 (겹치면 깜빡임)
ck.night_skyline(C, r=170, n=26, seed=21)
ck.moon(C, (70, 210, 95), r=11)

# ================================================================== 감방 내부 (따로, camp_c 전용)
C.group("CELL", on=0)
RX0, RX1 = 68.0, 72.2          # 방 x
RY_BARS, RY_BACK = -41.0, -38.8
CZ = 2.5
# 바닥·천장·벽
C.box("concrete_d", RX0 - 0.3, RX1 + 0.3, -45.0, RY_BACK + 0.3, -0.3, 0.0)
C.box("r41_panel", RX0 - 0.3, RX1 + 0.3, RY_BACK, RY_BACK + 0.3, 0, CZ)
C.box("r41_panel", RX0 - 0.3, RX0, -45.0, RY_BACK, 0, CZ)
C.box("r41_panel", RX1, RX1 + 0.3, -45.0, RY_BACK, 0, CZ)
C.box("r41_metal", RX0 - 0.3, RX1 + 0.3, -45.0, RY_BACK + 0.3, CZ, CZ + 0.2)
# 복도 바깥 벽 (뮤트 뒤 배경) + 휴대등 하나
C.box("r41_panel", RX0 - 0.3, RX1 + 0.3, -45.3, -45.0, 0, CZ)
C.box("r41_mag_d", RX0, RX1, -45.01, -44.99, 1.6, 1.7, kind="fine")
C.blob("r41_lamp", (RX0 + 0.6, -44.9, 1.9), 0.1, scale=(1.4, 0.6, 1.0), segs=10, rings=6)
C.cyl("magpool", (RX0 + 0.7, -44.2, 0.02), (RX0 + 0.7, -44.2, 0.03), 1.8, segs=20, kind="fine")
# 창살 (y = RY_BARS): 세로봉 0.24 m 간격 + 가로대 + 잠긴 문틀
for i in range(int((RX1 - RX0) / 0.24) + 1):
    x = RX0 + i * 0.24
    C.cyl("r41_metal", (x, RY_BARS, 0), (x, RY_BARS, CZ), 0.018, segs=6, kind="detail")
for z in (0.12, 1.15, CZ - 0.08):
    C.box("r41_metal", RX0, RX1, RY_BARS - 0.03, RY_BARS + 0.03, z - 0.035, z + 0.035, kind="detail")
C.box("r41_shell", RX0 + 2.6, RX0 + 2.75, RY_BARS - 0.08, RY_BARS + 0.02, 1.0, 1.3, kind="detail")   # 자물쇠
# 뒷벽 높은 창 (달빛) + 창살
C.rect("moonlit", ((RX0 + RX1) / 2, RY_BACK - 0.01, 2.05), (0, -1, 0), 0.9, 0.42, lift=0.0)
for b in range(5):
    bx = (RX0 + RX1) / 2 - 0.36 + b * 0.18
    C.box("r41_metal", bx - 0.02, bx + 0.02, RY_BACK - 0.05, RY_BACK - 0.01, 1.84, 2.26, kind="detail")
C.box("moonbeam", RX0 + 1.4, RX0 + 3.2, -40.6, RY_BACK, 0.01, 0.02, kind="fine")
# 침상·담요, 벤치 (로네)
C.box("bench_n", RX1 - 0.75, RX1 - 0.05, -40.2, RY_BACK, 0.0, 0.3)
C.box("mattress_n", RX0 + 0.05, RX0 + 1.0, -40.4, RY_BACK, 0.0, 0.14)
C.rbox("blanket_n", (RX0 + 0.5, -39.9, 0.17), (0.8, 0.6, 0.06), rot=(0, 0, 8), kind="detail")
C.rbox("tray_n", (RX1 - 0.3, -40.05, 0.32), (0.3, 0.22, 0.02), kind="detail")
ck.debris(C, RX0 + 0.2, RX1 - 0.2, -40.8, -39.0, n=6, seed=31)

# ================================================================== 사람들
C.group("npc")
RIFLE = "weapons/us/m4a1.glb"
RITA = (0.15, -0.9, 0.0)
north = (0.15, 12.0)
# 틈 앞: 리타와 분대 (camp_a, camp_b, camp_d, camp_e, camp_f)
YARD_SHOTS = "camp_a,camp_b,camp_d,camp_e,camp_f"
C.npc("rita", RITA, "characters/rita.glb", pose="cine_kneel_rifle", face=north, name="리타",
      props={"hold_R": RIFLE, "expr": "serious", "scene": YARD_SHOTS})
C.npc("sabre", (-2.1, -1.35, 0.0), "characters/squad_sabre.glb", pose="cine_kneel_rifle", face=(-0.6, 12), name="사브르",
      props={"hold_R": RIFLE, "expr": "serious", "scene": YARD_SHOTS})
C.npc("jesty", (-3.05, -1.85, 0.0), "characters/squad_jesty.glb", pose="cine_kneel_rifle", face=(-1.5, 12), name="제스티",
      props={"hold_R": RIFLE, "scene": YARD_SHOTS})
C.npc("rona", (-4.0, -2.35, 0.0), "characters/squad_rona.glb", pose="cine_kneel_rifle", face=(-2.5, 12), name="로나",
      props={"hold_R": RIFLE, "scene": YARD_SHOTS})
C.npc("karen", (2.2, -1.8, 0.0), "characters/squad_karen.glb", pose="cine_kneel_rifle", face=(1.2, 12), name="케이트",
      props={"hold_R": "weapons/us/m870.glb", "scene": YARD_SHOTS})
# 뮤트: 리타 오른쪽에 온다(camp_a), 틈을 지나 달린다(camp_b)
C.npc("mute", (1.05, -0.75, 0.0), "characters/mute.glb", pose="kneel", face=north, name="뮤트",
      props={"expr": "smirk", "scene": "camp_a,camp_b"})
# 순찰 둘 (camp_a): 마당 안쪽 철망을 따라 멀어진다
C.npc("r41_patrol_a", (0.9, 2.5, 0.0), "enemies/r41_rifleman_a.glb", pose="hold_rifle_ready", face=(-9, 6), name="R41",
      props={"hold_R": "weapons/r41/r41_carbine.glb", "scene": "camp_a,camp_b"})
C.npc("r41_patrol_b", (-0.2, 3.1, 0.0), "enemies/r41_rifleman_b.glb", pose="hold_rifle_ready", face=(-10, 7), name="R41",
      props={"hold_R": "weapons/r41/r41_carbine.glb", "scene": "camp_a,camp_b"})
for i, (x, y) in enumerate(((-9.5, 6.6), (-15.0, 11.5))):
    C.marker(f"WP_patrol_{i + 1:02d}", (x, y, 0.0))
# 뮤트가 달리는 길 (camp_b): 틈 → 마당 → 감방 동 문
# 감방 동 사이 골목(x=-5..-4)으로 사라진다
for i, (x, y) in enumerate(((0.3, 0.35), (-1.3, 6.8), (-3.4, 12.6), (-4.5, 17.4), (-4.5, 20.5))):
    C.marker(f"WP_mute_in_{i + 1:02d}", (x, y, 0.0))
# 문에서 나오는 사람들 (camp_d~f): 문 안쪽 어둠에서 시작
C.npc("mute_out", (0.15, 18.45, 0.0), "characters/mute.glb", pose="cine_run", face=(0, 0), name="뮤트",
      props={"expr": "serious", "scene": "camp_d,camp_e,camp_f"})
C.npc("elena", (-0.15, 18.75, 0.0), "characters/elena.glb", pose="cine_run", face=(0, 0), name="엘레나",
      props={"expr": "tired", "scene": "camp_d,camp_e,camp_f"})
C.npc("amelia", (0.3, 19.1, 0.0), "characters/amelia.glb", pose="cine_run", face=(0, 0), name="아멜리아",
      props={"expr": "serious", "scene": "camp_d,camp_e,camp_f"})
C.npc("rone", (0.0, 19.6, 0.0), "characters/rone.glb", pose="cine_camp_run_eat", face=(0, 0), name="로네",
      props={"hold_L": "props/cine_tonkatsu_plate.glb", "hold_R": "props/cine_fork.glb", "expr": "dreamy",
             "scene": "camp_d,camp_e,camp_f"})
# 달려 나오는 길 (사람마다 끝자리만 다르다): 문 → 마당 → 틈 안쪽
for i, (x, y) in enumerate(((0.0, 16.6), (-0.9, 11.6), (0.4, 5.2))):
    C.marker(f"WP_out_{i + 1:02d}", (x, y, 0.0))
C.marker("WP_end_mute", (-1.25, 1.55, 0.0))
C.marker("WP_gap", (0.15, 0.55, 0.0))
C.marker("WP_end_elena", (0.13, -0.05, 0.0))
C.marker("WP_end_amelia", (-0.38, 0.92, 0.0))
C.marker("WP_end_rone", (0.75, 1.75, 0.0))
for nid, (x, y) in (("elena", (-0.6, -6.6)), ("amelia", (-1.4, -6.9)), ("mute_out", (0.5, -6.4)), ("rone", (-0.2, -7.2))):
    C.marker(f"WP_back_{nid}", (x, y, 0.0))

# 감방 안 (CELL 그룹 = 그 노드가 보일 때만): 엘레나·아멜리아·로네, 창살 밖의 뮤트
C.group("CELL")
cell_face = ((RX0 + RX1) / 2, -45.0)
C.npc("elena_cell", (69.0, -39.25, 0.0), "characters/elena.glb", pose="cine_cell_sit", face=(69.4, -45), name="엘레나",
      props={"expr": "tired", "scene": "camp_c"})
C.npc("amelia_cell", (69.95, -39.2, 0.0), "characters/amelia.glb", pose="cine_cell_sit", face=(70.2, -45), name="아멜리아",
      props={"expr": "tired", "scene": "camp_c"})
C.npc("rone_cell", (RX1 - 0.4, -39.5, 0.0), "characters/rone.glb", pose="cine_sit_eat", face=(RX1 - 1.4, -42.0), name="로네",
      props={"seatZ": 0.3, "hold_L": "props/cine_tonkatsu_plate.glb", "hold_R": "props/cine_fork.glb", "expr": "dreamy",
             "scene": "camp_c"})
C.npc("mute_cell", (69.56, -42.15, 0.0), "characters/mute.glb", pose="cine_camp_crouch", face=(69.56, -39), name="뮤트",
      props={"expr": "serious", "scene": "camp_c"})

# ================================================================== 카메라
C.group("cams")
rx, ry = RITA[0], RITA[1]
C.cam("camp_a", [
    (0.0, (rx - 1.05, ry - 2.75, 1.2), (rx + 0.9, 8.0, 0.55), 38),
    (7.0, (rx - 0.85, ry - 2.35, 1.12), (rx + 0.7, 8.0, 0.6), 36),
])
C.cam("camp_b", [
    (0.0, (-5.8, -6.2, 1.9), (-0.6, 8.0, 0.5), 44),
    (6.0, (-5.2, -5.6, 1.75), (-2.2, 14.0, 0.8), 42),
])
C.cam("camp_c", [
    (0.0, (70.6, -44.3, 1.3), (69.9, -39.4, 0.45), 44),
    (4.5, (70.4, -43.4, 1.05), (69.8, -39.6, 0.5), 40),
])
C.cam("camp_d", [
    (0.0, (-1.55, -0.55, 0.78), (0.0, 17.5, 1.0), 22),
    (6.0, (-1.65, -0.8, 0.82), (0.0, 10.0, 0.9), 32),
    (12.0, (-1.8, -1.1, 0.86), (0.2, 4.0, 0.8), 40),
])
C.cam("camp_e", [
    (0.0, (1.5, -2.65, 0.98), (0.1, -0.45, 0.82), 32),
    (9.0, (1.35, -2.4, 0.95), (0.1, -0.45, 0.84), 30),
])
C.cam("camp_f", [
    (0.0, (1.75, -5.5, 0.85), (-0.2, 4.0, 1.35), 46),
    (6.0, (1.55, -5.0, 0.9), (-0.2, 4.0, 1.3), 42),
])
C.marker("SPAWN_player", (rx, ry - 0.6, 0), face=north)

# physics:false 디오라마: 키트 모듈(막사·감시탑·상자·표지판·공장)이 넣은 COL_은 쓰지 않는다
C.cols.clear()
C.ocols.clear()
C.ccols.clear()

ROOT = dict(ck.NIGHT_ROOT)
ROOT.update({
    "sky": "#0b1124",
    "fog": "30,210",
    "ambient": 1.55,
    "sunIntensity": 1.75,
    "hemiSky": "#5d6ca0",
    "music": "cine_dark",
    "timeOfDay": "night_blackout",
    "scene": "A2_CAMP",
    "shots": "camp_a,camp_b,camp_c,camp_d,camp_e,camp_f",
})
C.finish("levels/cine_camp.glb", root_props=ROOT, outline=0.022)
