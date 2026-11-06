# 엘프 베이스 키트 (`art/blender/lib/elf.py`)

모든 엘프 캐릭터(리타, 분대원, 원작 카메오, R41 병사, 1인칭 팔)를 같은 몸·리그·얼굴·화풍으로 만드는 키트다.
비율과 화풍의 근거는 `docs/art/reference-notes.md`에 있다.

- 데모: `art/blender/characters/_kit_base.py`(바디슈트), `_kit_elfinia_soldier.py`(엘피니아 전투복 병사), `_kit_posetest.py`(본 회전 확인)
- 결과물: `public/models/characters/_kit_*.glb`

---

## 1. 빠른 시작

```python
import os, sys
sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb, elf

cb.reset()
e = elf.Elf("rita")                          # 몸 + 리그 + 머리 + 귀 + 소켓이 바로 생긴다
e.face(eye_color="#5b7fb8")                  # 눈·눈썹·입·볼터치 + 표정 셰이프 키 5종
h = e.hair("#7a5140")                        # 머리카락 도구
h.cap(); h.bangs(); h.sides(); h.back(length=0.10)

jacket = elf.mat("rita_jacket", "#a3ada1")   # cb.mat과 같다
e.shirt(jacket, collar="stand")              # 몸판
e.sleeves(jacket, cuff=(elf.mat("rita_cuff", "#7f8a80"), 0.022, 0.0045))
e.pants(elf.mat("rita_pants", "#939e98"), blouse=0.02)
e.boots(elf.mat("rita_boots", "#58535d"), sole=(elf.mat("rita_sole", "#2f2b31"), 0.016))
e.belt(elf.mat("rita_belt", "#4a4149"), buckle=elf.mat("rita_metal", "#cfcac4"))

e.finalize()                                 # 맨살 생성 → 그룹별 합치기·스키닝 → 삼각형 보고
e.export("characters/rita.glb")              # outline 0.006 기본
```

```bash
npm run model -- art/blender/characters/rita.py      # [elf] 줄에 파츠별 삼각형 수가 찍힌다
npm run shot -- characters/rita.glb
npm run shot -- characters/rita.glb --focus rita_face --views front,34
npm run shot -- characters/rita.glb --mode fpbody --pitch -60
```

순서: `Elf()` → `face()` → `hair()` → 옷·장비 → `finalize()` → `export()`.
옷은 아무 순서로 불러도 된다. 맨살은 `finalize()` 때 옷에 덮이지 않은 부분만 만들어진다.

---

## 2. 몸 파라미터 `Elf(name, **kw)`

| 인자 | 기본 | 뜻 |
|---|---|---|
| `height` | 1.20 | 정수리까지 키(m), 귀·머리카락 제외 |
| `head` | 0.45 | 턱~정수리(m). 2.67등신. 머리카락까지 넣으면 약 2.45등신 |
| `head_w`, `head_d` | 1.06, 0.92 | 머리 폭과 깊이 (`head`에 대한 비율) |
| `cheek` | 0.10 | 볼 부풂 (0~0.2) |
| `shoulders`, `hips` | 1.0 | 어깨·골반 폭 배율 |
| `limb` | 1.0 | 팔다리 굵기 배율 |
| `arm`, `leg` | 1.0 | 팔·다리 길이 배율 |
| `chest` | 0.15 | 흉곽 앞뒤 두께 (0~1) |
| `bust` | 0 | 가슴(흉부) 형태 (0~1). 0이면 지금까지와 같은 평평한 몸통이다. 아래 '체형: bust' 참고 |
| `apose` | 40 | A 포즈 팔 각도 (수평에서 아래로, 도) |
| `ear_len`, `ear_width` | 0.095, 0.060 | 귀 길이·폭(m) |
| `ear_angle`, `ear_sweep` | 14, 12 | 귀를 위로 든 각, 뒤로 젖힌 각(도) |
| `ear_inner` | True | 안쪽 귀 음영 판 |
| `skin` | `#fff0ea` | 피부색 (hex 또는 머티리얼) |
| `line` | `#4a2229` | 라인색 (merge 시 공통) |
| `segs` | 1.0 | 전체 분할 배율. 다수 등장 단역은 0.7~0.85 |
| `hand_q` | 1.0 | 손 분할 배율. 1인칭 팔은 1.2, 3인칭 단역은 0.6~0.8 |
| `eye_depth` | 0.04 | `socket_eye`를 얼굴 표면에서 머리 안쪽으로 넣는 깊이(m). 7장 참고 |

기본 체격(m): 정수리 1.20, 눈 0.90, 턱 0.75, 어깨 관절 0.686(좌우 ±0.136), 고관절 0.348, 가랑이 0.298, 무릎 0.188, 발목 0.062.
`height`를 바꾸면 턱 아래 몸 전체가 같은 비율(`e.k`)로 줄거나 늘어난다. 옷과 장비 치수도 `e.k`를 곱해서 쓴다.

**체형: `bust`** (2026-11-02)
- 원작 스탠딩·SD에서 성인 체형으로 가슴 볼륨이 보이는 인물에게만 준다. 아이 체형 인물과 오리지널 인물은 0으로 둔다. 인물별 값과 원작 근거는 `docs/art/characters-cameo3.md` '체형' 절에 모은다.
- 모양: 정면 ±31°에 중심을 둔 두 둥근 볼륨이 가운데에서 이어진 한 덩어리다. 위쪽은 쇄골 아래부터 완만하게 올라오고, 아래쪽은 더 둥글게 닫힌다. 꼭짓점 높이는 `e.bust_z`(고관절~어깨의 71%)다. `bust=1`이면 꼭짓점이 `BUST_DEPTH`(0.052 m × `e.k`)만큼 나온다.
- 옷 층: 몸에서 띄운 거리(`off`)가 클수록 가운데 골이 메워지고(맨살 62% → 옷 86%) 아래쪽이 천처럼 완만하게 떨어진다. 몸에 붙는 옷도 골을 파지 않는다. 과장하지 않고 SD 툰 화풍 안에서 단정한 형태만 낸다.
- 따라가는 것: 맨살, `shirt`(앞여밈·단추 포함), `pants` 윗단, `torso_stations`로 만든 모든 관(`loft` station의 `disp`), `ring("torso", …)` 가슴띠(`band(disp=)`), `torso_point`/`anchor`를 쓰는 파우치·패치·끈·장비, cameo `Shell`(앞트임 재킷·코트·원피스). `torso_point`는 볼륨 곡면의 법선을 돌려준다.
- 직접 만든 몸통 파츠는 `e.bust_off(z, angle, off)`(바깥으로 더할 두께, m)를 더하면 같은 면을 따른다.
- 0이면 어떤 경로도 값을 더하지 않는다. 기존 모델은 같은 스크립트로 다시 만들어도 바이트 단위로 같다(rita, `_kit_elfinia_soldier`로 확인).

**표면 좌표 도우미** (장비를 직접 배치할 때)
- `e.torso_point(z, angle, off)` → (점, 법선). angle 0=정면, +90=캐릭터 왼쪽(+X), 180=등
- `e.limb_point("leg_R", t, angle, off)`. t는 팔다리 길이 비율(0=어깨·고관절, 1=손목·발목)
- `e.head_point(az, el, off)`. az 0=정면, 90=왼쪽, el은 위로 +도
- `e.anchor(at)` → `Anchor`(위치, 법선, 위 방향, 웨이트, fpHide 그룹). at은 `("torso", z, angle[, off])`, `("leg_L", t, angle[, off])`, `("arm_R", t, angle[, off])`, `("head", az, el[, off])`
- 높이 상수: `e.chest_z`, `e.waist_z`, `e.hipj_z`, `e.shoulder_z`, `e.torso_top`, `e.chin`, `e.eye_z()`

---

## 3. 리그

### 본 (38개 + 선택)

```
root
└ hips ─ spine ─ chest ─ neck ─ head ─ ear_L, ear_R, (hair_*)
  │               └ shoulder_L ─ upperarm_L ─ forearm_L ─ hand_L ─ thumb_01_L ─ thumb_02_L
  │                                                              ├ f1_01_L ─ f1_02_L   (검지 쪽)
  │                                                              ├ f2_01_L ─ f2_02_L
  │                                                              └ f3_01_L ─ f3_02_L   (새끼 쪽)
  ├ thigh_L ─ shin_L ─ foot_L
  └ (오른쪽 _R 대칭)
```
- 레스트 포즈는 A 포즈다(팔이 수평에서 40° 아래). 손바닥은 몸 쪽을 향하고 엄지는 앞을 향한다.
- `h.ponytail()`, `h.twintails()`는 `hair_tail_01/02`(또는 `hair_tail_L_01…`) 본을 더한다. 직접 더할 때는 `e.add_bone(name, head, tail, parent)`.

### 회전 규칙 (Blender 액션과 three.js 코드 모두 같다)

본 로컬 축: **+Y = 본 방향(자식 쪽)**, **+Z = 앞**(손·손가락은 손바닥 쪽, 발·귀는 위), X = Y × Z.
three.js에서 확인했다: glTF로 나가도 축이 그대로다(`bone.rotation.x` = Blender 로컬 X).

| 본 | 로컬 회전(도) | 결과 |
|---|---|---|
| `spine`, `chest`, `neck`, `head` | +X | 앞으로 숙임 |
| `head` | +Y | 캐릭터 왼쪽으로 고개 돌림 |
| `head` | +Z | 오른쪽 귀를 어깨 쪽으로 기울임 |
| `upperarm_*` | +X | 팔을 앞으로 들기 |
| `upperarm_L` / `upperarm_R` | **+Z / −Z** | 팔을 옆으로 들기 (좌우 반대 부호) |
| `forearm_*` | +X | 팔꿈치 굽힘 |
| `hand_*` | +X | 손목을 손바닥 쪽으로 |
| `thumb_*`, `f1~f3_*` | +X | 손바닥 쪽으로 말기 (주먹: `_01` 70°, `_02` 80°, 엄지 25°/40°) |
| `thigh_*` | +X | 다리를 앞으로 들기 |
| `shin_*` | **−X** | 무릎 굽힘 |
| `foot_*` | +X | 발끝 들기 |
| `ear_*` | +X | 귀 끝을 위로 |
| `hair_tail_*` | +X | 꼬리를 위·앞으로 |

포즈 확인용 액션은 `e.pose({"upperarm_L": (70, 0, 0), ...})`로 만든다. 확인 명령은 `npm run shot -- characters/_kit_posetest.glb --mode single --view 34`.

### 소켓 (빈 오브젝트, 본에 부착)

| 소켓 | 본 | 위치 | three.js 방향 |
|---|---|---|---|
| `socket_eye` | head | 두 눈 사이 중앙 높이(0.90 m), 얼굴 표면에서 `eye_depth` 안쪽 | 회전 없음 |
| `socket_hand_R` | hand_R | 주먹 안쪽 (손바닥에서 2.6 cm) | **−Z = 손가락 방향(총구)**, **+Y = 엄지 쪽(총 위)** → 무기 루트를 그대로 자식으로 붙인다 |
| `socket_hand_L` | hand_L | 같은 위치 (왼손) | 같은 규칙 |
| `socket_back` | chest | 등 뒤 5 cm | 회전 없음 |
| `socket_hip_R` | hips | 오른쪽 골반 바깥 3 cm | 회전 없음 |

---

## 4. 스키닝 방식과 근거

**결정: 모든 파츠를 '계산한 웨이트로 스키닝'한다. 자동 웨이트(bone heat)와 `parent_to_bone` 강체는 쓰지 않는다(얼굴만 예외).**

| 방식 | 헤드리스 안정성 | 관절 변형 | 드로우콜 | 결론 |
|---|---|---|---|---|
| `ARMATURE_AUTO`(bone heat) | 메시가 겹치거나 떨어져 있으면 "failed to find solution"으로 실패하고, 결과가 실행마다 달라질 수 있다 | 좋음 | 보통 | 안 씀 |
| `parent_to_bone` 강체 | 안정 | 관절이 갈라지거나 겹쳐 보인다 | 파츠 수만큼 늘어남 | 얼굴만 |
| **계산 웨이트 (채택)** | 항상 같은 결과, 실패 없음 | 관절 앞뒤로 부드럽게 섞음 | 그룹당 1메시 | **채택** |

- 몸·옷 관은 본 경로(`Chain`)를 따라 만들기 때문에 각 단면의 위치 t를 안다. 관절 앞뒤 32% 구간에서 두 본을 smoothstep으로 섞는다. 팔과 다리의 시작부는 `shoulder_*`·`hips`와 섞는다.
- 몸통은 높이에 따라 hips → spine → chest로 섞고, 어깨 위 바깥쪽은 `shoulder_*`, 가랑이 아래쪽은 `thigh_*`로 섞는다(`_torso_wfn`).
- 단단한 장비(버클, 파우치, 패치)는 붙는 지점(`anchor`)의 웨이트를 정점 전체에 그대로 쓴다. 결과는 강체처럼 움직이면서도 같은 메시에 합쳐진다.
- 손가락은 손가락마다 `hand → _01 → _02` 경로 웨이트, 귀는 뿌리에서 `head → ear_*`로 섞는다.
- 얼굴(`face`)은 head 본에 강체로 부착한다. 셰이프 키가 있는 메시에 Armature 모디파이어를 같이 쓰면 glTF 내보내기에서 모디파이어 적용과 충돌할 수 있어서다.
- `e.add(obj, bone="chest")`로 직접 만든 메시를 그 본에 100% 스키닝해 합칠 수 있다. 움직이는 장비를 따로 남기려면 `keep=True`를 준다.

검증: `_kit_posetest.glb`를 three.js(`--mode single`)에서 보면 팔·팔꿈치·손목·주먹·고개·허리·다리·무릎·귀·포니테일이 모두 따라온다. 표정 모프(smile)도 함께 확인했다.

---

## 5. 최종 메시 구조와 드로우콜

`finalize()`가 만드는 것:

| 노드 | 내용 | 스키닝 | 커스텀 속성 |
|---|---|---|---|
| `<이름>_body` | 몸통, 다리, 발/군화, 벨트, 파우치, 끈, 몸판 옷 | 계산 웨이트 | — |
| `<이름>_arms` | 위팔부터 손끝까지: 팔, 소매, 손/장갑, 팔 패치 | 계산 웨이트 | `fpHide="arms"` |
| `<이름>_head` | 목, 머리, 귀, 머리카락, 헬멧·모자, 머리 장비 | 계산 웨이트 | `fpHide="head"` |
| `<이름>_hair` | 머리카락 셸, 꼬리, 땋은 머리, 바보털 (모프 없음) | 계산 웨이트 (head + 흔들림 본) | `fpHide="head"`, `outline=0.0035` |
| `<이름>_hair_in` | 머리카락 속층, 광택 | 계산 웨이트 | `fpHide="head"`, `noOutline=1` |
| `<이름>_face` | 눈·눈썹·입·볼터치, 셰이프 키 | head 본에 부착 | `fpHide="head"`, `noOutline=1` |

- **merge=True(기본)**: 불투명 툰 머티리얼의 색을 정점색(`COLOR_0`)으로 굽고 머티리얼 하나(`<이름>_toon_vc`, `lineColor` 공통)로 합친다. UNLIT, 발광, 반투명 머티리얼은 따로 남는다.
  → 캐릭터 하나가 **보통 메시 6개(body, arms, head, hair, hair_in, face) × 머티리얼 1~2개**, 즉 드로우콜 7~8개(+아웃라인, hair_in·face 제외)다. 원작처럼 라인도 한 색이 된다.
- 머티리얼별 라인색이 꼭 필요하면 `finalize(merge=False)`를 쓴다. 이때 머티리얼 수가 예산(12개)을 넘지 않게 한다.
- `finalize(only=("arms",))`는 한 그룹만 남긴다(1인칭 팔). 리그와 소켓은 그대로 남는다.
- `[elf] <이름> tris=… hair=… helmet=…` 줄에 파츠별 삼각형 수가 찍힌다. 예산을 맞출 때 쓴다.

---

## 6. 얼굴과 표정 `e.face(**kw)`

| 인자 | 기본 | |
|---|---|---|
| `eye_color` | `#5a7fb5` | 홍채색. 짙은 띠, 밝은 반달, 동공 색은 자동으로 만든다(`iris_dark`, `iris_light`, `pupil`로 지정 가능) |
| `eye_size`, `eye_spacing`, `eye_height` | 1, 1, 0 | 크기 배율, 간격 배율, 높이 이동(m) |
| `lash`, `brow` | `#3a2027`, lash와 같음 | 속눈썹·눈썹 색 (머리색을 어둡게 해서 주면 자연스럽다) |
| `brow_th` | 1.0 | 눈썹 굵기 배율 |
| `mouth_color`, `tongue` | `#9a3b45`, `#f2898c` | |
| `blush`, `blush_size`, `blush_lines` | `#f9aca8`, 1, 0 | 볼터치. 빗금은 기본 0 (reference-notes 2장) |
| `lower_lash` | True | 아래 속눈썹 짧은 선 |
| `base` | — | 무표정 자체를 바꾸는 사전. 예: `{"eye": {"top": 0.022}}` → 기본이 졸린 눈 |
| `expr` | — | 표정 추가·덮어쓰기. 예: `{"wink_L": {...}}` |

**모프 타깃 이름** (glTF 순서 고정)
- 표정: `blink`, `serious`, `surprised`, `pained`, `smile`
- 말하기: `talk`(입만 연다), `talk_o`(오 모양). 눈·눈썹은 그대로다
- 시선: `look_L`, `look_R`, `look_up`, `look_down`. 캐릭터 기준 방향이고 두 눈이 같이 움직인다. 홍채·동공·하이라이트가 눈 윤곽 안에서 움직인다
- 교정 키: `blink_serious`, `blink_surprised`, `blink_pained`, `blink_smile`, `blink_look_L`, `blink_look_R`, `blink_look_up`, `blink_look_down`. 눈을 건드리지 않는 표정(talk)에는 없다
- 모프는 더해진다. 그래서 `blink`와 다른 표정을 함께 1로 두면 눈꺼풀이 겹친다(웃으면서 깜빡일 때 등).
- 교정 키는 '그 표정으로 눈을 감은 모양'에서 두 키의 합을 뺀 차이다. **런타임 규칙: `blink_`로 시작하는 모든 모프 키 `blink_<X>`에 대해 `blink × <X>`**. 인물이 `expr=`로 추가한 표정(예: alert, smirk)도 같은 규칙으로 처리된다. 예를 들어 smile 1에 blink 1이면 `blink_smile`도 1이고, 결과는 웃는 입에 감은 눈이다.
- `expr=`로 추가한 표정도 교정 키가 자동으로 생긴다(이름이 `blink`로 시작하거나 `close`를 쓰는 표정은 제외).
- 홍채 위쪽은 모든 표정에서 윗눈꺼풀에 잘리도록 둔다(`iris.cz + iris.ry` ≥ 윗눈꺼풀 높이). 사이에 흰 띠가 생기면 속눈썹이 두 번째 눈썹처럼 떠 보인다. `base=`나 `expr=`로 눈을 바꿀 때 이 조건을 지킨다.
- 뷰어 확인: `npm run shot -- characters/<이름>.glb --focus <이름>_face --views front --morph smile:1,blink:1,blink_smile:1`

**런타임 규칙 (NPC 대화·시선)**
1. **말하기**: 대사가 나오는 동안 `talk`를 0~1로 빠르게 진동시킨다. 예: `talk = env × (0.55 + 0.45 × sin(2π × 7Hz × t + 잡음))`, `env`는 대사 시작·끝에서 0.08초 페이드다. 둥근 모음(오·우)에서는 `talk` 대신 `talk_o`를 섞는다(`talk_o = env × o`, `talk = env × (1 - o)`). 다른 표정과는 그냥 더한다(smile + talk, serious + talk 모두 자연스럽다).
2. **시선**: 2축 값 `gx, gy ∈ [-1, 1]`(캐릭터 기준 왼쪽 +, 위 +)을 `look_L = max(gx, 0)`, `look_R = max(-gx, 0)`, `look_up = max(gy, 0)`, `look_down = max(-gy, 0)`으로 나눈다. 대각선도 두 축의 합으로 자연스럽다. 머리 회전(head 본)과 함께 쓰면 눈이 먼저, 머리가 뒤따르게 한다.
3. **눈을 가늘게 뜨는 표정과 시선**: 모프는 더해지므로 `smile`, `pained`, `serious`처럼 눈꺼풀이 좁아진 상태에서 시선을 끝까지 주면 홍채가 눈꺼풀 밖으로 조금 나온다. 시선 값에 `(1 - 0.6 × max(smile, pained, serious))`를 곱한다.
4. **깜빡임**: `blink_<X> = blink × <X>`는 시선 키에도 그대로 적용된다(위 `setFace` 예시가 처리한다).

표정 파라미터(`FACE_NEUTRAL`, `FACE_EXPR`)는 사전으로 되어 있다. 눈은 `top/bot/cin/cout/ktop/kbot/tilt_in/tilt_out/lift/close`, 홍채는 `rx/ry/cx/cz/pupil`, 눈썹은 `dz/dx/len/th/ang/arch`, 입은 `w/curve/open/top_arch/wave/dz`다.
모든 표정은 같은 정점 수로 다시 계산되므로 어떤 조합도 셰이프 키가 된다.

**three.js에서 표정 쓰기**: `face` 노드는 머티리얼 수만큼 자식 메시를 갖는다(본체 + UNLIT 하이라이트). **모든 자식에 같은 값을** 넣는다.
```ts
function setFace(root: THREE.Object3D, name: string, w: Record<string, number>) {
  const blink = w.blink ?? 0;
  root.getObjectByName(`${name}_face`)!.traverse((o) => {
    const m = o as THREE.Mesh;
    if (!m.morphTargetDictionary) return;
    for (const [key, i] of Object.entries(m.morphTargetDictionary)) {
      // 규칙: 'blink_'로 시작하는 모든 키 blink_<X> = blink × <X> (인물마다 추가한 표정도 자동으로)
      const v = key.startsWith('blink_') ? blink * (w[key.slice(6)] ?? 0) : (w[key] ?? 0);
      m.morphTargetInfluences![i] = v;
    }
  });
}
setFace(root, 'rita', { smile: 1, blink: 1 });   // 웃으며 눈 감기
```
아웃라인 헐은 같은 influence 배열을 공유한다(`toon.ts`). 얼굴은 `noOutline`이라 헐이 없다.

---

## 7. 1인칭 몸 규약 (하이브리드)

- **숨김 태그 `fpHide`**: `"head"`(목·머리·얼굴·머리카락·귀·모자/헬멧), `"arms"`(어깨 아래 팔·소매·장갑·손). 키트가 그룹을 나눠 자동으로 단다. 직접 만든 파츠는 `e.add(obj, group="head")`나 anchor로 그룹이 정해진다.
- **목은 head 그룹**이다. 내려다볼 때 목 단면이 카메라 안에 보이지 않는다. 몸판 옷의 목 구멍은 평평하게 막혀 있다.
- **socket_eye**: 두 눈 사이 중앙 높이(0.90 m)이고, 얼굴 표면에서 `eye_depth`(기본 0.04 m)만큼 머리 안쪽에 있다.
  - 이유: SD 머리는 얼굴이 가슴 앞면보다 약 0.17 m 앞에 있다. 얼굴 표면(0.012 m 안쪽)에 두면 -60°로 내려다봐도 군화 끝만 보인다. 0.1 m보다 깊으면 가슴 윗면이 화면을 덮는다. 0.04 m가 둘 사이 절충이다.
  - 실측(`_kit_elfinia_soldier`): **-30°** 땅만 보임 · **-60°** 화면 아래에 가슴 탄창 파우치 덮개·단추 · **-80°** 가슴 장비 전체(파우치, 멜빵, 견장, 계급장).
- **보이는 것과 안 보이는 것**: 서 있을 때 벨트·허벅지·군화는 SD 몸통(배와 가슴 장비)에 가려진다. 원작 비율에서 피할 수 없다. 그래서 **가슴 장비를 가슴 높이**(`e.chest_z` 근처)에 두어 내려다보는 시선이 닿게 한다. 다리는 걷거나 앉는 애니메이션에서 앞으로 나올 때 보인다.
- **1인칭 팔 뷰모델**은 같은 키트로 같은 소매·장갑을 입혀 `finalize(only=("arms",))`로 내보낸다(`hand_q=1.2`, outline 0.0015~0.0025). 전신 모델의 옷과 반드시 같은 함수·색을 쓴다.

---

## 8. 머리카락 (헤어 v2) `h = e.hair(color, dark=None, light=None, off=0.028, outline=0.0035, volume=1.0)`

**v1과 다른 점 (2026-11-01, 키트를 쓰는 에이전트는 꼭 읽기)**
- v1은 렌즈 단면 다발을 여러 개 겹쳐서 앞머리가 같은 크기의 톱니로 늘어서고(삐죽삐죽), 단면이 각졌고(뭉텅뭉텅), 다발끼리 깊게 파고든 틈으로 아웃라인 헐이 비집고 나와 검은 쐐기가 생겼다.
- v2는 **머리 덩어리 전체가 한 장의 매끈한 셸**이다. 정수리에서 경도마다 머리 표면을 따라 내려오고, 머리가 가장 넓은 곳부터는 아래로 떨어진다. 셸은 '다발'로 나뉘지만 **끝 쪽에서만 갈라지고**(다발마다 갈라짐 시작 길이가 다름), 위쪽은 한 면으로 이어진다. 다발끼리 서로 파고들지 않아서 쐐기가 생기지 않는다.
- 다발 끝은 `(1-x^p)^(1/p)` 곡선으로 폭과 두께를 유지하다 끝에서만 모인다. 다발마다 폭·길이·갈라짐 깊이·쓸림이 다르다. 경계에는 얕은 결 홈, 가르마에는 낮은 홈이 있다.
- **속층**(`<이름>_hair_in`, 어두운 머리색, `noOutline`)이 다발 사이 틈 뒤를 메운다. 머리 광택(`shine`)도 여기에 붙는다.
- 머리카락 메시는 `<이름>_hair` 노드로 따로 나오고 커스텀 속성 `outline=0.0035`(몸 0.006보다 얇음)를 단다. 둘 다 `fpHide="head"`이고 **모프(셰이프 키)는 없다**(얼굴 메시만 모프).
- 긴 머리(머리가 가장 넓은 곳에서 0.12m 넘게 떨어짐)는 흔들림 본 `hair_back_01..03`(chest 자식)을 만들고, 웨이트는 뿌리 head → 사슬로 섞는다. 고개를 돌려도 등에 남는다. 긴 옆머리는 `hair_side_L/R_01/02`.
- 포니테일·트윈테일·땋은 머리는 매끈한 스윕 볼륨에 본 사슬과 부드러운 웨이트를 쓴다. 뿌리는 셸 안에 묻고 묶음 띠로 덮는다.

**API 호환**
- 함수 이름과 기존 인자는 그대로다. 에러는 나지 않는다.
- `bangs/sides/back/ponytail/...`은 이제 **사양만 기록**하고, 실제 기하는 `h.done()`(finalize가 부름)에서 한 번에 만든다.
  - 그래서 v1처럼 `len(h.buf.f)`로 방금 만든 면 범위를 잡아 색을 바꾸는 방식(예: `cameo.recolor`)은 효과가 없다. v2에서는 `h.bangs(mat=...)`, `h.sides(mat=...)`, `h.back(mat=...)`로 영역 머티리얼을 준다.
- 의미가 바뀐 인자
  - `cap(segs, rows)`: 해상도 힌트다. 작게 주면 성글어진다(헬멧 아래 단역).
  - `back(length)`: 기준이 '목덜미 머리선 아래'로 바뀌었다(v1은 머리 뒤쪽 중간 기준). 같은 값이면 v2가 조금 더 길다.
- **무시되는 인자** (주면 `[elf] 경고:`를 출력하고 넘어간다)
  - `bangs(width)`: 다발 폭은 자동 변화. `n`, `spread`, `seed`로 조절한다
  - `sides(flare)`: `puff`, `curl`로 조절한다
  - `back(width)`, `back(flare)`, `back(layers)`: 속층이 항상 있고 폭은 자동이다. `n`, `spread`, `length`, `thick`로 조절한다
- 새 인자
  - `Hair(off=0.028, outline=0.0035, volume=1.0)`, `cap(volume=)`
  - `bangs(seed=, mat=, under_hat=)`: `under_hat`은 모자·헬멧 아래용 뭉툭하고 둥근 짧은 끝이다. None이면 `e.helmet`(모자)이 있을 때 자동으로 켜진다
  - `sides(mat=, left=, right=)`: 좌우 비대칭. 예: `sides(length=0.07, right=dict(length=0.0, width=0.05))`
  - `back(mat=)`
  - `ponytail/twintails(lift=, curve=, thick=)`: `lift`는 머리에서 튀어나오는 정도(1=기본), `curve`는 S자 휨(0=곧게, 1=기본), `thick`는 두께(m, 기본 폭의 0.8)
  - `braid(bones=, tilt=, tuft=)`
- 기본값 변경: `ponytail(height=34, width=0.115)`(굵고 높게), `twintails(width=0.10)`, `shine(size=1.35)`, `strand()` 기본 단면 분할 10, 길이 14.
- 꼬리(포니테일·트윈테일)는 `cameo.Tail` 기준으로 다시 만들었다. 굵은 한 덩어리 몸통이 묶은 자리에서 모였다가 부풀고, S자로 늘어지다 끝에서만 `clumps+1`갈래로 갈라진다. 묶음 띠는 묶은 자리 굵기의 1.12배로 자동으로 맞춘다.
- 모자·헬멧 squash: 겉면은 모자 두께의 0.7배, 속층은 그보다 깊은 0.385배까지 누른다(모자 띠 아래 어두운 점 방지). 꼬리·묶음 띠는 누르지 않는다.
- **`elf.sweep` 면 방향 수정 (2026-11-01)**: 예전에는 면이 안쪽을 봐서 `strand`, `ahoge`, 꼬리에 아웃라인이 생기지 않았다. 지금은 바깥을 보고, `elf.SWEEP_WINDING == "outward"`로 확인할 수 있다. 이 버그를 우회하려고 면을 뒤집던 코드는 이제 **이중으로 뒤집으므로** 빼야 한다(`cameo.flip_from` 사용처: `cameo.strand`, `cameo.ahoge`, `cameo.Tail`).

| 함수 | 주요 인자 | |
|---|---|---|
| `h.cap()` | `front=26, side=-12, back=-50`(머리선 높이, 도), `part`(가르마 방위), `volume`, `segs`, `rows` | 머리선과 가르마 |
| `h.bangs()` | `n=7`(5~9), `spread=55`, `tip_el=5`(끝 높이, 0≈눈썹), `length`, `part`, `sweep`, `curl`, `jag`, `seed`, `mat`, `under_hat` | 앞머리: 가르마 쪽 큰 다발 1~2 + 보조 다발, 이마를 따라 아치 |
| `h.sides()` | `length=0.10`(턱선 아래), `width=0.078`, `az=68`, `n=1`, `curl`, `puff`, `mat`, `left`, `right` | 귀 앞 옆머리. 끝이 턱 쪽으로 말림. 좌우 따로 가능 |
| `h.back()` | `length=0.08`(목덜미 머리선 아래), `n=9`(홀수), `spread=88`, `mat` | 뒷머리. 길면 흔들림 본 |
| `h.ponytail()` | `height=34, length=0.30, width=0.115, clumps=2, droop, lift=1, curve=1, thick, bones=True, tie` | 굵은 S자, 끝 갈래 + `hair_tail_01/02` |
| `h.twintails()` | `height=30, az=125, length=0.30, width=0.10, lift, curve, thick, bones=True` | `hair_tail_L/R_01/02` |
| `h.braid()` | `side, az=110, el=-25, length=0.30, width=0.04, beads=8, tilt=32, bones=True, tie, tuft` | 마디가 좌우로 기울어 반씩 겹친 연속 볼륨 + `hair_braid_L/R_01..03` |
| `h.ahoge()`, `h.bun()` | | 바보털(S자), 경단(매끈한 타원체) |
| `h.shine()` | `el=50, spread=74, n=2, size=1.35` | 정수리 둥근 광택 (머리 곡면에 붙음, 아웃라인 없음) |
| `h.strand(pts, width, thick, …)` | 제어점, `taper`, `normal`, `bend`, `w` | 임의 다발 (매끈한 렌즈·초승달 단면) |
| `h.sp(az, el, off)`, `h.path(az, s)` | | 머리 표면 점 / 머리 덩어리 바깥 면 점 |

예: 긴 생머리, 단발, 포니테일, 트윈테일은 `art/blender/characters/_kit_hair_test.py`에 있다.

헬멧이나 모자(`e.helmet`)가 있으면 그 안쪽으로 머리카락을 눌러 넣는다(`squash`). 테두리 아래로는 앞머리와 뒷머리 끝이 보인다.

---

## 9. 옷과 장비

모든 함수는 첫 인자로 머티리얼을 받는다. 치수는 기본 체격 기준 m이며, 내부에서 `e.k`를 곱한다.

| 함수 | 주요 인자 | 메모 |
|---|---|---|
| `e.shirt(m)` | `hem`(z), `off=0.010`, `flare=0.014`, `collar="stand"/"turtle"/None`, `collar_mat`, `placket`, `buttons` | 몸판. 밑단에 두께 테두리(lip). 몸통 맨살을 덮는다 |
| `e.sleeves(m)` | `length=0.97`, `off`, `flare`, `puff`, `cuff=(m, 높이, 두께)` | 양 소매 (arms 그룹) |
| `e.pants(m)` | `waist`, `length=0.92`, `off`, `bag`(통), `blouse`(블라우징), `cuff` | 골반부 + 양 다리 |
| `e.boots(m)` | `top=0.62`(목 높이: 다리 비율), `sole=(m, 두께)`, `cuff`, `laces`, `tab`, `straps`, `toe` | 맨발 대신 |
| `e.gloves(m)` | `cuff`, `cuff_h`, `inflate` | 맨손 대신 (손가락 본 그대로) |
| `e.belt(m)` | `z`, `h`, `th`, `off`, `buckle`, `buckle_size`, `loops` | |
| `e.pouch(m, at)` | `size`, `flap`, `button`, `molle`, `strap`(팔다리 고정끈), `tilt`, `lift` | at = anchor 튜플 |
| `e.ring(m, where, pos)` | `"leg_L"`/`"arm_R"`/`"torso"`, t 또는 z | 감는 띠 (허벅지끈, 완장, 가슴띠) |
| `e.strap(m, path)` | anchor 목록, `width`, `th` | 몸을 따라가는 끈 (멜빵, 슬링) |
| `e.pad(m, at)` | `size`, `strap`, `curve` | 무릎·팔꿈치·어깨 보호대 |
| `e.patch(m, at)` | `shape="rect"/"round"/"diamond"/"chevron"/"bars2"/"bars3"`, `size` | 계급장·부대 표식. 기하 도형만 |
| `e.epaulet(m)` | `button`, `width` | 견장 (어깨 고리) |
| `e.helmet(m)` | `off=0.036`, `front/side/back`(테두리 높이), `rim`, `band_mat`, `buckle`, `strap`, `ridge`, `visor`, `vents` | 둥근 헬멧, 진압 헬멧(`ridge`, `vents`), 바이저 |
| `e.gear(name, at, fn)` | `fn(buf, M, w)` | 임의 장비. 로컬 +Z=위, −Y=바깥 법선 |

저수준 도형(직접 장비를 만들 때): `elf.rbox(buf, size, M)`(둥근 상자, 64삼각형), `elf.disc(...)`(단추·렌즈), `elf.band(...)`(링 띠), `elf.loft(buf, stations)`(단면 관), `elf.pouch_geo(...)`, `elf.Buf()`(정점·면·웨이트 버퍼, `.obj(name)`).

예: 허벅지 파우치, 진압 무릎 보호대
```python
e.pouch(web, ("leg_R", 0.30, -75, 0.024 * e.k), size=(0.052, 0.026, 0.062), flap=web_d, button=metal, strap=belt)
e.pad(pad_mat, ("leg_L", 0.53, 0, 0.012 * e.k), size=(0.07, 0.018, 0.07), strap=belt)
```

---

## 10. 예산과 품질

| 모델 | 설정 | 삼각형 (머리카락 셸 + 속층) |
|---|---|---|
| `_kit_base` (바디슈트, 맨손·맨발, 단발 + 광택) | 기본 | 15.8k (3.8k + 0.7k) |
| `_kit_elfinia_soldier` (전투복 일체, 헬멧) | `segs=0.85, hand_q=0.8`, `cap(segs=20, rows=5)` | 18.0k (2.5k + 0.5k) |
| `_kit_hair_test_long` / `_bob` / `_pony` / `_twin` | 기본 | 15.9k / 15.1k / 16.0k / 16.6k (머리 4.2k / 3.4k / 4.2k / 4.9k + 0.7k) |
| R41 소총병 (r41_troops, 헬멧·베레모) | `segs=0.7, hand_q=0.6`, `cap(segs=18, rows=4)` | 14.8~15.5k (머리 1.9~2.3k) |
| 1인칭 팔 (소매 + 장갑) | `hand_q=1.2`, `only=("arms",)` | 4.3k |

- R41 병사(15k, ART_GUIDE 8장): `segs=0.7, hand_q=0.6`, 헬멧 아래 머리는 `cap(segs=18, rows=4)`, 앞머리 5, 뒷머리 5로 충분하다. 탄창 파우치 3개 + 멜빵 + 가슴띠가 약 1.5k다.
- 비싼 순서: 머리카락(셸 3~5k, `Elf(segs)`·`cap(segs, rows)`로 조절) > 헬멧 > 몸판 > 얼굴(약 1k) > 군화·장갑 > 파우치(약 130). `[elf]` 보고를 보고 줄인다.

---

## 11. 새 인물 만드는 법

1. `_kit_base.py`나 `_kit_elfinia_soldier.py`를 복사해 `art/blender/characters/<이름>.py`로 둔다.
2. `Elf()` 체격(키, 머리, 어깨)과 `face()`(눈색, 눈썹)로 얼굴 인상을 먼저 정한다. `--focus <이름>_face`로 확인한다.
3. 머리카락으로 실루엣을 잡는다. 원작 카메오는 머리색·헤어스타일·상징 소품만 유지한다.
4. 옷은 진영 색(reference-notes 5·6장)에서 고르고, 3차 디테일(버클, 덮개, 끈, 패치)을 한 겹 더한다.
5. `[elf]` 삼각형 보고와 ART_GUIDE 8장 예산을 맞춘다.
6. 시트 4방향, 얼굴 클로즈업, `--mode fpbody --pitch -30/-60/-80`를 찍어 직접 보고 고친다.

---

## 12. 알려진 한계와 다음 계획

- 옷 셸은 몸 단면을 부풀린 관이라 치마·망토·코트 자락 같은 '몸에서 떨어지는 천'은 아직 키트에 없다. 지금은 `art/blender/lib/cameo.py`의 `Shell`, r41_troops의 `coat_skirt`/망토가 따로 해결한다.
- 위장 무늬 같은 텍스처는 지원하지 않는다(정점색 병합 방식). 색 블록 몇 개는 `e.patch`로 낼 수 있다.
- 1인칭에서 서 있을 때 다리는 몸통에 가려 보이지 않는다(7장).
- 헤어 v2: 다발이 서로 교차하는 복잡한 묶음 머리(반묶음, 땋아 올린 머리)는 `strand()`/`braid()`를 직접 조합해야 한다. 아주 짧은 쇼트컷(목덜미가 드러남)은 `back(length=-0.05)`처럼 음수 길이로 근사한다.

**다음 순위 (계획, 출처: cameo.py · r41_troops.py)**
1. `e.drape()`: 몸에서 떨어지는 천. 앞트임 재킷·가운·코트 자락·치마·망토·한쪽 어깨 망토·프릴을 다룬다. cameo `Shell`(행·열 격자, 앞트임 gap, 테두리 trim)과 r41 `coat_skirt`·망토를 하나로 합친다. 웨이트는 몸통 + 허벅지 섞기다.
2. `e.face(expr=)` 확장: 비대칭 표정·윙크(cameo `face_expr`의 L/R/M 분리). 교정 키 규칙은 그대로다.
3. 모자: `e.beret()`(r41), 정모(헤일리 정복용). 머리카락 squash 연동.
4. 장갑 변형: `gloves(fingerless=True)`(r41 `fingerless_gloves`).
5. 판·띠: 몸을 감싸는 판 `e.panel()`(조끼 판, r41 `panel`/`plate_vest`), 두께 없는 띠 `elf.ribbon()`, 임의 면 엘프 로고 데칼(r41 `logo`).
6. 팔다리 관 노출: `e.limb_tube(limb, t0, t1, ...)`(cameo `leg_tube`/`arm_tube`)와 `elfinia_uniform()` 프리셋(cameo).
7. 미리보기: 포즈를 주고 소켓에 무기 glb를 붙이는 미리보기 모드(r41 `_preview`)를 키트와 뷰어 쪽 규약으로 올린다.

---

## 13. 인간 비율 키트 (`art/blender/lib/human.py`, 2026-11-02)

엘리아스의 인간(교주)처럼 SD 엘프가 아닌 성인 인간 비율이 필요할 때 쓴다. `human.Human`은 `elf.Elf`의 하위 클래스라 **본 이름·축·A 포즈 40°·소켓·계산 웨이트·`finalize()` 합치기·정점색 툰 머티리얼이 엘프 키트와 같다.** 그래서 런타임 NPC 시스템(자세·걷기·손 소켓 hold·아웃라인·툰)과 `cinePoses.arm()`이 그대로 맞는다. 첫 사용처는 `characters/kyoju.py`(characters-cameo3.md 9.9절).

```python
import cb, human
cb.reset()
e = human.Human("kyoju", height=1.78, head=0.235, head_mat=shadow, segs=0.9, hand_q=0.9, head_q=0.55)
e.sleeves(white, length=0.955, flare=0.022, cuff=(navy, 0.022, 0.0035))   # 엘프 키트 옷 함수도 쓸 수 있다
cass = human.Drape(e, white, zs, section_fn, cols=22, wfn=lambda q: human.skirt_w(e, q))  # 바닥까지 오는 자락
cass.strip_row(navy, 0.022, 0.003); cass.done("cassock")
e.finalize(); e.export("characters/kyoju.glb")
```

| 엘프 키트와 다른 점 | 내용 |
|---|---|
| 비율 | 키 1.78 m(정수리) 기준 성인 남성 실측 비율. 머리 0.235 m(7.6등신), 어깨 관절 1.445 m(좌우 ±0.182), 고관절 0.925 m, 무릎 0.505 m, 위팔 0.30 m, 아래팔 0.262 m. `height`를 바꾸면 전체가 같은 비율로 커진다(`e.s`) |
| `e.k` | 작은 디테일 배율 1.40 × `e.s`. 엘프 키트의 옷·장비 함수(sleeves, belt, ring, patch…)는 `e.k`를 곱하므로 그대로 써도 인간 크기에 맞는다 |
| 몸통 | `torso_at()`을 인간 단면 표(`human.TORSO`)로 바꿨다. 팔·다리 반경(`arm_r`, `leg_r`)도 인간 값 |
| 머리 | 사실적인 달걀형. `head_mat`으로 머리·목 재질을 따로 준다(교주: 그림자 UNLIT). `head_q`로 머리 분할을 낮춘다. `face()`를 부르지 않으면 표정 모프가 없다(FaceRig는 얼굴이 없으면 아무것도 안 한다) |
| 귀 | 만들지 않는다. `ear_L/R` 본은 리그 호환을 위해 남는다 |
| 손 | 다섯 손가락의 가는 손. 본은 엄지 + f1~f3 그대로이고 새끼손가락은 f3(약지) 본 웨이트를 따른다. 그래서 `fingers()` 자세가 다섯 손가락을 다 만다. 파지점(`socket_hand_*`)은 손바닥에서 3 cm |
| 발 | 신발 모양 덩어리(`foot(..., sole=(재질, 두께))`) |
| `Drape` | 몸에서 떨어지는 두께 있는 천(수단 자락, 망토·코프). 행 z 목록 × 열 방위, `section(z)`, 앞트임 `gap(z)`, 웨이트 `wfn`, 안감 `mat_in`, 가장자리 띠 `strip_edge`, 행 띠 `strip_row`, 표면 점 `surface(z, a)`. 엘프용 `cameo2.Shell`과 같은 생각이고 SD 상수를 쓰지 않는다 |
| `skirt_w(e, q, legs)` | 긴 자락 웨이트: 골반 위는 몸통 규칙, 아래로 갈수록 좌우 허벅지를 `legs`만큼 따라간다 |

- 런타임 NPC 크기: `Human.export()`가 리그 루트 extras에 충돌 캡슐 크기를 싣는다. `npcHeight`(캡슐 위 끝, 기본 정수리 + 4 cm), `npcRadius`(기본 0.25 m, 키 비례). `src/game/npc/Npc.ts`가 읽어 캡슐(발밑 2 cm부터)·조준점·애니메이션 예산의 화면 판정 구를 키에 맞춘다. 값이 없는 엘프 모델은 예전 엘프 캡슐(0.02~1.14 m, 반지름 0.2) 그대로다. 눈높이는 `socket_eye`에서 읽는다(교주 1.65 m).
- 그 밖의 NPC extras: `steadyArm`("L"/"R"/"LR")은 걷기 팔 흔들기를 빼고 그 손 소켓에 박힌 소품을 손목으로 곧게 세운다(교주의 목장). `strideScale`은 걷기 보폭 배율이다(바닥까지 오는 옷: 교주 0.6).
- 내비메시는 레벨마다 엘프 에이전트(`ELF_AGENT`: 반지름 0.22, 높이 1.2)로 하나만 굽는다. 인간이 내비 경로로 걸으면 1.2~2.1 m 높이의 처마 밑으로 길이 날 수 있으니 그런 곳을 지나는 길은 피한다.
- 공용 자세의 쥔 자리(`_holdR/_holdL`)는 엘프 기준 m 좌표라, 인간에게 손 IK 자세를 쓰려면 따로 자세를 만든다(교주는 목장을 소켓에 박고 FK 자세만 쓴다).
