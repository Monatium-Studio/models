# Combatium 아트 가이드 (3D)

트릭컬 리바이브 「엘리아스 침공전」 2차창작 웹 3D FPS. 원작의 SD 화풍을 3D로 옮기되 **베끼지 않는다.**
시나리오와 설정은 `docs/scenario.md`.

## 1. 스타일 목표

원작 화풍(엘레나 카드 일러스트 등에서 확인)의 특징:
- **SD 비율.** 머리가 키의 40~45%. 짧고 통통한 팔다리, 발은 단순한 덩어리
- 크고 둥근 눈, 단순한 하이라이트, **볼터치 스티커**(분홍 타원)
- **붉은 갈색 계열 컬러 라인**, 평평한 2~3단 셀 셰이딩, 채도 있는 파스텔 색감
- 엘프: **뾰족한 귀가 옆으로 뻗음**, 단신, **손가락 4개**(엄지 + 3)

3D 해석 규칙:
- 셰이딩은 three.js 툰 머티리얼(3단)과 인버티드 헐 아웃라인으로 **런타임에서** 입힌다 (`src/art/toon.ts`). Blender에서는 **색과 형태만** 만든다. 노멀맵이나 PBR 질감에 기대지 않는다.
- 아웃라인 색은 머티리얼 바탕색을 어둡게 한 색이 자동으로 쓰인다. 필요하면 `cb.mat(..., line="#5a2e2e")`로 지정한다.
- 귀여운 캐릭터에 **진지한 군용 장비**를 입힌다. 이 대비가 작품의 톤이다. 장비는 단순화하되 뭉개지 않는다.
- **베끼지 않기**
  - 원작 일러스트를 트레이싱한 듯한 형태나 문양, 로고, 게임 UI 요소를 그대로 옮기지 않는다.
  - **예외: 엘프 로고** (사용자 결정, 2026-11-01). 원작 엘프들의 로고는 그대로 쓴다. 원본 벡터는 `public/ui/elf_logo_mono.svg`다.
    - 모나티엄 스튜디오 로고(인트로)
    - R41 무기와 드론의 엠블럼 자리
    - 교주 차원 병기(엘피니아·모나티엄 제식)의 엠블럼 자리
    - 노획 미군 화기에는 넣지 않는다.
  - **예외: 에르피엔 깃발** (사용자 결정, 2026-11-02). 깃발은 원작 에르피엔 군기(짙은 초록 바탕 + 노란 나비)를 그대로 쓴다. 근거와 도안은 `docs/art/erpien.md` 5장, 공용 키트는 `art/blender/lib/erpien_flag.py`(런타임 텍스처 `src/game/cinematic/erpienFlag.ts`).
    - 큰 군기, 세로 현수막, 군중 손깃발, 탑·가로등·천막의 작은 깃발, 원경 깃발. 깃발 줄 삼각기는 군기의 초록·노랑
    - 정체 모를 임의 도안의 깃발은 만들지 않는다. 새 깃발은 키트 함수(`standard`, `banner`, `hand_flag`, `far_flag`)로 낸다.
    - 요정 왕국의 나비 문장도 같은 도안이다(2026-11-03): 경비대 샤코·부츠 원판·폴랑 망토, 네르 부츠·브로치, 머스킷 엠블럼, 성전군 보급 상자 스텐실, 퍼레이드 차 메달·보닛 장식, 대관식 바닥·단·아치·성문 문장과 지붕 조형. 키트의 `emblem()`(면에 그림), `badge()`(두께 있는 배지·조형), 도안 `outline()`·`edge_outline()`·`STROKES`(곡면 부조)로 낸다. 다시 그린 나비는 쓰지 않는다.
  - 원작 인물은 머리색, 헤어스타일, 상징 소품, 색 배합 같은 **식별 요소만 유지**하고 의상은 전시 상황에 맞게 재해석한다.
  - 오리지널 인물(리타, 분대원, R41 지휘부)은 완전히 새로 디자인한다.
- **저퀄 금지**
  - 실루엣이 한눈에 읽혀야 한다.
  - 하드 엣지에는 베벨, 곡면에는 충분한 분할이나 서브디비전을 쓴다.
  - 디테일은 1차(큰 형태), 2차(파츠), 3차(나사, 스티치, 끈, 테이프) 세 층을 모두 갖춘다.
  - 파츠가 공중에 뜨거나 서로 관통한 게 보이면 안 된다.

## 2. 단위와 좌표

| 항목 | 규칙 |
|---|---|
| 단위 | 1 BU = 1 m |
| 업 축 | Blender Z-up. glTF로 내보낼 때 Y-up으로 바뀜 (`cb.export`가 처리) |
| 캐릭터 | 발바닥 z=0, XY 원점 중심, **-Y를 바라봄**(Blender 정면 뷰에서 얼굴이 보임). 캐릭터의 왼쪽 = +X. three.js에서는 +Z를 바라봄 |
| 무기 | **총구가 +Y**, 원점 = **오른손 파지점**(권총 손잡이 중앙). three.js에서는 총구가 -Z |
| 이름 | 점(.) 금지 (three.js가 지움). 좌우는 `_L` / `_R` (캐릭터 기준 왼쪽 = +X) |

### 체격 기준 (엘프 성인)
원작 SD 스탠딩 6장을 실측해 정했다(`docs/art/reference-notes.md` 1장). 군인 엘프는 두개골 기준 2.65~2.8등신이고, 헬멧이나 머리숱을 넣으면 2.4~2.5등신이다.
- 키(정수리까지, 귀와 머리카락 제외) **1.20 m**
- 머리 높이(턱~정수리) **0.45 m**, 2.67등신. 머리카락을 넣은 겉보기는 약 0.49 m, 2.45등신
- 눈높이(두 눈 중심) **0.90 m**, 턱 위로 머리 높이의 1/3 지점. 1인칭 카메라는 이 높이의 `socket_eye`에 놓인다(6장)
- 턱 0.75 m, 어깨 관절 0.686 m, 가랑이 0.298 m, 발목 0.062 m. 얼굴 폭은 머리 높이와 거의 같은 0.477 m

정확한 값과 체형 파라미터는 엘프 베이스 키트(`art/blender/lib/elf.py`, `docs/art/ELF_KIT.md`)가 최종 기준이다.

## 3. 파일 배치

| 무엇 | 어디 |
|---|---|
| 모델 스크립트 (원본) | `art/blender/<분류>/<이름>.py` |
| 공용 라이브러리 | `art/blender/lib/cb.py` (기본 도구, **수정 금지**: 필요한 수정은 보고), `art/blender/lib/elf.py` (엘프 키트) |
| 결과물 | `public/models/<분류>/<이름>.glb` (`cb.export("<분류>/<이름>.glb")`) |
| 분류 | `characters/` (원작·오리지널 인물), `enemies/` (R41 병력), `viewmodels/` (1인칭 팔), `weapons/elfinia/`·`weapons/monatium/` (교주 차원 제식), `weapons/us/` (미군 노획), `weapons/r41/` (R41 노획), `drones/`, `props/` |
| 레퍼런스 이미지 | **프로젝트 밖** 스크래치패드에만 저장한다. 원작 이미지는 저장소에 넣지 않는다 |

## 4. 작업 순서와 검증

```bash
npm run model -- art/blender/weapons/us/m4a1.py           # Blender 헤드리스 실행 → .glb
npm run shot -- weapons/us/m4a1.glb --views side,34,top,muzzle   # 2x2 시트 PNG (shots/)
npm run shot -- characters/rita.glb                        # 기본: front,34,side,back
npm run shot -- characters/rita.glb --focus head --views front,34   # 특정 노드 확대
npm run shot -- weapons/us/m4a1.glb --mode fp --fp 0.13,-0.15,-0.28 # 1인칭 배치
npm run shot -- weapons/us/m4a1.glb --mode fp --arms viewmodels/rita_fp_arms.glb
npm run shot -- characters/rita.glb --mode fpbody --pitch -60 --arms viewmodels/rita_fp_arms.glb --weapon weapons/us/m4a1.glb
npm run dev                                                # 브라우저 갤러리 (사람용)
```
- `--mode fp`: 무기의 `fpOffset`(위치)과 `fpRot`("x,y,z" 도, 옆면이 보이게 살짝 돌리는 각도) 커스텀 속성을 자동으로 쓴다. `--fp`와 `--fprot`으로 덮어쓸 수 있다.
- `--mode fp --ads 1`: 정조준 시점. `sight_eye`가 카메라 위치에 온다. 레티클이나 가늠쇠가 화면 중앙에 와야 한다.
- 시트 모드에서는 원점 아래로 내려가는 모델(무기 등)이면 바닥 원판이 자동으로 숨겨진다. `--floor 0/1`로 강제할 수 있다.
- `--mode fpbody`: 1인칭 몸 보기. `fpHide` 메시를 숨기고 `socket_eye`에서 `--pitch`도(음수 = 아래)로 내려다본다. `--arms`와 `--weapon`은 카메라에 붙는 뷰모델이다. `--hide head`처럼 숨길 그룹을 고를 수 있다(기본 `head,arms`).

### 1인칭 몸 (하이브리드)
- 1인칭 화면은 **뷰모델**(1인칭 전용 팔 + 무기, 카메라에 붙음)과 **자기 전신 모델**(머리와 팔을 숨김)을 함께 그린다. 아래를 보면 가슴 장비, 벨트, 다리, 군화가 보인다.
- 캐릭터 모델은 `socket_eye`(head 본, 두 눈 사이)와 메시 커스텀 속성 `fpHide`(`"head"` 또는 `"arms"`)를 갖춘다. 자세한 규약은 6장과 `docs/art/ELF_KIT.md`.
- 1인칭 팔의 소매와 장갑은 전신 모델의 복장과 반드시 같아야 한다.
- 가능한 뷰 이름: `front back side left right top bottom 34 34r 34b muzzle low`
- 스크린샷은 **반드시 직접 열어 보고** 품질을 판단한 뒤 고친다. 이 과정을 반복한다.
- 스크립트에서 오류가 나면 `npm run model`이 종료 코드 1로 끝나고 파이썬 트레이스백을 보여준다.

## 5. Blender 쪽 규칙 (`cb` 사용)

```python
import os, sys
sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb
cb.reset()
skin = cb.mat("skin", "#ffe3d6")
eye_hl = cb.mat("eye_hl", "#ffffff", unlit=True)        # UNLIT_ → 조명 없는 단색
cb.box("receiver", size=(0.03, 0.2, 0.05), loc=(0, 0.05, 0.02), bevel=0.003, material=gunmetal)
cb.export("weapons/us/m4a1.glb", props={"outline": 0.0025, "fpOffset": "0.13,-0.15,-0.28"})
```
- 예제: `art/blender/examples/example_crate.py`
- `cb`의 도구: `box`, `cylinder`, `sphere`, `profile_extrude`(2D 외곽선 돌출, 총기 옆모습에 유용), `from_pydata`, `add_bevel`, `subsurf`, `mirror_x`, `solidify`, `smooth`, `join`, `armature`, `parent_to_bone`, `skin_to`, `empty`, `export`
- bmesh와 numpy를 직접 써도 된다 (Blender 5.2, Python 3.13, numpy 2.3).
- **커스텀 속성** (glTF extras → three.js `userData`)
  - `outline`: 아웃라인 두께(m). 자식에게 상속된다. 기본값 0.006
    - 캐릭터 0.005~0.007, 3인칭 무기 0.003, 1인칭 전용 0.0015~0.0025
  - `noOutline`: 1이면 아웃라인을 생략한다 (얼굴 스티커, 눈, 작은 데칼)
  - `fpOffset`: 무기 루트에 넣는 1인칭 배치 권장값 `"x,y,z"`
- 머티리얼 이름이 `UNLIT_`로 시작하면 조명 없는 단색이 된다 (눈 하이라이트, 화면, LED, 발광부).
- **겹친 면 금지**: 색이 다른 두 면을 같은 평면에 겹치지 않는다. 엔진은 표준 깊이 버퍼(로그 깊이 꺼짐)라 같은 깊이 편향 등급(`_fine` > `_detail` > 기본) 두 면은 몇 mm로는 30~50 m부터 깜빡인다. 테·문틀은 벽보다 튀어나오게, 데칼 층은 맨 아래를 약한 등급에, 같은 등급끼리는 보는 거리에 맞춰 띄운다. 규칙과 점검 도구(`node scripts/zfight-audit.mjs <glb>`)는 `docs/art/zfight-audit.md` 7장.
- **드로우콜**: 움직이지 않는 파츠는 마지막에 `cb.join`으로 머티리얼별, 강체 파츠별로 합친다. 움직이는 파츠(탄창, 노리쇠, 방아쇠, 뚜껑, 회전부)는 따로 남기고 이름을 붙인다.

## 6. 캐릭터 규약

캐릭터는 **엘프 키트**(`art/blender/lib/elf.py`)로 만든다. API와 예제는 `docs/art/ELF_KIT.md`에 있다.
- **본 이름** (모두 소문자 + `_L/_R`)
  - `root > hips > spine > chest > neck > head`
  - `chest > shoulder_L > upperarm_L > forearm_L > hand_L`
  - `hips > thigh_L > shin_L > foot_L`
  - 손가락: `thumb_01_L, thumb_02_L, f1_01_L, f1_02_L, f2_…, f3_…` (엄지 + 3 = 4개, f1이 검지 쪽)
  - 귀: `ear_L, ear_R`. 머리 꼬리(선택): `hair_tail_01/02`
- **본 축**: 로컬 +Y = 본 방향, +Z = 앞(손·손가락은 손바닥 쪽). 굽힘은 대부분 로컬 +X 회전이고, 무릎만 −X다. 팔을 옆으로 들 때는 왼팔 +Z, 오른팔 −Z다. 표는 ELF_KIT.md 3장.
- **소켓** (빈 오브젝트를 본에 부착)
  - `socket_hand_R`(주무기), `socket_hand_L`: three.js에서 −Z = 손가락 방향, +Y = 엄지 쪽. 7장 무기 규약과 같으므로 무기 루트를 그대로 자식으로 붙인다
  - `socket_back`(등 거치), `socket_hip_R`(권총)
  - `socket_eye`(head 본): 1인칭 카메라 위치. 두 눈 사이 중앙 높이이고 얼굴 표면에서 0.04 m 안쪽이다. SD 머리는 얼굴이 가슴보다 0.17 m 앞이라 표면에 두면 내려다봐도 몸이 안 보인다(ELF_KIT.md 7장)
- **레스트 포즈**: A 포즈. 팔이 수평에서 40° 아래, 손바닥은 몸 쪽, 엄지는 앞을 향한다.
- **표정**: 얼굴 파츠의 셰이프 키(모프 타깃). 최소 세트는 `blink`, `serious`, `surprised`, `pained`, `smile`이다. 얼굴 노드의 자식 메시(본체 + UNLIT 하이라이트) 모두에 같은 값을 넣는다. 아웃라인 헐은 모프를 따라간다.
  - 교정 키 `blink_<표정>`이 함께 있다. 모프는 더해지므로 깜빡임과 다른 표정을 겹치면 눈꺼풀이 어긋난다. 런타임 규칙은 `blink_`로 시작하는 모든 키 `blink_<X>`에 `blink × <X>`를 넣는 것이다. 인물별로 추가한 표정에도 그대로 적용된다(ELF_KIT.md 6장).
- **머리카락(헤어 v2)**: 머리 덩어리는 한 장의 매끈한 셸이고, 다발은 끝 쪽에서만 갈라진다. 긴 머리·꼬리·땋은 머리는 흔들림 본(`hair_back_*`, `hair_side_*`, `hair_tail_*`, `hair_braid_*`)을 쓴다. 자세한 내용은 ELF_KIT.md 8장, 원작 분석은 reference-notes.md 8장.
- **스키닝**: 자동 웨이트(bone heat)는 쓰지 않는다. 키트가 파츠를 만들 때 계산한 웨이트를 넣는다. 단단한 장비도 붙는 지점의 웨이트(한 본 100% 포함)로 스키닝해 같은 메시에 합친다. 예외는 셰이프 키가 있는 얼굴로, head 본에 강체로 붙인다. 근거는 ELF_KIT.md 4장.
- **최종 메시와 1인칭 숨김 태그 `fpHide`**
  - `<이름>_body`: 몸통, 다리, 군화, 벨트, 몸 장비 (태그 없음)
  - `<이름>_arms`: 어깨 아래 팔, 소매, 장갑, 손 → `fpHide="arms"`
  - `<이름>_head`: **목**, 머리, 귀, 머리카락, 모자·헬멧 → `fpHide="head"`
  - `<이름>_hair`: 머리카락 셸·꼬리 → `fpHide="head"`, `outline=0.0035`(몸보다 얇은 라인). 모프 없음
  - `<이름>_hair_in`: 머리카락 속층·광택 → `fpHide="head"`, `noOutline=1`
  - `<이름>_face`: 얼굴 파츠 → `fpHide="head"`, `noOutline=1` (모프는 얼굴 메시에만 싣는다)
  - 직접 만든 파츠도 이 셋 중 하나로 들어가야 한다(`e.add(obj, group=…)` 또는 anchor가 자동 결정). 목을 head에 넣는 이유는 내려다볼 때 목 단면이 보이지 않게 하기 위해서다.
- **드로우콜**: 키트 기본(`merge=True`)은 불투명 머티리얼을 정점색으로 합쳐 머티리얼 1개 + UNLIT만 남긴다. 라인색은 원작처럼 공통 붉은 갈색(`#4a2229`) 하나다.
- **1인칭 팔 뷰모델**: 같은 키트, 같은 소매·장갑 함수와 색으로 만들고 `finalize(only=("arms",))`로 팔 그룹만 내보낸다.

## 7. 무기 규약

- 원점 = 오른손 파지점, 총구 +Y (three.js에서 -Z)
- **앵커** (빈 오브젝트): `muzzle`(총구 끝), `grip_support`(왼손 위치), `sight_eye`(정조준 시 눈 위치, 가늠자 뒤), `eject`(탄피 배출구), `mag_well`
- **움직이는 파츠** (별도 오브젝트): `mag`, `bolt`(또는 `charging_handle`, `slide`), `trigger`, 필요 시 `pump`, `cylinder` 등
- 실제 크기 기준으로 약간 두툼하게 단순화한다. 엘프에게 인간의 총은 크다. 이 체격 차이가 볼거리다.

## 8. 성능 예산 (삼각형)

| 종류 | 상한 | 머티리얼 |
|---|---|---|
| 주인공 3인칭 (리타) | 25k | ≤ 12 |
| 1인칭 팔 | 15k | ≤ 8 |
| 원작 인물 / 분대원 | 18k | ≤ 12 |
| R41 병사 (다수 등장) | 15k (원거리 LOD는 추후) | ≤ 10 |
| 1인칭 무기 | 12k | ≤ 8 |
| 드론 | 5k | ≤ 6 |
| 소품 | 3k | ≤ 4 |

## 9. 진영별 색 방향

- **교주 차원 모나티엄 진압반**: 레퍼런스 조사 후 `docs/art/reference-notes.md`에 확정
- **엘피니아 군 전투복** (프롤로그, R41 병력의 바탕): 원작 **알레트, 타이다, 레이지의 전투복**이 기준이다. 정복(헤일리(멀쩡) 테마극장 복장)과 다르다.
- **R41**: 엘피니아·모나티엄 디자인 언어를 **더 차갑고 어둡게 비튼 거울상**. 무기 쪽에서 `docs/art/r41-style.md`로 확정한다.
- **노획 미군 물자**: OD 그린, 코요테 탄, 블랙. 모나티엄 창고 관리 태그나 테이프 같은 엘프식 개조 흔적을 약간 더한다.
