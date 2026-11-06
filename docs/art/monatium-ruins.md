# 모나티엄 폐허 키트 (monatium_ruins_kit) · M4 레벨

2막 「암흑」(둠스데이 정전 직후)의 모나티엄을 도시 키트(`monatium_city_kit`) 위에 조립한다. 도시 키트는 고치지 않고, 폐허·정전 변형만 새 파일에 둔다(`docs/art/monatium-city.md` 9장 폐허 변형 계획을 따름).

- 키트: `art/blender/lib/monatium_ruins_kit.py` (의존: `cb`, `home_weapons`, `monatium_city_kit`)
- 레벨: `art/blender/levels/m4_ruins.py` → `public/models/levels/m4_ruins.glb` (약 60k tris, 4.2 MB, 마커 121. 2026-11-04 늘림: 들어가는 사무동·편의점·뒷골목)
- 쓰는 곳: M4(폐허), M5·M6(`rubble`, `fire_barrel`, `trig`, `door`, `blackout` …)

```bash
npm run model -- art/blender/levels/m4_ruins.py
npm run shot -- levels/m4_ruins.glb --views top,34
```

## 1. 근거
- [원작] 둠스데이 프로토콜로 모나티엄의 인프라와 데이터가 파괴된다. 흑뉴아가 시청 폐허에서 엘레나·로네를 심문한다.
- [오리지널] 1막 끝 정전: 도시 전체 불이 꺼지고, 드론이 전부 떨어지고, 차량이 그 자리에 멈춘다. 그래서 키트는 시안 네트워크 발광을 끄고(`blackout`), 추락 드론은 `PROP_`, 멈춘 차량은 `VEH_ state=off`로 둔다.

## 2. 모듈
| 함수 | 내용 |
|---|---|
| `blackout(C)` | `finish` 직전. 도시 키트가 만든 `glow`→`glow_off`, `lamp`→`lamp_off`, 켜진 창·화면·R41 마젠타 → `char` |
| `trig(C, id, x0,x1,y0,y1,z0,z1)` / `door(C, id, …, move)` / `named_box` | `TRIG_`·`DOOR_`·이름 있는 박스 (City에 없는 노드) |
| `rubble(C, x, y, r, h)` | 엄폐 잔해 더미(덩어리 + 깨진 판 + 철근), 보이는 높이에 맞춘 COL (0.75~1.0 m면 웅크려 숨는다) |
| `rubble_wall` | 통행을 막는 큰 잔해 둑 (맵 가장자리) |
| `fallen_column`, `fallen_lamp`, `fallen_tree`, `burnt_car` | 쓰러진 포르티코 기둥·가로등·나무, 불탄 엘프 승용차(엄폐 1.15 m) |
| `fire_barrel(C, n, x, y)`, `campfire` | 불 피운 드럼통·모닥불 + `FX_fire_<n>` (미션이 깜빡이는 점광원을 붙인다) |
| `chemlight` | 바닥에 떨어진 R41 화학 발광봉 (정전에도 켜지는 마젠타, UNLIT `chem`) |
| `soot`, `crack` | 그을음 데칼, 바닥 갈라짐 |
| `ruined_building(C, …, broken)` | 도시 키트 `building` + 들쭉날쭉한 윗면·꺾인 슬래브·철근, 검은 창 구멍, 그을음, 앞 잔해 |
| `ruined_city_hall(C, cx, cy)` | `city_hall(초상·화면·깃발 없이)` + 그을음, 찢긴 현수막, 동쪽 끝 쓰러진 기둥, 계단에 엎어진 초상 액자. 가운데 계단 길과 정문은 비운다 |
| `monorail_dark`, `collapsed_span` | 정전된 모노레일(빈 경간 지원), 차도에 박힌 무너진 보(계단식 COL) |
| `overpass` | 고가 상판 한 조각 + 표지판 (지하도) |
| `dark_skyline` | 불 꺼진 원경 고층 |
| `wall_run`, `slab` | 구멍(문·창·기는 틈)을 비운 벽 한 줄·바닥판. 남는 칸을 상자로 쌓고 같은 COL을 준다 |
| `ruined_shell` | **들어가는 폐허 건물**: 바깥벽(구멍 / 유리 `glass_pane` / 방범 창살 `grille`), 층 바닥판(구멍), 안 기둥, 쓰러진 면(`gone`), 무너진 벽 끝 |
| `crawl_gap` | 벽 밑동의 기는 틈 (밑 0.52 m: 엎드린 플레이어만, 병사 내비는 못 지남). 떨어진 바닥판이 구멍에 걸려 기울었다. 길이는 1.2 m 안 (엎드려 기기는 내비 1 m 안에서만) |
| `wedge_ramp` | 밑이 잔해로 꽉 찬 비탈 판 (꺾여 내려앉은 바닥판 경사로, 미끄러져 내려온 벽판). COL은 판 윗면부터 바닥까지 한 덩이 쐐기: 판 밑 낮은 틈·비탈 천장이 없다 |
| `shop_interior`, `gondola`, `counter`, `cooler_bank` | 들어가는 1층 가게 (정면 +y 유리·문·깨진 칸·간판·차양), 진열대(서 있음 / 넘어짐), 계산대, 꺼진 냉장고 벽. 위층은 `ruined_building(z0=…)` |
| `roll_shutter` | 반쯤 올라간 셔터 문 `DOOR_` (밑으로 서서 지난다, 열면 셔터 상자로) |
| `dumpster`, `ac_unit`, `clothesline` | 뒷골목 소품 (벽에 붙인다: 틈 0) |

팔레트 추가: `rubble` `rubble_d` `rebar` `burnt` `char` `ash` `tarp_o` `barrel` `barrel_r` `far_n` `far_n2`, 발광 `ember` `chem`.

## 3. M4 배치 (Blender 좌표, 원점 = 광장 가운데, +Y = 시청)
```
 y  33 ┤        [시청 폐허 (0,26)]
    19 ┤         정문 ─ 계단 y 11.3~14 (단 0.15) ─ 포르티코 z 0.9
    11 ┤ 광장 ···· 분수(0,2) ···  [잔해 엄폐 x12.5~19.5] ← 시작 (16,9) 분대 넷
    14 ┤                         ┌─ 동쪽 골목 x24~60, y-1~14 (수색조 둘) ─┐
    -1 ┤                         └──────────┐ 옆길 x46~60 ─┐
   -21 ┤ ══ 엘레나대로 ══ 잔해 둑 x26~30 ══ 무너진 모노레일 x33~48 ══ 잔당 불 (70,-24) ══ 고가 밑 x94~106 (뮤트)
   -31 ┤ 남쪽 폐허 상가 줄
        -30            0                30            60            90         116
```
- 밤 환경: `sky #0d1220`, `fog 16,130`, 달빛 주광 `#9fb2e6` 0.8, 반구광 하늘 `#4a5a86` 땅 `#2a2430`.
- 마커 표: `docs/script/m4.md` 6장.

- 늘린 길 (2026-11-04, 한 줄 길): 골목 끝 → 옆길 남쪽 끝 둑 → 사무동 E1 남쪽 반(쪽문·기는 틈 → 로비 → 꺾인 바닥판 경사로 → 남쪽 벽이 쓰러진 2층 끝) → 벽판 비탈 → 큰길 건너기(서쪽 x 49~52.5 둑, 동쪽 고가 앞 x 88.5~94 둑과 무너진 모노레일) → 편의점 「모나티엄 25」 → 뒤 셔터 → 뒷골목 → 고가 밑 통로를 북쪽으로 → 뮤트. 마커 표: `docs/script/m4.md` 6.1장.
- 고가 상판은 y −58~16으로 늘렸고, 상판을 뚫고 서 있던 남쪽 상가 둘과 북쪽 블록은 고가 발자리(x 94~106)를 비웠다.

## 4. 남은 문제
- 시청 탑 관은 도시 키트 그대로 서 있다(탑 붕괴 변형은 도시 키트 플래그가 필요해 하지 않았다).
- 사무동 E1 남쪽 반과 편의점 1층 말고 다른 폐허 건물은 통짜 COL이라 안으로 들어갈 수 없다(밖에서 보는 배경).
- 광장 북동쪽 시청 날개 끝(17.3, 17)에서 북쪽 블록 뒤 빈 땅으로 나가는 틈이 예전부터 있다(막다른 고리라 진행 길과 이어지지 않는다).
