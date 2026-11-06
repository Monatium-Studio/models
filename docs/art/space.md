# 우주 장면: 엘피니아 함대, 지구, ICBM (space, levels/prologue_space)

프롤로그 오프닝 1·2(함대가 지구로 향함, 탐사선 관측)와 엔딩 `END_ATTACK`의 외부 컷(ICBM → 운동에너지 탄두 → 기함 함교 직격)에 쓰는 에셋과 장면이다. 시나리오는 `docs/scenario.md` 4장, 대본은 `docs/script/prologue.md`가 기준이다.

| 무엇 | 어디 |
|---|---|
| 공용 키트 | `art/blender/lib/space_kit.py` (초타원 로프트 `Hull`, 귀 지느러미 `fin`, 추진기·포탑·엠블럼·창 줄, 정점색 합치기 `Ship`, 텍스처 PNG 저장, UV 구) |
| 에셋 스크립트 | `art/blender/space/*.py` → `public/models/space/*.glb` |
| 지구 원본 데이터 | `art/blender/space/earth_data.py` (자동 생성, `earth_data_build.py`로 다시 만든다) |
| 장면 | `art/blender/levels/prologue_space.py` → `public/models/levels/prologue_space.glb` |

```bash
npm run model -- art/blender/space/elfinia_flagship.py        # 에셋 하나 (함선·지구·별하늘·ICBM·탄두·달)
npm run shot -- space/elfinia_flagship.glb --views front,34,side,top
SK_PREVIEW=bridge_damaged npm run model -- art/blender/space/elfinia_flagship.py   # 숨김 변형만 보이는 미리보기 (…__bridge_damaged.glb, 커밋하지 않음)
npm run model -- art/blender/levels/prologue_space.py         # 장면 (에셋 glb를 불러와 조립하므로 에셋을 먼저 만든다)
python3 art/blender/space/earth_data_build.py                 # Natural Earth에서 지구 데이터 다시 만들기 (네트워크)
```

---

## 1. 원작 근거 (2026-11-01 나무위키 「엘프(트릭컬 리바이브)」, 「헤일리(트릭컬 리바이브)」 확인)

| 원작 사실 | 반영 |
|---|---|
| 엘프는 우주를 건너 지구를 침공했고 우주선 제조 기술이 있다. '엘프 원정함대' | 함대 전체 [오리지널 디자인] |
| 헤일리가 인간들에게 함대 모습을 드러내 통신했고, 함선을 지구 한복판에 착륙시켰다. 반격으로 항법 장치가 고장 나고 통신이 마비됐다 | 기함 + 강습 수송함 편대. 대본: 수송함만 착륙, 기함은 고고도 |
| 헤일리는 망원 카메라로 인류가 평화로워 보인다고 판단했다 | 탐사선 「돋보기」의 망원 경통 |
| 헤일리는 함선 설계를 잘 알고 조타 실력이 뛰어나다 | 기함 「큰망치」를 헤일리의 배로 |
| 광자 무기 출력이 낮아 먹히지 않았다 | 함수 광자포, 시안 발광 |
| 엘레나 테마극장: "날아다니던 중 미사일을 맞았다" | 엔딩 피격 (ICBM, 운동에너지 탄두, 함교 직격은 [오리지널, 사용자 확정]) |

원작에 엘프 함선 그림은 없다(문서의 이미지는 인물·배경뿐). 엘리아스의 비행선 '빵주'는 이후 시대의 배라 참고하지 않았다. 형태는 전부 오리지널이고, 교주 차원 화기의 형태 문법(`weapons-home.md` 2장)을 함선 크기로 옮겼다.

## 2. 형태 언어 (함대 공통)

1. **둥근 판 → 통통한 초타원 로프트.** 단면 지수 n=2.5~4.5. 길이:폭이 짧은 SD 비율(기함 2.6:1). R41의 45° 모따기와 반대.
2. **엘프 귀 지느러미** [오리지널 서명]: 옆으로 뻗고 위로 휘어 오르는 잎 모양 날개(뿌리 시위 0.76 × 최대, 1/3 지점이 가장 넓고 끝이 뾰족). 끝은 밝은 남색, 좌현 빨강·우현 초록 항해등.
3. **헬멧 함교**: 엘피니아 전투 헬멧(둥근 돔, 테두리 챙, 정수리 세로 홈)을 닮은 자줏빛 회색 돔. 챙 아래 따뜻한 함교 창 띠.
4. **금색 고리**: 추진기 노즐 테, 기함 광자포의 나팔 포구, 포신 끝, 엠블럼 원판 테, 탐사선 경통 후드. 가는 줄에는 금색을 쓰지 않는다.
5. **둥근 창 줄**(시안 UNLIT) + 남색 창 띠, 남색 띠(살짝 부푼 로프트), 남색 원판 + 금테 + **원작 엘프 로고** 엠블럼(`hw.elf_logo`).
6. **진지한 군용 디테일**: 쌍열 포탑, 함번 스텐실(`01`, `03`), 정비 해치, 격납고 유도등, 패널선, 경고 노랑 승강구 테.

팔레트(`space_kit.PAL`)는 `home_weapons.PAL`의 엘피니아 계열을 따른다: 선체 회녹 `#8d988c`(밝은 `#a7b1a4`, 그림자 `#6f7a70`), 자줏빛 건메탈 `#5d555d`, 남색 `#2f3644`, 금색 `#d6b25e`, 시안 발광 `#7ff0ea`, 추진기 심지 `#eafffd`, 함교 창 `#ffe7a6`. 먹선은 원작 붉은 갈색 `#4a2229` 하나. 지구제 미사일은 일부러 흰 `#e6e3dc`·검정 띠·주황 화염(`#ffb054`)으로 엘프 시안과 대비시키고 먹선도 차가운 `#26242a`를 쓴다.

**그리기 호출**: `Ship.finish`가 불투명 파츠의 머티리얼 색을 정점색으로 구워 합친다. 함선 하나 = `<이름>_body`(툰, 아웃라인) + `_fine`(데칼, noOutline) + `_glow`(UNLIT) + `_plume`(UNLIT 반투명, 단면 컬링) 4개.

## 3. 에셋

삼각형은 내보낸 glb 기준(아웃라인 헐 제외). 함선 좌표: 함수 -Y(three.js +Z), 좌현 +X, 원점 = 선체 중심.

| 파일 | 이름 | 설정 | 크기 | 삼각형 | outline |
|---|---|---|---|---|---|
| `elfinia_flagship` | 기함 「큰망치」 01 | 헤일리의 기함. 리타·캐시의 정찰 침투조가 병력 구획 B에 탄다. 고래형 선체, 함수 광자포 + 금색 나팔 포구, 헬멧 함교, 큰 귀 지느러미, 주추진기 3 + 보조 2, 포탑 3 | 72 × 80 × 38 m | 11,921 (+ 숨김 변형 1,804) | 0.16 |
| `elfinia_cruiser` | 호위함 「송곳」 | 함대 수를 채우는 가벼운 호위함. 금색 깃 고리 충각, 작은 헬멧 함교, 남색 등 줄, 쌍열 포탑 | 36 × 30 × 12 m | 4,680 | 0.07 |
| `elfinia_transport` | 강습 수송함 「공구함」 03 | 공구함형 상자 선체 + D자 손잡이(통신 아치), 끝내 떨어지지 않은 강하 포드 10기, 병력 구획 창 2열, 함미 램프 | 44 × 34 × 23 m | 9,227 | 0.09 |
| `elfinia_probe` | 탐사선 「돋보기」 | 망원 경통(금색 후드 고리, 시안 렌즈), 접시 안테나, 센서 꼬투리, 귀 모양 광자 전지판 | 7.6 × 11 × 4 m | 4,538 | 0.025 |
| `earth` | 지구 | 툰 텍스처(UNLIT) + 대기 껍질 2겹 (4장) | 반지름 100 m | 4,656 | 없음 |
| `starfield` | 별하늘 | 성운 돔(1024×512) + 별 1,900 + 반짝이 36 | 반지름 540 m | 5,048 | 없음 |
| `moon` | 달 | 절차 생성 바다·크레이터 + 구운 위상 | 반지름 18 m | 728 | 없음 |
| `elias` | 엘리아스 | 1막 위성 브리핑의 궤도 첫 컷. 절차 생성 툰 행성 + 대기 껍질 2겹 (9장) | 반지름 100 m | 6,416 | 없음 |
| `earth_icbm` | 지구 ICBM | 3단 분리형 일반형(실존 미사일 복제 아님). 6장 | 23 m, 지름 1.9 m | 3,676 | 0.03 |
| `kinetic_warhead` | 운동에너지 탄두 | 폭약 없는 다트형 관통체 + 재진입 열 발광. 6장 | 3.6 m | 426 | 0.008 |

### 3.1 기함 함교 블록
- `bridge`: 헬멧 돔, 챙, 함교 창, 함번, 돛대. 평소 보인다.
- `bridge_damaged` (`hidden=1`): 직격 뒤 모습. 앞면(지구 쪽) 위쪽이 1.7 m 함몰되고 찢긴 구멍 + 주황 불씨(UNLIT), 말려 나온 장갑판 6장, 그을음, 맞은 쪽 60°가 떨어져 나간 챙과 처진 조각, 꺾인 돛대와 꺼진 등, 깨져 꺼진 창(맞은 쪽)과 붉은 비상등 창. **완파가 아니다**: 돔 형체는 남는다.
- `anchor_bridge_hit`: 직격 지점. 장면의 `FX_hit_bridge`, `MARK_hit_bridge`가 이 위치다.

### 3.2 강습 수송함과 대본
대본(`docs/script/prologue.md`)에서 리타의 배는 기함이다. 수송함은 함대 구성용(강습 돌격대)으로 남긴다. 측면 창 2열(위 숙소·대기실, 아래 훈련 구획)과 강하 포드는 '정찰 없이 착륙'을 말없이 보여 주는 소품이다.

## 4. 지구 텍스처 출처와 가공

| 항목 | 내용 |
|---|---|
| 원본 | **Natural Earth 1:50m** 벡터: `ne_50m_land`, `ne_50m_lakes`, `ne_50m_glaciated_areas`, `ne_50m_antarctic_ice_shelves_polys`, `ne_50m_geography_regions_polys`(Desert 분류), `ne_50m_populated_places_simple`(인구 상위 900곳, 밤 불빛) |
| 받은 곳 | Natural Earth 공식 저장소 GeoJSON `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/` |
| 라이선스 | **퍼블릭 도메인.** <https://www.naturalearthdata.com/about/terms-of-use/> (2026-11-01 확인): "All versions of Natural Earth raster + vector map data found on this website are in the public domain. You may use the maps in any manner, including modifying the content and design…" / 저장소 `LICENSE.md`: "Everything here is public domain." 출처 표기는 필요 없지만 여기 기록한다: *Made with Natural Earth.* |
| 저장 | `earth_data.py`(166 KB): 더글러스-포커 0.06° 단순화, 작은 섬·호수 버림, 0.02° 정수 양자화 int16 차분 + base64. 위성 사진 등 래스터는 쓰지 않았다 |
| 가공 (`earth.py`) | 짝홀 스캔라인으로 다각형을 칠하고, 2배(4096×2048)로 합성한 뒤 평균으로 줄여 2048×1024 PNG(약 380 KB, glb 523 KB). 평탄한 툰 색: 바다 2단 + 얕은 바다 띠 + 짙은 남청 해안 먹선, 위도·내륙 거리 노이즈로 나눈 식생 띠(열대·초원·건조·침엽·툰드라), Natural Earth 사막·빙하, 남위 62° 아래 빙상. 구름은 구면 3D 값 노이즈(위도로 눌러 동서로 길게, 도메인 왜곡)를 두 단으로 자르고 북미 위는 조금 걷었다 |
| 낮과 밤 | 태양을 북위 12°, 서경 128°에 고정해 텍스처에 굽는다: 낮 1.0 / 중간 0.86(살짝 푸르게) / 노을 분홍 띠 / 밤(남색 + 도시 불빛). 북미 중부는 오후 2시쯤이고 대서양에 경계가 보인다. 엔진 툰 조명은 밤 면을 0.5 밝기로 남기므로 지구는 **UNLIT**이다 |
| 대기 테 | 안쪽을 보는 구 껍질 2겹(1.026 R 불투명도 0.85, 1.065 R 0.32, UNLIT, 단면 컬링). 바깥에서는 지구 둘레 고리로만 보인다. 면마다 낮 하늘색 / 노을 분홍 / 밤 짙은 파랑 정점색 |
| 루트 속성 | `sunLocal`(구운 태양의 로컬 방향, Blender), `sunLatLon`, `radius`=100 |

로컬 좌표: +Z 북극, 그리니치 -Y, 동경 90° +X (`space_kit.uv_sphere`). 지구를 돌리면 구운 태양도 같이 돈다. 장면은 북미가 함대를 보게 돌리고, 돌린 `sunLocal`을 루트 `earthSun`으로 적는다.

## 5. 장면 `levels/prologue_space.glb`

에셋 glb를 불러와 놓는다(다시 만들지 않음). 89,136 삼각형, 4.1 MB, 머티리얼 9개.

| 노드 | 내용 |
|---|---|
| `earth` | 중심 (0, -360, -125) Blender, 반지름 100. 북미(북위 40°, 서경 98°)가 함대 쪽, 북쪽을 10° 기울임 |
| `starfield` | 중심 (0, -120, -40), 0.778배(반지름 420 m). 엔진 기본 far 600 m 안에 든다 |
| `moon` | 함대 전경 컷의 오른쪽 위. 장면 태양으로 다시 구움 |
| `ship_flagship` | 원점, 함수가 지구 쪽으로 6° 숙임. 자식 `bridge`, `bridge_damaged`(hidden=1), `anchor_*` |
| `fleet_escorts_*` | 호위함 7척을 그룹(body/fine/glow/plume)별로 합친 메시 |
| `fleet_transports_*` | 강습 수송함 3척을 합친 메시 (대본: 기함이 앞, 수송함이 뒤) |
| `ship_<n>` | 합친 함선마다 위치·방향 빈 오브젝트 (`shipClass`=cruiser/transport, 1~7 호위함, 8~10 수송함) |
| `ship_probe` | 지구 표면 58 m 위, 경통(-Y)이 `MARK_target`을 겨눔 |

**루트 속성**

| 키 | 값 | 뜻 |
|---|---|---|
| `sky` | `#05081a` | 배경색 (별하늘 돔 뒤) |
| `sun` | three.js 방향 | 함선 조명. 지구에 구운 태양과 같은 방위에서 38° 들어 올렸다 (그대로면 북미 남서쪽 태양이 함선을 아래에서 비춤) |
| `earthSun` | three.js 방향 | 지구·달에 구운 실제 태양 방향 (참고용) |
| `ambient` | 0.45 | 반구광 |
| `music` | `prologue_space` | |
| `camNear`, `camFar` | 0.5, 2000 | 이 장면에 권장하는 카메라 범위. 데칼(0.05~0.15 m 띄움)이 먼 거리에서 깜빡이지 않으려면 near를 키우는 편이 좋다. 지원하지 않아도 far 600 m 안에서 보이게 배치했다 |
| `skyNode` | `starfield` | 엔진이 지원하면 이 노드를 카메라 위치에 따라 옮겨(회전 없이) 무한 원경처럼 그린다. 지원하지 않으면 그대로 둔다 (긴 공격 레일에서 별이 약간 시차로 움직임) |
| `collider` | 0 | 충돌체 없음 (모든 메시에도 `collider=0`) |

## 6. 마커 규칙 (LEVELS.md 형식)

`docs/LEVELS.md`의 노드 규칙에 이 장면이 더하는 것. 해석은 미션·컷신 시스템이 한다.

| 접두사 | 종류 | 커스텀 속성 | 처리 |
|---|---|---|---|
| `CAM_<shot>_<nn>` / `LOOK_<shot>_<nn>` | 빈 오브젝트 | `t`, `fov` | LEVELS.md 그대로. 모든 점에 `LOOK_`이 있고, `CAM_`의 -Y도 같은 쪽을 본다 |
| `WP_icbm_<k>` | 빈 오브젝트 | `t`(그 점에 도달하는 시각, 초), `scale`(그 점에서의 모델 배율), 선택 `event` | 주 ICBM(`space/earth_icbm.glb`)의 경로. three.js에서 모델 +Z가 진행 방향이므로 다음 점을 `lookAt`. `scale`은 작은 지구(반지름 100 m)와 실척 함대를 잇는 원근 속임으로, 점 사이를 보간한다. `event`: `launch`, `sep_stage_1`(stage_1 분리, exhaust_1 켬), `sep_stage_2`(stage_2 분리, exhaust_2 켬), `release`(stage_3 끄고 shroud_L/R 벌림, 탄두 방출), `bus_drift` |
| `WP_warhead_<n>_<k>` | 빈 오브젝트 | `t`, `scale` | 탄두 n(`space/kinetic_warhead.glb`)의 경로. 첫 점 = 버스 방출 지점·시각 |
| `FX_<kind>_<id>` | 빈 오브젝트 | `t`(시작 시각), `size`(지름 m), 종류별 추가 | `FX_hit_*`: 피탄 섬광·충격파 (`kind`=`graze`면 스침), `target`·`show`·`hide`가 있으면 그 시각에 `target` 노드 아래 `hide` 노드를 숨기고 `show` 노드를 켠다. `FX_smoke_*`: 연기 (`dur` 초), `FX_debris_*`: 파편 (`count`) |
| `MARK_target` | 빈 오브젝트 | | 관측 목표 (미시간호 남쪽 끝). 탐사선 경통과 `CAM_scope`가 여기를 본다 |
| `MARK_hit_bridge`, `MARK_launch_<i>` | 빈 오브젝트 | | 직격점(=`FX_hit_bridge`)과 ICBM 발사 지점(0 = 주 ICBM, 1~3 = 함께 솟는 다른 발). 미션 시스템의 임시 연출(`src/game/cinematic/attack.ts`)이 찾는다 |
| `ship_<n>` | 빈 오브젝트 | `shipClass` | 합친 함선의 위치 |

노드 커스텀 속성 **`hidden=1`**: 엔진이 불러올 때 숨긴다 (`bridge_damaged`, ICBM의 `exhaust_1`·`exhaust_2`·`exhaust_bus`).

### 6.1 카메라 레일

| 레일 | 길이 | 내용 |
|---|---|---|
| `CAM_fleet_00~04` | 10 s | 기함 좌현 뒤 낮게(추진기 너머 지구) → 귀 지느러미 바깥을 지나며 → 위로 올라서며 함교·엠블럼·광자포 → 뒤·위로 빠져 **진형 전체와 지구를 한 화면에**(8~10 s). FOV 42→50 |
| `CAM_probe_00~02` | 7 s | 탐사선 옆(경통이 북미를 겨눔, 지구가 화면을 채움) → 어깨 너머로 들어가 경통과 같은 시선. FOV 40→32 |
| `CAM_scope_00~01` | 9 s | 망원 카메라 시점: 렌즈 앞에서 `MARK_target`을 FOV 24→9로 당김 (위성 영상풍 오버레이 아래 깔림) |
| `CAM_attack_00~08` | 11 s | 발사장을 비스듬히 내려다봄(대기 띠를 뚫고 상승) → 1단 분리(1.9) → 2단 분리(2.9) → 버스 뒤에서 함대를 향해 탄두 방출(4.2) → 함대 앞에서 다가오는 탄두들(6.2) → 기함 옆 → **함교 직격 9.0** → 불타는 함교 유지 |

공격 시각은 `src/game/cinematic/attack.ts`의 `ATTACK_TIMES`(stage1 1.9, stage2 2.9, mirv 4.2, impact 9.0)와 맞췄다. 탄두 0 = 함교 직격(9.0), 1 = 우현 앞 호위함 선체 스침(`FX_hit_1`, 8.8), 2 = 강습 수송함 옆 빗나감, 3 = 기함과 좌현 호위함 사이 통과.

### 6.2 ICBM과 탄두 노드
- `earth_icbm`: 원점 = 1단 노즐 끝, 진행 방향 three.js +Z. `stage_1`(+1·2단 사이 링, `exhaust_0`), `stage_2`(`exhaust_1` hidden), `stage_3`(`exhaust_2` hidden), `bus`(`shroud_L`/`shroud_R`: `move`="±2.5,0,1.5" 벌어지는 방향, `warhead_slot_0~3`, `exhaust_bus` hidden). 화염 노드는 원점 = 노즐 끝이고 three.js -Z로 뻗는다(길이 배율로 깜빡임을 주기 좋음). 반투명 겉껍질은 `<화염>_haze` 자식.
- `kinetic_warhead`: 원점 = 무게 중심, 진행 방향 three.js +Z. `heat_glow`(촉 열 발광, UNLIT) > `heat_glow_trail`(반투명 플라스마 덮개와 꼬리). 버스에서 풀린 직후 꺼 두었다가 돌입하며 켜도 된다.

## 7. 검증
- 에셋 시트: `shots/space/sheet_{flagship,flagship_bridge_damaged,cruiser,transport,probe,earth,icbm,kinetic_warhead}.png` (뷰어는 `hidden`을 모르므로 기함은 `SK_PREVIEW=bridge` / `bridge_damaged`로 내보낸 미리보기를 찍었다)
- 레일 미리보기: 뷰어에 카메라 모드가 없어 임시 페이지(엔진과 같은 `loadModel` 툰·아웃라인, near 0.03 / far 600, 루트 `sky`·`sun`·`ambient` 적용, `WP_`·`FX_`·`hidden` 흉내)로 찍었다: `shots/space/rail_*.png`
- 실제 재생: `npm run gamecheck -- --query "mission=prologue&autostart=1"`에서 `OPEN_FLEET`·`OPEN_PROBE`가 이 레일로 재생된다 (`shots/game-1280x720-space_*.png`)

## 8. 남은 일과 주의
- 망원 화면(`CAM_scope` FOV 9)에서는 지구 텍스처(2048, 0.18°/px)가 뭉개진다. 확대 화면의 세부(도시, 경기장 등)는 브리핑 오버레이가 맡는다.
- 공격 레일은 지구에서 함대까지 300 m를 11초에 지나므로, 별하늘을 카메라에 붙이지(`skyNode`) 않으면 별이 시차로 조금 움직인다.
- ICBM 경로의 `scale` 보간과 `FX_`의 `target/show/hide`는 이 장면이 정한 규칙이다. 미션 시스템이 아직 읽지 않으면 ICBM이 지구 곁에서 실척으로 보이고 함교가 바뀌지 않는다.

---

## 9. 엘리아스 행성 `space/elias.glb` (1막 로딩 영상 1의 궤도 첫 컷)

위성 브리핑은 궤도의 엘리아스 → 모나티엄 일대 → 도심 → 작전 구역으로 끊어 들어간다(`docs/scenario.md` 1막). 그 첫 단계의 행성이다. 배경 별하늘은 `space/starfield.glb`를 그대로 쓴다.

```bash
npm run model -- art/blender/space/elias.py          # 약 2분 30초 (4096×2048로 합성 후 2048×1024로 줄임)
npm run shot -- space/elias.glb --views front,34
```

| 구분 | 내용 |
|---|---|
| **[원작]** | 엘리아스 가운데의 세계수 엘드르, 숲 너머의 안개(경계), 모나티엄은 엘리아스 동부(정령산·에르피엔 접경)의 엘프 도시 |
| **[오리지널]** | 엘리아스를 **구(행성)로 그린 것과 그 지리 전체**. 원작에 행성 모습이나 지도는 없다. 큰 대륙 하나 + 작은 대륙 넷 + 섬, 대륙 가운데 엘드르의 방사형 수관, 알려진 땅을 두른 안개 띠, 정령산 산줄기, 남쪽 작은 산줄기, 호수, 숲·초원·건조지·툰드라 띠, 구름 띠, 모나티엄 얼룩과 시안 빛무리 |

파이프라인은 지구(4장)와 같다: 반지름 100 UV 구(64×32) + 절차 텍스처 PNG(UNLIT) + 안쪽을 보는 대기 껍질 2겹. 실제 지리 자료는 쓰지 않고 `earth.py`의 구면 값 노이즈·팽창·흐림·대기 껍질 함수를 가져다 쓴다.

| 요소 | 위치 (경도, 위도) | 표현 |
|---|---|---|
| 큰 대륙 | 중심 (4°, 15°), 반지름 약 40° | 각거리 + 도메인 왜곡 노이즈로 깎은 해안, 얕은 바다 띠, 짙은 남청 해안선 |
| 세계수 엘드르 | (2°, 17°) | 반지름 약 5.6°의 짙은 초록 수관(가장자리 9갈래 물결, 밝은 덩어리와 방사 줄, 가운데 더 짙음), 해 반대쪽 그림자 |
| 에르피엔 | 엘드르 둘레 | [원작] 왕국 한가운데 세계수: 수관 둘레를 두른 폭 약 1.5°의 흰 시가 고리(붉은·청록 지붕 점, 고리 길 둘, 방사형 큰길 여섯, 바깥 성벽 띠), 그 밖의 밝은 풀밭 고리 (2026-11-02 정정. 전에 모나티엄 동쪽에 두었던 '에르피엔 쪽 작은 마을 얼룩'은 뺐다) |
| 안개 경계 | 엘드르에서 39° | 옅은 흰 띠(폭 약 3°, 노이즈로 흔들림) + 바깥으로 흩날리는 자락 |
| 정령산 | (12.5°, 33.5°) → (22.5°, 18°) 굽은 줄기 | 봉우리 덩어리 16개를 겹친 바위색 산줄기, 눈 모자, 산기슭 짙은 숲 |
| 모나티엄 | (26°, 12°) | 반지름 약 1.7°의 회색 얼룩 + 밝은 도심, 옅은 시안 빛무리(도시 키트 네트워크 색 #7ff0ea) |
| 구름 | | 위도 띠 + 도메인 왜곡 2단 구름. 엘드르와 모나티엄 위는 걷었다 |
| 낮과 밤 | 태양: 모나티엄에서 보아 앞-왼쪽(서)·조금 위 | 부드러운 낮밤 경계(smoothstep) + 노을 기운, 밤 면은 남색과 드문 마을 불빛. 모나티엄을 정면으로 보면 원판 동쪽(오른쪽)에 경계가 걸린다 |

**루트 속성**: `radius`=100, `monatium`="0.42879,0.20791,0.87915"(중심 → 모나티엄 단위 벡터, three.js 좌표 x=bx, y=bz, z=-by), `monatiumLocal`(Blender), `monatiumLatLon`, `eldr`(three.js), `eldrLatLon`, `hazeDeg`=39, `sunLocal`(구운 태양, Blender, 지구와 같은 규약), `sunThree`, `sunLatLon`. 자식 빈 오브젝트 `MARK_monatium`, `MARK_eldr`는 표면 점이라 구를 돌려도 따라 돈다.

주의: 구운 태양은 모나티엄의 오후 쪽(서쪽)이다. 위성 전경(`act1_overview`)은 아침 해(동남동)이므로, 두 컷을 이어 붙일 때 낮밤 경계 방향이 마음에 걸리면 `elias.py`의 `sun_dir()`에서 서쪽 성분의 부호를 바꿔 다시 굽는다.

