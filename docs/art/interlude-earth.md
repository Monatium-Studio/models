# 인터루드 1~3 디오라마 세트 (지구)

`docs/scenario.md` '인터루드: 기록'의 1~3번 장면(투항, 포로 생활, 대탈주)을 찍는 세트다. 대본은 `docs/script/interlude.md` 4.1~4.3. 세트는 컷신 카메라가 담는 만큼만 꾸몄다. 몽타주(미션·연출 담당)가 각 세트의 `CAM_`/`LOOK_` 레일을 재생하고, NPC 마커에 포즈를 입히고, 게이트·조명·달력 노드를 켜고 끈다. 엘리아스 쪽 세트(4~7번)는 `docs/art/interlude-elias.md`이고, 루트 속성·NPC 속성·포즈 이름을 그쪽과 맞췄다.

| 무엇 | 스크립트 | 결과물 | 삼각형 |
|---|---|---|---|
| 키트 | `art/blender/lib/interlude_kit.py` | — | — |
| 1 투항 | `art/blender/levels/interlude_surrender.py` | `public/models/levels/interlude_surrender.glb` | 59,291 |
| 2 포로 생활 | `art/blender/levels/interlude_camp.py` | `public/models/levels/interlude_camp.glb` | 49,220 |
| 3 대탈주 | `art/blender/levels/interlude_escape.py` | `public/models/levels/interlude_escape.glb` | 57,094 (그중 쫓아오는 경비 플립북 12k) |
| 백기 | `art/blender/props/interlude_white_flag.py` | `public/models/props/interlude_white_flag.glb` | 1,248 |
| 산타 인형 | `art/blender/props/interlude_santa_doll.py` | `public/models/props/interlude_santa_doll.glb` | 676 |
| 빼돌린 칩 | `art/blender/props/interlude_chip.py` | `public/models/props/interlude_chip.glb` | 485 |

```bash
npm run model -- art/blender/levels/interlude_surrender.py
npm run shot -- levels/interlude_surrender.glb --views top,34
```

---

## 1. 원작 근거

조회: 2026-11-01, 나무위키 「엘프(트릭컬 리바이브)」(지구 침공, 2.12.1 지구 침략 당시, 포로 생활 주석), 「엘레나(트릭컬 리바이브)/작중 행적」(2.2.3 크리스마스 테마극장, 2.2.10·2.2.13 탈출, 4.2.4 '뜨거운 도시의 믿을만한 녀석' 회상). 이미지는 저장소에 넣지 않았다.

| [원작] 서술 (요약) | 세트 반영 |
|---|---|
| 협상하려고 함선을 지구(미국 땅)에 착륙시켰다. 말단 병사의 선제공격 뒤 반격으로 항법·통신 장비가 망가져 고립됐다 | 들판에 처박힌 기함 잔해(`space/elfinia_flagship.glb` 재사용, 피격 함교), 꺼진 창, 붉은 비상등, 연기 3줄기 |
| 헤일리가 무기를 내려놓고 먼저 투항해 인명 피해를 줄였다. 엘레나가 계급을 무시하고 헤일리를 질타했고, 헤일리는 책임을 지고 항복하겠다고 했다 | 헤일리가 백기(왼손)와 권총(오른손)을 들고 줄 앞으로 나와 권총을 먼저 내려놓고 무릎을 꿇는다. 줄이 따라 소총을 내려놓는다 (손에 든 소품 → `DROP_`) |
| '50개 별의 가호를 받는 왕국'(미국) | 밀밭·나무 울타리·전봇대·박공지붕 헛간과 사일로가 있는 농촌. 국기·휘장·문자는 넣지 않았다 |
| 수십 년 동안 기술·노동력을 착취당했다. 납땜·부품 조립 같은 단순 노동, 주 5일 하루 8시간 | 작업장의 기판·인두·부품통, 벽 안내판 "근무: 주 5일 / 1일 8시간" |
| 크리스마스 장난감을 1년 내내 조립·포장·상하차했다(엘레나: 목각인형 조립, 인형 눈 붙이기, 포장). 크리스마스·산타 트라우마 | 작업대의 산타 인형(몸통·머리 따로), 인형 눈 접시, 컨베이어의 선물 상자, 포장대와 "XMAS" 상자 탑, 한여름의 크리스마스 나무 견본과 "크리스마스까지 D-173" 칠판 |
| 점심 돈까스는 맛있었다. 엘레나: 저녁 메뉴가 돈까스였는데 콩자반이 나왔다 | 메뉴판 "오늘의 저녁 / 돈까스 / (콩자반)" 아래 식판의 콩자반 |
| 붕붕드링크(카페인 음료)를 억지로 마셨다 | 작업대·의자·막사 바닥의 노랑·검정 캔 (디자인은 새로 만듦) |
| 엘레나가 노역 중 칩을 빼돌려 차원 게이트를 조립하고 탈출했다. 전원이 빠져나가지는 못했다. 엘레나는 동족을 한 명이라도 더 데려가려 했다 | 비밀 작업장의 게이트, 칩 기판 8장, 막사 문 앞에 남는 엘프 셋(`left_*`) |
| 엘프들이 지구 총기 약 20정을 들고 나왔다 | (반영 안 함: 무기 PROP는 투항 장면에만) |

토마토 주스 같은 소품은 원작 근거를 찾지 못해 넣지 않았다(프롤로그의 토마토 주스 내기는 이 작품의 오리지널 설정).

**[오리지널]** 새벽 들판, 미군식 수용소(퀀셋 막사, 이중 철망과 윤형 철조망, 나무 감시탑), 엘프가 나무 상자를 딛고 인간 높이 작업대에서 일하는 모습, 장난감 공장 재료로만 만든 게이트(컨베이어 롤러, 자동차 배터리, 크리스마스 전구 줄, 포장 리본으로 묶은 케이블, 마스코트 산타 인형), 리본으로 감아 빼돌린 칩, 기함 안테나로 만든 백기.

---

## 2. 키트 `interlude_kit`

`level_kit.Level`(지오메트리 누적, 정점색 합치기, 마커, `cam_rail`, `special`)을 그대로 쓰고 지구 팔레트와 모듈만 더했다. **`level_kit.py`(프롤로그 담당)에 의존한다.**

- `ik.begin(name, mode)` → `cb.reset` + 팔레트 등록 + `Level`. `mode="night"`이면 불투명 팔레트 전체를 남청으로 눌러 등록한다(`night()`). 엔진 주광 세기가 2.4로 고정이라 밤을 조명만으로 만들 수 없어서 색 자체를 밤색으로 칠한다. UNLIT 발광은 그대로 밝다.
- `ik.finish(L, path, root_props)` → 묶음 노드와 불러온 glb를 루트 아래로 옮기고 모든 메시에 `collider=0`.
- `ik.Frame(origin, yaw)`: 지역 좌표계. `ik.Group(L, name, pivot, props)`: 피벗(빈 오브젝트) 아래 머티리얼별 자식 메시(게이트, 달력 장, 서치라이트 머리).
- 모듈: `terrain`, `tree`, `tuft`, `cloud`, `hills_ring`, `sky_backdrop`(UNLIT 하늘 띠), `rail_fence`, `power_line`, `barn`, `smoke_column`, `scorch`, `human`/`vehicle_silhouette`/`helicopter_silhouette`, `quonset`, `chain_fence`(마름모 철망, 가시철사, 윤형 철조망), `watchtower`, `searchlight`, `alarm_light`, `shed`/`wall_x`/`window`(작업장 창고), `workbench`, `step_crate`, `pcb`, `santa_doll`, `gift`, `cardboard`, `drink_can`, `bunk_bed`, `shelf_unit`, `board`, `calendar`, `import_glb`.
- **인간 병사 실루엣** (`human`): 얼굴·휘장 없는 저분할 덩어리를 UNLIT 단색(가까울수록 짙음: `hum_0` `#2b2f36` → `hum_2` `#5d6570`)으로 칠하고, 같은 메시를 법선 방향으로 5 cm 부풀려 면을 뒤집은 반투명 껍질(`halo_*`, 뒷면 컬링)을 겹쳐 가장자리가 번진 '초점 나간' 느낌을 낸다. 키 1.82 m로 엘프(1.2 m)와 체격 차이를 보여 준다. 자세 `aim`/`ready`/`stand`/`walk`/`run_a`/`run_b`(뛰는 걸음, 상체를 숙이고 총은 낮은 겨눔). 차량(트럭·바퀴형 장갑차)과 헬기도 같은 방식이고 표식이 없다.
- **뛰어드는 인간 병사** (`human_runner`): 움직이는 실루엣을 플립북으로 만든다. 묶음 `HUMAN_<id>`(피벗 = 발밑, Z 회전 = 처음 방향, `hidden=1`, `kind=human_runner`, `frames`) 아래 자세마다 자식 묶음 `HUMAN_<id>_<자세>`(첫 자세만 보이고 나머지는 `hidden=1`). 미션이 묶음을 경로를 따라 옮기며 `run_a`/`run_b`를 걸음마다 바꾸고(0.8 m마다, 위아래 5 cm 흔들림) 멈추면 마지막 자세를 보인다. `tone="n"`은 밤에 빛 앞을 지나는 역광 실루엣(`hum_n` `#121419`, `halo_n`). `torch=True`면 총구 아래 전등 렌즈(`search`)와 빛줄기(`searchbeam`, 4.5 m)를 걸음 자세와 `aim`에 단다.

---

## 3. 공통 규약

### 3.1 루트 속성
엔진이 읽는 값: `sky`, `fog`, `sun`, `ambient`, `music`. 나머지는 엘리아스 세트와 같은 키의 확장이다(엔진이 아직 읽지 않음).

| 키 | 투항 | 포로 생활 | 대탈주 |
|---|---|---|---|
| `sky` | `#d9c2b6` 새벽 복숭아빛 | `#5b5e93` 해 질 녘 위 하늘(남쪽은 배경판 띠) | `#0e1428` 밤 |
| `fog` | 70,360 | 90,320 | 35,240 |
| `sun` (three.js) | 1.0,0.34,-0.18 (동쪽 낮은 해) | -1.0,0.28,0.35 (서쪽 지는 해) | -0.45,0.8,-0.4 (달) |
| `ambient` | 1.25 | 1.15 | 0.9 |
| `sunColor` / `sunIntensity` | `#ffd6b0` / 2.1 | `#ffb27e` / 1.7 | `#9fb2e0` / 0.9 |
| `hemiSky` / `hemiGround` | `#f1d9cc` / `#7d6b5c` | `#d9a6a6` / `#5a5560` | `#4a5a8a` / `#191a24` |
| `timeOfDay` | dawn | dusk | night |
| `scene` / `shots` | `IL_SURRENDER` | `IL_CAMP` | `IL_ESCAPE` |
| `physics` | 0 (디오라마: `loadLevel({physics:false})`로 읽는다. 충돌체 없음) | 0 | 0 |

포로 생활의 실내 컷(막사, 작업장)은 창 유리가 UNLIT `sunwin`(한여름 창빛)이라 루트 하늘이 해 질 녘이어도 낮으로 읽힌다.

### 3.2 NPC 마커 속성
| 속성 | 뜻 |
|---|---|
| `model` | 인물 glb |
| `pose` | 기본 자세 (4장) |
| `scene` | 이 NPC가 보이는 컷 목록(쉼표). 같은 인물이 컷마다 다른 자리면 id를 나눈다(`elena` / `elena_hide`, `rita` / `rita_run`) |
| `poseStart`, `poseNext` | 컷 안에서 바뀌는 자세 제안. 투항 줄은 `poseNext` = 소품을 내려놓은 뒤 자세 (`surrender_hands_up`, `kneel_hands_up`, `kneel_head_down` …) |
| `hold_R`, `hold_L` | 손에 든 소품 glb (`weapons/elfinia/elfinia_rifle.glb`, `props/interlude_white_flag.glb`). 처음부터 손 소켓에 쥔다. 선택 `holdGrip_R/L`(쥐는 점 "x,y,z"), `holdRot_R/L`(소켓 안 회전, 도). `docs/LEVELS.md` 'NPC가 든 소품' |
| `placePose` | 소품을 내려놓을 때 숙이는 자세 (기본 `kneel_place`, 앉은 부상병 `sit_place`, 헤일리 `kneel_place_flag`) |
| `expr` | 표정 키 제안 (`serious`, `held_back`, `weary`, `wink` …) |
| `gesture` | 대본의 제스처 (`인형들기`) |
| `seatZ` | 앉는 자세의 엉덩이 높이(m). 마커는 바닥에 있다 |
| `standZ`, `standOn` | 상자 위에 선다: 마커 z가 이미 상자 윗면(0.28) |
| `lookAt` | 바라볼 노드 이름 (`NPC_rita`) |
| `prop` | 붙일 소품 제안 (`props/interlude_santa_doll.glb`: 무릎의 인형, `gift`: 선물 상자). 손에 드는 것은 `hold_R`/`hold_L` |
| `group`, `order`, `delay`, `silhouette`, `note` | 묶음, 순서, 늦춤(초), 역광 실루엣으로 처리, 설명 |

### 3.3 특수 노드
| 노드 | 세트 | 내용 |
|---|---|---|
| `SMOKE_<id>` | 투항 | 정적 툰 연기 기둥(묶음). 같은 자리의 `FX_smoke_<id>`로 입자 연기를 쓰면 숨긴다 |
| `FX_<id>` | 전체 | 연출 지점: `smoke`, `fire`, `wind`, `rotor`, `birds`, `portal`, `spark`, `alarm_sound`, `searchlight_pool` (`kind` 속성) |
| `PROP_<id>` | — | 지구 세트에는 없다. 손에 드는 소품(소총·권총·백기·산타 인형·칩)은 NPC의 `hold_R`/`hold_L`로 처음부터 쥐고, 내려놓거나 꽂는 자리만 `DROP_`로 둔다 |
| `DROP_<npcId>` | 투항·대탈주 | 손에 든 무기를 내려놓을 바닥 자리(소품 없음, `slot=R`). 무기 원점(오른손 파지점)이 이 자리·회전으로 옆으로 눕는다. 줄 엘프마다 하나(무릎 꿇고 숙인 손 바로 앞 0.36 m), 앉은 부상병은 오른쪽 옆, `DROP_haley`는 권총 |
| `CAL_page_01..12` | 포로 생활 | 벽 달력 장. 01이 맨 앞(7월부터 12장). 피벗 = 윗변 가운데. 노드에 벽 방향 yaw가 들어 있으므로 `page.rotateX(flipDeg°)`(지역 X축, `flipDeg`=-170)로 위로 넘기고 숨긴다. `month` 속성 |
| `GATE_off` | 대탈주 | 꺼진 게이트 부분(어두운 램프 10, 꺼진 전구 40, 꺼진 화면, 붉은 대기 LED). 처음에 보인다 |
| `GATE_on` | 대탈주 | 켜진 부분(발광 램프·전구, 문 면, 바닥 빛, 빛기둥, 켜진 화면, 초록 LED). **`hidden=1`: 로드 직후 숨긴다.** 켤 때 `toggle`(=`GATE_off`)을 숨긴다 |
| `GATE_on_swirl` | 대탈주 | `GATE_on`의 자식. `spin="140,0,0"`으로 문 면 소용돌이가 돈다 |
| `LIGHT_search_01/02` | 포로(꺼짐)·대탈주(켜짐) | 서치라이트 머리 묶음(하우징, 렌즈, 빛기둥). 피벗 = 받침 위 회전축. `sweep="-35,35"`(도), `sweepHz`로 Y축(three.js) 왕복을 미션이 구현 |
| `LIGHT_alarm_01..04` | 대탈주 | 회전 경광등(빨간 렌즈 + 빛살 2개). `spin="0,240,0"`이라 엔진이 돌린다. `emissiveToggle`, `blink` |
| `LIGHT_worklamp` | 대탈주 | 작업대 작업등 |
| `HUMAN_rush_01..02` | 대탈주 | 쫓아오는 인간 경비 플립북(`kind=human_runner`, `hidden=1`, 둘 다 총 전등). 자식 `_run_a`/`_run_b`/`_ready`(01) 또는 `_aim`(02). 속성 `path`(경로점 `WP_<path>_nn`. 첫 점에서 나타나 마지막 점에서 멈춤), `stop`(멈춘 자세), `delay`(컷 시작 기준, 초), `speed`(m/s), `decel`(멈추기 전 줄이는 거리, m), `scene=escape_c,escape_d`. 컷마다 다른 길은 `<속성>_<컷>`(`path_escape_c`, `delay_escape_c`, `speed_escape_c`) |
| `WP_yard_nn_01..05` | 대탈주 | `escape_c`의 길: 막사 사이(남는 엘프들 오른쪽 뒤, 줌 화면 밖) → 남는 엘프들 앞 → 운동장 → 큰 문 → 작업장 안 |
| `WP_rush_nn_01..04` | 대탈주 | `escape_d`의 길: 작업장(상자 벽 서쪽) → 상자 벽 틈의 남쪽 절반(북쪽 절반은 방수포가 머리 높이까지 내려와 있다) → 게이트 앞 |

게이트 몸체(고리, 롤러, 기판, 받침, 배터리, 케이블, 콘솔)는 `zone_secret`의 일반 메시라 늘 보인다.

---

## 4. 포즈 목록 (`pose`)

미션 담당이 `src/game/npc/poses.ts`에 구현한다. 엘리아스 세트와 겹치는 이름은 뜻을 맞췄다. 본 회전 방향은 ELF_KIT 3장(+X 숙임·굽힘, upperarm_L +Z 들기, shin -X 무릎 굽힘).

| 이름 | 설명 | 쓰는 곳 | 비고 |
|---|---|---|---|
| `stand_attention` | 차렷. 기존 `attention`과 같게 둬도 된다 | 투항 줄, 헤일리 시작 | 별칭 |
| `attention_head_down` | 차렷 + 고개를 푹 숙임(head·neck +X 20~30°) | 투항 줄 | 새 |
| `kneel` | 한쪽 무릎 꿇기(오른 무릎 땅, 왼발 앞), 손은 허벅지 | 헤일리, 투항 줄 | 엘리아스와 공용 |
| `hold_rifle_ready` | 총을 든 채 대기: 소총을 배 앞에 비스듬히(총구 왼쪽 아래), 오른손 손잡이, 왼손 손받침(IK) | 투항 줄 시작 | 새 (쥔 자리 `_holdR`) |
| `kneel_place` | 오른 무릎을 꿇고 엉덩이부터 깊이 숙여 든 총을 무릎 앞 바닥 가까이 | 투항 줄 (`placePose`) | 새 (쥔 자리) |
| `kneel_hands_up`, `kneel_head_down` | 무릎 꿇은 채 손을 듦 / 고개를 숙임 | 투항 줄 `poseNext`, 리타 | 새 |
| `sit_slumped_rifle`, `sit_place` | 주저앉아 무릎 위에 총 / 오른쪽으로 기울어 옆 바닥에 | 부상병 | 새 (쥔 자리) |
| `stand_flag`, `kneel_place_flag`, `kneel_flag` | 헤일리: 백기를 왼손에 세워 든 채 섬 / 숙여 권총을 내려놓음 / 무릎 꿇고 깃대를 땅에 세워 쥠 | 헤일리 | 새 (쥔 자리 `_holdL`·`_holdR`) |
| `lower_weapon` | 무릎과 허리를 굽혀 두 손으로 총을 땅에 내려놓는 순간 (예전 정적 배치용. 지금 투항은 `kneel_place` + 내려놓기) | — | 남겨 둠 |
| `surrender_hands_up` | 두 팔을 들어 손바닥을 앞으로(어깨 높이 위팔, 아래팔 세움), 고개 살짝 숙임 | 투항 줄 | 새 |
| `sit_slumped` | 땅에 주저앉아 다리를 뻗고 고개를 떨굼 (부상병) | 투항 줄 | 새 |
| `sit_tired` | 지쳐 앉음(`seatZ`: 침대 0.54, 상자 0.28), 어깨 처짐 | 막사, 작업장 | 공용 |
| `lie_sleep` | 위 칸 매트리스에 누워 잠. 마커 z = 매트리스 윗면, 머리 = 마커 -Y | 막사 | 새 (루트 회전 필요) |
| `work_bench` | 작업대 앞에서 두 손을 앞으로 모아 작업(아래팔 수평), 고개 숙임 | 작업장(상자 위, `standZ`) | 공용 |
| `carry_box` | 상자를 두 팔로 안고 섬. 상자는 든 소품이라 오른손·왼손이 양 옆면을 쥔다(쥔 자리 `_holdR`, 상자 `grip_support`) | 작업장 | 공용 |
| `work_doll` | `work_bench` + 오른손에 든 산타 인형을 세워 들고 들여다봄. `인형들기` 제스처가 쥔 자리를 풀고 팔을 들어 보인다 | 캐시 (camp_b) | 새 |
| `assemble_insert` | `assemble`에서 몸을 기울여 왼손의 칩을 기판에 꽂음 (`placePose`) | 엘레나 (escape_b) | 새 |
| `look_up` | 고개·상체를 젖혀 하늘을 봄(head -X 30°대), 팔은 내림 | 철망 앞 리타 | 공용. `IL_ARRIVAL`과 같은 구도 |
| `hide_chip` | 작업대 아래 쪼그려 앉아(엉덩이 약 0.3 m) 두 손을 가슴에 모아 칩을 옷 안에 넣음. 칩은 오른손에 든다(`hold_R`) | 엘레나 (escape_a) | 새 |
| `assemble` | 서서 두 손을 앞으로 내밀어 조립(손 높이 0.8~0.9 m) | 엘레나 (게이트 기판) | 공용 |
| `lookout` | 문 옆 벽에 등을 붙이고 상체를 기울여 바깥을 엿봄, 고개는 문 쪽 | 리타 (escape_a·c) | 새 |
| `run` | 달리는 중간 자세 | 탈주 무리, `rita_run` | 공용 |
| `wave_beckon` | 한 팔을 크게 휘저어 부름(손짓 osc) | 게이트 옆 엘프 | 새 (제스처 `beckon`을 자세로) |
| `stand_watch` | 차렷에 가깝게 굳어 서서 멀리 봄 | 남는 엘프 | 새 |
| `il_escape_run_eat`, `il_escape_run_eat_dip` | 로네: 왼손 접시를 가슴 앞에 평평하게, 오른손 포크를 입에 / 포크를 접시로 내려 한 조각 찍음(고개 숙임). 몽타주가 번갈아 걸어 먹는 동작을 만든다 | 로네 (escape_c) | 새 (`interlude.ts`가 더함, 쥔 자리 `_holdL`·`_holdR`) |

---

## 5. 세트별 구성

### 5.1 투항 `interlude_surrender` (새벽, 20초)
- **들판**: 가까운 곳 2 m → 먼 곳 40 m로 성기는 격자 지형. 밀밭·풀·흙 고랑(잔해가 미끄러져 온 자국), 이랑 띠, 풀 덤불 170, 돌, 풀 얼룩 데칼. 나무 울타리 농로, 전봇대 줄, 먼 헛간 2채와 사일로, 나무, 언덕 띠, 낮은 구름, 동쪽 지평선의 해.
- **기함 잔해**: `space/elfinia_flagship.glb`를 불러와(`import_glb`) 북쪽 96 m에 함수를 처박고(+7°) 가까운 쪽 귀 지느러미가 땅에 묻히게 기울였다(-14°). `bridge`는 빼고 `bridge_damaged`(찌그러진 함교, 불씨, 비상등)를 보인다. 시안 창은 꺼진 남색으로 칠했다. 흙 둔덕, 선체 판·남색 띠·금색 포구 고리 조각, 엘프 보급 상자 5개, 그을음과 불씨(`FX_fire_01..05`).
- **연기**: `SMOKE_bridge`(58 m), `SMOKE_engines`, `SMOKE_bow` + 같은 이름의 `FX_smoke_*`.
- **엘프 줄**: y=0에 14명(병사 12 + 캐시 + 리타). 모두 소총을 손에 든 채(`hold_R`, `hold_rifle_ready`) 시작하고, 바닥에 미리 놓인 총은 없다. 발 앞에 내려놓을 자리 `DROP_<id>`. 헤일리는 백기(`hold_L`, 깃대 0.42 m 높이를 쥠)와 권총(`hold_R`)을 들고 `WP_haley_from`(줄)에서 줄 앞 2.75 m로 걸어 나온다. `DROP_haley`는 권총 자리.
- **내려놓기 연출** (`src/game/missions/interlude.ts` `layDown`): 02와 함께 헤일리가 먼저 숙여 권총을 내려놓고 백기를 땅에 세워 쥔 채 무릎을 꿇는다 → 1.1초 뒤 줄이 헤일리 가까운 쪽부터 물결처럼(거리 1 m당 0.22초) 무릎 꿇고 숙여 총을 바닥에 내려놓고(닿을 때 `weapon_down` 소리) `poseNext`로 → `surrender_c`에서 캐시가 내려놓고 일어서 리타를 보고, 리타는 한 박자 늦게 내려놓고 무릎 꿇은 채 고개를 숙인다.
- **인간**: 실루엣 9명(조준·경계·걷기), 트럭·장갑차 4대, 헬기 2대(`FX_heli_*`).

| 컷 | 길이 | 내용 |
|---|---|---|
| `surrender_a` | 7초 | 인간 실루엣 어깨 너머로 들판, 엘프 줄, 연기 나는 잔해. 천천히 민다 |
| `surrender_b` | 7초 | 헤일리 정면 낮은 각도로 밀고 들어감. 뒤에 줄과 연기 (IL_SURRENDER_01~02) |
| `surrender_c` | 6초 | 줄 앞을 옆으로 훑어 캐시와 리타 둘 샷으로 끝남 (`held_back`) |

### 5.2 포로 생활 `interlude_camp` (막사·작업장 실내 + 해 질 녘 운동장, 22초)
- **막사**(`zone_barracks`): 퀀셋 반원통 막사 2동(골함석 띠, 끝벽 문·창 안팎). 안쪽은 인간 규격 이층 침대 8개(매트리스, 담요, 베개, 사다리), 침대 밑 상자, 매단 전등 3, 끝의 난로와 연통, 의자 위 붕붕드링크.
- **작업장**(`zone_work`): 16×10 m 골함석 창고(띠장, 기둥, 박공 트러스, 창 6과 한여름 빛살). 11 m 작업대(기판 12, 부품통, 인두, 돋보기등, 인형 몸통·머리, 인형 눈 접시, 완성 인형 줄), 엘프가 딛는 나무 상자 4, 선물 상자·인형이 흐르는 컨베이어(롤러, 모터 상자), 포장대(열린 상자, 테이프, 선풍기), "XMAS" 상자 탑, 크리스마스 나무 견본(전구), 선반 2, 화환·반짝이 줄, 칠판 "크리스마스까지 D-173", 안내판 "근무: 주 5일 / 1일 8시간", 동쪽 벽의 달력(`CAL_page_01..12`)과 메뉴판, 콩자반 식판.
- **운동장**(`zone_yard`): 자갈 마당, 이중 철망(안쪽은 리타 앞만 촘촘한 마름모 + 윤형 철조망), 경고판(RESTRICTED AREA), 감시탑 2(서치라이트 꺼짐, 탑 위 인간 경비 실루엣), 꺼진 가로등, 빨랫줄의 작은 작업복, 리타 발치의 들꽃.
- **하늘**: 남쪽 반원 UNLIT 띠 배경판(주황 → 분홍 → 보라 → 남보라, 루트 `sky`로 이어짐), 지는 해, 분홍 구름, 철망 너머로 나는 새(`FX_birds`).

| 컷 | 길이 | 내용 |
|---|---|---|
| `camp_a` | 6초 | 막사 문 쪽에서 침대 사이 통로를 따라 |
| `camp_b` | 8초 | 작업대를 따라 옆으로(작업자들, 캐시의 산타 인형) → 동쪽 벽 달력과 메뉴판으로 돈다. 달력 넘김은 이 컷 끝에서 |
| `camp_c` | 8초 | 철망 앞 리타: 등 뒤 낮은 곳에서 노을 하늘 → 옆으로 돌아 `weary` 얼굴(뒤로 감시탑과 막사) |

### 5.3 대탈주 `interlude_escape` (밤, 30초)
- **창고**(`zone_work`, 20×12 m): 서쪽 벽에 열린 큰 미닫이 문(운동장 쪽), 남쪽 창의 달빛 빛살. 북쪽 작업대(기판, 인형, 작업등 `LIGHT_worklamp`), 남쪽 멈춘 컨베이어, 쓰러진 의자와 떨어진 인형(급히 떠난 흔적), 문 위 경광등 2.
- **상자 벽**(`zone_boxwall`, x≈3.8): 포장 상자를 천장 가까이 쌓아 뒤 공간을 가렸다. 가운데 1.7 m 틈, 반쯤 걷힌 방수포("XMAS").
- **게이트**(`zone_secret` + `GATE_off/on`): 지름 2.4 m 고철 고리, 구리 코일과 감은 띠, 컨베이어 롤러 12, 칩 기판 8, 크리스마스 전구 줄 40알, 팔레트 받침과 A자 다리, 포장 자루, 자동차 배터리 7, 포장 리본으로 묶은 케이블, 콘솔(나무 상자, CRT, 자판, 칼날 스위치, 테이프로 붙인 산타 인형).
- **운동장**: 막사 2동(창에 불), 경광등 기둥 2, 가로등과 빛 웅덩이, 감시탑 2(서치라이트 켜짐: 01은 막사 문 앞을 비춰 남는 엘프들이 역광 실루엣이 된다), 경비 실루엣(망루 2 + 뛰어오는 3), 철망, 달, 별 130, 먼 언덕·나무.
- **쫓아오는 경비**(`zone_humans`, `escape_c`·`escape_d`): 플립북 둘(`HUMAN_rush_01..02`, 역광 `tone="n"`, 총 전등). `escape_c` 끝에 막사 사이에서 나와 서치라이트 속 남는 엘프들 앞을 지나 큰 문으로 달려오고, `escape_d`에서 작업장을 가로질러 틈으로 들어와 게이트로 달려든 뒤 꺼진 고리 앞에 멈춘다(가운데 01은 총을 내린 `ready`, 왼쪽 02는 `aim`으로 빈 고리를 전등으로 비춘다).

| 컷 | 길이 | 내용 |
|---|---|---|
| `escape_a` | 7초 | 작업대 밑에서 칩을 숨기는 엘레나(`elena_hide`) → 큰 문 옆에서 망보는 리타 (IL_ESCAPE_01) |
| `escape_b` | 7초 | 상자 벽 틈으로 밀고 들어가 게이트, 왼손에 든 칩을 기판(`DROP_elena`)에 꽂는 엘레나(1.5초에 기울이고 2.0~2.6초에 꽂힘). **꽂힌 뒤 2.7초에 `GATE_off` → `GATE_on`** (IL_ESCAPE_02) |
| `escape_c` | 10초 | 게이트 앞에서 뒤돌아봄: 틈으로 뛰어드는 무리 → 문 너머 서치라이트 속에 남는 엘프 셋으로 줌(8초, fov 15). 무리 맨 끝의 로네(`rone`, 돈까스 접시 `hold_L`·포크 `hold_R`, `dreamy`)가 먹으며 종종걸음으로 뒤처지다 5초쯤부터 홀로 틈을 지나 6.2초쯤 화면 오른쪽으로 빠진다. 손짓하던 `soldier_08`도 로네까지 지나간 뒤 화면 밖에서 들어간다 → 6.75·7.05초에 경비 둘이 막사 사이에서 나와(8.4초쯤 화면에 들어옴) 남는 엘프들 앞을 지나 큰 문으로 달려오고, 줌이 fov 21로 조금 풀린다(10초에 문 앞) |
| `escape_d` | 5.6초 + 암전 0.7초 | 소용돌이 치는 문 면 바로 앞(2.2 m, fov 36) → 경비들이 카메라 밑으로 지나 달려드는 동안 뒤 위로 물러나 내려다본다(fov 48~50, 사람이 문 면을 가리지 않게). 1.45초에 문 면이 깜빡이고 소용돌이가 빨라진다 → 1.85초에 가운데로 빨려 들어가 `GATE_off`(2.07초 섬광 `FX_gate_core`, 불꽃 `FX_gate_spark_*`, 흔들림) → 경비들이 꺼진 고리 앞에 멈춘다(2.2~2.7초) → 짧은 정적, 사이렌이 잦아든다 |

---

## 6. 소품

| 소품 | 원점 | 앵커 | 쓰는 곳 |
|---|---|---|---|
| `interlude_white_flag` | 막대 아래 끝(땅) | `grip`(0.7 m), `cloth_tip` | 투항: 헤일리가 왼손에 든다(`hold_L`, `holdGrip_L`="0,0.42,0"로 깃대를 낮게 쥐어 아래 끝이 땅에 닿을 듯, `holdRot_L`="0,180,0"로 천이 바깥쪽) |
| `interlude_santa_doll` | 바닥 가운데, 정면 -Y | `grip` | 포로 생활: 캐시가 처음부터 오른손에 세워 든다(`hold_R`, `holdRot_R`="-90,0,0", 자세 `work_doll`), 제스처 `인형들기`로 들어 보인다. 막사의 무릎 위 인형은 `prop` |
| `interlude_chip` | 기판 가운데 | `grip` | 대탈주: `elena_hide`가 오른손에(`hold_R`), 게이트의 `elena`가 왼손에(`hold_L`) 들고 있다가 기판 자리 `DROP_elena`(slot L, 반쯤 꽂힌 모습)에 꽂는다. 엘레나는 짧은 팔이 닿게 고리에서 0.52 m |

---

## 7. 몽타주 담당 메모

- **읽기**: `loadLevel({ id, path: 'levels/interlude_<id>.glb', physics: false })`. 충돌체가 없다.
- **컷별 NPC**: `scene`으로 거른다. `escape_c`의 달리는 무리는 컷 동안 게이트 쪽으로 움직여야 끝에서 남는 엘프들이 보인다(정지 상태로 두면 앞을 가린다). `elena`와 `elena_hide`, `rita`와 `rita_run`은 같은 컷에 동시에 쓰지 않는다.
- **hidden**: `hidden=1` 노드(`GATE_on`)는 로드 직후 숨긴다. 엘리아스 세트와 같은 규칙이다.
- **게이트 가동**: `GATE_on.visible = true; GATE_off.visible = false`. `FX_gate_core`, `FX_gate_spark_*`에 섬광·불꽃. 경광등(`LIGHT_alarm_*`)은 가동과 함께 켜면 좋다(`on` 속성은 1로 내보냈다).
- **게이트 꺼짐** (`SetDirector.gateClosing` → `gateCollapse`): 소용돌이(`GATE_on_swirl`의 spin)가 빨라지고 문 면·램프·전구가 점점 잦게 깜빡인다 → 나머지 발광부를 끄고(`GATE_off`) 문 면과 소용돌이만 `GATE_on` 피벗(고리 가운데)으로 0.22초 동안 줄여 빨려 들어가게 한 뒤, `FX_gate_core`의 빛 스프라이트가 퍼지며 사라지고 `FX_gate_spark_*`에서 불꽃(입자)이 튀어 1~2초 잦아든다. 문 면·소용돌이·바닥 빛은 반투명이라 깊이를 쓰지 않게 하고 소용돌이를 문 면 뒤에 그린다(보는 각도에 따라 소용돌이가 문 면을 가리던 문제). `GATE_on_gate_beam`(빛기둥)은 위에서 내려다보면 화면을 가로지르는 판으로 보여 `escape_d`에서 끈다.
- **뛰어드는 경비** (`SetDirector.rush(shot)`): 그 컷의 `HUMAN_*`를 `delay` 뒤 `speed`로 경로를 따라 옮긴다. 남은 거리가 `decel`보다 짧으면 줄여서(끝에서 30%) 멈추고, 바라볼 점(게이트 가운데)으로 돌아 멈춘 자세를 보인다. 걸음마다 `onStep`(발소리). 컷이 바뀌면 숨기고 처음 자리로.
- **달력**: `CAL_page_01`부터 하나씩 `rotateX`로 0 → `flipDeg`까지 돌리고 숨긴다(`rotation.x`를 직접 바꾸면 yaw와 섞여 축이 틀어진다). 12장이 한 해(7월~6월)이고, 기록 문구의 억류 연차 카운터와 함께 빠르게 넘긴다.
- **서치라이트**: `LIGHT_search_*` 묶음의 처음 `rotation.y`(yaw)에 `sweep` 범위의 각을 더해 왕복시킨다. 포로 생활(해 질 녘)에서는 꺼져 있다(`on=0`, 빛기둥 없음).
- **연기**: `SMOKE_*` 정적 메시가 기본이다. 입자 연기로 바꾸면 `SMOKE_*`를 숨기고 `FX_smoke_*`(`height`, `radius`, `lean`)에 띄운다.
- **조명 확장**: `sunColor`/`sunIntensity`/`hemiSky`/`hemiGround`를 적용하면 새벽·노을·밤 대비가 더 산다. 적용하지 않아도 밤 세트는 팔레트 자체가 밤색이라 밤으로 읽힌다(검증은 엔진 기본값으로 했다).
- **포로복**: 포로 생활·대탈주의 엘프는 주황 죄수복(`art/blender/lib/prisoner.py`)을 입는다. 리타·캐시·엘레나는 `characters/{rita,cathy,elena}_prisoner.glb`, 무명 엘프는 `prisoner_a/b/c`를 돌려 쓴다. 투항 세트는 아직 군복이다.

## 8. 검증과 남은 문제

- `escape_c` 끝·`escape_d` 확인: 게임 화면(`gamecheck`, `?mission=interlude&scene=IL_ESCAPE&nointro=1`)으로 `escape_c` 5.5·8.4·9.0·9.5·10.0초, `escape_d` 0.1·1.2·1.8·2.1·5.5초를 찍었다. 카메라와 경비 머리의 가장 가까운 거리는 0.55 m(`escape_d` 1.17초, 메시 안으로 들어가지 않음). 경비 둘 × 자세 3장 × 번짐 껍질로 세트가 57k다.
- **수용소 경보**: 게이트 가동 0.6초 뒤 `base_siren_on` → 기계식 사이렌 루프 `ambience/base_siren_loop`(Federal Signal Thunderbolt 1000 실제 녹음, CC0, `docs/audio/README.md` 5.6절). 게이트가 꺼지고 0.85초 뒤 `siren_fade`로 2.2초 동안 잦아든다.
- 시트(top·34): `shots/levels__interlude_{surrender,camp,escape}.png`, 근접 `shots/levels__interlude_camp-work.png`, `shots/levels__interlude_surrender-near.png`, 소품 `shots/props__interlude_{white_flag,santa_doll,chip}.png`.
- CAM 시점 근사: `shots/levels__interlude_{surrender,camp,escape}-cams.png`, 게이트 켜짐 `shots/levels__interlude_escape-cams-on-g.png`. 레일 재생(`src/game/cinematic/CameraRail.ts`)이 아직 커밋되지 않아, 그 파일의 `CameraRail`과 게임 로더(`src/art/loader.ts`)를 그대로 쓰는 임시 하네스(저장소 밖)로 컷마다 처음·가운데·끝을 렌더했다. NPC는 마커 자리에 놓고 대략의 자세만 입혔다(포즈 라이브러리 아님). 엔진 기본 조명(주광 2.4 + 반구광 `ambient`)이다.
- 기함 이름은 「큰망치」로 통일됐다(우주 장면 담당이 '모루'에서 바꿈). 세트에는 이름을 쓰지 않았다(함번 01만 보임).
- `level_kit.py`가 아직 커밋되지 않았다면 이 키트도 다시 빌드할 수 없다(결과 glb는 커밋되어 있다).
- 투항 세트는 예산(60k)에 거의 찼다(59.3k, 그중 기함 12k). 더 넣으려면 먼 나무·언덕부터 줄인다.
