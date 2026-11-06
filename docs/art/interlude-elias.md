# 인터루드 4~7 디오라마 세트 (엘리아스)

`docs/scenario.md` '인터루드: 기록'의 4~7번 장면을 찍는 세트다. 몽타주(미션·연출 담당)가 각 세트의 `CAM_`/`LOOK_` 레일을 재생하고, NPC 마커에 포즈를 입히고, 단계·화면·경보 노드를 켜고 끈다. 지구 쪽 세트(1~3번)는 다른 담당이 만든다.

- 키트: `docs/art/monatium-city.md` (`art/blender/lib/monatium_city_kit.py`)
- 노드 규칙: `docs/LEVELS.md`, 키트 확장 노드: `monatium-city.md` 5장

| 장면 | 스크립트 → 결과물 | 삼각형 | 머티리얼 | CAM |
|---|---|---|---|---|
| 4 엘리아스 불시착 | `art/blender/levels/interlude_arrival.py` → `levels/interlude_arrival.glb` | 38.0k | 28 | `arrival_a/b/c` |
| 5 모나티엄 건설 | `interlude_construction.py` → `levels/interlude_construction.glb` | 59.8k (단계 전부) | 61 | `build_a/b/c` |
| 6 평화로운 일상 | `interlude_daily.py` → `levels/interlude_daily.glb` | 72.1k | 55 | `daily_a/b/c` |
| 7 R41 침공 개시 (D-7) | `interlude_invasion.py` → `levels/interlude_invasion.glb` | 75.2k | 61 | `invasion_a/b/c` |

삼각형은 NPC·소품 glb를 뺀 세트 자체 값이다(상한 80k). 6·7번은 같은 `downtown()` 배치이고, 5번의 STAGE_2·3도 같은 좌표(시청 (0, 26), 코어 AI (32, 36), 광장 중심 (0, 0))에 지었다. 타임랩스의 도시가 100년 뒤의 광장으로 자란다.

---

## 1. 공통 규약

### 1.1 루트 속성
엔진이 읽는 값: `sky`, `fog`, `sun`, `ambient`, `near`(0.1), `far`, `music`. 아래는 지구 쪽 인터루드 세트와 같은 키의 확장이다(엔진이 아직 읽지 않음, 몽타주 담당 참고).

| 키 | 불시착 | 건설 | 일상 | 침공 D-7 |
|---|---|---|---|---|
| `sky` | `#b8e3ee` 옅은 청록 | `#b9dcee` (단계별 `STAGE_n.sky`) | `#a6d8f4` 맑은 낮 | `#c3a7d4` **이상한 하늘빛**: 라벤더·분홍 해 질 녘 |
| `fog` | 240,2600 | 180,1500 | 140,760 | 110,640 |
| `sun` (three.js) | 0.35,0.85,0.45 | 0.4,0.9,0.35 | 0.45,1,0.35 | -0.55,0.42,-0.5 (낮은 해) |
| `ambient` | 1.6 | 1.55 | 1.55 | 1.2 |
| `sunColor` / `sunIntensity` | `#fff8e6` / 2.3 | `#fff4e0` / 2.3 | `#fff4e0` / 2.4 | `#ffc6d9` / 1.7 |
| `hemiSky` / `hemiGround` | `#eefaff` / `#7f8a6a` | — | `#eaf4ff` / `#8a8070` | `#e9d4ff` / `#6a5470` |
| `timeOfDay` | morning | timelapse | noon | dusk_d7 |
| `scene` / `shots` | `IL_ARRIVAL` | `IL_CONSTRUCTION` (+ `stages`) | `IL_DAILY` | `IL_INVASION` |
| `physics` | 0 | 0 | 0 | 0 |

### 1.2 NPC 마커 속성
| 속성 | 뜻 |
|---|---|
| `model` | 인물 glb. 없으면 `fallback` → 엘피니아 병사 키트 (NpcSet 규칙) |
| `pose` | 기본 자세 이름 (3장). 포즈 라이브러리는 미션 담당이 구현한다 |
| `name` | 자막 이름 |
| `look` | `player` / NPC id / `none` (NpcSet 규칙) |
| `scene` | 이 NPC가 보이는 컷 목록(쉼표). 몽타주는 그 컷의 NPC만 보인다. 같은 인물이 컷마다 다른 자리에 있으면 id를 나눈다(`rita_drill`, `rita_plaza`) |
| `stage` | 건설 세트에서 보이는 단계(`STAGE_0`..`STAGE_3`). STAGE 노드 아래에 있지만 NPC는 `level.dynamic`에 놓이므로 몽타주가 이 값으로 켜고 끈다 |
| `seatZ` | 앉는 자세의 엉덩이 높이(벤치 0.32). 마커는 바닥에 있다 |
| `expr` | 표정 키 제안 (`smile` 등) |
| `lookAt` | 노드 이름을 바라보라는 제안 (`RIFT_01`) |
| `airborne`, `fallVel` | 공중에 뜬 NPC(게이트에서 떨어지는 엘프). `fallVel`은 three.js m/s. NPC는 마커 위치에 한 번 놓이므로 몽타주가 움직인다 |

### 1.3 카메라
`CAM_<shot>_<nn>` + `LOOK_<shot>_<nn>`, 컷마다 점 3개, `t`(초)와 `fov`. 컷 길이 6~12초. 시선 높이는 엘프 눈높이(0.9 m) 언저리에 둔다.

---

## 2. 세트별 구성

### 2.1 인터루드 4 「엘리아스 불시착」 `interlude_arrival`
원작: 엘레나가 빼돌린 칩으로 조립한 차원 게이트는 작동했지만 엘프들은 모성이 아니라 엘리아스에 불시착했다. 엘리아스는 세계수 엘드르가 가운데 선 땅이고, 원래 식생이 나쁘지 않았다. 고기가 나무에서 열리고, 숲 너머는 안개로 둘러싸여 있다. 모나티엄 자리는 엘리아스 동부(정령산·에르피엔 접경).
오리지널 연출: '낯선 하늘' = 낮에도 떠 있는 두 달과 지평선 위로 산보다 높이 솟은 세계수. [원작] 세계수는 요정 왕국 에르피엔의 한가운데에 있어, 지평선의 세계수 밑동에 왕궁과 성벽 두른 시가의 실루엣이 함께 보인다(공용 키트 `erpien_kit`, `docs/art/erpien.md`, 2026-11-02 사용자 정정).

| 노드·구역 | 내용 |
|---|---|
| `zone_land` | 방사형 초원(가운데 40 m 평지, 밖으로 언덕) |
| `zone_far` | 에르피엔(`erpien_kit` 원경: 세계수 높이 420 m, (80, 1050), 약 1.05 km. 밑동을 두른 왕궁, 시가 고리, 이중 성벽), 그 아래 들판 원판, 원경 산 16개(눈 모자, 세계수 쪽은 비움), 안개 경계 고리(반지름 1450 m, 세계수 너머) |
| `zone_sky` | 두 달, 뭉게구름 7개 |
| `zone_woods`, `zone_meadow` | 숲 7무리(원경 LOD), 가로수 10그루, **고기 나무** 3그루, 꽃밭, 바위, 불시착 자국 |
| `GATE_escape` | 하늘의 구멍(탈출 게이트 출구, 시안). `_disc`·`_swirl` spin. `scenes="arrival_a,arrival_b"` → arrival_c에서는 닫힘(스케일 0) |
| `LIGHT_gate_escape` | 시안 점광원 제안 |
| `zone_portal`, `FALLING` | 같이 떨어진 짐: 엘피니아 회녹 상자, 파란 방수포, `PROP_ammo_01/02`(지구제 탄약통). `FALLING`(drift 아래로)은 떨어지는 상자 |

| CAM | 길이 | 내용 |
|---|---|---|
| `arrival_a` | 8 s | 낮은 와이드, 게이트에서 쏟아진 엘프들, 오른쪽 위 세계수, 왼쪽 위 달. 천천히 다가감 |
| `arrival_b` | 6 s | 주저앉은 리타 얼굴 → 고개를 따라 하늘의 달로 틸트 |
| `arrival_c` | 8 s | 엘레나 어깨 너머 세계수 → 뒤로 빠지며 일행 전체 |

NPC: 엘레나(`look_far`, 세계수를 봄), 리타(`sit_dazed`), 캐시(`lie_sprawl`), 헤일리(`help_up`), 로네(`il_arrival_sit_plate`: 대탈주에서 들고 온 빈 돈까스 접시 `hold_L`·포크 `hold_R`, `dreamy`), 아멜리아(`kneel`, 풀을 만짐), 엘프 6명(`look_up`, `look_around`, `point_far`, `lie_sprawl`, `carry_box`), 떨어지는 엘프(`tumble`, 공중).
모델 메모: 탈출 직후라 모두 주황 죄수복(`art/blender/lib/prisoner.py`)이다. 엘레나·리타·캐시·헤일리·로네·아멜리아는 `characters/<이름>_prisoner.glb`, 무명 엘프는 `prisoner_a/b/c`를 돌려 쓴다.

### 2.2 인터루드 5 「모나티엄 건설」 `interlude_construction`
원작: 당장 먹고 살기 위해 테라포밍 장치로 엘프 도시 모나티엄을 세웠다(도시·공장·발전소 계획, 정령 에너지). 모나티엄 AI가 운영하는 도시, 초대 시장 엘레나.

| 단계 노드 | 내용 | 단계 속성 |
|---|---|---|
| `STAGE_0` 천막 | 천막 40여 동 3겹(캔버스·지구 방수포·엘피니아 회녹), 모닥불 3, **테라포밍 장치**(시청 자리, 시안 빛기둥 + 퍼지는 풀 고리 4겹), 짐 상자, 엘피니아 깃발, 작업대 | `timeOfDay=dawn`, `sky=#cfe4ea` |
| `STAGE_1` 공장 | 흙길, 톱니 지붕 공장 3동(굴뚝 연기), **정령 발전소**, 타워 크레인 2, 비계에 둘러싸인 시청 기단·벽·탑 골조, 코어 기단, 자재 더미 | `noon`, `#bfe0ee` |
| `STAGE_2` 도시 | 광장·분수·화단, 시청(초상), **코어 AI 탑(꺼짐)**, 중앙로·모노레일 한 구간, 광장 둘레 건물 7동, **취임 연단**(포르티코 바닥 z=0.9) | `afternoon`, `#aed8f0` |
| `STAGE_3` 기동 (겹침) | 코어 띠 발광·빛 고리·빛기둥(하늘로 90 m)·바닥 네트워크 선, 탑 로고 빛 고리, 분수 빛, **취임 축하 현수막** "엘레나 시장 취임 · 모나티엄 원년", 종이꽃 70조각, `LIGHT_core_on` | `showWith=STAGE_2`, `dusk`, `#f2c7a8` |

몽타주 순서: `STAGE_0` → `STAGE_1` → `STAGE_2` → `STAGE_2 + STAGE_3`. 한 번에 한 단계만 켜되 STAGE_3은 STAGE_2와 함께 켠다. 초원·세계수·산·하늘(`zone_land/far/woods`)은 항상 보인다. 세계수는 북북서 지평선 약 1.07 km((−240, 1040), 높이 420 m)의 에르피엔 한가운데에 있다(`erpien_kit` 원경, 불시착 세트와 같은 디자인).

| CAM | 길이 | 내용 |
|---|---|---|
| `build_a` | 12 s | 타임랩스 고정 와이드(남서쪽 높이 30 m). 모든 단계가 같은 레일 |
| `build_b` | 6 s | 코어 AI 기동: 광장 북동에서 탑을 올려다보며 틸트 업 |
| `build_c` | 8 s | 취임식: 군중 옆에서 연단의 엘레나로 다가감 |

NPC(단계별 `stage`): STAGE_0 엘레나(`point_far`, 테라포밍 장치를 가리킴)·정착민 6(`work_bench`, `sit_tired`, `carry_box`, `assemble`, `kneel`)·리타(`carry_box`), STAGE_1 일꾼 7(`carry_box`, `assemble`, `work_bench`)·리타, STAGE_3 엘레나(`speech`, `expr=smile`)·아멜리아(`attention`, 비서)·로네(`clap`)·헤일리(`salute`)·군중 20(`cheer`, `clap`, `wave`)·리타(`clap`)·캐시(`cheer`).

### 2.3 인터루드 6 「평화로운 일상」 `interlude_daily`
원작: 정착 약 100년 뒤의 모나티엄. 오리지널: 리타의 진압반 특수작전부 생활, 분대원, 칸나의 잔소리, 캐시와의 재회.

배치는 `downtown(variant="day")` 그대로다(`monatium-city.md` 6장): 엘레나 초상의 시청, 코어 AI 탑(켜짐), 중앙로·모노레일(`MONORAIL_train`, drift 8 m/s로 머리 위를 지나감), 상가 줄(모나티엄 25, 커틀릿 하우스, 엘프 은행, MELU CORP. …), 홀로 광고, 동쪽 대형 화면 건물, 서쪽 **진압반 훈련장**과 EBI 본부, 알프토반 진입로, 원경 고층.

| CAM | 길이 | 내용 | NPC (`scene`) |
|---|---|---|---|
| `daily_a` | 8 s | 큰길 건너 남쪽 보도에서 본 광장과 시청, 모노레일 기둥 사이로 옆 이동 | 시민 12: `walk`, `chat`, `sit_bench`, `phone`, `wave`, `eat`, `carry_box` |
| `daily_b` | 8 s | 훈련장 표적 쪽에서 본 사수 선, 칸나 쪽으로 이동 | 리타·로나·사브르·케이트 `train_drill`(진압 카빈을 손에 든다: `hold_R`=`weapons/monatium/monatium_riot_carbine.glb`), 제스티 `sheepish`(카빈 없음), 칸나 `scold`(look=제스티), 진압반원(카빈) |
| `daily_c` | 7 s | 자판기 앞 캐시와 리타, 어깨 너머로 다가감 | 캐시 `wave`, 리타 `idle`(서로 look), 로나·케이트 벤치 `eat`(seatZ), 사브르 `chat`, 제스티 `laugh` |

### 2.4 인터루드 7 「R41 침공 개시」(D-7, 선언 방송) `interlude_invasion`
원작: 흑뉴아가 부시장 자격으로 사멜리아의 배신을 알리고 교주 차원 침공을 선언한다. **차원문은 선언 1주일 뒤에 열린다.** R41 수색 진압반이 차원을 뒤지며 차원 미아가 생긴다. → 대규모 차원문(`GATE_`)은 두지 않는다(키트 `gate_r41`로만 만들어 1막에서 쓴다).

같은 `downtown(variant="dusk")`(가로등 켜짐) 위에:

| 노드 | 내용 |
|---|---|
| `RIFTS` > `RIFT_01`..`RIFT_07` | R41 수색용 작은 차원 틈. 찢긴 마젠타 틈 + 보라 테 + 밝은 중심 + 떠 있는 파편 + 빛 번짐. 시청 탑 뒤(01, 리타의 시선), 코어 탑 위(02), EBI 위(03), 상가 위(04), 원경 큰 틈(05), 모노레일 바로 위 낮은 틈(06), 화면 건물 위(07). 03·07은 처음 `state=closed`. 각자 `flicker` 간격이 다르다 |
| `PROP_drone_recon_01/02` | 틈 너머로 엿보는 D-4 정찰 드론 두 대(`rift` 속성으로 어느 틈인지, 느린 `drift`, `collider=0`) |
| `SCREEN_plaza` (12 × 6.75 m), `SCREEN_cityhall` (5.1 × 2.9 m), `SCREEN_street` (7.2 × 4.05 m) | 흑뉴아 선언 방송을 띄울 화면 |
| `ALERTS` > `LIGHT_alert_01`..`11` | 경보등(광장 가로등 위 6, 시청 지붕·포르티코 3, EBI 지붕·화면 건물 지붕 2). `FX_siren_*` 8곳 |
| `LIGHT_rift_glow` | 마젠타 점광원 제안 (RIFT_01) |

| CAM | 길이 | 내용 | NPC |
|---|---|---|---|
| `invasion_a` | 6 s | 리타 얼굴(앞 위) → 왼쪽 옆을 돌아 어깨 너머 로우 앵글(옆얼굴, 시청 탑 뒤 틈 RIFT_01) → 머리 위로 올라 리타 시점 | 리타 `look_up`(시선 추적 없이 자세만으로 RIFT_01 쪽. `lookAt`을 더하면 고개가 하늘로 꺾인다), 캐시 `cower`(look=리타) |
| `invasion_b` | 10 s | 광장 낮은 와이드: 시청 화면의 방송과 하늘의 틈들, 위로 틸트 | 리타·캐시·제스티 `point_up`·로나 `look_up`, 시민 |
| `invasion_c` | 8 s | 광장 동쪽 대형 화면 앞 시민들 → 화면 건물 지붕 경보등과 틈 07로 틸트 | 시민 14: `look_up`, `phone_up`, `point_up`, `cover_mouth`, `hold_hands`, `run`, `freeze` |

연출 순서 제안: 틈 깜빡임(`_open` 숨김/보임 반복, closed 틈은 `_closed` 실금만) → 화면들에 노이즈 → 선언 방송 → `LIGHT_alert_*` `on=1` + 사이렌 → 타이틀 카드 "1막".

---

## 3. 포즈 목록 (`pose`)

미션 담당이 포즈 라이브러리(`src/game/npc/poses.ts`)에 구현한다. 지구 쪽 세트와 겹치는 이름은 같은 이름을 쓴다.

| 이름 | 설명 | 쓰는 곳 | 비고 |
|---|---|---|---|
| `idle` | 편히 선 자세 | daily_c 리타 | 이미 있음 |
| `attention` | 차렷 | 취임식 아멜리아 | 이미 있음 |
| `salute` | 경례를 유지 | 취임식 헤일리 | 제스처 `salute`를 자세로 |
| `look_up` | 고개·상체를 젖혀 하늘을 봄, 팔은 내림 | 불시착, D-7 리타·시민 | 지구 쪽과 공용 |
| `kneel` | 한쪽 무릎 꿇기 | 불시착 아멜리아(풀을 만짐), 천막촌 | 공용 |
| `carry_box` | 상자를 두 팔로 안고 섬 | 불시착, 천막·공장, 거리 | 공용 |
| `sit_tired` | 땅에 지쳐 앉음 | 천막촌 모닥불 | 공용 |
| `work_bench` | 작업대 앞에서 손을 움직임 | 천막촌, 공장 | 공용 |
| `assemble` | 서서 무언가 조립(두 손 앞) | 천막·공장 | 공용 |
| `run` | 달리는 중간 자세 | D-7 시민 | 공용 |
| `look_around` | 두리번거림(고개 좌우 osc) | 불시착 엘프 | 새 이름 |
| `look_far` | 먼 곳을 바라봄, 손을 눈썹에 얹음 | 불시착 엘레나(세계수) | 새 |
| `sit_dazed` | 다리를 뻗고 주저앉아 멍함, 고개 살짝 기울임 | 불시착 리타 | 새 |
| `il_arrival_sit_plate` | `sit_dazed`의 다리 + 무릎 위로 빈 접시를 앞으로 기울여 들고 포크를 세워 듦 | 불시착 로네 | 새 (`interlude.ts`가 더함, 쥔 자리) |
| `lie_sprawl` | 엎어져 대자로 뻗음 | 불시착 캐시·엘프 | 새 |
| `help_up` | 허리를 굽혀 한 손을 아래로 내밂 | 불시착 헤일리 | 새 |
| `point_far` | 팔을 뻗어 먼 곳을 가리킴 | 불시착 엘프, 천막촌 엘레나 | 새 (제스처 `point`를 자세로) |
| `tumble` | 공중에서 허우적댐(팔다리 벌림, 몸 기울어짐) | 게이트에서 떨어지는 엘프 | 새, `airborne` |
| `speech` | 연설대에 한 손, 다른 팔을 들어 올림 | 취임식 엘레나 | 새 |
| `clap` | 가슴 앞 박수 (손 osc) | 취임식 | 새 |
| `cheer` | 두 팔 번쩍 | 취임식 군중 | 새 |
| `wave` | 한 손 흔들기 (osc) | 캐시 재회, 거리, 군중 | 새 |
| `walk` | 걷는 중간 자세 | 거리 시민 | 새 |
| `chat` | 마주 보고 이야기, 한 손 제스처 | 거리, 광장 | 새 |
| `sit_bench` | 벤치에 앉음(`seatZ`) | 거리 시민 | 새 |
| `eat` | 앉거나 서서 한 손으로 먹을 것을 입에 | 벤치의 분대원, 거리 | 새 (앉은 경우 `seatZ`) |
| `phone` | 휴대폰을 내려다봄 | 거리 시민 | 새 |
| `phone_up` | 휴대폰을 들어 하늘을 찍음 | D-7 시민 | 새 |
| `train_drill` | 진압반 카빈 견착 사격 자세. 카빈을 들었으면(`hold_R`) 쥔 자리 `_holdR`로 가슴 앞 정면에 겨누고 왼손이 앞 손잡이를 쥔다 | 훈련장 분대 | 새 |
| `sheepish` | 어깨 움츠리고 뒤통수 긁기 | 혼나는 제스티 | 새 |
| `scold` | 허리에 한 손, 다른 손 검지로 가리키며 몸을 숙임 | 칸나 | 새 |
| `laugh` | 배를 잡고 웃음 | 광장 제스티 | 새 |
| `cower` | 몸을 웅크리고 남 뒤에 숨음 | D-7 캐시 | 새 |
| `point_up` | 하늘을 가리킴 | D-7 제스티·시민 | 새 |
| `cover_mouth` | 두 손으로 입을 가림 | D-7 시민 | 새 |
| `hold_hands` | 옆 사람과 손을 잡고 몸을 붙임 | D-7 시민 둘 | 새 |
| `freeze` | 굳어 선 채 팔이 반쯤 들림 | D-7 시민 | 새 |

---

## 4. 몽타주 담당 메모

- **컷별 NPC**: `scene`(인터루드 4·6·7)과 `stage`(인터루드 5)로 거른다. 표시 안 할 NPC는 숨기거나 `level.dynamic`에서 뺀다.
- **STAGE**: `level.nodes.get('STAGE_n').visible`로 켠다. 단계 노드의 `sky`, `timeOfDay`로 하늘색을 바꾸면 타임랩스가 산다. NPC는 STAGE 노드 밖에 놓이므로 `stage` 값으로 따로 켠다.
- **RIFT**: `RIFT_<n>_open`을 `flicker` 간격으로 껐다 켠다. `state=closed`인 틈은 `_closed`(실금)만 보이게 시작하고, 방송 직전에 열면 좋다. `hidden=1` 노드는 로드 직후 숨긴다.
- **SCREEN**: `SCREEN_*` 메시의 머티리얼(UNLIT)에 비디오·캔버스 텍스처를 넣는다. UV는 정면 기준 왼쪽 아래 (0,0).
- **GATE_escape**: 루트 스케일 0→1(열림), 1→0(닫힘). arrival_c에서는 닫는다.
- **drift**: `MONORAIL_train`, `FALLING`, 정찰 드론은 엔진이 계속 움직이므로 컷 시작에 위치를 되돌린다.
- **조명**: 점광원은 `LIGHT_gate_*`, `LIGHT_rift_glow`, `LIGHT_core_on`(빈 오브젝트, `pointLight=1`). 경보등은 메시 `LIGHT_alert_*`(`emissiveToggle`).

---

## 5. 검증

- 시트(top·34): `npm run shot -- levels/interlude_<id>.glb --views top,34` → `shots/levels__interlude_{arrival,construction,daily,invasion}.png`
- CAM 시점 근사: 레일 재생이 아직 커밋되지 않아, 레벨 glb를 읽고 NPC·PROP 마커 자리에 모델을 붙인 뒤(포즈 없이 A 포즈) 각 컷의 첫·끝 CAM에서 렌더하는 임시 하네스(저장소 밖)로 봤다. 툰 셰이딩·아웃라인은 게임 로더(`src/art/loader.ts`)와 같다.
- R41 대규모 차원문 모듈은 `_tmp/gate_r41_preview.glb`(커밋 안 함)로 확인했다.
