# 프롤로그 함내 레벨 `prologue_ship`

헤일리의 기함 「큰망치」(선봉대 기함, 병력 수송 겸용) 내부다. 리타의 정찰 침투조가 이 배에 타고 있다. 오프닝 컷신(브리핑 → 함내 이동 → 사격장 클로즈업)과 튜토리얼(T01~T13), 엔딩이 한 레벨에서 이어진다.

- 시나리오: `docs/scenario.md` '프롤로그', 대본: `docs/script/prologue.md`, 노드 규칙: `docs/LEVELS.md`
- 스크립트: `art/blender/levels/prologue_ship.py` → `public/models/levels/prologue_ship.glb`
- 모듈 키트: `art/blender/lib/level_kit.py` (벽·바닥·천장·문틀·창·계단·난간·표지·별 배경, 마커, 정점색 병합)
- 소품: `art/blender/props/ship_*.py` → `public/models/props/ship_*.glb` (PROP_ 마커로 배치)
- 미션: `src/game/missions/prologue.ts`(`?mission=prologue`). 노드 이름은 미션 그레이박스(`src/game/level/greybox/prologueShip.ts`)의 규약을 따른다.

```bash
npm run model -- art/blender/levels/prologue_ship.py               # 본 glb
PREVIEW=1 npm run model -- art/blender/levels/prologue_ship.py     # _tmp 미리보기: 천장·별 빼고 소품 불러오고 마커 표시
PREVIEW=col npm run model -- art/blender/levels/prologue_ship.py   # COL_ 박스를 붉게
npm run shot -- _tmp/prologue_ship_preview.glb --views top           # 평면
npm run gamecheck -- --query "mission=prologue&step=T02_MOVE&autostart=1&nodebug=1" --steps '[...]'
```

---

## 1. 평면도

Blender 좌표(X 오른쪽 = 우현, Y 앞 = 함미, Z 위). three.js에서는 (x, z, -y). 뱃머리는 -Y. 주갑판 z=0, 상갑판 z=4.4.

```
 y=60 ┌───────────────┐
      │  사로 5개      │                                   사격 방향 +Y
      │  (x -7..2)    │
      │  40 m ─────── │
 y=41 │               │ ┌───┬───┐┌──────────────────────────────────────┐
      │               │ │통│통│││ 북쪽 통로: 점프 상자 0.45/0.90 → 기는 굴(0.88) → │
      │  20 m ─────── │ │로│로││├──3번 벽(섬 북벽) 옆 0.55 m 틈 = 지름길 ───────┤
 y=36 │               │ │A │B │││직│                              │ 동쪽 통로     │
      │               │ │  │상│││선│   섬(표적 구역, 표적 9개)      │ (사격 구간)   │
      │               │ │달│자│││로│   서·북 벽 2.0 m, 남 벽 2.7 m   │ 엄폐벽 0.7 m  │
      │  10 m ─────── │ │리│배│││ │                               │ 앉기 막 0.88  │
      │               │ │기│관│││1·2번│                            │ 점프 상자 0.45│
 y=16 ├─사대(턱 0.75)─┤ └──┴──┘││벽  │                            │ 계단 6단 ↑    │
 y=15 │ 칸막이·노란 선 │        │├출발┴──────────────────────────┬──┴──────────┤
      │ 대기실: 기록판·리타 시작·캐시          문→ 대기실 ↓뛰어내림 결승│ 위 통로 z 1.08 │
 y=11 └──문─────────────────────┘         └─────────────────────────────────┘
       x=-7      x=2   x=5.9 x=6.3                                        x=22.3
 y=10.6┌──────────문─────┐
      │ 병력 구획 B (x -7..7)           침상 5(좌현, 둥근 창 5) · 사물함 4 · 거치대 2 · 브리핑 보드
 y=-2.2└─────문(DOOR_bay_hatch)─┘
 y=-2.6┌────────────────┐
      │ 승강 구간 (x -7..4.8, 높이 8.8)  좌현 큰 창 3 · 중력 승강기 빛기둥 · 계단(0.22 x 20단, 중간 층계참)
 y=-12.6└─────┬통로┬──┘   위 층계참 z 4.4
 y=-16.4┌─────┴DOOR_bridge┴──┐
      │ 함교 (z 4.4, 높이 3.6)  지휘 단상 · 홀로 테이블 · 떠 있는 지구 망원 화면 · 콘솔 6
 y=-29 └──── 앞 창 5칸 ─────┘
```

| 구역 (`zone_*`) | 범위 (m) | 천장 | 의도 |
|---|---|---|---|
| bridge 함교 | x -7..7, y -29..-16.4, z 4.4 | 3.6 | 오프닝 3 브리핑. 앞 창 너머 함대와 목적지 행성, 떠 있는 망원 화면(북미 조준), 홀로 테이블 지구 홀로그램, 금색 바닥 고리 |
| atrium 승강 구간 + 통로 | x -7..4.8, y -12.6..-2.6 (통로 x 3.2..4.8, y -16.2..-12.8) | 8.8 (통로 2.4) | 오프닝 4. 함교 문 → 좁은 통로 → 트인 2층 공간. 좌현 큰 창으로 함대, 가운데 빛기둥을 타고 내려간다 |
| troop 병력 구획 B | x -7..7, y -2.2..10.6 | 2.9 | 정찰 침투조 대기. 둥근 창 아래 침상, 사물함, 7식 소총 거치대, 브리핑 보드 '정찰 침투조 · 함내 대기' |
| range 사격장 | 대기실 x -7..5.9, y 11..15 / 사로 x -7..2, y 15..60 / 옆 통로 x 2.3..5.9, y 15..38.2 | 3.2 (옆 통로 2.6) | 오프닝 5와 T01~T10. 사로 5개, 리타는 3번 사로. 옆 통로 A·B가 U자로 이어진 기동 훈련로 |
| course 훈련 구획 | x 6.3..22.3, y 11..41 | 4.6 | T11~T13 타임 어택. 남색 홀로 방 + 시안 격자, 하드 라이트 홀로 벽 |
| space 창밖 | 좌현 x -40, 앞 y -64 | | 별 판 2장, 함대 실루엣 8척, 목적지 행성 |

## 2. 치수 (엘프 체격, `docs/LEVELS.md`)

| 항목 | 값 | 기준 |
|---|---|---|
| 문 | 1.0~2.0 x 2.0~2.1 m (함교 1.0 x 2.0, 병력 구획 1.8 x 2.1, 사격장 2.0 x 2.1, 훈련 구획 1.6 x 2.1) | 높이 1.8 이상, 폭 0.9 이상 |
| 통로 | 상갑판 통로 1.6, 옆 통로 A 1.6 · B 1.8, 코스 통로 3.2~3.8 | 1.2 이상 |
| 계단 | 승강 구간 단 0.22 x 디딤 0.32 (10단 x 2), 지휘 단상 0.18 x 2, 코스 0.18 x 6 (디딤 0.32) | 자동 오르기 0.28 |
| 점프 | 사격장 탄약 상자 0.42 (옆 높은 더미 1.26), 코스 점프 상자 0.45 → 0.90, 동쪽 점프 상자 0.45 | 점프 0.6 |
| 앉기 | 사격장 배관 밑 0.88, 코스 기는 굴 0.88 (길이 3 m), 동쪽 앉기 막 0.88 | 앉은 키 0.82 |
| 사대 | 턱 높이 0.75 (눈높이 0.9 아래), 칸막이 1.45, 노란 선은 턱 0.65 m 앞 | |
| 경사 | 없음 (모든 높이 차이는 계단) | 46° |

## 3. 동선

### 3.1 오프닝 카메라 (`CAM_<shot>_<nn>` + `LOOK_`)
| 레일 | 점 | 길이 | 내용 |
|---|---|---|---|
| `brief_a` | 2 | 7 s | 단상 왼쪽 위에서 넓게: 헤일리, 홀로 테이블, 망원 화면, 창 |
| `brief_b` | 2 | 6 s | 헤일리 얼굴 클로즈업 (fov 30 → 27) |
| `brief_c` | 2 | 6 s | 홀로그램 너머 지구 망원 화면 (북미 조준 표시) |
| `brief_d` | 2 | 6 s | 헤일리 뒤에서 승무원 쪽 역방향 |
| `descent` | 8 | 16 s | 함교 문 → 통로 → 위 층계참(창 너머 함대) → 빛기둥 → 병력 구획 문 → 침상·대원 → 사격장 문 → 기록판 |
| `closeup` | 7 | 11 s | (예비) 리타 어깨 너머 캐시 → 캐시 → 기록판 → 리타 → 리타의 눈. 마지막 점 = SPAWN_player 눈높이 0.9 m, 정면 +Y |

미션은 `brief_*`를 대사마다 골라 자르고, 클로즈업은 NPC 눈 위치로 직접 만든다. 함내 이동 컷 동안 `DOOR_bay_hatch`를 연다.

### 3.2 튜토리얼 (`docs/script/prologue.md` 6~7장, 미션 `prologue.ts` 이름)
| 단계 | 장소 | 노드 |
|---|---|---|
| 시작 | 사격장 대기실, 리타 사로 뒤 3.1 m | `SPAWN_player`, `NPC_rita`(같은 자리, 컷신용) |
| T01 둘러보기 | 대기실에서 3번 사로 끝 | `TARGET_ads_1..3`(static, `lamp=1`, 25/29.5/33.5 m), 옆 사로 `TARGET_decor_1..6`(불 꺼짐), 소화기 `MARK_extinguisher` |
| T02 걷기 | 3번 사로 노란 선 | `MARK_range_line`, `TRIG_range_line`, 옆 칸 `TRIG_lane_left`(2번), `TRIG_lane_right`(4번) |
| T03 달리기 | 옆 통로 A 입구 → 20 m 끝 표시선 | `MARK_sprint_start`, `TRIG_sprint_start`, `MARK_sprint_end`, `TRIG_sprint_end` |
| T04 점프 | 통로 A 끝에서 U자로 돌아 통로 B의 탄약 상자 0.42 m | `MARK_jump`, `TRIG_jump_zone`, `TRIG_jump_done` |
| T05 앉기 | 통로 B 낮은 배관(틈 0.88 m) | `MARK_crouch`, `TRIG_crouch_zone`(배관 밑, 높이 0.88까지), `TRIG_crouch_done` |
| T06~T10 | 통로 B 끝 → 대기실 → 3번 사대 | `TRIG_range_line`, `TARGET_hip_1..3`(5.5~8.2 m), `TARGET_ads_*`(T07), `TARGET_pistol_1..3`(11~15 m) |
| T11 | 훈련 구획 출발선 | `MARK_course_start`, `TRIG_course_start` |
| T12 | 직선로(1·2번 지그재그 벽) → 북쪽 점프 상자·기는 굴 → 북동 반환점 → 동쪽 사격 구간 → 계단 → 위 통로 → 결승 → 대기실로 뛰어내림 | `TRIG_course_cp1`(북동), `TRIG_course_cp2`(동쪽 계단 아래), `MARK_course_cp1/cp2`, `TRIG_course_end`, `MARK_course_end`, `TARGET_course_01..10` + 이동 표적 `TARGET_course_mv`(`WP_course_mv_01/02`) |
| T13 | 결승 뒤 출발선으로 | `MARK_course_start` |

타임 어택 추정: 코스 길이 약 75 m, 표적 11개. 첫 주행 40~45초, 익숙하면 30~33초를 노렸다(달리기 5.4 m/s, 앉기 1.7 m/s, 표적당 0.8~2초). 캐시 기록 33.70초는 3번 벽 옆 0.55 m 틈(기는 굴을 서서 지나감)으로 1.5~2초를 줄인 기록이라는 설정이다.

## 4. 마커 목록

| 종류 | 이름 |
|---|---|
| SPAWN | `SPAWN_player` (-2.2, 12.6, 0), 정면 +Y |
| NPC | `haley`(characters/haley.glb, at_ease), `cathy`(cathy_prologue, cross_arms, look player), `rita`(rita_prologue, role cinematic), 함교 `crew_01..03`·`bridge_01..03`, 승강 구간 `runner_01..03`(path `runner_n` → `WP_runner_n_01..04`), 병력 구획 `bay_01..06`, 사격장 `range_01..03`. 엑스트라 모델은 `characters/_kit_elfinia_soldier.glb`, `pose`는 미션 자세 이름(idle, at_ease, attention, cross_arms, hands_hips) |
| TARGET | `ads_1..3`(static, lamp), `decor_1..6`(static), `hip_1..3`, `pistol_1..3`, `course_01..10`(popup), `course_mv`(moving, speed 1.3) |
| TRIG | `range_line`, `lane_left`, `lane_right`, `sprint_start`, `sprint_end`, `jump_zone`, `jump_done`, `crouch_zone`, `crouch_done`, `course_start`, `course_cp1`, `course_cp2`, `course_end` |
| MARK | `range_line`, `sprint_start`, `sprint_end`, `jump`, `crouch`, `course_start`, `course_cp1`, `course_cp2`, `course_end`, `record_board`(기록판 화면 앞, 아래에 레벨 기록판 메시가 붙어 있음), `extinguisher`, `bridge` |
| WP | `cathy_board/booth/passage/door/course/finish`, `course_mv_01/02`, `runner_1..3_01..04` |
| DOOR | `DOOR_bay_hatch`(병력 구획 ↔ 승강 구간, 위로 2.2 m, 기본 닫힘), `DOOR_bridge`(함교 뒤 문, +X로 1.05 m, 기본 닫힘) |
| LIGHT | `LIGHT_alert_01..07`(경고등, group alert), `LIGHT_radio_01/02`(스피커 고리, group radio), `LIGHT_emergency_01..29`(적색 비상등, group emergency), `LIGHT_main_01..08`(평상 천장 조명판, group main, `on=1`). 모두 `emissiveToggle=1` |
| SPEAKER | `SPEAKER_radio_01`(사격장 대기실), `SPEAKER_radio_02`(훈련 구획) |
| FX·DEBRIS | `FX_spark_01..18`, `FX_smoke_01..11`, `FX_debris_01..08` + 자식 `DEBRIS_01..08` (8장) |
| HOLO | `HOLO_range`, `HOLO_course`, `HOLO_bridge_earth`(`spin`), `HOLO_bridge_target`(on=0), `HOLO_bridge_record`(on=0, `spin`) |
| WINDOW | `WINDOW_bridge_1..5`, `WINDOW_atrium_1..3`, `WINDOW_troop_1..5` |
| 상태 | `BRIDGE_intact`(on=1), `BRIDGE_damaged`(on=0) |
| PROP | `bunk_01..05`, `locker_01..04`, `gear_rack_01/02`, `range_rack_01/02`, `bench_*`, `crate_*`, `jump_crate_01/02`, `tall_crate_01..03`, `range_crate_*`, `console_*`(6), `extinguisher_01` |

## 5. 시각 언어

- 벽(아래부터): 남색 걸레받이 → 짙은 회녹 징두리 → 남색 턱 + **시안 발광 줄**(높이 1 m, 길잡이) → 밝은 회녹 벽판(둥근 사각 패널선) → 남색 코니스. 2~3 m마다 건메탈 기둥, 금색 고리, 볼트.
- 엘피니아 형태 문법(`weapons-home.md` 2장)을 건축에 옮겼다: 둥근 문틀(위 모서리 둥금, 금색 안테), 스타디움 창, 둥근 창, 금색은 고리·테·로고에만.
- 원작 엘프 로고: 문 위 둥근 판, 함교 뒷벽(1.15 m), 승강 구간 우현 벽(1.3 m), 바닥(병력 구획, 대기실, 훈련 구획, 승강기 바닥), 사대 턱, 사로 끝 방탄판, 표지판, 소품.
- 훈련 구획은 같은 벽 구조를 남색 바탕 + 시안 격자로 바꾼 '홀로 방'이다. 홀로 벽은 반투명 시안 판 + 건메탈 기둥 + 발광 위 테. 벽 번호 1~3.
- 발광은 모두 UNLIT: 시안 줄·화면·조명판, 경고등, 별, 엔진 불빛. 반투명(UNLIT + alpha): 홀로그램, 유리, 빛기둥.

## 6. 성능

| 항목 | 값 |
|---|---|
| 레벨 삼각형 | 66,679 (아웃라인 헐 제외, `BRIDGE_damaged` 4.2k 포함) |
| 소품 (배치 수 반영) | 침상 2,821 x 5, 사물함 2,096 x 4, 거치대 2,922 x 4, 콘솔 901 x 6, 상자 1,170 x 16, 벤치 615 x 3, 소화기 1,038 → 약 58k |
| 합계 | 약 125k (목표 150k 이하). 인물 NPC 제외 |
| 메시 | 187개 (구역·층·종류별 정점색 메시 + UNLIT 머티리얼별 메시 + 이름 있는 메시: 문, 조명, 창, 패널) |
| 머티리얼 | 23 (정점색 `lk_vc`, `lk_vc_dark` + UNLIT·반투명 색) |
| 충돌 | COL_ 박스 203개 (축 정렬, 회전·축척 없음), TRIG_ 13개 |
| glb | 3.9 MB (4,089,836 바이트, 레벨), 소품 7종 합계 0.58 MB |

- 불투명 팔레트 색은 정점색(Col)으로 합쳐 구역·층(천장 따로)·종류(main/detail/fine)마다 메시 하나다. 먹선은 밝은 색 `#4a2229`, 짙은 색 `#24100f` 두 가지.
- 보이는 메시는 모두 `collider=0`. 걷는 바닥·벽·소품 충돌은 단순한 COL_ 박스다.
- 소품은 3k 삼각형, 머티리얼 4개 이하(ART_GUIDE 8장). 소품 메시도 `collider=0`이고 레벨의 COL_ 박스가 충돌을 맡는다.

## 7. 조명 (루트 속성)

`sky` `#0d1428`(우주 남색, 창밖 배경), `fog` `30,160`(사로 40 m 끝만 살짝), `sun` `0.35,1,0.25`(위에서 내려오는 주광), `ambient` 1.3, `music` `prologue_ship`. 실내 분위기는 UNLIT 조명판과 시안 줄이 만든다.

## 8. 엔딩 연출 노드 (함대 피격: 운동에너지 탄두가 함교를 직격)

`docs/scenario.md` '엔딩: 함대 피격'. 규칙은 `docs/LEVELS.md` 노드 표(`LIGHT_`, `FX_`, `DEBRIS_`, `HOLO_`, `WINDOW_`, 상태 노드).

| 노드 | 내용 |
|---|---|
| `LIGHT_main_01..08` | 방마다 천장 조명판 한 메시 (`room`: bridge, corridor, atrium, troop, range, range_lanes, range_passage, course). 끄면 아래 꺼진 렌즈판(회청색)이 보인다 |
| `LIGHT_emergency_01..29` | 적색 비상등 (함교 4, 통로·승강 구간 4, 병력 구획 5, 사격장 11, 훈련 구획 5). 남색 함 + 어두운 붉은 렌즈 위에 발광 렌즈. `room` 속성 |
| `FX_spark_*` | 벽 배선함(남색 함 + 경고 띠 + 천장 배관)에서 튄다. `dir`는 벽 바깥 아래쪽. 함교 쪽 통로 4, 병력 구획 3, 사격장 5, 훈련 구획 2, 직격 뒤 함교 4(`state=damaged`) |
| `FX_debris_*` + `DEBRIS_*` | 천장 패널 (남색 판 + 보강대). 함교 쪽 통로 2, 위 층계참 1, 병력 구획 2, 사격장 3(리타 사로 바로 앞 포함). `floor` = 떨어질 바닥 높이 |
| `FX_smoke_*` | 통로 2, 병력 구획 2, 사격장 3, 훈련 구획 1, 직격 뒤 함교 3(`state=damaged`) |
| `delay` | 직격 지점(함교 앞 창 가운데)에서 거리 / 35 m/s. 함교 쪽 통로 0.4초 → 병력 구획 0.8초 → 사격장 1.2초 → 훈련 구획 1.5초. 충격이 함교 방향에서 번져 온다 |
| `HOLO_range` | 사로 거리선, 매달린 홀로 거리 표지(10/20/40 m), 탄 받침 발광, 옆 통로 A 진행 화살 |
| `HOLO_course` | 홀로 벽 판·위 테·벽 번호, 앉기 막·기는 굴 홀로 막, 출발·결승 문 발광과 글자, 바닥 격자, 진행 화살, 벽 홀로 패널선, 섬 가운데 투사기 빛기둥 |
| `HOLO_bridge_*` | 지구 홀로그램(기본 켜짐, `spin 0,12,0`), 그 아래 `HOLO_bridge_target`(북미 붉은 표시, 브리핑 05에서 켠다), `HOLO_bridge_record`(골든 레코드 원반, 브리핑 02에서 켠다, `spin 0,40,0`). 셋 다 `BRIDGE_intact` 아래에 있다 |
| `WINDOW_*` | 함교 앞 창 5(`BRIDGE_intact` 아래), 승강 구간 큰 창 3, 병력 구획 둥근 창 5 |
| `BRIDGE_intact` | 직격 때 숨길 부분: 앞 벽과 창, 떠 있는 망원 화면, 옆 벽 화면, 홀로 테이블 발광, 홀로그램 |
| `BRIDGE_damaged` | 기본 숨김. 가운데가 찢긴 앞 벽(구멍 x -3.9..3.7, 안쪽으로 휜 선체 판과 부러진 늑골, 불씨), 그을림(벽·바닥·천장), 바닥 잔해 16, 홀로 테이블에 기댄 꺼진 망원 화면, 꺼진 홀로 테이블과 옆 화면(금 감), 늘어진 천장 판과 배선 3가닥 |
| `CAM_bridge_hit_01..03` | 직격 뒤 함교를 다시 보여 주는 레일 (8초, 단상에서 뚫린 앞 벽 쪽으로) |

미션 쪽 연결 메모
- `ShipEmergency`(`src/game/cinematic/emergency.ts`)는 지금 `FX_panel_*`을 떨어지는 패널로 찾는다. 이 레벨은 `FX_debris_*`이고 패널 메시(`DEBRIS_*`)가 마커의 자식이라 `/^(panel|debris)/`로 넓히면 그대로 동작한다.
- `LIGHT_main_*`은 이름에 `light`가 있어 지금의 '평상 조명 띠' 탐지에도 걸린다. `LightGroups.set('main', false)`로 직접 꺼도 된다.
- 직격 순간: `BRIDGE_intact` 숨김 + `BRIDGE_damaged` 보임, `HOLO_*` 끔, `LIGHT_main` 끔 → `LIGHT_emergency` 켬, `FX_*`는 `delay` 순서로.

## 9. 확인 (2026-11-01)

- 뷰어: `shots/_tmp__prologue_ship_preview.png`(평면), 카메라 미리보기(임시 도구 `shots/_lvlcam`)로 `CAM_brief_*`, `CAM_descent_*`, `CAM_closeup_*`, 눈높이 장면을 봤다.
- `gamecheck`(`mission=prologue&step=T02_MOVE`)로 실제 이동을 확인했다.
  - 탄약 상자 0.42: 걸으면 막히고 점프하면 넘는다. 배관 0.88: 서면 막히고 앉으면 지난다.
  - 승강 구간 계단 20단: 바닥에서 상갑판 통로까지 끊김 없이 오른다. 코스 계단 6단: 위 통로(1.08)로 오른다.
  - 코스 점프 상자 0.45 → 0.90 연속 점프, 기는 굴(서면 막힘, 앉으면 통과), 3번 벽 옆 틈(서서 통과), 위 통로에서 대기실로 뛰어내림.

## 10. 남은 문제

- **엔진(플레이어 컨트롤러)**: 높이 0.6~1.8 m 턱에 점프해 부딪히면 캡슐이 모서리에 걸려 공중(발 0.47 m)에 멈추고, 한 번 더 점프하면 올라선다. 위 통로(1.08 m)는 한 방향으로 만들었지만 이 현상으로 거꾸로 오를 수 있다. 사대 턱(0.75 m)도 같은 방법으로 넘을 수 있다. 미션의 반환점 순서(cp1 → cp2)가 지름길을 막는다. `Player.ts`의 접지 판정(모서리 접촉 노멀) 확인이 필요하다.
- 미션 `PROLOGUE_STEPS`의 `quickStart` 좌표는 그레이박스 기준이다. 이 glb에서는 `MARK_range_line`, `MARK_sprint_end`, `MARK_jump`, `MARK_crouch`, `MARK_course_start` 같은 마커 위치를 쓰면 된다.
- 소품·NPC는 PROP_/NPC_ 마커로만 들어 있어서 뷰어(`viewer.html`)에서는 보이지 않는다. `PREVIEW=1` 미리보기에는 소품이 들어간다.
