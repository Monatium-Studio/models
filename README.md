# Monatium Studio 모델

**한국어** · [English](README.en.md) · [日本語](README.ja.md)

모나티엄 스튜디오에서 제작하는 트릭컬 리바이브 2차 창작 게임 제작에 활용된 모델 및 블렌더 스크립트를 모아둔 저장소입니다. 자세한 사용 조건은 아래 [라이선스](#라이선스) 및 [저작권](#저작권) 항목을 참조하여 주시기 바랍니다.

## 구성

| 경로 | 내용 |
|---|---|
| `public/models/**.glb` | 게임이 읽는 완성 모델 (glTF 바이너리) |
| `art/blender/**.py` | 모델을 만드는 Blender 헤드리스 스크립트 (공용 도구는 `art/blender/lib`) |
| `docs/art/` | 아트 가이드와 모델별 설계 문서 (`ART_GUIDE.md`부터) |
| `public/ui/elf_logo_mono.svg` | 차량 데칼 스크립트가 읽는 입력 |
| `index.html`, `viewer.ts`, `vite.config.ts` | 모델 뷰어 (아래 [모델 뷰어](#모델-뷰어)) |

## 다시 만들기

Blender가 설치되어 있어야 합니다 (`blender`가 PATH에 있거나 macOS 기본 설치 위치).

```sh
npm run model -- art/blender/<분류>/<이름>.py
```

결과는 같은 이름의 `public/models/<분류>/<이름>.glb`에 쓰입니다.

## 모델 뷰어

브라우저에서 `public/models` 아래 모델을 둘러볼 수 있습니다. 뷰어는 [strawberry-cake-engine](https://github.com/Monatium-Studio/strawberry-cake-engine)의 모델 뷰어를 씁니다.
Node.js 20.19 이상(또는 22.12 이상)이 필요합니다.

```sh
npm install              # 처음 한 번 (엔진과 Vite를 받습니다)
npm run viewer           # 개발 서버 → http://127.0.0.1:5190/
```

정적 사이트로 빌드해서 띄울 수도 있습니다. 결과물은 모델을 포함해 `dist/`에 생기고, 어느 경로에 올려도 동작합니다.

```sh
npm run viewer:build     # dist/ 에 빌드
npm run viewer:preview   # 빌드 결과 확인 → http://127.0.0.1:5191/
```

**조작**

| 동작 | 방법 |
|---|---|
| 모델 고르기 | 왼쪽 목록을 클릭합니다. 페이지를 다시 읽지 않고 그 자리에서 바뀝니다 |
| 검색 | `/` 또는 Ctrl·Cmd+K로 검색칸에 들어갑니다. 띄어 쓴 낱말이 모두 경로에 들어 있는 모델만 남습니다. ↑↓로 고르고 Enter로 엽니다. Esc를 누르면 검색어가 지워집니다 |
| 앞뒤 모델 | 목록을 클릭해 초점을 둔 뒤 ↑↓를 누릅니다 |
| 돌려 보기 | 드래그는 회전, 휠은 확대·축소, 오른쪽 드래그는 이동입니다 |
| 주소 | 지금 보는 모델이 `?model=<분류>/<이름>.glb`로 주소에 남습니다. 새로고침, 뒤로 가기, 링크 공유가 됩니다 |
| 볼 리그 | 볼 본이 있는 캐릭터는 오른쪽 아래에 조작판이 생깁니다: P 부풀리기, S 눌림, L·R·B 늘리기, 스페이스 놓기, H 흔들기, J 달리기 |

`npm run model`로 모델을 다시 만든 뒤에는 목록에서 다시 고르거나 새로고침하면 새 파일이 보입니다.

## AI 생성 자료

이 저장소의 Blender 스크립트와 문서는 AI(Anthropic의 Claude)를 활용해 작성되었고, 모델(glb)은 그 스크립트로 생성되었습니다. Monatium Studio가 방향을 정하고 결과를 확인했습니다.

## 라이선스

[MIT 라이선스](LICENSE). Monatium Studio가 만든 스크립트·모델 데이터·문서에 적용됩니다.

## 출처 표시

이 저장소의 모델을 직접 쓸 때는 (게임·영상·이미지·다른 프로젝트에 넣거나 고쳐서 쓰는 경우 모두) 출처를 표시해 주세요. 크레딧이나 설명란 등 보는 사람이 확인할 수 있는 곳에 아래처럼 적으면 됩니다.

```
Models by Monatium Studio (https://github.com/Monatium-Studio/models), MIT License
```

## 저작권

- 원작 「트릭컬 리바이브 (Trickcal: Revive)」의 캐릭터·세계관·디자인 등 원작에 대한 모든 권리는 **EPIDGames**에 있습니다. Trickcal Revive © EPIDGames Inc. All rights reserved.
- 이 저장소의 스크립트·모델 데이터·문서는 **Monatium Studio**가 만들었습니다. © 2026 Monatium Studio.
- MIT 라이선스는 Monatium Studio가 가진 권리에만 적용되며, 원작에 대한 권리를 부여하지 않습니다. 원작 캐릭터·디자인을 쓸 때는 EPIDGames의 2차 창작 가이드라인을 따르세요.
- 이 저장소는 트릭컬 리바이브의 비공식 2차 창작물이며, EPIDGames와 제휴하거나 EPIDGames의 승인을 받지 않았습니다.

## 상표

Trickcal, Trickcal: Revive(트릭컬, 트릭컬 리바이브) 및 기타 파생 브랜드는 EPIDGames의 등록상표입니다.

## 외부 자료

- 지구 지형 데이터: [Natural Earth](https://www.naturalearthdata.com/) (퍼블릭 도메인)
