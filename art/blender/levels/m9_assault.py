"""M9 「종막」: 에르피엔 외곽 총공격 → 숲 가장자리 능선 (해 질 녘).

npm run model -- art/blender/levels/m9_assault.py   → public/models/levels/m9_assault.glb
npm run shot -- levels/m9_assault.glb --views top,34
미션: src/game/missions/m9.ts (마커 계약은 이 설명 아래 표), 키트: art/blender/lib/battlefield_kit.py

[원작] 성전군의 총공격. 마카샤와 실라의 지휘로 요정들이 돌격한다. 에르피엔 결전에서 R41 돌격 편대가 중성자탄이 자기들을
       향했다는 것을 알고 동요해 대거 이탈한다. 마지막에 에르핀과 네르가 흑뉴아를 제압한다.
[오리지널] 리타의 분대가 에르피엔 외곽에서 요정 돌격의 앞을 열고 흑뉴아를 따르는 R41 잔당을 소탕한다. 들판의 참호선,
       요정 마을 외곽 폐허, R41 침공군 야전 지휘소(미션 플래그가 꺼지면 버려진 채로 남는다), 숲 가장자리 능선의 생김새와 배치.
       리타는 에르피엔 바깥 성문 앞에서 약 200 m 떨어진 하늘(성문 너머 세계수 수관 앞)의 결전을 지켜보기만 한다.
       결전 컷신 세트 cine_finale.py는 이 끝 자리를 원점으로 옮긴 같은 성문 앞이다 (세트 좌표 + (−31.75, 721.25) = 이 레벨 좌표).

좌표 (Blender, m): 원점 = 출발 참호 가운데, +Y = 북쪽(에르피엔), 낮은 해는 서쪽(-X)에서.
  y  -46..-12   성전군 후방(MARK_rear -14,-31): 천막·보급 수레·상자·머스킷 거치대·깃발·모닥불.
                지휘관 둔덕 (13,-17) +1.3 m: NPC_makasha, NPC_sila, 큰 깃발, 북
  y  -1.1..3    출발 참호 (깊이 0.75, 널빤지 벽, 북쪽 흉벽): 서쪽 x -46..-15, 동쪽 x -11..46, 그 사이 둑길(보급로·포로 호송길)
                돌격 계단 굴(바깥으로 판 계단) 8곳 = 요정 여섯 쌍 x ±22/31/40 + 분대 x ±6. 연락호 x 9.5 → 남쪽 계단
  y   3..72     들판: 돌담 조각·포탄 구덩이·건초·그루터기·불탄 R41 차량. 요정 돌격로 WP_charge_nn_01..03 (y 9 → 36 → 64~70)
                y 73.5 철조망 띠 (틈 x -11.5..-4.5 둑길 앞, -26..-23, 11..15, 29..33)
                       돌격 때 전차 고폭탄이 여는 통로 BRK_wire_lane_w·e (x -18..-13, 4.5..9.5)
  y  78.9..81.1 R41 참호선 1 앞 참호 (깊이 0.65, 회색 패널 벽, 남쪽 흉벽, 사격 발판 +0.18): 서 x -44..-10 / 동 x -5..44, 둑길 x -10..-5
                벙커 셋 (x -32, 6, 32, 앞면 = 참호 북벽, 문 = 참호 바닥) + 북쪽 계단 굴 넷, 연락호 x -24 / 21
  y  96.9..99.1 지원 참호 (서 -30..-10 / 동 -5..26): 남쪽 계단 굴 x 0.5..3.5 = 투항 1 자리, 북쪽 계단 굴 둘
  y 108..150    마을로 오르는 비탈 (0 → 2.2 m)
  y 121..212    요정 마을 외곽 폐허: 남쪽 돌담(틈), 돌집 다섯 + 헛간, 우물(4,182), 풍차(31,187) = 투항 2 자리,
                R41 차단벽(y 158)과 전진 초소 컨테이너(6,177), 서쪽 옆길(생울타리 x -44..-36, 측면 우회로)
  y 212..226    지휘소 앞 풀밭 (3.0 m), R41 차단벽 지그재그, 철조망
  y 228..272    R41 야전 지휘소 (울타리 x -26..14): 남문 x -6, 북문(뒷문) x -15.5, 지휘 컨테이너 (-4,262) 안 북벽 콘솔,
                차양 아래 작전 탁자, 안테나 탑(6,263), 발전기, 창고 컨테이너 둘, 천막, 모래주머니 진지, 투광등,
                동쪽 울타리 포탄 구멍 (y 258..266.5) → 능선 길 어귀 (콘솔에서 능선으로 곧장 나가는 앞길)
  y 270..346    능선 길: 지휘소 동쪽 (21,278)에서 숲 사이로 올라 → 숲 가장자리 전망대 (2,340) z 15.
                전망대 빈터 남쪽 모래주머니 둥지 둘 = R41 후위 감시조 (ENEMY_rg_*)
  y 346..470    [진격로 연장, 2026-11-03] 전망대 바위 틈 → 숲 내리막 길 (z 15 → −18, 가장 가파른 곳 23°)
  y 470..530    골짜기 바닥: 동서 골짜기 길과 갈림길 (−3,482) = 1구역 「숲 끝」(R41 후위 차단선, 서쪽 농가 뒤에서 장갑차 1).
                동쪽 헛간 뒤 = 성전군 전차 집결지 (MNT M1A1 둘이 능선 차선으로 내려와 모인다)
  y 530..575    강 (에르피엔을 두른 강, 세계수에서 482 m 고리. 얕다: 물 0.65 m) + 돌다리 (−17.4, 560) = 2구역 「다리」
                (북쪽 둑 R41 진지, 서쪽 둔덕 뒤 장갑차 2)
  y 575..700    성문 방사 큰길: 세계수 → 성문 → 다리로 곧게. 밭·과수원
  y 690..765    성문 앞 = 3구역 「성문」: R41 포위 진지(차단벽·모래주머니·컨테이너), 동쪽 둔덕 뒤 장갑차 3, 서쪽 문지기 마구간
                뒤에서 장갑차 4. 끝 자리 MARK_end (성문 앞 43 m). 에르피엔 바깥 성문루·성벽·탑 = erpien_kit.city_gate
                (원경 성벽과 같은 자리·크기, 문 위에 에르피엔 군기 나비, 탑에 군기 현수막)
  전차 차선     TANK_LANE: 지휘소 앞 → 지휘소 동쪽 → 능선 동쪽 숲속 흙길(x 34~36)로 마루 → 숲 동쪽 내리막(x 37~48) → 헛간과
                창고 사이 → 헛간 뒤 집결지. 지형을 깎고 돋운 길 (lane_cut, 가장 가파른 곳 약 17°)
  동쪽 차선     성전군 전차가 진격로 동쪽 24~34 m를 따라 나란히 간다 (요정 날개·플레이어 길과 떨어져, 여울로 강을 건넌다)
  →             에르피엔 (−60, 1040, z −40): 한가운데 세계수(높이 380 m), 밑동을 두른 왕궁, 시가 고리, 이중 성벽(바깥 약 275 m).
                하늘의 결전 MARK_finale은 성문 너머 세계수 수관 앞 하늘 (끝 자리에서 올려다보는 각 약 38°). 북쪽 원경 산, 저녁 구름
경계: 생울타리·돌담·지형 언덕·숲 + 보이지 않는 COL 벽 (서 x -54.5/-50.5/-46 → 연장 서쪽 벽, 동 x 54.5/50.5/46 → 연장 동쪽 벽,
      남 y -48, 북 = 에르피엔 성벽).

마커 계약 (이름은 m9.ts가 쓴다, 마커는 바닥 위, -Y = 정면):
  SPAWN_player(출발 참호, 북) SPAWN_line1(참호선 1 바로 너머) SPAWN_village SPAWN_hq(남문 앞) SPAWN_ridge(능선 길 시작)
  ALLY_rona/sabre/jesty/karen (follow, m4a1)  ALLY_fairy_01..12 (fairy, advance, path=charge_nn; 화기는 전투 시스템의 요정 기본값)
  WP_charge_nn_01..03 (nn 01..12)  NPC_makasha(point_far) NPC_sila(cheer)
  ENEMY_l1_01..06(line1) ENEMY_l1w_01..04(line1_wave, manual) ENEMY_sur1(sur1, manual) ENEMY_l2_01..07(line2)
  ENEMY_l2w_01..05(line2_wave, manual) ENEMY_sur2_01..03(sur2, manual) ENEMY_hq_01..06(hq) ENEMY_hqw_01..05(hq_wave, manual)
  ENEMY_rg_01..04(ridge, manual: 능선 후위 감시조)
  VEH_vapc1..3 (r41_apc, enemy, group = 이름, manual, driver none: 마을 기갑) VEH_vraid1·2 (r41_raider, driver ai, path vraidN)
      + WP_vraid1_01..05 · WP_vraid2_01..03 (옆길을 북 → 남으로 훑는다)
  COVER_* (height low|high)  MARK_line1 MARK_sur1 MARK_village MARK_sur2 MARK_hq MARK_hq_console MARK_ridge MARK_finale
  MARK_erpien MARK_rear  WP_rear_01..04  TRIG_line1 TRIG_village TRIG_hq TRIG_ridge  CAM_finale_01..03 + LOOK_finale_01..03
  [연장] SPAWN_descent SPAWN_valley SPAWN_bridge SPAWN_gate SPAWN_end  MARK_descent MARK_valley2 MARK_bridge MARK_gate MARK_end
  MARK_door  TRIG_descent_mid TRIG_valley TRIG_bridge TRIG_gate TRIG_end
  ENEMY_v_*(valley) ENEMY_vw_*(valley_wave) ENEMY_b_*(bridge) ENEMY_bw_*(bridge_wave) ENEMY_g_*(gate) ENEMY_gw_*(gate_wave)
      (모두 spawn=manual: 그 단계에 등장 규칙으로 들어온다)
  VEH_ifv1..4 (r41_apc, faction enemy, group ifv1..4, spawn manual; 1·4는 driver ai + path, 2·3은 둔덕 뒤에 박혀 있음)
  VEH_tank1·2 (m1a1, faction ally, group tanks, spawn manual, driver ai, crew 1, path tankN_a) + WP_tankN_s/a/b/c
      (M9 성전군 전차는 둘뿐: 2026-11-04 사용자 「헛간 뒤에서 증원되는 전차 없애. M9에서 총 투입 전차는 2대야.」)
      (s/t/u/v/h/w/x = 출발 참호 앞 → 철조망 앞 → 1선 너머 → 마을 어귀 → 마을 길 → 지휘소 앞 → 전차 차선으로 능선 마루
       → 헛간 뒤 집결지, tank1·2만. VEH_ 자리는 골짜기 헛간 뒤 집결지 = 경로 a의 첫 점)
  ALLY_riot_01..06 (riot, hold, m4a1): 모나티엄 진압반 기동대 보병. 전차와 함께 나아간다
  WP_ext_01..NN: 진격로 연장 (능선 다음 → 성문 앞). 요정 전열(act3kit FairyLine)이 extend()로 잇는다
끝에 계약 노드 좌표표를 출력한다.
"""
import inspect
import math
import os
import random
import sys

import bmesh

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import battlefield_kit as bk  # noqa: E402
import erpien_kit as ek  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
import erpien_flag as ef  # noqa: E402

cb.reset()
C = mk.City("m9_assault")
S = bk.S
NZ = mk.noise2
rng = random.Random(9)

# ================================================================== layout constants
LANES = [-40.0, -31.0, -22.0, 22.0, 31.0, 40.0]      # 요정 돌격 계단 굴 (쌍마다 하나)
PLAYER_BAYS = [-6.0, 6.0]
EX, EY, EZ = -60.0, 1040.0, -40.0                   # 에르피엔 중심 = 세계수, 분지 바닥
ERP_H = 380.0                                       # 세계수 높이 ([원작] 왕국 한가운데 세계수, erpien_kit)
RIDGE = (2.0, 340.5)                                # 전망대
NEAR = (-140.0, 140.0, -110.0, 800.0)               # 가까운 지형(충돌) 범위 (진격로 연장: 성문 너머까지)
CARBINE = "r41_carbine"

# ---- 진격로 연장 (2026-11-03): 전망대 → 숲 내리막 → 골짜기 → 강 다리 → 성문 앞
# 성문은 원경 왕국 키트의 바깥 성벽과 같은 수식(erpien_kit.gate_plan): 세계수에서 전망대 쪽(face) 방사선 위.
GP = ek.gate_plan(EX, EY, ERP_H, (RIDGE[0] - EX, RIDGE[1] - EY))
FO = GP["F"]                                        # 바깥 (세계수 → 성문 → 다리)
TT = GP["T"]                                        # 성문을 볼 때 오른쪽 (동쪽)


def radial(r, lat=0.0):
    """세계수에서 성문 방사선으로 r m, 성문을 볼 때 오른쪽으로 lat m."""
    return (EX + FO.x * r + TT.x * lat, EY + FO.y * r + TT.y * lat)


R_RIV = 482.0                                       # 강 고리 반지름 (세계수 중심)
BRIDGE = radial(R_RIV)                              # 돌다리 가운데 (−17.4, 559.9)
END = radial(320.0)                                 # 끝 자리 (성문 앞 약 43 m)
SIEGE = radial(352.0)                               # R41 포위 차단선 (성문 큰길 위)
TRACK = [(2.0, 340.5), (5.0, 350.0), (8.0, 368.0), (6.0, 392.0), (1.0, 418.0), (-2.0, 445.0), (-3.0, 470.0)]
JUNCTION = (-3.0, 482.0)
SOUTH_ROAD = [JUNCTION, (-8.0, 515.0), (-14.0, 545.0), radial(R_RIV + 11.0)]
GATE_ROAD = [radial(R_RIV - 11.0), radial(420.0), radial(380.0), radial(347.0)]
VROAD = [(-160.0, 492.0), (-75.0, 487.0), (-40.0, 484.0), JUNCTION, (30.0, 486.0), (75.0, 492.0), (170.0, 500.0)]
FARM_W = (-30.0, 500.0)                             # 서쪽 농가 (장갑차 1이 뒤에 숨어 있다)
BARN_E = (36.0, 497.0)                              # 동쪽 헛간 (전차 집결지를 가린다)
SHED_E = (55.0, 500.0)
TOLL = radial(R_RIV - 22.0, 13.0)                   # 다리 북쪽 동쪽 돌 초소
STABLE = (-62.0, 742.0)                             # 문지기 마구간 (장갑차 4가 뒤에서 나온다)
IFV_SPOTS = {"ifv2": (-36.0, 590.0), "ifv3": (-6.0, 738.0)}
# 성전군 전차 차선 (2026-11-03 사용자 지적 "처음부터 오던 전차들은 왜 마을에서 사라지는데?": 지휘부를 지나면 화면 밖에서 골짜기로
# 옮겼다). 지휘소 앞 → 지휘소 동쪽 (울타리와 생울타리 사이) → 능선 동쪽 숲속 흙길로 올라 마루 → 숲 동쪽 내리막 → 골짜기 길 →
# 헛간과 창고 사이 → 헛간 뒤 집결지. 지형을 깎고 돋워 오르막 약 12°, 내리막 약 17° (보병 숲길은 23°). 폭 6.8 m (M1A1 3.7 m)
TANK_LANE = [(2.0, 206.0), (10.0, 206.5), (20.0, 212.5), (28.0, 221.0), (32.0, 234.0), (33.5, 250.0), (34.0, 266.0),
             (34.5, 282.0), (34.5, 298.0), (35.0, 314.0), (35.5, 328.0), (36.0, 340.0), (37.5, 354.0), (39.0, 368.0),
             (40.5, 382.0), (42.0, 396.0), (43.5, 410.0), (45.0, 424.0), (46.5, 438.0), (47.5, 452.0), (48.0, 466.0),
             (48.0, 478.0), (48.0, 490.0), (48.0, 499.0)]
LANE_CREST = 11                                     # TANK_LANE[11] = 능선 마루 (z 15)
LANE_FROM, LANE_TO = 6, 21                          # 깎고 돋우는 구간 (지휘소 동쪽 y 266 → 골짜기 y 478)
LANE_HALF, LANE_BLEND = 3.4, 8.0                    # 차선 반폭 (평평), 그 바깥 섞임 폭
LANE_CLEAR = 9.0                                    # 차선 가운데에서 나무까지 (침엽수 아래 원뿔 COL은 반지름 4 m, 머리 높이)
# 보이지 않는 벽 (연장): 서쪽·동쪽 (끝은 에르피엔 성벽 바깥 면)
WEST_WALL = [(-46.0, 340.0), (-46.0, 380.0), (-44.0, 420.0), (-52.0, 465.0), (-58.0, 500.0), (-62.0, 540.0),
             (-66.0, 580.0), (-72.0, 630.0), (-80.0, 690.0), (-84.0, 740.0), (-84.0, 768.0)]
EAST_WALL = [(46.0, 340.0), (46.0, 380.0), (50.0, 420.0), (62.0, 465.0), (68.0, 505.0), (62.0, 540.0), (55.0, 580.0),
             (45.0, 630.0), (32.0, 690.0), (24.0, 740.0), (22.0, 780.0)]
CORRIDOR = WEST_WALL + list(reversed(EAST_WALL))


def in_poly(x, y, poly):
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def poly_dist(x, y, pts):
    best = 1e9
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 < 1e-9 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
        best = min(best, math.hypot(x - (ax + dx * t), y - (ay + dy * t)))
    return best


def in_corridor(x, y, margin=0.0):
    """연장 구간 통로 안 (margin만큼 벽에서 더 들어가야 참; 음수면 벽 밖으로 넓힘)."""
    if y < 340.0:
        return False
    if not in_poly(x, y, CORRIDOR):
        return margin < 0 and min(poly_dist(x, y, WEST_WALL), poly_dist(x, y, EAST_WALL)) < -margin
    return min(poly_dist(x, y, WEST_WALL), poly_dist(x, y, EAST_WALL)) >= margin

# ================================================================== terrain function

def prof(y):
    """남북 기본 높이: 들판 0 → 마을 2.2 → 지휘소 3.0 → 능선 15 → 숲 내리막(걸어 내려가는 길, 가장 가파른 곳 23°)
    → 골짜기 −18 → 강 → 에르피엔 분지 -40 → 먼 북쪽 언덕."""
    z = 9.0 * S((-60.0 - y) / 140.0)
    z += 2.2 * S((y - 108.0) / 42.0)
    z += 0.8 * S((y - 205.0) / 20.0)
    z += 12.0 * S((y - 280.0) / 52.0)
    z -= 33.0 * S((y - 350.0) / 118.0)
    z -= 9.0 * S((y - 468.0) / 150.0)
    z += 70.0 * S((y - 1500.0) / 900.0)
    return z


def half_w(y):
    return 50.0 + 2.0 * S((y - 110.0) / 20.0) - 6.0 * S((y - 205.0) / 20.0) + 20.0 * S((y - 350.0) / 60.0)


def lateral(x, y):
    return (9.0 + 3.0 * NZ(x * 0.4, y * 0.4, 9)) * S((abs(x) - half_w(y)) / 28.0)


def far_noise(x, y):
    out = max(abs(x) - 160.0, 0.0) + max(-150.0 - y, 0.0)
    return 16.0 * NZ(x * 0.12, y * 0.12, 4) * S(out / 300.0)


def und_amp(y):
    a = 0.12
    a += 0.23 * S((y - 112.0) / 12.0) * (1 - S((y - 212.0) / 10.0))
    a += 0.45 * S((y - 275.0) / 15.0) * (1 - 0.6 * S((y - 465.0) / 20.0))   # 골짜기 바닥은 밭 (덜 울퉁불퉁)
    return a


def und(x, y):
    return und_amp(y) * NZ(x * 1.3, y * 1.3, 5) / 1.7


PADS = []          # (x0, x1, y0, y1, target | None, soft)


def pad(x0, x1, y0, y1, *, target="auto", soft=3.0):
    if target == "auto":
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        target = prof(cy) + und(cx, cy) + lateral(cx, cy)
    PADS.append((x0, x1, y0, y1, target, soft))


BUMPS = [(13.0, -17.0, 6.5, 1.3)]                    # 지휘관 둔덕


def river_cut(x, y):
    """강 바닥 (세계수에서 R_RIV 고리, 가운데 1.15 m, 양쪽 8.5 m 완만한 둑. 물은 둑보다 0.5 m 낮다)."""
    dr = abs(math.hypot(x - EX, y - EY) - R_RIV)
    if dr >= 8.5:
        return 0.0
    return 1.15 * (1 - S(dr / 8.5))


def H_all(x, y):
    return lane_cut(x, y, H_base(x, y)) - river_cut(x, y)


_LANE_S = [0.0]
for (ax, ay), (bx, by) in zip(TANK_LANE, TANK_LANE[1:]):
    _LANE_S.append(_LANE_S[-1] + math.hypot(bx - ax, by - ay))
_LANE_Z = []                                        # (s0, z0, s1, z1) 오르막·내리막 (lane_cut이 처음 불릴 때 정한다)


def lane_z(s):
    """차선 높이: 지휘소 동쪽(지형) → 마루 15 m → 골짜기(지형). 구간마다 직선과 smoothstep을 반씩 (기울기 최대 = 평균 x 1.25)."""
    if not _LANE_Z:
        a, c, b = LANE_FROM, LANE_CREST, LANE_TO
        za, zb = H_base(*TANK_LANE[a]), H_base(*TANK_LANE[b])
        _LANE_Z.extend([(_LANE_S[a], za, _LANE_S[c], 15.0), (_LANE_S[c], 15.0, _LANE_S[b], zb)])
    for (s0, z0, s1, z1) in _LANE_Z:
        if s <= s1:
            t = max(0.0, min(1.0, (s - s0) / (s1 - s0)))
            return z0 + (z1 - z0) * (0.5 * t + 0.5 * S(t))
    return _LANE_Z[-1][3]


def lane_near(x, y):
    """차선에서 가장 가까운 점: (거리, 차선 진척 s)."""
    best = (1e9, 0.0)
    for i, ((ax, ay), (bx, by)) in enumerate(zip(TANK_LANE, TANK_LANE[1:])):
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        t = max(0.0, min(L, ((x - ax) * dx + (y - ay) * dy) / L))
        d = math.hypot(x - (ax + dx * t / L), y - (ay + dy * t / L))
        if d < best[0]:
            best = (d, _LANE_S[i] + t)
    return best


def near_lane(x, y, r):
    return lane_near(x, y)[0] < r


def lane_cut(x, y, z):
    """차선 자리를 깎고 돋운다 (반폭 안은 차선 높이, 바깥 섞임 폭에 걸쳐 지형으로). 끝 12 m는 지형으로 이어진다."""
    if not (20.0 < x < 64.0 and 236.0 < y < 506.0):
        return z
    d, s = lane_near(x, y)
    if d >= LANE_HALF + LANE_BLEND:
        return z
    s0, s1 = _LANE_S[LANE_FROM], _LANE_S[LANE_TO]
    if not (s0 < s < s1):
        return z
    w = S((LANE_HALF + LANE_BLEND - d) / LANE_BLEND) * S((s - s0) / 12.0) * S((s1 - s) / 12.0)
    return z + (lane_z(s) - z) * w


def H_base(x, y):
    z = prof(y) + lateral(x, y) + far_noise(x, y) + und(x, y)
    for (x0, x1, y0, y1, tg, soft) in PADS:
        mx = S((x - (x0 - soft)) / soft) * S(((x1 + soft) - x) / soft)
        if mx <= 0:
            continue
        my = S((y - (y0 - soft)) / soft) * S(((y1 + soft) - y) / soft)
        m = mx * my
        if m <= 0:
            continue
        z = z + ((prof(y) if tg is None else tg) - z) * m
    for (bx, by, br, bh) in BUMPS:
        d = math.hypot(x - bx, y - by)
        if d < br:
            z += bh * S(1 - d / br)
    d = math.hypot(x - EX, (y - EY) * 0.9)
    bm = S((470.0 - d) / 160.0)
    if bm > 0:
        z += (EZ - z) * bm
    return z


# 평평한 터 (참호 띠, 지휘소, 전망대, 마을 집터) — 지형 함수가 정해지기 전에 모은다
pad(-52, 52, -30, 18, target=None, soft=4.0)         # 출발 참호 띠 (z = 0)
pad(-50, 50, 62, 112, target=None, soft=4.0)         # 참호선 1 띠 (z = 0)
pad(-34, 22, 216, 280, target=3.0, soft=6.0)         # 지휘소
pad(-12, 16, 331, 348, target=15.0, soft=6.0)        # 전망대
COTTAGES = [  # (cx, cy, w, d, axis, door, roof, broken, seed)
    (-18.0, 136.0, 8.0, 5.5, "x", "-y", "roof_r", 0.45, 1),
    (13.0, 141.0, 7.0, 5.0, "x", "-y", "roof_g", 0.85, 2),
    (-21.0, 166.0, 7.5, 5.0, "y", "+x", "roof_r", 0.55, 3),
    (16.0, 168.0, 8.0, 5.5, "x", "-y", "roof_g", 0.3, 4),
    (-15.0, 193.0, 10.0, 6.0, "x", "-y", "thatch", 0.65, 5),
    (15.0, 199.0, 6.0, 4.5, "y", "-x", "roof_r", 0.45, 6),
]
for (cx, cy, w, d, ax, *_r) in COTTAGES:
    hx, hy = (w / 2, d / 2) if ax == "x" else (d / 2, w / 2)
    pad(cx - hx - 0.6, cx + hx + 0.6, cy - hy - 0.6, cy + hy + 0.6, soft=3.0)
MILL = (31.0, 187.0)
pad(MILL[0] - 3.4, MILL[0] + 3.4, MILL[1] - 3.4, MILL[1] + 3.4, soft=3.0)
WELL = (4.0, 182.0)
pad(WELL[0] - 1.4, WELL[0] + 1.4, WELL[1] - 1.4, WELL[1] + 1.4, soft=2.5)
POST = (6.0, 177.0)
pad(POST[0] - 1.6, POST[0] + 1.6, POST[1] - 3.2, POST[1] + 3.2, soft=2.5)
# 연장: 농가·헛간·초소 집터, 장갑차 2 둔덕 자리, 갈림길
for (cx, cy, hw, hd) in ((FARM_W[0], FARM_W[1], 5.2, 3.8), (BARN_E[0], BARN_E[1], 8.8, 5.2), (SHED_E[0], SHED_E[1], 4.2, 3.6),
                         (TOLL[0], TOLL[1], 3.8, 3.4), (IFV_SPOTS["ifv2"][0], IFV_SPOTS["ifv2"][1], 5.0, 5.0),
                         (JUNCTION[0] - 10.0, JUNCTION[1] + 2.0, 18.0, 6.0)):
    pad(cx - hw, cx + hw, cy - hd, cy + hd, soft=3.0)

# ================================================================== trenches

ST = bk.Trenches("start", style="fairy")
ST.rect(-46, -15, -1.1, 1.1)
ST.rect(-11, 46, -1.1, 1.1)
ST.steps(-17.0, -15.0, -1.1, 1.1, "+x")            # 둑길로 올라가는 끝 계단
ST.steps(-11.0, -9.0, -1.1, 1.1, "-x")
ST.steps(-46.0, -44.0, -1.1, 1.1, "-x")
ST.steps(44.0, 46.0, -1.1, 1.1, "+x")
for L in LANES + PLAYER_BAYS:
    ST.rect(L - 1.5, L + 1.5, 1.1, 3.0)
    ST.steps(L - 1.5, L + 1.5, 1.1, 3.0, "+y")
ST.rect(8.8, 10.2, -12.0, -1.1)                    # 연락호 (후방으로)
ST.steps(8.8, 10.2, -12.0, -10.2, "-y")

F0, F1 = 78.9, 81.1                                # 앞 참호
S0, S1 = 96.9, 99.1                                # 지원 참호
L1 = bk.Trenches("line1", style="r41", depth=0.65)
L1.rect(-44, -10, F0, F1)
L1.rect(-5, 44, F0, F1)
L1.steps(-12.0, -10.0, F0, F1, "+x")
L1.steps(-5.0, -3.0, F0, F1, "-x")
L1.steps(-44.0, -42.0, F0, F1, "-x")
L1.steps(42.0, 44.0, F0, F1, "+x")
FRONT_BAYS = [-39.5, -17.0, 14.5, 39.5]
for bx in FRONT_BAYS:
    L1.rect(bx - 1.5, bx + 1.5, F1, 83.0)
    L1.steps(bx - 1.5, bx + 1.5, F1, 83.0, "+y")
L1.rect(-24.7, -23.3, F1, S0)                      # 연락호
L1.rect(20.3, 21.7, F1, S0)
L1.rect(-30, -10, S0, S1)
L1.rect(-5, 26, S0, S1)
L1.steps(-30.0, -28.0, S0, S1, "-x")
L1.steps(-12.0, -10.0, S0, S1, "+x")
L1.steps(-5.0, -3.0, S0, S1, "-x")
L1.steps(24.0, 26.0, S0, S1, "+x")
SUR1_BAY = (0.5, 3.5)
L1.rect(SUR1_BAY[0], SUR1_BAY[1], 94.9, S0)       # 투항 1: 지원 참호 남쪽 계단 굴
L1.steps(SUR1_BAY[0], SUR1_BAY[1], 94.9, S0, "-y")
for bx in (-20.0, 10.0):
    L1.rect(bx - 1.5, bx + 1.5, S1, 101.0)
    L1.steps(bx - 1.5, bx + 1.5, S1, 101.0, "+y")
L1.fire_step(-42.0, -12.0, F0, F0 + 0.6)
L1.fire_step(-3.0, 42.0, F0, F0 + 0.6)
BUNKERS = [(-32.0, 1.5), (6.0, -1.5), (32.0, 1.5)]   # (중심 x, 문 u)

# ================================================================== ground

G = bk.Ground(H_all)
C.group("terrain")
fx_ = bk.axis_lines(-2600, 2600, 260, fine=[(-1000, 1000, 125)], extra=[NEAR[0], NEAR[1]])
fy_ = bk.axis_lines(-2200, 3200, 260, fine=[(380, 1800, 125)], extra=[NEAR[2], NEAR[3]])


def far_skip(xc, yc):
    return NEAR[0] < xc < NEAR[1] and NEAR[2] < yc < NEAR[3]


G.patch(C, "far", fx_, fy_, key="far_grass", skip=far_skip, collider=False, kind="far")


def H_near(x, y):
    w = max(S((abs(x) - 112.0) / 28.0), S((-82.0 - y) / 28.0), S((y - 772.0) / 28.0))
    z = H_all(x, y)
    if w > 0:
        z += (G.far_lin(0, x, y) - z) * w
    return z


G.fn = H_near
XB = bk.axis_lines(-140, 140, 20, fine=[(-96, 72, 6.2)])
G.patch(C, "rear", XB, bk.axis_lines(-110, -26, 12, fine=[(-62, -26, 5.0)]), fn=H_near)
G.patch(C, "start", XB + ST.xlines(), bk.axis_lines(-26, 14, 5.0, extra=ST.ylines()), fn=H_near, skip=ST.skip)
G.patch(C, "field", XB, bk.axis_lines(14, 68, 6.0), fn=H_near)
G.patch(C, "line1", XB + L1.xlines(), bk.axis_lines(68, 106, 5.0, extra=L1.ylines()), fn=H_near, skip=L1.skip)
LANE_XS = [26.0 + 2.0 * k for k in range(14)]       # 전차 차선 띠 (x 26..52): 깎은 차선 단면이 격자에 보이게
G.patch(C, "north", XB + LANE_XS, bk.axis_lines(106, 800, 20, fine=[(106, 352, 6.5), (352, 546, 6.0), (546, 580, 1.5), (580, 790, 6.0)]), fn=H_near)


def fz(x, y):
    """그 자리 바닥 (참호 안이면 참호 바닥·계단, 아니면 지형)."""
    for T in (ST, L1):
        z = T.floor_z(x, y)
        if z is not None:
            return z
    return G.h(x, y)


CONTRACT = []


def M_(name, x, y, z=None, *, face=None, yaw=None, **props):
    loc = (x, y, fz(x, y) if z is None else z)
    C.marker(name, loc, face=face, yaw=yaw, props=props)
    CONTRACT.append((name, loc))


def north(x, y):
    return (x, y + 10.0)


def south(x, y):
    return (x, y - 10.0)


# 돌격로·호송로 (장애물을 두지 않을 선분)
CHARGE = {}
FINAL_X = [-44.0, -37.0, -31.0, -25.0, -18.0, -12.0, 12.0, 18.0, 25.0, 31.0, 37.0, 44.0]
FINAL_Y = [66.0, 69.0, 64.0, 68.0, 65.0, 70.0, 69.0, 65.0, 68.0, 64.0, 69.0, 66.0]
for i in range(12):
    lane = LANES[i // 2]
    sx = lane + (-0.6 if i % 2 == 0 else 0.6)
    xf = FINAL_X[i]
    p0 = (sx, 0.0)
    p1 = (sx, 9.0)
    p2 = (sx + (xf - sx) * 0.55 + rng.uniform(-1.0, 1.0), 36.0 + rng.uniform(-2.0, 2.0))
    p3 = (xf, FINAL_Y[i])
    CHARGE[i + 1] = [p0, p1, p2, p3]
REAR = [(-13.0, 64.0), (-12.5, 34.0), (-13.0, 0.0), (-14.0, -27.0)]
SUR1 = (2.0, 97.9)
SUR2 = [(27.2, 182.0), (28.6, 182.6), (27.6, 183.6)]
PATHS = [CHARGE[k] for k in CHARGE] + [REAR, [SUR1, REAR[0]], [SUR2[0], REAR[0]]]


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 < 1e-9 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - (ax + dx * t), p[1] - (ay + dy * t))


def clear_of_paths(x, y, r):
    for P in PATHS:
        for a, b in zip(P, P[1:]):
            if seg_dist((x, y), a, b) < r + 1.0:
                return False
    return True


# ================================================================== start trench + rear
C.group("start")
ST.build(C)
sol = bk.Solid("start")
for side, c, a0, a1 in ST.boundary():
    if side == "+y" and abs(c - 1.1) < 1e-3:              # 북쪽 흉벽
        bk.berm(sol, (a0, c), (a1, c), 0.0, (0, 1), w=1.4, h=0.3)
    elif side == "-y" and abs(c + 1.1) < 1e-3:            # 남쪽 배벽 (낮아서 넘어간다)
        bk.berm(sol, (a0, c), (a1, c), 0.0, (0, -1), w=1.1, h=0.22)
sol.flush(C)
# 흉벽 위 모래주머니 (계단 굴 사이 군데군데)
for x0, x1 in ((-37.5, -33.5), (-28.5, -24.5), (-3.5, 3.5), (12.0, 18.0), (25.0, 28.5), (34.0, 37.5)):
    bk.bag_row(C, (x0, 1.2), (x1, 1.2), 0.0, rows=1, col=False, seed=int(x0))
# 참호 깃발·사다리 대신 계단 굴 옆 표지 말뚝, 깃발 넷 (참호 뒤)
for i, x in enumerate((-35.5, -17.5, 17.5, 35.5)):
    bk.fairy_banner(C, x, -3.2, G.h(x, -3.2), yaw=0.0, h=3.8, w=1.0, L=1.5)
# 참호 안 소품: 탄약 상자, 머스킷 거치대
for (x, y) in ((-27.0, -0.55), (-8.0, -0.6), (15.0, -0.6), (35.0, -0.55)):
    bk.fairy_crate(C, x, y, ST.zf, s=0.6, yaw=90, emblem=True)
bk.musket_rack(C, 26.0, -0.5, ST.zf, yaw=0.0, n=5)

C.group("rear")
RX, RY = -14.0, -31.0
for (x, y, yaw) in ((-24.0, -30.0, 90.0), (-24.0, -37.0, 90.0), (-5.0, -38.0, 180.0), (-31.0, -22.0, 60.0)):
    bk.fairy_tent(C, x, y, G.h(x, y), yaw=yaw)
bk.supply_cart(C, -8.0, -27.0, G.h(-8.0, -27.0), yaw=20.0)
for (x, y, s, st, e) in ((-17.5, -35.0, 0.7, 2, True), (-16.6, -36.2, 0.7, 1, False), (-11.0, -34.5, 0.65, 1, True),
                         (-19.0, -26.5, 0.6, 1, False), (-4.0, -32.0, 0.7, 2, True)):
    bk.fairy_crate(C, x, y, G.h(x, y), s=s, yaw=rng.uniform(-20, 20), emblem=e, stack=st)
bk.musket_rack(C, -20.0, -30.5, G.h(-20.0, -30.5), yaw=90.0)
mk.campfire(C, -14.0, -38.5, z=G.h(-14.0, -38.5), lit=True)
for (x, y) in ((-21.0, -40.0), (-8.0, -22.0)):
    bk.fairy_banner(C, x, y, G.h(x, y), yaw=20.0, h=4.2)
# 지휘관 둔덕
KX, KY = 13.0, -17.0
bk.fairy_banner(C, 15.9, -15.4, G.h(15.9, -15.4), yaw=-8.0, h=5.0, w=1.3, L=2.1)
bk.fairy_banner(C, 9.8, -15.6, G.h(9.8, -15.6), yaw=10.0, h=4.0)
bk.war_drum(C, 11.2, -19.0, G.h(11.2, -19.0))
bk.war_drum(C, 11.9, -19.6, G.h(11.9, -19.6), r=0.24)
C.npc("makasha", (12.1, -16.3, G.h(12.1, -16.3)), "characters/makasha.glb", pose="point_far", name="마카샤",
      fallback="characters/fairy_guard_officer.glb", look="none", face=(6.0, 30.0))
C.npc("sila", (14.5, -17.3, G.h(14.5, -17.3)), "characters/sila.glb", pose="cheer", name="실라",
      fallback="characters/fairy_guard_officer.glb", look="player", face=(14.0, 10.0))
CONTRACT.append(("NPC_makasha", (12.1, -16.3, G.h(12.1, -16.3))))
CONTRACT.append(("NPC_sila", (14.5, -17.3, G.h(14.5, -17.3))))
# 보급로 (후방 → 출발 둑길 → 들판 → 참호선 둑길 → 마을)
ROAD = [(-13.0, -46.0), (-13.0, -4.0), (-13.0, 4.0), (-11.5, 40.0), (-7.5, 70.0), (-7.5, 106.0), (-4.0, 124.0),
        (-1.0, 145.0), (-2.0, 168.0), (0.5, 188.0), (-3.0, 208.0), (-6.0, 226.0)]
C.group("field")
bk.drape(C, "earth", ROAD, 3.0, G, lift=0.04, step=2.0, fillet=8.0)
for k in range(2):
    off = -0.75 + 1.5 * k
    bk.drape(C, "mud", [(p[0] + off, p[1]) for p in ROAD[:6]], 0.35, G, lift=0.06, step=2.0, fillet=8.0)

# ================================================================== field
C.group("field")
sol = bk.Solid("field")
CRATERS = [(-3.0, 14.0, 2.6), (9.0, 19.0, 3.2), (-27.0, 18.0, 2.8), (35.5, 14.0, 2.4), (-36.0, 41.0, 3.0),
           (2.0, 41.0, 3.4), (16.0, 34.0, 2.6), (-20.5, 52.0, 2.6), (27.0, 50.0, 3.0), (-6.0, 58.0, 2.4),
           (8.0, 62.0, 2.8), (-44.0, 58.0, 2.4), (44.0, 40.0, 2.6), (-14.0, 27.0, 2.2), (22.0, 23.0, 2.2),
           (39.0, 58.0, 2.4), (-33.0, 63.0, 2.2), (19.0, 74.5, 2.2), (-37.0, 86.0, 2.4), (-14.0, 89.0, 2.6),
           (36.0, 90.0, 2.4), (-40.0, 104.0, 2.6), (30.0, 106.0, 2.4)]
COVERS = []                                     # (x, y, height, enemy_dir)
USED = []
for i, (x, y, r) in enumerate(CRATERS):
    if not clear_of_paths(x, y, r) or L1.inside(x, y, eps=-r * 1.3) or ST.inside(x, y, eps=-r * 1.3):
        continue
    USED.append((x, y, r))
# 돌격로 사이 빈 자리에 구덩이를 더 (작게)
for (x, y) in bk.scatter((-47.0, 47.0, 7.0, 71.0), 14, seed=21, min_d=9.0,
                         avoid=lambda x, y: (not clear_of_paths(x, y, 2.0)
                                             or any(math.hypot(x - a, y - b) < c + 5.0 for a, b, c in USED))):
    USED.append((x, y, rng.uniform(1.6, 2.3)))
for i, (x, y, r) in enumerate(USED):
    bk.crater(C, G, sol, x, y, r, seed=i)
    if y < 76:
        COVERS.append((x, y - r * 0.82, "low", "n"))
print(f"[m9] 포탄 구덩이 {len(USED)}개")
sol.flush(C)
# 돌담 조각 (낮은 엄폐, 남쪽에 COVER)
WALLS = [((-9.0, 22.0), (-3.0, 22.6)), ((3.5, 28.5), (9.5, 28.0)), ((-5.5, 47.5), (0.5, 47.0)),
         ((5.0, 53.5), (11.0, 54.5)), ((-36.0, 30.0), (-33.0, 30.4)), ((26.5, 42.0), (29.5, 42.4)),
         ((-27.5, 44.0), (-24.5, 44.5)), ((34.5, 28.0), (36.8, 28.6)), ((-17.0, 60.0), (-14.0, 59.6))]
for i, (a, b) in enumerate(WALLS):
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    if not all(clear_of_paths(*p, 0.6) for p in (a, mid, b)):
        continue
    bk.stone_wall(C, G, [a, b], h=0.85, seed=i, broken=((1.2, 2.0),) if i % 3 == 0 else ())
    COVERS.append((mid[0], mid[1] - 0.9, "low", "n"))
# 건초 더미·그루터기·불탄 R41 차량·육각 장애물
for i, (x, y, yaw) in enumerate(((-46.5, 22.0, 80), (-45.0, 25.0, 20), (46.0, 30.0, 70), (-46.0, 70.0, 10),
                                 (14.5, 9.5, 60), (46.0, 64.0, 0))):
    if clear_of_paths(x, y, 1.0):
        bk.hay_bale(C, x, y, G.h(x, y), yaw=yaw)
        if abs(x) < 30:
            COVERS.append((x, y - 1.0, "low", "n"))
for i, (x, y) in enumerate(((-29.5, 31.0), (11.0, 46.0), (-1.0, 66.0), (46.5, 50.0), (-47.0, 46.0), (24.0, 60.0))):
    if clear_of_paths(x, y, 0.5):
        bk.stump(C, x, y, G.h(x, y), seed=i, h=rng.uniform(0.6, 1.4))
WRECK = (16.0, 44.5)
if clear_of_paths(*WRECK, 2.0):
    bk.wreck_raider(C, WRECK[0], WRECK[1], G.h(*WRECK), yaw=200.0)
    COVERS.append((WRECK[0] - 0.4, WRECK[1] - 2.4, "high", "n"))
for i, (x, y) in enumerate(((-30.0, 76.0), (-19.0, 76.5), (3.0, 76.0), (26.0, 76.4), (36.0, 76.0), (-41.0, 76.2))):
    if clear_of_paths(x, y, 0.8):
        bk.hedgehog(C, x, y, G.h(x, y), yaw=rng.uniform(0, 60))
# 철조망 띠 (y 73.5, 틈 넷). [오리지널] 돌격하는 요정 경비대가 참호선 15 m 앞에 닿을 때 성전군 전차 둘이 고폭탄으로 통로 둘을 낸다
# (2026-11-04 사용자 지시 「요정 경비대가 돌진할때 전차들은 포격으로 철조망을 철거해줘. 고폭탄 사용해.」, 「경비대가 참호선 앞 15m쯤
# 도달했을때 고폭탄 작렬시켜」, 미션 src/game/missions/m9.charge.ts WIRE_LANES).
# 통로 자리 5 m만 부서지는 소품(BRK_wire_lane_w·e: 주포 고폭탄 3.5 m 안이면 무너진다, level/destructibles.ts)이고 나머지 띠는
# 그대로 정적 묶음이다. 부서진 모습(BRKD_)은 고폭탄에 찢겨 흩어진 고리 토막·땅에 늘어진 가닥·날아가 쓰러진 말뚝·그을린 땅이다
# (높이 0.25 m 아래, 충돌체 없음: 넘어 다닌다). 통로는 언덕 고슴도치(y 76) 사이에 둔다
WIRE_Y = 73.5
WIRE_LANES = (("w", -18.0, -13.0), ("e", 4.5, 9.5))


def wire_blasted(x0, x1, y, seed):
    """고폭탄에 찢긴 철조망 (부서진 모습). 폭심은 통로 가운데 앞(남쪽)이라 토막은 대부분 북쪽으로 날아갔다."""
    rr = random.Random(seed)
    cx = (x0 + x1) / 2
    L = x1 - x0
    bmw = C.bm("wire", "fine")
    # 그을린 땅: 폭심 둘레 (지형 데칼, 다른 마른 풀·그을음 원판보다 조금 위)
    bk.ground_disc(C, "scorch_e", cx, y - 0.4, L * 0.55, G, n=12, rings=2, lift=0.05, seed=seed)
    bk.ground_disc(C, "scorch_e", cx + rr.uniform(-1.0, 1.0), y + 1.6, L * 0.32, G, n=10, rings=1, lift=0.052, seed=seed + 1)
    # 찢긴 고리 토막: 오각 고리의 두세 변만, 기울어 흩어짐
    for k in range(9):
        qx = rr.uniform(x0 - 0.6, x1 + 0.6)
        qy = y + rr.uniform(-1.2, 2.8) * (1.0 if k % 3 else 0.6)
        z0 = G.h(qx, qy)
        r = rr.uniform(0.22, 0.34)
        a0 = rr.uniform(0, 2 * math.pi)
        tilt = rr.uniform(0.25, 0.6)
        yaw = rr.uniform(0, 2 * math.pi)
        cyw, syw = math.cos(yaw), math.sin(yaw)
        segs = rr.randint(2, 3)
        pts = []
        for i in range(segs + 1):
            a = a0 + 2 * math.pi * i / 5
            u, v = math.cos(a) * r, math.sin(a) * r
            lx, lz = u, v * tilt
            pts.append(Vector((qx + lx * cyw, qy + lx * syw, z0 + 0.04 + r * tilt + lz)))
        for i in range(segs):
            pa, pb = pts[i], pts[i + 1]
            w = Vector((-syw, cyw, 0)) * 0.012
            bmw.faces.new([bmw.verts.new(pa - w), bmw.verts.new(pb - w), bmw.verts.new(pb + w), bmw.verts.new(pa + w)])
    # 땅에 늘어진 가닥 토막
    for k in range(7):
        qx = rr.uniform(x0 - 0.8, x1 + 0.8)
        qy = y + rr.uniform(-0.8, 2.4)
        ang = rr.uniform(0, 2 * math.pi)
        ln = rr.uniform(0.5, 1.4)
        ex, ey = qx + math.cos(ang) * ln, qy + math.sin(ang) * ln
        C.strip("wire", (qx, qy, G.h(qx, qy) + 0.05), (ex, ey, G.h(ex, ey) + 0.06), 0.014, normal=(0, 0, 1), lift=0.0)
    # 말뚝: 날아가 쓰러진 것 셋, 부러져 선 그루터기 하나
    for k in range(3):
        qx = rr.uniform(x0, x1)
        qy = y + rr.uniform(0.6, 2.6)
        ang = rr.uniform(0, 2 * math.pi)
        z0 = G.h(qx, qy)
        C.beam("stake", (qx, qy, z0 + 0.04), (qx + math.cos(ang) * 0.75, qy + math.sin(ang) * 0.75, z0 + 0.06), 0.05, 0.05,
               kind="detail")
    sx = rr.uniform(x0 + 0.8, x1 - 0.8)
    C.beam("stake", (sx, y, G.h(sx, y) - 0.1), (sx + 0.04, y + 0.03, G.h(sx, y) + 0.24), 0.05, 0.05, kind="detail")


for (x0, x1) in ((-47.0, -26.0), (-23.0, -11.5), (-4.5, 11.0), (15.0, 29.0), (33.0, 47.0)):
    a = x0
    for (nm, l0, l1) in WIRE_LANES:
        if not (x0 < l0 and l1 < x1):
            continue
        bk.wire_coil(C, G, (a, WIRE_Y), (l0, WIRE_Y), seed=int(a))
        # 이름 있는 통로는 차례 번호를 쓰지 않는다 (뒤 구역의 BRK_wire_nn 이름이 밀리지 않게)
        brk_n = dict(bk._BRK_COUNT)
        with bk.Breakable(C, "wire", f"lane_{nm}") as brk:
            bk.wire_coil(C, G, (l0, WIRE_Y), (l1, WIRE_Y), seed=int(l0 * 7))
            with brk.broken():
                wire_blasted(l0, l1, WIRE_Y, seed=int(l0 * 13) + 500)
        bk._BRK_COUNT.clear()
        bk._BRK_COUNT.update(brk_n)
        a = l1
    bk.wire_coil(C, G, (a, WIRE_Y), (x1, WIRE_Y), seed=int(x0) if a == x0 else int(a))
# 마른 풀 자국·그을음
for i in range(18):
    x, y = rng.uniform(-46, 46), rng.uniform(-40, 74)
    if ST.inside(x, y, eps=-4) or L1.inside(x, y, eps=-4):
        continue
    bk.ground_disc(C, "dry" if i % 3 else "meadow_d", x, y, rng.uniform(2.0, 4.5), G, n=10, rings=1, lift=0.035,
                   seed=i)
for i, (x, y) in enumerate(((-3.0, 14.0), (2.0, 41.0), (27.0, 50.0), (16.0, 44.5), (-20.0, 52.0))):
    bk.ground_disc(C, "scorch_e", x + 1.5, y + 1.5, 2.4, G, n=10, rings=1, lift=0.025, seed=40 + i)
# 생울타리 (들판 양쪽)
bk.hedgerow(C, G, [(-49.5, -44.0), (-49.5, 12.0)], seed=1)
bk.hedgerow(C, G, [(-49.5, 18.0), (-49.5, 112.0)], seed=2)
bk.hedgerow(C, G, [(49.5, -44.0), (49.5, 50.0)], seed=3)
bk.hedgerow(C, G, [(49.5, 56.0), (49.5, 112.0)], seed=4)
bk.hedgerow(C, G, [(-49.0, -46.5), (49.0, -46.5)], seed=5, h=1.7)
for i, (x, y) in enumerate(((-49.5, 30.0), (49.5, 8.0), (-49.5, 84.0), (49.5, 96.0), (-49.0, -20.0))):
    bk.tree_round(C, x, y, G.h(x, y), h=rng.uniform(7.5, 9.5), seed=i)

# ================================================================== R41 line 1
C.group("line1")
L1.build(C)
sol = bk.Solid("line1")
SANDBAG_X = [-36.0, -26.0, -19.0, 2.0, 18.0, 36.0]       # 앞 참호 사격 자리 (모래주머니 흉벽)
for side, c, a0, a1 in L1.boundary():
    if side == "-y" and abs(c - F0) < 1e-3:               # 앞 참호 남쪽 흉벽
        cuts = sorted((x - 1.5, x + 1.5) for x in SANDBAG_X if a0 < x < a1)
        cur = a0
        for lo, hi in cuts:                               # 사격 자리: 낮은 모래주머니 한 줄 (총구가 넘어가게)
            if lo > cur:
                bk.berm(sol, (cur, c), (lo, c), 0.0, (0, -1), w=1.6, h=0.32)
            bk.bag_row(C, (lo, c - 0.2), (hi, c - 0.2), 0.0, rows=1, seed=int(lo * 3))
            cur = hi
        if a1 > cur:
            bk.berm(sol, (cur, c), (a1, c), 0.0, (0, -1), w=1.6, h=0.32)
    elif side == "-y" and abs(c - S0) < 1e-3:             # 지원 참호 남쪽 흉벽
        bk.berm(sol, (a0, c), (a1, c), 0.0, (0, -1), w=1.4, h=0.3)
    elif side == "+y" and abs(c - F1) < 1e-3:             # 앞 참호 북쪽 배벽 (벙커 자리 빼고)
        segs = [(a0, a1)]
        for (bx, _) in BUNKERS:
            nxt = []
            for lo, hi in segs:
                if hi <= bx - 3 or lo >= bx + 3:
                    nxt.append((lo, hi))
                else:
                    if lo < bx - 3:
                        nxt.append((lo, bx - 3))
                    if hi > bx + 3:
                        nxt.append((bx + 3, hi))
            segs = nxt
        for lo, hi in segs:
            if hi - lo > 0.3:
                bk.berm(sol, (lo, c), (hi, c), 0.0, (0, 1), w=1.0, h=0.22)
sol.flush(C)
for i, (bx, du) in enumerate(BUNKERS):
    bk.r41_bunker(C, bx - 3.0, bx + 3.0, F1 - 0.05, F1 + 4.4, L1.zf, 0.0, door=(du, 0.95), seed=i)
# 참호선 뒤: 컨테이너, 상자, 연료통, 불탄 벙커 연기
bk.r41_container(C, -36.0, 91.5, G.h(-36.0, 91.5), axis="x", L=5.2, door="+y", label="R41-21")
bk.r41_container(C, 33.0, 92.0, G.h(33.0, 92.0), axis="x", L=5.2, door="-y", label="R41-22", burnt=True)
for (x, y, st) in ((-31.0, 89.0, 2), (-29.8, 89.4, 1), (27.0, 88.0, 1), (12.0, 90.0, 2), (-18.0, 104.5, 1)):
    bk.r41_crate(C, x, y, G.h(x, y), yaw=rng.uniform(-15, 15), stack=st)
for (x, y) in ((14.0, 88.5), (14.7, 89.1), (-40.0, 94.0)):
    bk.drum_r41(C, x, y, G.h(x, y))
bk.drum_r41(C, 13.0, 87.6, G.h(13.0, 87.6), lie=True, yaw=40)
bk.smoke(C, 32.0, 92.0, G.h(32.0, 92.0) + 2.0, h=40.0, r=2.6, seed=3, dark=0.55, kind="fine", segs=8, rings=5)
for (x, y) in ((-26.0, 86.0), (2.0, 87.0), (-3.0, 103.0), (20.0, 103.0)):
    COVERS.append((x, y, "low", "n"))

# ================================================================== village
C.group("village")
for (cx, cy, w, d, ax, door, roof, broken, seed) in COTTAGES:
    bk.cottage(C, G, cx, cy, w=w, d=d, axis=ax, door=door, roof=roof, broken=broken, seed=seed)
bk.smoke(C, 13.0, 141.0, G.h(13.0, 141.0) + 2.0, h=46.0, r=2.8, seed=7, dark=0.5, kind="fine", segs=8, rings=5)
bk.windmill(C, G, MILL[0], MILL[1], sail_yaw=-35.0, broken=True, seed=2)
bk.well(C, WELL[0], WELL[1], G.h(*WELL))
# 남쪽 돌담 (틈: 보급로, x 8..11, 27..31) + 마을 안 돌담
bk.stone_wall(C, G, [(-36.0, 121.0), (-7.8, 121.0)], seed=11, broken=((9.0, 11.0),))
bk.stone_wall(C, G, [(-0.8, 121.0), (8.0, 121.0)], seed=12)
bk.stone_wall(C, G, [(11.0, 121.0), (27.0, 121.0)], seed=13)
bk.stone_wall(C, G, [(31.0, 121.0), (46.0, 121.0)], seed=14)
bk.stone_wall(C, G, [(-30.0, 152.0), (-9.0, 152.0)], seed=15, broken=((7.0, 9.0),))
bk.stone_wall(C, G, [(6.0, 155.0), (24.0, 155.0)], seed=16)
bk.stone_wall(C, G, [(22.0, 132.0), (40.0, 132.0)], seed=17)
bk.stone_wall(C, G, [(40.0, 132.0), (40.0, 176.0)], seed=18, broken=((20.0, 23.0),))
bk.stone_wall(C, G, [(-31.0, 181.0), (-24.0, 181.0)], seed=19)
for (x0, x1, y) in ((-30.0, -9.0, 152.0), (6.0, 24.0, 155.0), (-36.0, -7.8, 121.0), (11.0, 27.0, 121.0),
                    (-0.8, 8.0, 121.0), (22.0, 40.0, 132.0)):
    for k in range(2):
        COVERS.append((x0 + (x1 - x0) * (0.3 + 0.4 * k), y - 0.9, "low", "n"))
# 정원 울타리·고기 나무·건초·수레
bk.picket(C, G, (-24.0, 131.5), (-12.0, 131.5), broken=((4.0, 6.0),), seed=1)
bk.picket(C, G, (9.0, 136.0), (18.0, 136.0), seed=2)
for (x, y) in ((-26.0, 128.0),):
    mk.meat_tree(C, x, y, h=4.0, seed=int(x) - 1, z=G.h(x, y))   # seed -26은 잎 덩어리 둘이 거의 한 면에서 겹친다
for (x, y, yaw) in ((24.0, 160.0, 30), (25.4, 158.6, 75), (-28.0, 175.0, 10)):
    bk.hay_bale(C, x, y, G.h(x, y), yaw=yaw)
bk.supply_cart(C, -6.5, 183.0, G.h(-6.5, 183.0), yaw=110.0, load=False, seed=3)
for i, (x, y) in enumerate(((-29.0, 140.0), (25.0, 147.0), (-6.0, 203.0), (27.0, 207.0), (36.0, 200.0),
                            (42.0, 192.0), (-30.0, 200.0), (37.0, 142.0))):
    bk.tree_round(C, x, y, G.h(x, y), h=rng.uniform(6.5, 8.5), seed=20 + i)
    C.col(x - 0.3, x + 0.3, y - 0.3, y + 0.3, G.h(x, y) - 0.3, G.h(x, y) + 4.0)
# R41 잔당: 차단벽·모래주머니·전진 초소 컨테이너
for (x, y, yaw) in ((-6.0, 158.0, 0), (1.5, 158.2, 5), (-13.0, 162.0, -20)):
    bk.r41_barrier(C, x, y, G.h(x, y), yaw=yaw)
    COVERS.append((x, y - 0.9, "low", "n"))
bk.bag_row(C, (4.0, 157.4), (7.6, 157.4), 0.0, rows=3, zfn=G.h, seed=5)
bk.r41_container(C, POST[0], POST[1], G.h(*POST), axis="y", L=5.4, door="-x", label="R41-31")
COVERS.append((POST[0] - 0.4, POST[1] - 3.4, "high", "n"))
for (x, y, st) in ((2.8, 173.0, 2), (9.0, 172.6, 1), (-9.5, 164.0, 1)):
    bk.r41_crate(C, x, y, G.h(x, y), yaw=rng.uniform(-20, 20), stack=st)
for i, (x, y, r) in enumerate(((-4.0, 150.0, 2.2), (9.0, 186.0, 2.4), (-30.0, 160.0, 2.2), (22.0, 186.0, 2.0))):
    bk.ground_disc(C, "scorch_e", x, y, r * 0.8, G, n=10, rings=1, lift=0.04, seed=60 + i)
# 서쪽 옆길 (생울타리 사이, 측면 우회로)
bk.hedgerow(C, G, [(-36.0, 125.0), (-36.0, 148.0)], seed=21)
bk.hedgerow(C, G, [(-36.0, 152.0), (-36.0, 176.0)], seed=22)
bk.hedgerow(C, G, [(-36.0, 180.0), (-36.0, 203.0)], seed=23)
bk.hedgerow(C, G, [(-44.0, 112.0), (-44.0, 211.0)], seed=24)
bk.hedgerow(C, G, [(47.0, 114.0), (47.0, 212.0)], seed=25)
bk.drape(C, "earth", [(-40.0, 110.0), (-40.0, 150.0), (-40.0, 190.0), (-38.0, 206.0), (-28.0, 214.0), (-12.0, 222.0)], 2.2,
         G, lift=0.04, step=2.0, fillet=8.0)
bk.drape(C, "earth", [(-1.0, 150.0), (12.0, 160.0), (24.0, 176.0), (28.0, 181.0)], 1.6, G, lift=0.045, step=2.0,
         fillet=6.0)
for (x, y) in ((-39.0, 135.0), (-41.0, 165.0), (-39.0, 190.0)):
    COVERS.append((x, y, "high", "n"))

# ================================================================== HQ compound
C.group("hq")
HX0, HX1, HY0, HY1 = -26.0, 14.0, 228.0, 272.0
ZH = 3.0
bk.hq_fence(C, G, (HX0, HY0), (HX1, HY0), gaps=((16.5, 23.5),))
bk.hq_fence(C, G, (HX0, HY1), (HX1, HY1), gaps=((7.5, 13.5),))
bk.hq_fence(C, G, (HX0, HY0), (HX0, HY1))
# [오리지널] 동쪽 울타리의 포탄 구멍 (y 258..266.5): 지휘 회선을 끊은 콘솔에서 능선 길 어귀(17,266)로 곧장 나가는 앞길 (레일슈터 외길 동선,
# 2026-11-04 사용자 「레일슈터에 맞게 동선배치나 레벨 디자인좀 손좀 봐줘」). 예전에는 뒷문(북서)이나 남문으로 나가 울타리를 돌아가야 했다.
# 쓰러진 철망 토막은 바깥(동쪽) 땅에 눕고(충돌 없음), 구멍 앞에는 포탄 구덩이 (아래 hq 구덩이 목록)
HQ_BREACH = (258.0, 266.5)
bk.hq_fence(C, G, (HX1, HY0), (HX1, HY1), gaps=((HQ_BREACH[0] - HY0, HQ_BREACH[1] - HY0),))
bk._mesh_fence_flat(C, G, Vector((HX1, HQ_BREACH[0] + 0.4, 0.0)), Vector((HX1, HQ_BREACH[0] + 4.2, 0.0)), 2.0, random.Random(258))
bk._mesh_fence_flat(C, G, Vector((HX1, HQ_BREACH[1] - 3.6, 0.0)), Vector((HX1, HQ_BREACH[1] - 0.4, 0.0)), 2.0, random.Random(266))
bk.ground_disc(C, "scorch_e", HX1 + 2.5, 262.0, 3.0, G, n=12, rings=2, lift=0.045, seed=262)
bk.drape(C, "earth", [(HX1 - 3.0, 262.0), (HX1 + 1.0, 262.4), (17.0, 266.0)], 1.8, G, lift=0.05, step=1.5, fillet=4.0)
bk.hq_gate(C, -6.0, HY0, G.h(-6.0, HY0), yaw=0.0, w=6.4)
bk.hq_gate(C, -15.5, HY1, G.h(-15.5, HY1), yaw=180.0, w=5.4, sign=("R41 · 후문", "REAR GATE"))
CP = bk.command_post(C, -4.0, 262.0, ZH, L=6.6, W=2.7, H=2.5, door_u=-1.3)
# 차양 + 작전 탁자 (지휘 컨테이너 서쪽)
for (x, y) in ((-14.2, 259.0), (-14.2, 265.0), (-7.6, 259.0), (-7.6, 265.0)):
    C.cyl("r41_metal", (x, y, ZH), (x, y, ZH + 2.3), 0.05, segs=6, kind="detail")
    C.col(x - 0.06, x + 0.06, y - 0.06, y + 0.06, ZH, ZH + 2.3)            # 차양 기둥
bk.quad_slab(C.bm("r41_tarp", "main"), [(-14.6, 258.6, ZH + 2.15), (-7.3, 258.6, ZH + 2.15), (-7.3, 265.4, ZH + 2.5),
                                        (-14.6, 265.4, ZH + 2.5)], 0.04)
bk.map_table(C, -11.0, 262.0, ZH, yaw=0.0)
bk.antenna_mast(C, 6.0, 263.0, ZH, h=14.0, guy=6.0)
bk.generator(C, -18.0, 268.0, ZH, yaw=180.0)
bk.cable(C, [(-17.0, 267.4, ZH + 0.05), (-12.0, 266.4, ZH + 0.03), (-7.4, 263.5, ZH + 0.03)])
bk.cable(C, [(5.2, 263.0, ZH + 0.05), (0.0, 263.6, ZH + 0.03), (-0.6, 263.0, ZH + 0.5)])
bk.r41_container(C, -20.0, 244.0, ZH, axis="y", L=5.6, door="+x", label="R41-HQ2")
bk.r41_container(C, 8.0, 246.0, ZH, axis="y", L=5.6, door="-x", label="R41-HQ3")
bk.r41_container(C, 7.5, 237.0, ZH, axis="x", L=4.8, door="-y", label="R41-HQ4", burnt=True)
mk.tent(C, -17.0, 255.0, yaw=90.0, w=3.0, d=4.2, h=2.1, key="r41_tarp", z=ZH)   # COL은 도시 키트 천막 껍질
for (cx, cy) in ((-12.5, 232.0), (0.5, 232.0)):
    bk.bag_row(C, (cx - 1.6, cy), (cx + 1.6, cy), ZH, rows=3, seed=int(cx))
    bk.bag_row(C, (cx - 1.8, cy + 0.2), (cx - 1.8, cy + 1.6), ZH, rows=2, seed=int(cx) + 1)
    bk.bag_row(C, (cx + 1.8, cy + 0.2), (cx + 1.8, cy + 1.6), ZH, rows=2, seed=int(cx) + 2)
bk.bag_row(C, (2.5, 260.0), (5.5, 260.0), ZH, rows=2, seed=31)
for (x, y) in ((-23.0, 231.0), (11.0, 231.0), (-23.0, 269.0), (11.0, 269.0)):
    bk.floodlight(C, x, y, ZH, yaw=bk.face_yaw((x, y), (-6.0, 250.0)))
for (x, y, st) in ((-23.0, 250.0, 2), (-22.6, 251.0, 1), (10.5, 252.0, 2), (-9.0, 246.0, 1), (-8.2, 246.6, 1),
                   (1.0, 268.5, 1)):
    bk.r41_crate(C, x, y, ZH, yaw=rng.uniform(-15, 15), stack=st)
for (x, y) in ((-22.0, 238.0), (-22.6, 238.6), (-21.4, 239.0), (-16.0, 268.6)):
    bk.drum_r41(C, x, y, ZH)
# 지휘소 앞: 차단벽 지그재그 + 철조망 + 구덩이
for (x, y, yaw) in ((-10.0, 221.0, 0.0), (-2.5, 218.0, 0.0), (-13.5, 214.0, 10.0)):
    bk.r41_barrier(C, x, y, G.h(x, y), yaw=yaw, w=2.2)
    COVERS.append((x, y - 0.9, "low", "n"))
bk.wire_coil(C, G, (-25.0, 225.6), (-10.5, 225.6), seed=71)
bk.wire_coil(C, G, (-1.5, 225.6), (13.0, 225.6), seed=72)
sol = bk.Solid("hq")
for i, (x, y, r) in enumerate(((10.0, 214.0, 2.6), (-24.0, 216.0, 2.4), (24.0, 236.0, 2.6), (-34.0, 246.0, 2.4),
                               (19.5, 258.5, 1.8))):             # 마지막: 동쪽 울타리 포탄 구멍 앞
    bk.crater(C, G, sol, x, y, r, seed=80 + i)
sol.flush(C)
for (x, y, h) in ((-20.0, 247.5, "high"), (5.0, 249.0, "high"), (-12.5, 234.0, "low"), (0.5, 234.0, "low"),
                  (4.0, 258.8, "low")):
    COVERS.append((x, y, h, "n"))
bk.hedgerow(C, G, [(-40.0, 212.0), (-40.0, 276.0)], seed=31)
bk.hedgerow(C, G, [(40.0, 214.0), (40.0, 262.0)], seed=32)

# ================================================================== ridge
C.group("ridge")
RIDGE_PATH = [(17.0, 266.0), (21.0, 278.0), (24.5, 292.0), (20.0, 306.0), (11.0, 318.0), (5.0, 330.0), (2.0, 340.0)]
PP = bk.drape(C, "earth", RIDGE_PATH, 1.8, G, lift=0.05, step=1.5, fillet=6.0)
PPXY = [(p.x, p.y) for p in PP]


def near_path(x, y, r):
    return any((x - px) ** 2 + (y - py) ** 2 < r * r for px, py in PPXY)


def forest_avoid(x, y):
    if HX0 - 4 < x < HX1 + 4 and y < 277:
        return True
    if near_path(x, y, 3.4):
        return True
    if math.hypot(x - RIDGE[0], y - RIDGE[1]) < 10.5:
        return True
    if y > 341.0 and abs(x - RIDGE[0]) < 26:
        return True
    if -26 < x < -6 and y < 294:
        return True                                   # 후문 밖 (지휘소 증원 자리)
    return near_lane(x, y, LANE_CLEAR)               # 전차 차선


TREES = bk.scatter((-44.0, 44.0, 276.0, 346.0), 64, seed=4, avoid=forest_avoid, min_d=5.0)
for i, (x, y) in enumerate(TREES):
    z = G.h(x, y)
    if i % 5 in (0, 2, 3):
        bk.conifer(C, x, y, z, h=rng.uniform(8.0, 12.0), seed=i, ground=G.h)   # 비탈에서도 잎 밑면이 머리 + 점프 위
    else:
        bk.tree_round(C, x, y, z, h=rng.uniform(7.0, 9.5), seed=i, keys=("foliage", "foliage_au", "foliage_d"))
    C.col(x - 0.28, x + 0.28, y - 0.28, y + 0.28, z - 0.3, z + 4.0)
# 성전군 전차 차선 (지휘소 앞 → 능선 마루): 흙길 + 궤도 자국 둘. 마루 너머는 '숲 내리막'에서
def lane_road(pts):
    bk.drape(C, "earth", pts, 5.6, G, lift=0.05, step=1.5, fillet=10.0)
    for off in (-1.3, 1.3):
        bk.drape(C, "mud", bk_offset(pts, off), 0.6, G, lift=0.07, step=1.5, fillet=10.0)


def bk_offset(pts, off):
    """선을 옆으로 off m (진행 방향 오른쪽 +) 민다 (꼭짓점은 앞뒤 방향 평균)."""
    out = []
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        out.append((x + dy / L * off, y - dx / L * off))
    return out


lane_road(TANK_LANE[:LANE_CREST + 1])
# 전망대: 바위 턱 + 쓰러진 통나무 + 낡은 난간
for i, (x, y, s) in enumerate(((-6.8, 346.0, 1.6), (-9.5, 344.6, 1.3), (10.6, 345.6, 1.8), (13.0, 344.2, 1.2),
                               (-3.6, 348.4, 0.8))):            # (4.8, 347.2)의 작은 바위는 내리막 길목이라 옮겼다
    mk.rock(C, x, y, s=s, z=G.h(x, y) - 0.15, seed=i)
LOG = ((-3.5, 337.0, G.h(-3.5, 337.0) + 0.22), (0.2, 335.4, G.h(0.2, 335.4) + 0.22))
C.cyl("bark_d", LOG[0], LOG[1], 0.24, segs=8)
bk.bm_col(C, lambda b: mk._bm_cyl(b, LOG[0], LOG[1], 0.24, segs=8))   # 비스듬한 통나무 그대로 (예전 축 상자는 0.4 m 넘게 컸다)
for (x, y, hh) in ((-11.0, 346.4, 0.85), (-9.2, 346.7, 0.6), (13.5, 346.2, 0.8), (15.3, 345.8, 0.7)):
    C.beam("timber", (x, y, G.h(x, y) - 0.2), (x, y, G.h(x, y) + hh), 0.1, 0.1, kind="detail")
    C.col(x - 0.06, x + 0.06, y - 0.06, y + 0.06, G.h(x, y) - 0.2, G.h(x, y) + hh)     # 낡은 난간 기둥
for (a, b) in (((-11.0, 346.4, G.h(-11.0, 346.4) + 0.7), (-9.2, 346.7, G.h(-9.2, 346.7) + 0.5)),
               ((13.5, 346.2, G.h(13.5, 346.2) + 0.65), (15.0, 347.0, G.h(15.0, 347.0) + 0.08))):
    C.beam("timber", a, b, 0.07, 0.07, kind="detail")
    bk.beam_col(C, a, b, 0.09, z_min=min(G.h(*a[:2]), G.h(*b[:2])) + 0.3)              # 가로대 (발목 위)
bk.ground_disc(C, "dry", RIDGE[0] - 1.0, RIDGE[1] - 1.5, 3.2, G, n=10, rings=2, lift=0.04, seed=91)
mk.flowers(C, -5.0, 341.0, r=2.0, n=6, seed=3, z=G.h(-5.0, 341.0))
mk.flowers(C, 9.0, 339.0, r=2.0, n=6, seed=4, z=G.h(9.0, 339.0))
# [오리지널] 능선 R41 후위 감시조 (능선 단계의 짧은 싸움: 진압반 선봉이 능선 길을 먼저 올라 친다, 2026-11-04 레일슈터 동선).
# 전망대 빈터(나무 없는 반경 10.5 m) 남쪽 끝의 모래주머니 둥지 둘: 능선 길(5,330)을 내려다본다. 병사는 ENEMY_rg_* (ridge, manual)
RIDGE_NESTS = [(7.0, 332.6), (-4.2, 333.0)]
for i, (nx, ny) in enumerate(RIDGE_NESTS):
    zn = G.h(nx, ny)
    bk.bag_row(C, (nx - 1.5, ny - 1.0), (nx + 1.5, ny - 1.0), 0.0, rows=3, zfn=G.h, seed=340 + i)
    bk.bag_row(C, (nx - 1.7, ny - 0.8), (nx - 1.7, ny + 0.4), 0.0, rows=2, zfn=G.h, seed=342 + i)
    bk.bag_row(C, (nx + 1.7, ny - 0.8), (nx + 1.7, ny + 0.4), 0.0, rows=2, zfn=G.h, seed=344 + i)
    COVERS.append((nx, ny - 1.9, "low", "n"))
# 숲 둘레 (경계 밖 언덕): 가까운 침엽수 띠 + 먼 숲
NEAR_TREES = bk.scatter(lambda r: (r.choice((-1, 1)) * r.uniform(52.0, 78.0), r.uniform(-60.0, 350.0)), 70, seed=5,
                        min_d=6.0)
for i, (x, y) in enumerate(NEAR_TREES):
    inside = abs(x) < 55.0                       # 생울타리 틈으로 들어가는 경계 안쪽 띠의 나무: 줄기 COL, 잎 밑면은 머리 + 점프 위
    if i % 3:
        bk.conifer(C, x, y, G.h(x, y), h=rng.uniform(9.0, 13.0), seed=100 + i, ground=G.h if inside else None)
    else:
        bk.tree_round(C, x, y, G.h(x, y), h=rng.uniform(8.0, 10.0), seed=100 + i)
    if inside:
        C.col(x - 0.3, x + 0.3, y - 0.3, y + 0.3, G.h(x, y) - 0.3, G.h(x, y) + 4.0)

# ================================================================== 진격로 연장 (2026-11-03): 전망대 → 성문 앞
# [오리지널] 리타의 분대가 능선에서 내려가 에르피엔 바깥 성문 앞까지 길을 연다. 리뉴아(R41)를 따르는 R41 잔당이 성문을
#   포위하고 있다. 동쪽 차선으로 성전군 전차(노획 M1A1, 모나티엄 엘프 승무원)가 나란히 간다.
EXT_COVERS = []                                    # (x, y, height): 적은 북쪽에 있다


def ext_cover(x, y, h="low"):
    EXT_COVERS.append((x, y, h))


def lane(fn, *args, cover=None, **kw):
    """성전군 전차 차선 위의 장애물 (철조망·모래주머니·낮은 담·울타리): 전차가 돌아가지 않고 깔고 지나간다.
    부서지는 소품 키트(battlefield_kit의 breakable=True)가 있으면 켜서 세우고, 아직 없으면 세우지 않는다(전차가 막히지 않게).
    키트가 들어오면 레벨을 다시 굽기만 하면 된다. cover = (x, y, h): 세웠을 때만 엄폐 마커"""
    if "breakable" not in inspect.signature(fn).parameters:
        return False
    fn(*args, breakable=True, **kw)
    if cover:
        ext_cover(*cover)
    return True


# ---- 숲 내리막 (전망대 바위 틈 → 골짜기)
C.group("descent")
TP = bk.drape(C, "earth", TRACK + [JUNCTION], 2.2, G, lift=0.05, step=1.5, fillet=8.0)
TPXY = [(p.x, p.y) for p in TP]


def near_track(x, y, r):
    return any((x - px) ** 2 + (y - py) ** 2 < r * r for px, py in TPXY)


def descent_avoid(x, y):
    if not in_corridor(x, y, 2.0):
        return True
    if near_track(x, y, 4.6) or near_lane(x, y, LANE_CLEAR):
        return True
    return math.hypot(x - RIDGE[0], y - RIDGE[1]) < 12.0


lane_road(TANK_LANE[LANE_CREST:])                   # 전차 차선 내리막 (마루 → 헛간과 창고 사이)
DTREES = bk.scatter((-46.0, 62.0, 350.0, 458.0), 64, seed=41, avoid=descent_avoid, min_d=6.5)
for i, (x, y) in enumerate(DTREES):
    z = G.h(x, y)
    if i % 5 in (0, 2, 3):
        bk.conifer(C, x, y, z, h=rng.uniform(8.5, 12.5), seed=200 + i, ground=G.h)
    else:
        bk.tree_round(C, x, y, z, h=rng.uniform(7.0, 9.5), seed=200 + i, keys=("foliage", "foliage_au", "foliage_d"))
    C.col(x - 0.28, x + 0.28, y - 0.28, y + 0.28, z - 0.3, z + 4.0)
# 길가 바위·쓰러진 통나무 (내려가며 숨는 자리)
for i, (x, y, s) in enumerate(((10.5, 384.0, 1.5), (-4.0, 404.0, 1.7), (7.5, 430.0, 1.4), (-7.0, 452.0, 1.6),
                               (5.0, 458.0, 1.3))):
    mk.rock(C, x, y, s=s, z=G.h(x, y) - 0.15, seed=60 + i)
    ext_cover(x, y - s * 0.7)
for (a, b) in (((-9.5, 438.0), (-4.2, 441.5)), ((6.0, 446.0), (11.5, 444.0))):
    za, zb = G.h(*a) + 0.26, G.h(*b) + 0.26
    C.cyl("bark_d", (a[0], a[1], za), (b[0], b[1], zb), 0.28, segs=8)
    bk.bm_col(C, lambda bb, a=a, b=b, za=za, zb=zb: mk._bm_cyl(bb, (a[0], a[1], za), (b[0], b[1], zb), 0.28, segs=8))
    ext_cover((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.8)

# ---- 골짜기 바닥: 동서 길, 갈림길 차단선 (1구역), 서쪽 농가, 동쪽 헛간 (전차 집결지)
C.group("valley")
bk.drape(C, "earth", VROAD, 3.6, G, lift=0.04, step=2.0, fillet=12.0)
# 0.04: 남쪽 길 위 포탄 구덩이(vcr3)의 진흙 원판(0.045)과 같은 높이에 겹쳐 깜빡였다
bk.drape(C, "earth", SOUTH_ROAD, 3.4, G, lift=0.04, step=2.0, fillet=10.0)
for k in range(2):
    off = -0.8 + 1.6 * k
    bk.drape(C, "mud", [(p[0], p[1] + off) for p in VROAD[1:-1]], 0.35, G, lift=0.06, step=2.0, fillet=12.0)
FW = bk.cottage(C, G, FARM_W[0], FARM_W[1], w=9.0, d=6.0, axis="x", door="-y", roof="roof_r", broken=0.2, seed=31, h=2.8)
bk.cottage(C, G, BARN_E[0], BARN_E[1], w=16.0, d=9.0, axis="x", door="+y", roof="thatch", broken=0.0, seed=32, h=3.8,
           chimney=False, flowers=False)
bk.cottage(C, G, SHED_E[0], SHED_E[1], w=7.0, d=5.6, axis="y", door="-x", roof="roof_g", broken=0.35, seed=33, h=2.6,
           chimney=False)
# 밭 (그루터기·건초 줄), 낮은 돌담, 우물 대신 물통·수레
for i, (x0, x1, y0, y1, key) in enumerate(((-52.0, -16.0, 506.0, 530.0, "dry"), (6.0, 58.0, 518.0, 538.0, "meadow_d"),
                                           (-56.0, -24.0, 466.0, 480.0, "meadow_d"))):
    for k in range(int((y1 - y0) // 3.2)):
        yy = y0 + 1.6 + k * 3.2
        bk.drape(C, key, [(x0, yy), (x1, yy)], 1.1, G, lift=0.035, step=3.0)
for (x, y, yaw) in ((-44.0, 518.0, 20), (-40.5, 521.0, 70), (-5.0, 528.0, 10), (52.0, 530.0, 80), (-20.0, 514.0, 40)):
    bk.hay_bale(C, x, y, G.h(x, y), yaw=yaw)
    ext_cover(x, y - 1.0)
bk.stone_wall(C, G, [(-50.0, 476.0), (-22.0, 477.0)], seed=41, broken=((9.0, 11.5),))
bk.stone_wall(C, G, [(14.0, 477.5), (40.0, 476.0)], seed=42)
for (x, y) in ((-40.0, 476.3), (-30.0, 476.6), (22.0, 476.9), (32.0, 476.4)):
    ext_cover(x, y - 0.9)
bk.supply_cart(C, -16.0, 495.0, G.h(-16.0, 495.0), yaw=65.0, load=False, seed=7)
ext_cover(-16.0, 493.0, "high")
# 전차 차선: 헛간 마당 울타리·낮은 담(집결지에서 굴러 나오며 깔고 지나간다), 들판 담, 남쪽 둑 R41 철조망
lane(bk.picket, C, G, (36.5, 503.0), (36.5, 517.0), seed=7)
lane(bk.stone_wall, C, G, [(48.5, 505.0), (48.5, 518.0)], seed=45, h=0.8, seg=6.5)
lane(bk.stone_wall, C, G, [(4.0, 520.0), (40.0, 521.0)], seed=46, h=0.8, seg=6.0, cover=(12.0, 519.6, "low"))
lane(bk.wire_coil, C, G, (0.0, 536.0), (34.0, 536.5), seed=95)
# R41 후위 차단선: 갈림길 서쪽 (모래주머니 반원 진지, 차단벽, 쓰러진 통나무, 철조망)
for (cx, cy) in ((-14.0, 489.0), (6.0, 490.0)):
    bk.bag_row(C, (cx - 2.0, cy - 1.0), (cx + 2.0, cy - 1.0), 0.0, rows=3, zfn=G.h, seed=int(cx) + 300)
    bk.bag_row(C, (cx - 2.2, cy - 0.8), (cx - 2.2, cy + 0.8), 0.0, rows=2, zfn=G.h, seed=int(cx) + 301)
    bk.bag_row(C, (cx + 2.2, cy - 0.8), (cx + 2.2, cy + 0.8), 0.0, rows=2, zfn=G.h, seed=int(cx) + 302)
for (x, y, yaw) in ((-6.5, 487.5, 8.0), (-25.0, 481.4, -10.0)):
    bk.r41_barrier(C, x, y, G.h(x, y), yaw=yaw)
for (x, y, st) in ((-21.0, 492.0, 2), (-20.0, 493.2, 1), (9.0, 493.5, 1)):
    bk.r41_crate(C, x, y, G.h(x, y), yaw=rng.uniform(-20, 20), stack=st)
bk.drum_r41(C, -11.0, 492.5, G.h(-11.0, 492.5))
bk.wire_coil(C, G, (-36.0, 480.0), (-18.0, 480.5), seed=91)
bk.wire_coil(C, G, (12.0, 481.0), (28.0, 480.5), seed=92)
for i, (x, y, r) in enumerate(((-2.0, 474.0, 2.6), (8.0, 497.0, 2.4), (-38.0, 478.5, 2.2), (-8.0, 506.0, 2.6))):
    sol = bk.Solid(f"vcr{i}")
    bk.crater(C, G, sol, x, y, r, seed=120 + i)
    sol.flush(C)
bk.smoke(C, -38.0, 478.5, G.h(-38.0, 478.5) + 1.0, h=36.0, r=2.4, seed=33, dark=0.5, kind="fine", segs=8, rings=5)
# 숲 끝 생울타리 (갈림길 남쪽 숲 가장자리를 따라, 길 틈)
bk.hedgerow(C, G, [(-50.0, 466.0), (-8.0, 468.0)], seed=43)
bk.hedgerow(C, G, [(4.0, 468.5), (42.0, 466.74)], seed=44)          # 틈 x 42..54: 전차 차선
bk.hedgerow(C, G, [(54.0, 466.19), (58.0, 466.0)], seed=47)
for (x, y) in ((-30.0, 467.0), (-18.0, 467.4), (16.0, 467.9), (30.0, 467.6)):
    ext_cover(x, y - 0.9, "high")

# ---- 강 + 돌다리 (2구역) + 북쪽 둑 R41 진지
C.group("river")
mk.PAL.setdefault("stream", "#77a2ac")
mk.PAL.setdefault("stream_l", "#a8c9c9")


def ring_pt(r, a):
    return (EX + math.cos(a) * r, EY + math.sin(a) * r)


def water_z(x, y):
    return H_base(x, y) - 0.5


A_RIV = math.atan2(BRIDGE[1] - EY, BRIDGE[0] - EX)
wb = C.bm("stream", "under")
rows = []
NA = 64
for k in range(NA + 1):
    a = A_RIV + math.radians(-17.0 + 34.0 * k / NA)          # 통로 양쪽 너머까지 (약 ±140 m)
    row = []
    for dr in (-5.6, 5.6):
        x, y = ring_pt(R_RIV + dr, a)
        cx_, cy_ = ring_pt(R_RIV, a)
        row.append(wb.verts.new((x, y, water_z(cx_, cy_))))
    rows.append(row)
for k in range(NA):
    wb.faces.new((rows[k][0], rows[k][1], rows[k + 1][1], rows[k + 1][0]))
# 물결 줄 (밝은 띠)
for j, dr in enumerate((-2.6, 1.4, 3.4)):
    pts = []
    for k in range(0, NA + 1, 2):
        a = A_RIV + math.radians(-17.0 + 34.0 * k / NA) + 0.004 * j
        x, y = ring_pt(R_RIV + dr, a)
        cx_, cy_ = ring_pt(R_RIV, a)
        pts.append((x, y, water_z(cx_, cy_) + 0.02))
    for p0, p1 in zip(pts[::2], pts[1::2]):
        C.strip("stream_l", p0, p1, 0.18, (0, 0, 1), lift=0.0)
# 둑의 갈대·돌
for i in range(26):
    a = A_RIV + math.radians(rng.uniform(-9.0, 9.0))
    side = rng.choice((-1, 1))
    x, y = ring_pt(R_RIV + side * rng.uniform(6.0, 9.5), a)
    if math.hypot(x - BRIDGE[0], y - BRIDGE[1]) < 14:
        continue
    z = G.h(x, y)
    for k in range(5):
        dx, dy = rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5)
        C.cyl("foliage_d", (x + dx, y + dy, z - 0.1), (x + dx * 1.3, y + dy * 1.3, z + rng.uniform(0.7, 1.2)), 0.04,
              segs=4, kind="detail")
# 돌다리: 방사 큰길 방향, 길이 24 m, 폭 6.6 m, 가운데가 0.8 m 솟은 등. 아래는 막혀 있다 (속을 COL로 채움)
BL, BW = 12.0, 3.3
bfr = bk.Local((BRIDGE[0], BRIDGE[1], 0.0), math.degrees(math.atan2(FO.x, -FO.y)))   # 로컬 -Y = 바깥(남쪽), +Y = 성문 쪽
ZS = H_base(*bfr.p(0.0, -BL).xy) + 0.08          # 남쪽 끝 (둑 높이)
ZN = H_base(*bfr.p(0.0, BL).xy) + 0.08           # 북쪽 끝
BZ = min(ZS, ZN)


def deck_z(s):
    """다리 윗면: 두 끝은 둑 높이, 가운데가 0.7 m 솟은 등."""
    return ZS + (ZN - ZS) * (s + BL) / (2 * BL) + 0.7 * (1 - (s / BL) ** 2)


sol = bk.Solid("bridge")
bb = sol("stone_v")
NS = 16
top, bot = [], []
for k in range(NS + 1):
    s = -BL + 2 * BL * k / NS
    zt = deck_z(s)
    top.append([bb.verts.new(bfr.p(u, s, zt)) for u in (-BW, BW)])
    bot.append([bb.verts.new(bfr.p(u, s, BZ - 2.4)) for u in (-BW, BW)])
fs = []
for k in range(NS):
    fs.append(bb.faces.new((top[k][0], top[k][1], top[k + 1][1], top[k + 1][0])))
    fs.append(bb.faces.new((top[k][0], top[k + 1][0], bot[k + 1][0], bot[k][0])))
    fs.append(bb.faces.new((top[k][1], bot[k][1], bot[k + 1][1], top[k + 1][1])))
fs.append(bb.faces.new((top[0][0], bot[0][0], bot[0][1], top[0][1])))
fs.append(bb.faces.new((top[NS][1], bot[NS][1], bot[NS][0], top[NS][0])))
bmesh.ops.recalc_face_normals(bb, faces=fs)
sol.flush(C)
# 포장 띠, 난간(돌), 아치 그늘(옆면), 끝 기둥 + 작은 에르피엔 깃발
for k in range(NS):
    s0, s1 = -BL + 2 * BL * k / NS, -BL + 2 * BL * (k + 1) / NS
    for sx in (-1, 1):
        a = bfr.p(sx * (BW - 0.2), s0, deck_z(s0) - 0.05)
        b = bfr.p(sx * (BW - 0.2), s1, deck_z(s1) - 0.05)
        # 폭 0.38: 바깥 면이 다리 옆면보다 1 cm 안 (난간 아래 끝이 다리 옆면과 같은 평면에 겹쳐 깜빡였다)
        C.beam("stone_vd", a + Vector((0, 0, 0.45)), b + Vector((0, 0, 0.45)), 0.38, 0.9)
for sx in (-1, 1):
    for s in (-BL + 0.3, BL - 0.3):
        p = bfr.p(sx * (BW - 0.2), s, deck_z(s))
        C.cyl("stone_vd", (p.x, p.y, p.z - 0.3), (p.x, p.y, p.z + 1.25), 0.36, segs=8)
        C.cyl("fy_gold", (p.x, p.y, p.z + 1.25), (p.x, p.y, p.z + 1.4), 0.4, segs=8, kind="detail")
        C.ccyl(p.x, p.y, 0.36, p.z - 0.3, p.z + 1.4, n=8)       # 끝 기둥 COL (난간 COL보다 굵어 몸이 기둥 속으로 들어갔다)
    # 아치 그늘 (물 위 반원)
    for s in (-4.6, 4.6):
        c = bfr.p(sx * BW, s, deck_z(s) - 2.1)
        n = bfr.d(sx, 0, 0)
        arc = [(2.4 * math.cos(math.pi * i / 10), 1.4 * math.sin(math.pi * i / 10)) for i in range(11)]
        C.decal("erk_slit", arc, (c.x, c.y, c.z), (n.x, n.y, 0.0), up=(0, 0, 1), lift=0.03, kind="detail")
        band = [(2.75 * math.cos(math.pi * i / 10), 1.75 * math.sin(math.pi * i / 10)) for i in range(11)] + list(reversed(arc))
        C.decal("stone_vd", band, (c.x, c.y, c.z), (n.x, n.y, 0.0), up=(0, 0, 1), lift=0.03, kind="detail")
for k in range(4):
    s0, s1 = -BL + 6 * k, -BL + 6 * (k + 1)
    # 난간 COL: 보이는 난간(데크 -0.05 ~ +0.85, 폭 0.38)을 마디 두 끝의 데크 높이에 맞춘 볼록 껍질 (보는 것보다 조금 높게).
    # 예전 COL은 마디의 낮은 끝 데크 높이에 세운 수평 보(+0.28 ~ +0.73)라 등이 솟은 끝에서 데크 위 0.2 m만 남아
    # 걸어서 넘어 보이는 난간 속으로 들어갔다(그대로 다리 밖 강으로 떨어질 수 있다. 2026-11-04 이동 충돌 감사 walk: river_stone_vd 8곳)
    for sx in (-1, 1):
        C.ccol([tuple(bfr.p(sx * (BW - 0.2) + du, s, deck_z(s) + dz))
                for s in (s0, s1) for du in (-0.23, 0.23) for dz in (-0.1, 0.95)])
# 다리 아래 (속): 상자 COL 셋 (물에서 다리 밑으로 들어가 갇히지 않게)
for (s0, s1) in ((-BL, -4.0), (-4.0, 4.0), (4.0, BL)):
    c = bfr.p(0.0, (s0 + s1) / 2, 0.0)
    C.ocol((c.x, c.y, BZ - 2.4), (2 * BW, s1 - s0, min(deck_z(s0), deck_z(s1)) - (BZ - 2.4) - 0.08), yaw=bfr.yaw)
for (sx, s) in ((-1, BL + 0.6), (1, BL + 0.6)):
    p = bfr.p(sx * (BW + 0.9), s, 0)
    bk.fairy_banner(C, p.x, p.y, G.h(p.x, p.y), yaw=bfr.yaw, h=3.6, w=0.9, L=1.3)
# 다리 북쪽 동쪽 돌 초소 (R41이 진지로 썼다)
bk.cottage(C, G, TOLL[0], TOLL[1], w=6.0, d=5.0, axis="x", door="+y", roof="roof_g", broken=0.55, seed=34, h=2.6)
ext_cover(TOLL[0] - 3.6, TOLL[1] + 3.2, "high")
# R41 북쪽 둑 진지: 모래주머니 둥지 셋, 다리 북쪽 끝 차단벽(한쪽 비움), 장갑차 2 둔덕
BN = radial(R_RIV - 12.5)
for (dl, dr_) in ((-11.0, -2.0), (9.0, -4.0), (-24.0, -8.0)):
    p = radial(R_RIV - 12.0 + dr_, dl)
    a, b = radial(R_RIV - 12.0 + dr_, dl - 2.2), radial(R_RIV - 12.0 + dr_, dl + 2.2)
    bk.bag_row(C, a, b, 0.0, rows=3, zfn=G.h, seed=int(dl * 7) + 400)
    ext_cover(p[0] + FO.x * 0.8, p[1] + FO.y * 0.8)
for (lat, dd) in ((-2.4, -3.0), (3.0, -5.5)):
    p = radial(R_RIV - 12.0 + dd, lat)
    bk.r41_barrier(C, p[0], p[1], G.h(*p), yaw=math.degrees(math.atan2(FO.x, -FO.y)) + rng.uniform(-8, 8))
I2 = IFV_SPOTS["ifv2"]
sol = bk.Solid("ifv2_berm")
bdir = (BRIDGE[0] - I2[0], BRIDGE[1] - I2[1])
bl = math.hypot(*bdir)
bu = (bdir[0] / bl, bdir[1] / bl)
bp = (I2[0] + bu[0] * 4.6, I2[1] + bu[1] * 4.6)
bt = (-bu[1], bu[0])
bk.berm(sol, (bp[0] - bt[0] * 3.4, bp[1] - bt[1] * 3.4), (bp[0] + bt[0] * 3.4, bp[1] + bt[1] * 3.4), G.h(*bp) - 0.05,
        bu, w=2.4, h=0.75, crest=0.7)
sol.flush(C)
bk.bag_row(C, (bp[0] - bt[0] * 3.0 - bu[0] * 0.3, bp[1] - bt[1] * 3.0 - bu[1] * 0.3),
           (bp[0] + bt[0] * 3.0 - bu[0] * 0.3, bp[1] + bt[1] * 3.0 - bu[1] * 0.3), G.h(*bp) + 0.45, rows=1, seed=410)
for (x, y, st) in ((-31.0, 595.0, 2), (-30.2, 596.2, 1), (-9.0, 590.0, 1)):
    bk.r41_crate(C, x, y, G.h(x, y), yaw=rng.uniform(-20, 20), stack=st)

# 전차 차선 (북쪽 둑): R41 모래주머니 둥지 하나가 동쪽 차선 위에 있다 (전차가 여울을 건너 깔고 지나간다)
for (lat, rr) in ((30.0, 463.0),):
    lane(bk.bag_row, C, radial(rr, lat - 2.4), radial(rr, lat + 2.4), 0.0, rows=3, zfn=G.h, seed=430,
         cover=(*radial(rr + 1.0, lat), "low"))
    lane(bk.bag_row, C, radial(rr, lat - 2.6), radial(rr - 1.8, lat - 2.6), 0.0, rows=2, zfn=G.h, seed=431)
    lane(bk.bag_row, C, radial(rr, lat + 2.6), radial(rr - 1.8, lat + 2.6), 0.0, rows=2, zfn=G.h, seed=432)

# ---- 성문 큰길 (다리 → 성문): 밭, 과수원, 생울타리
C.group("approach")
# 전차 차선: 밭 철조망 띠, 낮은 밭담 (성문까지 가며 깔고 지나간다)
lane(bk.wire_coil, C, G, radial(440.0, 17.0), radial(440.0, 46.0), seed=96)
lane(bk.stone_wall, C, G, [radial(410.0, 16.0), radial(410.0, 46.0)], seed=47, h=0.8, seg=6.0, cover=(*radial(411.0, 20.0), "low"))
bk.drape(C, "earth", GATE_ROAD, 4.0, G, lift=0.045, step=2.0)
bk.drape(C, "erk_pave", [radial(348.0), radial(282.0)], 6.4, G, lift=0.06, step=2.0)
for side in (-1, 1):
    for r0, r1 in ((462.0, 430.0), (405.0, 372.0)):
        a, b = radial(r0, side * 9.0), radial(r1, side * 9.0)
        bk.hedgerow(C, G, [a, b], seed=int(r0) + side, h=1.4)
        ext_cover((a[0] + b[0]) / 2 + side * TT.x * -1.0, (a[1] + b[1]) / 2, "high")
# 과수원 (길 서쪽): 줄지은 둥근 나무 (COL 줄기)
for i in range(4):
    for j in range(3):
        x, y = radial(445.0 - i * 13.0, -22.0 - j * 8.5)
        if not in_corridor(x, y, 3.0):
            continue
        bk.tree_round(C, x, y, G.h(x, y), h=rng.uniform(5.0, 6.2), seed=300 + i * 3 + j, keys=("foliage", "foliage_l", "foliage_d"))
        C.col(x - 0.25, x + 0.25, y - 0.25, y + 0.25, G.h(x, y) - 0.3, G.h(x, y) + 3.0)
for i, (lat, rr) in enumerate(((14.0, 440.0), (-8.0, 395.0), (19.0, 380.0), (-14.0, 362.0))):
    x, y = radial(rr, lat)
    bk.hay_bale(C, x, y, G.h(x, y), yaw=rng.uniform(0, 90))
    ext_cover(x - FO.x * -1.0, y - FO.y * -1.0)
for i, (lat, rr, r) in enumerate(((4.0, 450.0, 2.4), (-12.0, 410.0, 2.6), (14.0, 418.0, 2.2), (-30.0, 382.0, 2.4))):
    x, y = radial(rr, lat)
    sol = bk.Solid(f"acr{i}")
    bk.crater(C, G, sol, x, y, r, seed=140 + i)
    sol.flush(C)

# ---- 성문 앞 (3구역): 바깥 성문루·성벽 (erpien_kit), 포석 마당, R41 포위 진지
C.group("gate", outline=0.03)
GATE = ek.city_gate(C, GP, G.h, kind="main", scorch=0.8, lit="lamp_warm", seed=9)
GFRONT = GATE["front"]
C.group("forecourt")
# 포석 마당 (성문 앞 반원)
PC = radial(GP["r_wall"] + 18.0)
pv = []
for k in range(25):
    a = math.atan2(FO.y, FO.x) + math.radians(-90 + 180 * k / 24)
    pv.append((PC[0] + math.cos(a) * 24.0 - FO.x * 14.0, PC[1] + math.sin(a) * 24.0 - FO.y * 14.0))
pz = G.h(*PC)
C.poly("erk_pave", [(x, y, pz + 0.045) for x, y in pv], normal=(0, 0, 1), kind="detail")
for k in range(8):
    a, b = radial(GP["r_wall"] + 8.0 + k * 4.0, -22.0), radial(GP["r_wall"] + 8.0 + k * 4.0, 22.0)
    C.strip("stone_vd", (a[0], a[1], pz + 0.05), (b[0], b[1], pz + 0.05), 0.12, (0, 0, 1), lift=0.012)
# 문지기 마구간 (흰 돌, 청록 지붕): 장갑차 4가 그 뒤(성벽 쪽)에서 나온다
SB = bk.Local((STABLE[0], STABLE[1], G.h(*STABLE)), math.degrees(math.atan2(FO.x, -FO.y)))
SB.box(C, "erk_wall", -5.5, 5.5, -3.2, 3.2, -0.5, 4.2, col=True)
SB.box(C, "erk_wall_d", -5.7, 5.7, -3.4, 3.4, -0.55, 0.9)   # 밑면을 몸통(-0.5)과 다른 높이에 (같은 평면 겹침 방지)
rb = C.bm("erk_roof", "main")
rv = [rb.verts.new(SB.p(*q)) for q in ((-6.0, -3.8, 4.1), (6.0, -3.8, 4.1), (6.0, 3.8, 4.1), (-6.0, 3.8, 4.1),
                                         (-6.0, 0.0, 6.6), (6.0, 0.0, 6.6))]
rfs = [rb.faces.new((rv[0], rv[1], rv[5], rv[4])), rb.faces.new((rv[2], rv[3], rv[4], rv[5])),
       rb.faces.new((rv[3], rv[0], rv[4])), rb.faces.new((rv[1], rv[2], rv[5]))]
bmesh.ops.recalc_face_normals(rb, faces=rfs)
for u in (-3.0, 0.5, 3.6):
    SB.rect(C, "erk_slit", (u, -3.2, 2.2), (0, -1, 0), 1.2, 1.6, lift=0.03)
SB.rect(C, "erk_door_d", (-0.9, -3.2, 1.3), (0, -1, 0), 1.6, 2.4, lift=0.03)
ef.far_flag(ef.city(C), SB.M @ Matrix.Translation((5.4, 3.0, 4.2)), W=1.2, pole=3.2, layers={"cloth": "detail"})
ext_cover(*(SB.p(2.0, -4.2, 0)).xy, "high")
# R41 포위 진지: 큰길 차단벽 줄(남쪽을 본다), 모래주머니 둥지, 지휘 컨테이너, 상자, 그을음·구덩이
for k, lat in enumerate((-14.0, -8.5, 6.5, 12.0)):
    p = radial(352.0, lat)
    bk.r41_barrier(C, p[0], p[1], G.h(*p), yaw=math.degrees(math.atan2(FO.x, -FO.y)) + rng.uniform(-6, 6), w=2.2)
    ext_cover(p[0] + FO.x * 1.0, p[1] + FO.y * 1.0)
for (lat, rr) in ((-26.0, 340.0), (20.0, 338.0), (-4.0, 318.0), (-40.0, 322.0)):
    a, b = radial(rr, lat - 2.0), radial(rr, lat + 2.0)
    bk.bag_row(C, a, b, 0.0, rows=3, zfn=G.h, seed=int(rr + lat) + 500)
    c = radial(rr - 1.6, lat)
    bk.bag_row(C, radial(rr, lat - 2.2), radial(rr - 1.6, lat - 2.2), 0.0, rows=2, zfn=G.h, seed=int(rr + lat) + 501)
    bk.bag_row(C, radial(rr, lat + 2.2), radial(rr - 1.6, lat + 2.2), 0.0, rows=2, zfn=G.h, seed=int(rr + lat) + 502)
    ext_cover(*radial(rr + 1.0, lat))
CPOS = radial(330.0, -30.0)
bk.r41_container(C, CPOS[0], CPOS[1], G.h(*CPOS), axis="x", L=5.6, door="+y", label="R41-91")
ext_cover(CPOS[0] + FO.x * 1.8, CPOS[1] + FO.y * 1.8 - 0.0, "high")
for (lat, rr, st) in ((-18.0, 326.0, 2), (-17.0, 325.0, 1), (14.0, 330.0, 1), (24.0, 312.0, 2)):
    x, y = radial(rr, lat)
    bk.r41_crate(C, x, y, G.h(x, y), yaw=rng.uniform(-20, 20), stack=st)
for (lat, rr) in ((26.0, 318.0), (26.6, 318.8), (-36.0, 336.0)):
    x, y = radial(rr, lat)
    bk.drum_r41(C, x, y, G.h(x, y))
I3 = IFV_SPOTS["ifv3"]
sol = bk.Solid("ifv3_berm")
p3 = (I3[0] + FO.x * 4.6, I3[1] + FO.y * 4.6)
bk.berm(sol, (p3[0] - TT.x * 3.4, p3[1] - TT.y * 3.4), (p3[0] + TT.x * 3.4, p3[1] + TT.y * 3.4), G.h(*p3) - 0.05,
        (FO.x, FO.y), w=2.4, h=0.75, crest=0.7)
for i, (lat, rr, r) in enumerate(((-10.0, 304.0, 2.4), (14.0, 296.0, 2.2), (-30.0, 300.0, 2.6), (2.0, 330.0, 2.2))):
    x, y = radial(rr, lat)
    bk.crater(C, G, sol, x, y, r, seed=160 + i)
sol.flush(C)
# 연기 기둥: 성문 앞 서쪽 (끝 장면에서 결전의 하늘을 가리지 않게, 전차 사선 밖)
bk.smoke(C, *radial(342.0, -50.0), -39.0, h=60.0, r=3.0, seed=41, dark=0.55, kind="fine", segs=8, rings=5)
bk.wire_coil(C, G, radial(360.0, -30.0), radial(360.0, -16.0), seed=93)
bk.wire_coil(C, G, radial(360.0, 9.0), radial(360.0, 16.0), seed=94)
lane(bk.wire_coil, C, G, radial(360.0, 16.5), radial(360.0, 30.0), seed=97)
# 성문 앞 돌 기둥 둘 (작은 에르피엔 깃발)
for sx in (-1, 1):
    x, y = radial(GP["r_wall"] + 30.0, sx * 15.0)
    z = G.h(x, y)
    C.box("erk_wall_d", x - 0.6, x + 0.6, y - 0.6, y + 0.6, z - 0.3, z + 0.6)
    C.cyl("erk_wall", (x, y, z + 0.6), (x, y, z + 4.2), 0.38, segs=10)
    C.cyl("erk_gold", (x, y, z + 4.2), (x, y, z + 4.5), 0.46, segs=10, kind="detail")
    C.ccyl(x, y, 0.6, z - 0.3, z + 4.5)
    ef.far_flag(ef.city(C), Matrix.Translation((x, y, z + 4.5)) @ Matrix.Rotation(math.atan2(FO.y, FO.x) + math.pi / 2, 4, "Z"),
                W=1.3, pole=2.2, layers={"cloth": "detail"})
# 통로 가장자리 숲 (벽 바깥 6~26 m 띠): 통로가 숲에 둘러싸여 읽히게. 그룹을 남북으로 나눠 화면 밖은 그리지 않는다
EDGE = bk.scatter((-120.0, 110.0, 345.0, 735.0), 150, seed=51, min_d=7.0,
                  avoid=lambda x, y: in_corridor(x, y, -6.0) or not in_corridor(x, y, -26.0)
                  or math.hypot(x - EX, y - EY) < GP["r_wall"] + 12.0)
for i, (x, y) in enumerate(EDGE):
    C.group("edge_s" if y < 530 else "edge_m" if y < 640 else "edge_n")
    if i % 3:
        bk.conifer(C, x, y, G.h(x, y), h=rng.uniform(9.0, 13.5), seed=400 + i)
    else:
        bk.tree_round(C, x, y, G.h(x, y), h=rng.uniform(8.0, 10.5), seed=400 + i)
# 통로 안 가장자리 나무 (벽을 가린다, 줄기 COL)
INNER = bk.scatter((-90.0, 75.0, 470.0, 720.0), 40, seed=52, min_d=8.0,
                   avoid=lambda x, y: (not in_corridor(x, y, 0.5)) or in_corridor(x, y, 6.0)
                   or math.hypot(x - 60.0, y - 513.0) < 8.0)       # 집결지 동쪽 끝 (예전 셋째 전차 자리, 나무 배치는 그대로)
for i, (x, y) in enumerate(INNER):
    C.group("edge_s" if y < 530 else "edge_m" if y < 640 else "edge_n")
    z = G.h(x, y)
    if abs(math.hypot(x - EX, y - EY) - R_RIV) < 9.5:
        continue
    bk.tree_round(C, x, y, z, h=rng.uniform(7.0, 9.0), seed=450 + i)
    C.col(x - 0.28, x + 0.28, y - 0.28, y + 0.28, z - 0.3, z + 4.0)

# ================================================================== far: valley, Erpien, world tree, mountains, sky
C.group("far")


def far_region(x0, x1, y0, y1):
    return lambda r: (r.uniform(x0, x1), r.uniform(y0, y1))


def far_avoid(x, y):
    if NEAR[0] + 6 < x < NEAR[1] - 6 and NEAR[2] + 6 < y < NEAR[3] - 6 and abs(x) < 80:
        return True
    if math.hypot(x - EX, y - EY) < ERP_H * 0.77:       # 바깥 성벽(0.72h) 안은 비운다
        return True
    if in_corridor(x, y, -10.0):
        return True                                   # 진격로 연장 통로 (가까운 숲이 따로 있다)
    return abs(math.hypot(x - EX, y - EY) - R_RIV) < 10.0   # 강


FAR = []
FAR += bk.scatter(far_region(-360, 260, 670, 795), 130, seed=11, avoid=far_avoid, min_d=9.0)     # 성벽 앞 숲 띠
FAR += bk.scatter(far_region(-420, 420, 440, 690), 80, seed=12, avoid=far_avoid, min_d=16.0)    # 골짜기
FAR += bk.scatter(far_region(-900, -150, 150, 1400), 65, seed=13, avoid=far_avoid, min_d=30.0)  # 서쪽 언덕
FAR += bk.scatter(far_region(150, 900, 150, 1400), 65, seed=14, avoid=far_avoid, min_d=30.0)    # 동쪽 언덕
FAR += bk.scatter(far_region(-700, 700, -700, -120), 60, seed=15, avoid=far_avoid, min_d=34.0)  # 남쪽 뒤
FAR += bk.scatter(far_region(-700, -90, -120, 300), 45, seed=16, avoid=far_avoid, min_d=24.0)
FAR += bk.scatter(far_region(90, 700, -120, 300), 45, seed=17, avoid=far_avoid, min_d=24.0)
bk.far_trees(C, G, FAR[:130], seed=3, h=(16, 26))
bk.far_trees(C, G, FAR[130:], seed=4, h=(11, 19))

C.group("erpien")
ek.haze("#e9b79c", 0.2)          # 해 질 녘 원경
ERP = ek.erpien(C, EX, EY, EZ, ERP_H, hfun=G.h, face=(RIDGE[0] - EX, RIDGE[1] - EY), kind="far", detail=0, seed=11,
                lit="lamp_warm", density=0.85, skip=GP["skip"])   # 성문 둘레 성벽·탑은 가까운 세트(city_gate)가 대신한다
ERP["castle_z"] = EZ + ERP_H * 0.26                  # 세계수 줄기 (왕궁 위): MARK_erpien, 끝 원경
for i, (dx, dy, h) in enumerate(((-90.0, -70.0, 170.0), (70.0, 40.0, 150.0), (-20.0, 130.0, 190.0))):
    bk.smoke(C, EX + dx, EY + dy, EZ, h=h, r=12.0, drift=(0.25, 0.06), seed=20 + i, dark=0.6, segs=6, rings=3, kind="fine")
bk.far_mountains(C, [((-1900, 1100), (-500, 2050), 7, (150, 260)), ((-300, 2150), (1100, 2050), 7, (190, 330)),
                     ((1300, 1900), (2150, 700), 6, (140, 240)), ((-2200, 200), (-1900, -900), 4, (100, 170)),
                     ((2100, -200), (2000, -1000), 4, (100, 160))], G.h, seed=7)
for (x, y, h) in ((720.0, 520.0, 150.0), (-880.0, 260.0, 120.0)):
    bk.smoke(C, x, y, G.h(x, y), h=h, r=11.0, drift=(0.25, 0.06), seed=int(x), dark=0.5, segs=6, rings=3, kind="fine")
C.group("sky")
for i, (x, y, z, s) in enumerate(((-650, 1500, 380, 220), (420, 1300, 330, 170), (1250, 950, 300, 190),
                                  (-1450, 820, 270, 180), (-150, 2050, 430, 260))):
    bk.cloud(C, x, y, z, size=s, seed=i)

# ================================================================== 레일슈터 엄폐·보병 (2026-11-04)
# 사용자 「M9 레벨 디자인 개선하면서 엄폐물좀 더 추가해. 적 보병도 별로 없고 장갑차가 저 멀리서 포격을 날리는데 개활지에서 뭐 어쩌라는거야.」
# 플레이어 길(출발 참호 → 1선 둑길 → 마을 어귀 → … → 골짜기 남쪽 길 → 성문 큰길)을 따라 8~15 m마다 웅크려 숨을 엄폐(높이 0.85~1.6 m,
# 충돌체가 탄을 막는다)와 COVER_ 마커. 돌격로(WP_charge)·전차 길에는 두지 않는다. 적 보병을 더 세우는 자리의 모래주머니 둥지는
# 부서지는 소품이다(BRK_sandbag_nest_*: 성전군 전차가 고폭 한 발로 무너뜨릴 수 있다, combat/vehicleAi.ts)
RAIL_COVER = []          # (kind, x, y, yaw/arg)


def rail_wall(x0, y0, x1, y1, seed):
    """낮은 돌담 토막 (0.85 m). 남쪽(플레이어 쪽)에 COVER"""
    bk.stone_wall(C, G, [(x0, y0), (x1, y1)], h=0.85, seed=seed)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    COVERS.append((mx, my - 0.9, "low", "n"))
    RAIL_COVER.append(("wall", mx, my))


def rail_wreck(x, y, yaw, cover_dy=-2.4):
    """불탄 R41 습격차 잔해 (1.6 m 높은 엄폐)"""
    bk.wreck_raider(C, x, y, G.h(x, y), yaw=yaw, embers=False)
    COVERS.append((x, y + cover_dy, "high", "n"))
    RAIL_COVER.append(("wreck", x, y))


def rail_hay(x, y, yaw):
    bk.hay_bale(C, x, y, G.h(x, y), yaw=yaw)
    COVERS.append((x, y - 1.0, "low", "n"))
    RAIL_COVER.append(("hay", x, y))


NEST_N = [0]


def r41_nest(x, y, face, seed):
    """R41 모래주머니 둥지 (부서지는 소품, 앞줄 3 m × 6단 0.9 m + 옆 둘). x, y = 둥지 안 병사 자리, face = 적(성전군)이 오는 쪽 점.
    앞줄 바깥(face 쪽)과 둥지 안에 COVER (아군·적 모두 쓴다)"""
    dx, dy = face[0] - x, face[1] - y
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    fx, fy = x + ux * 1.0, y + uy * 1.0
    NEST_N[0] += 1
    n = NEST_N[0]
    bk.bag_row(C, (fx - px * 1.5, fy - py * 1.5), (fx + px * 1.5, fy + py * 1.5), 0.0, rows=6, zfn=G.h, seed=seed,
               breakable=True, brk_name=f"nest_{n:02d}")
    for s in (-1, 1):
        a = (fx + px * s * 1.7 - ux * 0.2, fy + py * s * 1.7 - uy * 0.2)
        b = (x + px * s * 1.7 - ux * 0.6, y + py * s * 1.7 - uy * 0.6)
        bk.bag_row(C, a, b, 0.0, rows=4, zfn=G.h, seed=seed + 3 + s)
    COVERS.append((x - ux * 0.1, y - uy * 0.1, "low", "n"))
    COVERS.append((fx + ux * 0.9, fy + uy * 0.9, "low", "n"))
    RAIL_COVER.append(("nest", x, y))


# 출발 들판 가운데 길 (분대·플레이어 길, x -4..4): 돌담 y 22·28·47·53, 구덩이 y 14·41·58 사이를 메운다
C.group("field")
for (x, y, yaw) in ((-2.0, 34.5, 80.0), (3.0, 64.5, 15.0)):
    if clear_of_paths(x, y, 1.0):
        rail_hay(x, y, yaw)
if clear_of_paths(-1.0, 70.0, 2.0):
    rail_wreck(-1.0, 70.0, 95.0)
# 1선 너머 → 마을 남쪽 담 비탈 (y 100..121): 전차 길(x -8..-4)을 비우고 양옆에
C.group("line1")
rail_wall(-17.0, 107.5, -11.5, 108.0, 401)
rail_wall(-0.5, 110.5, 4.5, 110.8, 402)
rail_wall(8.5, 115.2, 13.5, 115.6, 403)
rail_hay(-12.5, 116.0, 30.0)
# 마을: 남쪽 담 안 R41 둥지 (가운데 서쪽, 담 y 152 앞), 동쪽 집 곁
C.group("village")
r41_nest(-16.0, 149.4, (-12.0, 125.0), 411)
r41_nest(21.0, 162.2, (10.0, 140.0), 412)
# 골짜기 남쪽 길 (갈림길 → 다리 남쪽 둑): 밭 사이
C.group("valley")
rail_hay(-2.0, 521.0, 40.0)
rail_wall(-15.5, 527.5, -11.5, 528.0, 421)
rail_wreck(-6.0, 536.0, 160.0)
r41_nest(-10.0, 497.0, (-6.0, 470.0), 422)
r41_nest(13.0, 499.5, (4.0, 472.0), 423)
# 다리 북쪽 둑 R41 둥지 둘
C.group("river")
r41_nest(*radial(R_RIV - 22.0, 4.0), radial(R_RIV + 10.0, 4.0), 431)
r41_nest(*radial(R_RIV - 28.0, -9.0), radial(R_RIV + 10.0, -9.0), 432)
# 성문 큰길 (다리 북쪽 → 포위 차단선): 길 양옆 3~5 m에 번갈아 (생울타리 ±9 m 안쪽, 전차 차선 동쪽 22 m 밖)
C.group("approach")
for k, (rr, lat, kind) in enumerate(((456.0, 4.5, "wreck"), (437.0, -4.5, "wall"), (425.0, 4.5, "hay"), (414.0, -4.5, "wreck"),
                                     (398.0, 4.5, "wall"), (386.0, -4.5, "hay"), (372.0, 4.5, "wall"))):
    x, y = radial(rr, lat)
    if kind == "wall":
        a, b = radial(rr, lat - 2.0), radial(rr, lat + 2.0)
        bk.stone_wall(C, G, [a, b], h=0.85, seed=440 + k)
        cx, cy = radial(rr + 1.0, lat)
        COVERS.append((cx, cy, "low", "n"))
        RAIL_COVER.append(("wall", x, y))
    elif kind == "hay":
        bk.hay_bale(C, x, y, G.h(x, y), yaw=90.0 + k * 13)
        cx, cy = radial(rr + 1.2, lat)
        COVERS.append((cx, cy, "low", "n"))
        RAIL_COVER.append(("hay", x, y))
    else:
        bk.wreck_raider(C, x, y, G.h(x, y), yaw=math.degrees(math.atan2(FO.x, FO.y)) + 15.0 * (1 if k % 2 else -1), embers=False)
        cx, cy = radial(rr + 2.6, lat)
        COVERS.append((cx, cy, "high", "n"))
        RAIL_COVER.append(("wreck", x, y))
# 성문 앞 R41 둥지 셋 (포위 차단선 남쪽)
C.group("forecourt")
r41_nest(*radial(361.0, -8.0), radial(400.0, -8.0), 451)
r41_nest(*radial(364.0, 5.0), radial(400.0, 5.0), 452)
r41_nest(*radial(345.0, -2.5), radial(400.0, -2.5), 453)
print(f"[m9] 레일슈터 엄폐 {len(RAIL_COVER)}개: " + ", ".join(f"{k}({x:.0f},{y:.0f})" for k, x, y in RAIL_COVER))

# ================================================================== 엄폐 빈 곳 메우기 (2026-11-04)
# 진격로 30 m 안에 15 m 넘게 엄폐(COVER_)가 없던 구간: 마을 북쪽 끝 → 지휘소 앞 차단벽(41 m), 능선 길(지휘소 동쪽 울타리 구멍 → 전망대,
# 나무 줄기뿐), 숲 내리막(전망대 → 갈림길, 50 m와 22~24 m), 돌다리 앞 남쪽 둑 → 북쪽 둑(41 m). 탄을 막는 엄폐(높이 0.85~1.1 m: 모래주머니
# 6단, 마른 돌담, 큰 바위)를 진격로 옆 4~7 m에 8~13 m마다 두고, 남쪽(플레이어 쪽)에 COVER_. 전차 차선(마을 길 x -5..2, 지휘소 앞
# y 206 동쪽, 능선·내리막 동쪽 숲 차선)·돌격로(출발 들판)·진격로 가운데는 비운다. 다른 충돌체와 0.7 m 넘게 띄운다(끼는 틈 금지).
FILL_COVER = []


def fill_clear(x, y, r):
    """(x, y) 둘레 r m 안에 다른 COL(상자·돌린 상자·볼록)이 없나 (발 높이 ~ 2 m)"""
    z = fz(x, y)
    for (_, x0, x1, y0, y1, z0, z1) in C.cols:
        if z1 < z - 0.2 or z0 > z + 2.0:
            continue
        if math.hypot(max(x0 - x, 0.0, x - x1), max(y0 - y, 0.0, y - y1)) < r:
            return False
    for (_, ox, oy, oz, sx, sy, sz, yaw) in C.ocols:
        if oz > z + 2.0 or oz + sz < z - 0.2:
            continue
        if math.hypot(x - ox, y - oy) < r + max(sx, sy) / 2:
            return False
    for (_, vs) in C.ccols:
        xs = [v[0] for v in vs]
        ys = [v[1] for v in vs]
        zs = [v[2] for v in vs]
        if max(zs) < z - 0.2 or min(zs) > z + 2.0:
            continue
        if math.hypot(max(min(xs) - x, 0.0, x - max(xs)), max(min(ys) - y, 0.0, y - max(ys))) < r:
            return False
    return True


def fill_spot(x, y, r):
    """(x, y)가 막혔으면 둘레 1~2.5 m로 옮겨 본다 (못 찾으면 None)"""
    if fill_clear(x, y, r):
        return (x, y)
    for d in (1.0, 1.6, 2.5):
        for k in range(8):
            a = k * math.pi / 4
            q = (x + math.cos(a) * d, y + math.sin(a) * d)
            if fill_clear(*q, r):
                return q
    print(f"[m9] 경고: 엄폐 메우기 ({x:.1f},{y:.1f}) 자리 없음")
    return None


def fill_rock(x, y, s, seed, face=(0.0, 1.0)):
    """큰 바위 (s 2.2: 지름 약 2.6 m, 높이 0.85~1.1 m). face = 적 쪽 단위 방향: COVER는 반대쪽"""
    q = fill_spot(x, y, 0.6 * s + 0.7)
    if not q:
        return
    x, y = q
    mk.rock(C, x, y, s=s, z=G.h(x, y) - 0.15, seed=seed)
    COVERS.append((x - face[0] * (0.6 * s + 0.55), y - face[1] * (0.6 * s + 0.55), "low", "n"))
    FILL_COVER.append(("rock", x, y))


def fill_bags(x, y, seed, w=3.0, face=(0.0, 1.0)):
    """모래주머니 앞줄 6단 (0.9 m) + 양옆 둘. x, y = 앞줄 가운데, face = 적 쪽"""
    q = fill_spot(x, y, w / 2 + 0.8)
    if not q:
        return
    x, y = q
    ux, uy = face
    px, py = uy, -ux
    a, b = (x - px * w / 2, y - py * w / 2), (x + px * w / 2, y + py * w / 2)
    bk.bag_row(C, a, b, 0.0, rows=6, zfn=G.h, seed=seed)
    for sg in (-1, 1):
        e = (x + px * sg * (w / 2 + 0.2), y + py * sg * (w / 2 + 0.2))
        bk.bag_row(C, e, (e[0] - ux * 1.0, e[1] - uy * 1.0), 0.0, rows=3, zfn=G.h, seed=seed + 2 + sg)
    COVERS.append((x - ux * 0.9, y - uy * 0.9, "low", "n"))
    FILL_COVER.append(("bags", x, y))


def fill_wall(x0, y0, x1, y1, seed):
    """마른 돌담 토막 (0.95 m), 남쪽에 COVER"""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    if not fill_clear(mx, my, math.hypot(x1 - x0, y1 - y0) / 2 + 0.8):
        print(f"[m9] 경고: 엄폐 메우기 담 ({mx:.1f},{my:.1f}) 자리 없음")
        return
    bk.stone_wall(C, G, [(x0, y0), (x1, y1)], h=0.95, seed=seed)
    COVERS.append((mx, my - 0.9, "low", "n"))
    FILL_COVER.append(("wall", mx, my))


# 마을 북쪽 끝 → 지휘소 앞 (마을 길 = 전차 길 x -5..2: 길 서쪽 x -9..-11, 동쪽 x 6..9). 보급 수레(-6.5, 183) 뒤에도 COVER
C.group("village")
COVERS.append((-6.5, 181.3, "low", "n"))
FILL_COVER.append(("cart", -6.5, 183.0))
fill_bags(7.5, 191.2, 461)
fill_wall(-11.5, 200.0, -7.5, 200.2, 462)
fill_bags(-8.5, 208.4, 463)
# 능선 길 (지휘소 동쪽 울타리 구멍 → 전망대): 길 옆 4~6 m의 큰 바위 (전차 차선 x 34 쪽은 비운다)
C.group("ridge")
for i, (x, y) in enumerate(((24.0, 266.5), (14.5, 275.0), (17.5, 284.5), (18.0, 298.5), (21.5, 311.0), (6.5, 314.5), (3.5, 322.5))):
    fill_rock(x, y, 2.2, 470 + i)
# 전망대 바위 둘(옛 바위)에 COVER, 숲 내리막 길 옆 큰 바위 (길 = TRACK, 전차 차선은 동쪽 숲 x 37~48)
C.group("descent")
for (x, y, sz) in ((-6.8, 346.0, 1.6), (10.6, 345.6, 1.8)):
    COVERS.append((x, y - 0.6 * sz - 0.55, "low", "n"))
for i, (x, y) in enumerate(((-3.0, 357.5), (12.5, 364.5), (1.0, 374.5), (11.5, 396.5), (-4.0, 416.5), (-8.5, 432.0), (6.5, 449.5))):
    fill_rock(x, y, 2.2, 480 + i)
# 돌다리 앞 남쪽 둑 (길 양옆) → 다리 북쪽 끝 양옆 (적은 성문 쪽: 방사선 안쪽 -FO)
C.group("river")
_fo = (-FO.x, -FO.y)
fill_rock(*radial(R_RIV + 15.0, -7.0), 2.2, 490, face=_fo)
fill_bags(*radial(R_RIV + 9.0, 6.0), 491, face=_fo)
fill_rock(*radial(R_RIV - 15.5, -6.5), 2.2, 492, face=_fo)
fill_bags(*radial(R_RIV - 15.0, 6.5), 493, face=_fo)
print(f"[m9] 엄폐 메우기 {len(FILL_COVER)}개: " + ", ".join(f"{k}({x:.1f},{y:.1f})" for k, x, y in FILL_COVER))

# ================================================================== markers
C.group("markers")
# 스폰
M_("SPAWN_player", -6.0, 2.15, face=north(-6.0, 2.15))
M_("SPAWN_line1", -0.5, 83.5, face=north(-0.5, 83.5))
M_("SPAWN_village", -3.0, 126.0, face=north(-3.0, 126.0))
M_("SPAWN_hq", -6.0, 215.0, face=north(-6.0, 215.0))
M_("SPAWN_ridge", 21.2, 278.5, face=(24.0, 290.0))
M_("SPAWN_descent", 3.0, 343.0, face=(5.0, 360.0))
M_("SPAWN_valley", -4.0, 476.0, face=(-8.0, 515.0))
SPB = radial(R_RIV - 16.0)
M_("SPAWN_bridge", SPB[0], SPB[1], face=radial(420.0))
M_("SPAWN_end", END[0], END[1], face=(GFRONT.x, GFRONT.y))
# 분대
for who, (x, y) in (("rona", (-8.2, 0.3)), ("sabre", (-3.6, 0.3)), ("jesty", (-9.8, -0.4)), ("karen", (-2.0, -0.5))):
    M_(f"ALLY_{who}", x, y, face=north(x, y), who=who, behavior="follow", weapon="m4a1")
# 성전군 요정 + 돌격로
for i in range(1, 13):
    pts = CHARGE[i]
    sx, sy = pts[0]
    M_(f"ALLY_fairy_{i:02d}", sx, sy, face=north(sx, sy), who="fairy", behavior="advance", path=f"charge_{i:02d}")
    for k, (x, y) in enumerate(pts[1:], start=1):
        M_(f"WP_charge_{i:02d}_{k:02d}", x, y)
# 적


def foe(name, x, y, kind, group, behavior, *, spawn="start", z=None, face=None):
    p = {"kind": kind, "group": group, "behavior": behavior, "spawn": spawn}
    if kind not in ("drone",):
        p["weapon"] = CARBINE
        p["drop"] = CARBINE
    M_(name, x, y, z, face=face or south(x, y), **p)


FS = L1.zf + 0.18                                    # 사격 발판 윗면
L1_FOES = [(-36.0, "rifleman_a"), (-26.0, "rifleman_b"), (-19.0, "rifleman_c"), (2.0, "officer"),
           (18.0, "rifleman_a"), (36.0, "rifleman_b")]
for i, (x, k) in enumerate(L1_FOES, 1):
    foe(f"ENEMY_l1_{i:02d}", x, F0 + 0.3, k, "line1", "hold", z=FS)
for i, (x, y, k) in enumerate(((-30.5, 80.3, "rifleman_a"), (4.5, 80.3, "assault"), (-20.0, 98.0, "rifleman_b"),
                               (16.0, 98.0, "rifleman_c")), 1):
    foe(f"ENEMY_l1w_{i:02d}", x, y, k, "line1_wave", "advance", spawn="manual")
foe("ENEMY_sur1", SUR1[0], SUR1[1], "rifleman_b", "sur1", "hold", spawn="manual")
M_("MARK_sur1", SUR1[0], SUR1[1])
L2 = [(-5.5, 159.0, "rifleman_a", "hold"), (1.5, 159.2, "rifleman_b", "hold"), (-14.0, 140.4, "rifleman_c", "hold"),
      (12.0, 155.9, "rifleman_a", "advance"), (-21.0, 152.9, "rifleman_b", "advance"), (19.5, 172.2, "rifleman_c", "advance"),
      (2.5, 175.2, "rifleman_a", "hold")]
# 2026-11-04 (「적 보병도 별로 없고」): 마을 폐허·둥지에 다섯 더 (집 모퉁이 셋, 모래주머니 둥지 둘: 레일슈터 엄폐 절)
L2 += [(8.0, 140.0, "rifleman_b", "hold"), (-23.0, 141.0, "rifleman_a", "hold"), (21.5, 170.0, "rifleman_c", "hold"),
       (-16.0, 149.4, "assault", "hold"), (21.0, 162.2, "rifleman_a", "hold")]
for i, (x, y, k, b) in enumerate(L2, 1):
    foe(f"ENEMY_l2_{i:02d}", x, y, k, "line2", b)
L2W = [(-40.0, 196.0, "rifleman_a", "flank"), (-39.0, 200.0, "rifleman_b", "flank"), (-40.5, 204.0, "rifleman_c", "flank"),
       (-38.5, 208.0, "assault", "flank"), (-40.0, 191.0, "riot", "rush")]
for i, (x, y, k, b) in enumerate(L2W, 1):
    foe(f"ENEMY_l2w_{i:02d}", x, y, k, "line2_wave", b, spawn="manual")
for i, ((x, y), k) in enumerate(zip(SUR2, ("rifleman_a", "rifleman_b", "rifleman_c")), 1):
    foe(f"ENEMY_sur2_{i:02d}", x, y, k, "sur2", "hold", spawn="manual", face=(x - 4.0, y - 8.0))
M_("MARK_sur2", 27.8, 182.6)
HQ = [(-12.5, 233.2, "hq_guard", "hold"), (0.5, 233.2, "hq_guard", "hold"), (-19.0, 248.0, "hq_guard", "advance"),
      (5.0, 250.5, "hq_guard", "advance"), (3.5, 259.0, "hq_guard", "hold"), (-7.0, 259.2, "officer", "hold")]
for i, (x, y, k, b) in enumerate(HQ, 1):
    foe(f"ENEMY_hq_{i:02d}", x, y, k, "hq", b)
HQW = [(-15.5, 279.0, "hq_guard", "advance"), (-12.5, 282.0, "assault", "flank"), (-18.5, 283.0, "hq_guard", "advance"),
       (-14.0, 286.0, "assault", "flank"), (-20.0, 287.5, "hq_guard", "advance")]
for i, (x, y, k, b) in enumerate(HQW, 1):
    foe(f"ENEMY_hqw_{i:02d}", x, y, k, "hq_wave", b, spawn="manual")
# 능선 R41 후위 감시조 (ridge, manual: 능선 단계에 부른다). 전망대 빈터 남쪽 둥지에서 능선 길을 내려다본다
RG = [(7.0, 333.2, "rifleman_a", "hold"), (-4.2, 333.6, "rifleman_b", "hold"), (-1.2, 337.8, "rifleman_c", "hold"),
      (11.8, 340.4, "assault", "advance")]
for i, (x, y, k, b) in enumerate(RG, 1):
    foe(f"ENEMY_rg_{i:02d}", x, y, k, "ridge", b, spawn="manual", face=(8.0, 318.0))
# ---- 연장 구역 (모두 manual: 그 단계에 등장 규칙으로 들어온다. 먼 구역 AI가 미리 돌지 않게)
OUT = (FO.x, FO.y)


def facing_out(x, y):
    return (x + OUT[0] * 10.0, y + OUT[1] * 10.0)


V1 = [(-14.0, 490.4, "rifleman_a", "hold"), (6.0, 491.4, "rifleman_b", "hold"), (-21.0, 494.6, "rifleman_c", "advance"),
      (-25.5, 483.2, "officer", "hold"), (9.5, 495.4, "rifleman_a", "advance")]
V1 += [(-10.0, 497.0, "rifleman_b", "hold"), (13.0, 499.5, "assault", "hold")]      # 모래주머니 둥지 (2026-11-04)
for i, (x, y, k, b) in enumerate(V1, 1):
    foe(f"ENEMY_v_{i:02d}", x, y, k, "valley", b, spawn="manual", face=(x, y - 10.0))
V1W = [(-36.0, 507.5, "rifleman_b", "flank"), (-25.0, 509.0, "assault", "advance"), (-40.0, 497.0, "rifleman_c", "flank")]
for i, (x, y, k, b) in enumerate(V1W, 1):
    foe(f"ENEMY_vw_{i:02d}", x, y, k, "valley_wave", b, spawn="manual", face=(x + 6.0, y - 10.0))
B2 = [(*radial(R_RIV - 15.5, -11.0), "rifleman_a", "hold"), (*radial(R_RIV - 17.5, 9.0), "rifleman_b", "hold"),
      (*radial(R_RIV - 21.5, -24.0), "rifleman_c", "hold"), (*radial(R_RIV - 16.0, -2.0), "officer", "hold"),
      (*radial(R_RIV - 26.0, 17.5), "rifleman_a", "advance"), (*radial(R_RIV - 30.0, -16.0), "assault", "advance")]
B2 += [(*radial(R_RIV - 22.0, 4.0), "rifleman_c", "hold"), (*radial(R_RIV - 28.0, -9.0), "rifleman_a", "hold")]   # 둥지 (2026-11-04)
for i, (x, y, k, b) in enumerate(B2, 1):
    foe(f"ENEMY_b_{i:02d}", x, y, k, "bridge", b, spawn="manual", face=facing_out(x, y))
B2W = [(*radial(436.0, -6.0), "rifleman_b", "advance"), (*radial(432.0, 12.5), "assault", "flank"),
       (*radial(440.0, -18.0), "rifleman_c", "flank"), (*radial(428.0, 16.0), "riot", "rush")]
for i, (x, y, k, b) in enumerate(B2W, 1):
    foe(f"ENEMY_bw_{i:02d}", x, y, k, "bridge_wave", b, spawn="manual", face=facing_out(x, y))
G3 = [(*radial(350.4, -14.0), "rifleman_a", "hold"), (*radial(350.4, 6.5), "rifleman_b", "hold"),
      (*radial(338.2, -26.0), "rifleman_c", "hold"), (*radial(336.2, 20.0), "rifleman_a", "hold"),
      (*radial(328.0, -30.0), "officer", "hold"), (*radial(316.2, -4.0), "rifleman_b", "advance"),
      (*radial(320.2, -40.0), "assault", "advance")]
G3 += [(*radial(361.0, -8.0), "rifleman_b", "hold"), (*radial(364.0, 5.0), "rifleman_c", "hold"),
       (*radial(345.0, -2.5), "assault", "hold")]                                       # 포위 차단선 남쪽 둥지 (2026-11-04)
for i, (x, y, k, b) in enumerate(G3, 1):
    foe(f"ENEMY_g_{i:02d}", x, y, k, "gate", b, spawn="manual", face=facing_out(x, y))
G3W = [(*radial(300.0, -36.0), "rifleman_c", "flank"), (*radial(296.0, -22.0), "assault", "advance"),
       (*radial(304.0, 18.0), "rifleman_a", "flank"), (*radial(300.0, 8.0), "riot", "rush")]
for i, (x, y, k, b) in enumerate(G3W, 1):
    foe(f"ENEMY_gw_{i:02d}", x, y, k, "gate_wave", b, spawn="manual", face=facing_out(x, y))
# ---- 차량: R41 보병전투차 넷 (승무원: 해치 지휘관 + 운전수), 성전군 M1A1 둘 (모나티엄 엘프 승무원)


def veh(vid, x, y, vehicle, faction, face, **props):
    M_(f"VEH_{vid}", x, y, face=face, vehicle=vehicle, faction=faction, **props)


IFV1_PATH = [(-30.0, 512.0), (-44.0, 506.0), (-44.5, 493.0), (-31.0, 487.5), (-20.0, 486.4)]
IFV4_PATH = [(-70.0, 754.0), (-74.0, 738.0), (-62.0, 727.0), (-52.0, 724.0)]
veh("ifv1", *IFV1_PATH[0], "r41_apc", "enemy", IFV1_PATH[1], state="ready", group="ifv1", spawn="manual", driver="ai",
    path="ifv1")
veh("ifv2", *IFV_SPOTS["ifv2"], "r41_apc", "enemy", BRIDGE, state="ready", group="ifv2", spawn="manual", driver="none")
veh("ifv3", *IFV_SPOTS["ifv3"], "r41_apc", "enemy", facing_out(*IFV_SPOTS["ifv3"]), state="ready", group="ifv3",
    spawn="manual", driver="none")
veh("ifv4", *IFV4_PATH[0], "r41_apc", "enemy", IFV4_PATH[1], state="ready", group="ifv4", spawn="manual", driver="ai",
    path="ifv4")
for nm, P_ in (("ifv1", IFV1_PATH), ("ifv4", IFV4_PATH)):
    for i, (x, y) in enumerate(P_, 1):
        M_(f"WP_{nm}_{i:02d}", x, y)
# [오리지널] 마을 기갑 (2026-11-04 사용자 「M9 마을에 장갑차도 3대 배치해. 강습차량 2대랑.」): R41 기관포 장갑차 셋은 길목에 박혀 쏘고
# (1 남쪽 담 안 마당: 마을 어귀 비탈을 덮음, 2 마을 광장 서쪽: 차단벽 줄과 마을 길, 3 북쪽 갈림길: 서쪽 옆길이 마을로 드는 곳),
# V-7 '나나니' 습격차 둘은 옆길을 훑으며 내려온다 (1 서쪽 옆길 북 → 남, 2 동쪽 담 밖 띠 북 → 남). 마을 길·전차 길에는 두지 않는다
# (부서진 잔해가 성전군 전차 길을 막지 않게). 차례는 미션이 정한다 (m9.village.ts: 어귀 → 광장 → 북쪽 물결)
VAPC = {"vapc1": ((30.0, 126.5), (8.0, 116.0)), "vapc2": ((-13.0, 180.0), (-2.0, 160.0)), "vapc3": ((-22.0, 207.0), (-6.0, 190.0))}
for vid, ((x, y), fc) in VAPC.items():
    veh(vid, x, y, "r41_apc", "enemy", fc, state="ready", group=vid, spawn="manual", driver="none")
VRAID = {"vraid1": [(-30.0, 214.5), (-37.0, 208.5), (-40.0, 196.0), (-40.0, 180.0), (-40.0, 160.0), (-40.0, 134.0)],
         "vraid2": [(44.0, 186.0), (43.5, 176.0), (43.5, 156.0), (43.5, 131.0)]}
for vid, P_ in VRAID.items():
    veh(vid, P_[0][0], P_[0][1], "r41_raider", "enemy", P_[1], state="ready", group=vid, spawn="manual", driver="ai", path=vid)
    for i, (x, y) in enumerate(P_[1:], 1):
        M_(f"WP_{vid}_{i:02d}", x, y)
# 전차: 헛간 뒤 집결지 → (a) 갈림길 동쪽 사격 자리 → (b) 강 남쪽 둑 동쪽 → (c) 여울을 건너 동쪽 차선 → 성문 앞
TANKS = {
    "tank1": [[(30.0, 510.0), (22.0, 507.0), (16.0, 505.0)],
              [(16.0, 505.0), (10.0, 525.0), radial(R_RIV + 15.0, 22.0)],
              [radial(R_RIV + 15.0, 22.0), radial(470.0, 24.0), radial(430.0, 26.0), radial(392.0, 26.0), radial(358.0, 22.0)]],
    "tank2": [[(42.0, 511.0), (34.0, 509.5), (28.0, 509.0)],
              [(28.0, 509.0), (20.0, 527.0), radial(R_RIV + 19.0, 32.0)],
              [radial(R_RIV + 19.0, 32.0), radial(468.0, 34.0), radial(428.0, 36.0), radial(392.0, 36.0), radial(364.0, 34.0)]],
}
for tid, legs in TANKS.items():
    x0, y0 = legs[0][0]
    veh(tid, x0, y0, "m1a1", "ally", (x0 - 10.0, y0), state="ready", group="tanks", spawn="manual", driver="ai",
        path=f"{tid}_a", crew="1")
    for leg, pts in zip("abc", legs):
        for i, (x, y) in enumerate(pts, 1):
            M_(f"WP_{tid}_{leg}_{i:02d}", x, y)
# 모나티엄 기동대 (2026-11-03 사용자 지시: 칸나 "기동대를 보낼게. 아주 끝장내버리자고!"): 돌격 신호에 전차 둘이 출발 참호 앞에서
# 들판으로 굴러 나가 1선을 친다 (WP_tankN_s). 그 뒤로 진격로를 끝까지 몰고 간다 (전차 차선으로 능선을 넘어 골짜기 집결지까지).
# 진압반 보병 여섯(ALLY_riot_nn, M4A1)이 전차 곁에서 함께 나아간다 (미션이 전차 뒤 자리로 부른다)
# 2026-11-03 사용자 지적 "전차 왜 안 움직여?": 출발 들판 사격 자리에서 멈춰 있지 않고 진격에 맞춰 단계마다 더 나아간다
#   s = 돌격 신호: 출발 참호 앞 → 철조망 띠 앞 (1선을 친다)
#   t = 1선 항복 장면: 철조망 틈(x -11.5..-4.5)·1선 둑길(x -10..-5)·지원 참호 둑길을 지나 1선 너머 (tank2는 동쪽 들판에서 길로 들어와 뒤따른다)
#   u = 마을에 들어설 때: 마을 남쪽 돌담 틈을 지나 마을 어귀 (R41 차단벽 앞에서 선다)
#   v = 마을 투항 장면: 차단벽 틈(x -5.1..0.6)으로 마을 길을 지나 북쪽 끝, h = 지휘부 단계: 지휘소 앞 사격 자리
#   w = 지휘 회선을 끊은 뒤: 지휘소 동쪽으로 돌아 차선을 따라 능선 마루 (tank2는 16 m 뒤)
#   x = 숲 내리막: 차선을 따라 골짜기로, 헛간과 창고 사이를 지나 헛간 뒤 집결지 (경로 a의 첫 점)
#   헛간 뒤에서 기다리던 셋째 전차(증원)는 없앴다: M9 성전군 전차는 이 둘뿐이다 (2026-11-04 사용자 지시)
# 헛간 뒤로 꺾어 들어가는 길: 헛간 북동 모서리(44, 501.5)에 걸리지 않게 들판 담(부서짐)을 밟고 더 올라가서 서쪽으로 꺾는다
LANE_IN = [(48.2, 505.5), (46.0, 509.6), (40.0, 510.6), (34.0, 510.3)]   # tank1 → 집결지 (30, 510)
START_TANKS = {
    "tank1": {"s": [(-13.5, 12.0), (-11.8, 30.0), (-9.6, 50.0), (-8.0, 63.0)],
              "t": [(-8.0, 63.0), (-7.5, 76.0), (-7.5, 90.0), (-7.5, 104.0), (-6.0, 113.0)],
              "u": [(-6.0, 113.0), (-4.0, 124.0), (-2.2, 134.0), (-1.6, 141.0)],
              "v": [(-1.6, 141.0), (-2.1, 149.0), (-2.25, 158.1), (-2.0, 166.0), (-1.3, 175.0), (-1.0, 184.0),
                    (-1.0, 193.0)],
              "h": [(-1.0, 193.0), (0.0, 200.0), TANK_LANE[0]],
              "w": TANK_LANE[:LANE_CREST + 1],
              "x": TANK_LANE[LANE_CREST:] + LANE_IN + [TANKS["tank1"][0][0]]},
    "tank2": {"s": [(18.0, 14.0), (19.5, 26.0), (21.0, 38.0), (21.5, 50.0)],
              # 들판 남쪽으로 돌아 tank1 길(철조망 틈 → 1선 둑길)을 곧게 따른다 (예전 길은 그루터기·철조망 끝·참호 벽에 걸려 섰다)
              "t": [(21.5, 50.0), (12.0, 49.5), (0.0, 50.5), (-9.6, 52.0), (-8.5, 60.0), (-7.5, 68.0), (-7.5, 80.0),
                    (-7.5, 91.0)],
              "u": [(-7.5, 91.0), (-7.5, 104.0), (-6.0, 112.0)],
              "v": [(-6.0, 112.0), (-4.0, 124.0), (-2.4, 134.0), (-1.9, 142.0), (-2.15, 150.0), (-2.25, 158.1),
                    (-2.0, 166.0), (-1.4, 174.0)],
              "h": [(-1.4, 174.0), (-1.2, 182.0), (-2.0, 189.0), (-3.0, 194.0)],
              "w": [(-3.0, 194.0), (-1.0, 201.0), (3.5, 205.0)] + TANK_LANE[1:LANE_CREST - 1] + [(35.3, 324.0)],
              "x": [(35.3, 324.0)] + TANK_LANE[LANE_CREST - 1:] + [(48.2, 505.5), (45.5, 509.8),
                                                                   TANKS["tank2"][0][0]]},
}
for tid, legs in START_TANKS.items():
    for leg, pts in legs.items():
        for i, (x, y) in enumerate(pts, 1):
            M_(f"WP_{tid}_{leg}_{i:02d}", x, y)
for i, (x, y) in enumerate(((-17.5, 7.0), (-9.5, 7.0), (22.5, 9.0), (13.5, 14.5), (-39.0, 7.5), (-31.5, 7.0)), 1):
    M_(f"ALLY_riot_{i:02d}", x, y, face=north(x, y), who="riot", behavior="hold", weapon="m4a1")
# 진격로 연장 (요정 전열): 능선 전망대 다음부터 성문 앞까지. 미션이 전열 진격로 끝(능선)에 extend()로 잇는다
EXT = TRACK[1:] + [JUNCTION, (-8.0, 515.0), (-14.0, 545.0), BRIDGE, radial(R_RIV - 11.0), radial(420.0), radial(380.0),
                   SIEGE, END]
for i, (x, y) in enumerate(EXT, 1):
    M_(f"WP_ext_{i:02d}", x, y, deck_z(0.0) if (x, y) == BRIDGE else None)
# 엄폐 (COL 상자 안에 빠진 자리는 버린다)


def in_col(x, y, z):
    if any(x0 < x < x1 and y0 < y < y1 and z0 < z + 0.4 < z1 for (_, x0, x1, y0, y1, z0, z1) in C.cols):
        return True
    for (_, ox, oy, oz, sx, sy, sz, yaw) in C.ocols:      # 돌린 COL 상자 (키트 소품)
        a = math.radians(yaw)
        lx = (x - ox) * math.cos(a) + (y - oy) * math.sin(a)
        ly = -(x - ox) * math.sin(a) + (y - oy) * math.cos(a)
        if abs(lx) < sx / 2 and abs(ly) < sy / 2 and oz < z + 0.4 < oz + sz:
            return True
    for (_, vs) in C.ccols:                                # 볼록 COL (건초 더미 등): 경계 상자로 본다
        if (min(v[0] for v in vs) < x < max(v[0] for v in vs) and min(v[1] for v in vs) < y < max(v[1] for v in vs)
                and min(v[2] for v in vs) < z + 0.4 < max(v[2] for v in vs)):
            return True
    return False


COVERS += [(x, y, h, "n") for (x, y, h) in EXT_COVERS]
n_cov = 0
for (x, y, h, d) in COVERS:
    if in_col(x, y, fz(x, y)):
        continue
    n_cov += 1
    M_(f"COVER_{n_cov:02d}", x, y, face=north(x, y), height=h)
# 목표 지점
M_("MARK_line1", -7.5, 80.0)
M_("MARK_village", -1.0, 146.0)
M_("MARK_hq", -6.0, 227.0)
cx_, cy_, cz_ = CP["console"]
M_("MARK_hq_console", cx_, cy_, cz_, face=(cx_, cy_ + 5.0))
M_("MARK_ridge", RIDGE[0], RIDGE[1], face=north(*RIDGE))
ZR = G.h(*RIDGE)
# 연장 목표 지점
M_("MARK_valley2", JUNCTION[0], JUNCTION[1] + 3.0, face=(-8.0, 515.0))
M_("MARK_bridge", *radial(R_RIV - 13.0), face=radial(420.0))
M_("MARK_gate", *SIEGE, face=(GFRONT.x, GFRONT.y))
M_("MARK_end", END[0], END[1], face=(GFRONT.x, GFRONT.y))
GD = GATE["door"]
M_("MARK_door", GD.x, GD.y, GD.z)
ZE = G.h(*END)
# 하늘의 결전: 성문 너머 세계수 수관 앞 하늘 (왕성 위, 끝 자리에서 올려다보는 각 약 38°). 수관 아래 그늘에 금빛이 읽힌다
FIN = (*radial(165.0, -8.0), EZ + 125.0)
M_("MARK_finale", *FIN)
M_("MARK_erpien", EX, EY, ERP["castle_z"])
M_("MARK_rear", RX, RY)
for i, (x, y) in enumerate(REAR, 1):
    M_(f"WP_rear_{i:02d}", x, y)
# 트리거
TRIGS = []


def trig(tid, x0, x1, y0, y1, z0, z1):
    o = mk._box_obj(f"TRIG_{tid}", x0, x1, y0, y1, z0, z1)
    o["collider"] = 0
    C.add_node(o)
    TRIGS.append((f"TRIG_{tid}", (x0, x1, y0, y1, z0, z1)))


trig("line1", -46.0, 46.0, 76.0, 102.0, -2.0, 4.0)
trig("village", -34.0, 34.0, 124.0, 146.0, -1.0, 8.0)
trig("hq", -16.0, 4.0, 218.0, 234.0, 0.0, 8.0)
trig("ridge", -8.0, 12.0, 333.0, 347.4, ZR - 3.0, ZR + 5.0)
trig("descent_mid", -50.0, 66.0, 396.0, 404.0, G.h(4.0, 400.0) - 6.0, G.h(4.0, 400.0) + 8.0)
ZJ = G.h(*JUNCTION)
trig("valley", -24.0, 16.0, 471.0, 498.0, ZJ - 2.0, ZJ + 6.0)
TB = radial(R_RIV - 15.0)
trig("bridge", TB[0] - 16.0, TB[0] + 16.0, TB[1] - 6.0, TB[1] + 6.0, G.h(*TB) - 2.0, G.h(*TB) + 6.0)
TG = radial(352.0)
trig("gate", TG[0] - 24.0, TG[0] + 24.0, TG[1] - 6.0, TG[1] + 8.0, EZ - 1.5, EZ + 6.0)
trig("end", END[0] - 12.0, END[0] + 12.0, END[1] - 7.0, END[1] + 14.0, EZ - 1.5, EZ + 6.0)
# 마지막 광각 (성문 앞 → 에르피엔 하늘)
C.cam("finale", [
    (0.0, (END[0] + 1.6, END[1] + 4.0, ZE + 1.5), (FIN[0], FIN[1], FIN[2] - 60.0), 50.0),
    (6.0, (END[0] - 7.0, END[1] - 3.0, ZE + 0.9), (FIN[0] + 10.0, FIN[1], FIN[2] - 30.0), 44.0),
    (12.0, (END[0] + 6.0, END[1] + 14.0, ZE + 7.0), (EX, EY, ERP["castle_z"] + 60.0), 38.0),
])

# ================================================================== bounds (보이지 않는 벽)
C.group("bounds")


def wall_line(pts, z0=-12.0, z1=40.0, t=1.0):
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        x0, x1 = sorted((ax, bx))
        y0, y1 = sorted((ay, by))
        zs = [prof(y) for y in (y0, (y0 + y1) / 2, y1)]
        C.col(x0 - t / 2, x1 + t / 2, y0 - t / 2, y1 + t / 2, min(zs) + z0, max(zs) + z1)


wall_line([(-54.5, -48.0), (-54.5, 113.0), (-50.5, 113.0), (-50.5, 212.0), (-46.0, 212.0), (-46.0, 348.0)])
wall_line([(54.5, -48.0), (54.5, 113.0), (50.5, 113.0), (50.5, 212.0), (46.0, 212.0), (46.0, 348.0)])
wall_line([(-54.5, -48.0), (54.5, -48.0)])


def wall_slope(pts, t=1.0, below=6.0, above=34.0):
    """비스듬한 보이지 않는 벽 (마디마다 돌린 상자, 땅 높이를 따른다). 축 정렬 상자는 대각선 마디에서 통로 안으로 튀어나왔다."""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        if L < 0.1:
            continue
        zs = [G.h(ax + (bx - ax) * k / 6, ay + (by - ay) * k / 6) for k in range(7)]
        C.ocol(((ax + bx) / 2, (ay + by) / 2, min(zs) - below), (L + t, t, max(zs) - min(zs) + below + above),
               yaw=math.degrees(math.atan2(by - ay, bx - ax)))


# 진격로 연장: 전망대 → 성문 앞 (예전 북쪽 막힘 벽 y 348은 걷었다). 끝은 에르피엔 성벽 몸통 속
wall_slope(WEST_WALL)
wall_slope(EAST_WALL)

# ================================================================== checks + export
ROOT = {
    "sky": "#efb592",              # 해 질 녘 복숭아빛 하늘 (안개색과 같다)
    "fog": "140,2600",
    "sun": "-0.93,0.24,0.27",      # 서남서의 낮은 해 (three.js: -x = 서쪽, +z = 남쪽), 그림자가 동쪽으로 길게
    "sunColor": "#ffb877",
    "sunIntensity": 2.25,
    "ambient": 1.1,
    "hemiSky": "#cdb8d8",
    "hemiGround": "#6f5d55",
    "near": 0.05,
    "far": 5000,
    "music": "m9",
    "timeOfDay": "dusk",
}

STAND = ("ENEMY_", "ALLY_", "COVER_", "SPAWN_", "WP_", "MARK_sur", "MARK_hq", "MARK_ridge", "MARK_rear", "MARK_line1",
         "MARK_village", "NPC_", "MARK_valley2", "MARK_bridge", "MARK_gate", "MARK_end", "VEH_")
for (nm, loc, rot, props, g, sc) in C.markers:
    if not nm.startswith(STAND):
        continue
    x, y, z = loc
    if in_col(x, y, z):
        print(f"[m9] 경고: {nm} ({x:.1f},{y:.1f},{z:.2f}) 가 COL 안")
# 돌격로 직선 검사: COL 상자를 지나가면 경고
for i in range(1, 13):
    pts = CHARGE[i]
    for (a, b) in zip(pts, pts[1:]):
        for k in range(1, 40):
            t = k / 40
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            z = fz(x, y)
            for (cn, x0, x1, y0, y1, z0, z1) in C.cols:
                if x0 < x < x1 and y0 < y < y1 and z0 < z + 0.5 < z1:
                    print(f"[m9] 경고: 돌격로 {i:02d} ({x:.1f},{y:.1f}) 가 {cn}를 지난다")
                    break

# 전차 차선: 차체 폭(반폭 2.6 m: 1.83 + 조향 흔들림) · 높이(3.2 m: 큐폴라·전차장) 안을 지나는 COL, 땅 기울기, 깎고 돋운 높이
lane_cols = set()
LANE_SEGS = [seg for pts in [TANK_LANE] + [START_TANKS[t][k] for t in START_TANKS for k in "stuvhx"] + [TANKS[t][0] for t in TANKS]
             for seg in zip(pts, pts[1:])]
for (a, b) in LANE_SEGS:
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    for k in range(int(L) + 1):
        for off in (-2.6, -1.3, 0.0, 1.3, 2.6):
            x, y = a[0] + ux * k - uy * off, a[1] + uy * k + ux * off
            z = G.h(x, y)
            for (cn, x0, x1, y0, y1, z0, z1) in C.cols:
                if x0 < x < x1 and y0 < y < y1 and z0 < z + 3.2 and z1 > z + 0.35 and "BRK" not in cn:
                    lane_cols.add(f"{cn} ({x:.1f},{y:.1f})")
            for (cn, ox, oy, oz, sx, sy, sz, yaw) in C.ocols:
                a_ = math.radians(yaw)
                lx = (x - ox) * math.cos(a_) + (y - oy) * math.sin(a_)
                ly = -(x - ox) * math.sin(a_) + (y - oy) * math.cos(a_)
                if abs(lx) < sx / 2 and abs(ly) < sy / 2 and oz < z + 3.2 and oz + sz > z + 0.35:
                    lane_cols.add(f"{cn} ({x:.1f},{y:.1f})")
            for (cn, vs) in C.ccols:
                if (min(v[0] for v in vs) < x < max(v[0] for v in vs) and min(v[1] for v in vs) < y < max(v[1] for v in vs)
                        and min(v[2] for v in vs) < z + 3.2 and max(v[2] for v in vs) > z + 0.35):
                    lane_cols.add(f"{cn} ({x:.1f},{y:.1f})")
for c in sorted(lane_cols):
    print(f"[m9] 경고: 전차 차선이 {c}를 지난다")
grade, cut = 0.0, 0.0
for i in range(int(_LANE_S[-1])):
    def lp(s):
        j = max(k for k in range(len(_LANE_S) - 1) if _LANE_S[k] <= s)
        (ax, ay), (bx, by) = TANK_LANE[j], TANK_LANE[j + 1]
        t = (s - _LANE_S[j]) / (_LANE_S[j + 1] - _LANE_S[j])
        return ax + (bx - ax) * t, ay + (by - ay) * t
    p0, p1 = lp(i), lp(min(i + 2, _LANE_S[-1] - 0.01))
    grade = max(grade, math.degrees(math.atan2(abs(G.h(*p1) - G.h(*p0)), math.dist(p0, p1))))
    cut = max(cut, abs(G.h(*p0) - H_base(*p0)))
print(f"[m9] 전차 차선 {_LANE_S[-1]:.0f} m, 가장 가파른 곳 {grade:.1f}°, 깎고 돋운 높이 최대 {cut:.1f} m, COL {len(lane_cols)}곳")

stats = C.finish("levels/m9_assault.glb", root_props=ROOT, outline=0.025)

print("[m9] ---- 계약 노드 (Blender x, y, z) ----")
for (nm, loc) in sorted(CONTRACT, key=lambda t: t[0]):
    if nm.startswith(("COVER_", "WP_charge_")):
        continue
    print(f"[m9] {nm:22s} {loc[0]:8.2f} {loc[1]:8.2f} {loc[2]:7.2f}")
print(f"[m9] COVER {sum(1 for n, _ in CONTRACT if n.startswith('COVER_'))}개, "
      f"WP_charge {sum(1 for n, _ in CONTRACT if n.startswith('WP_charge_'))}개")
for nm, b in TRIGS:
    print(f"[m9] {nm:22s} x {b[0]:.1f}..{b[1]:.1f} y {b[2]:.1f}..{b[3]:.1f} z {b[4]:.1f}..{b[5]:.1f}")
