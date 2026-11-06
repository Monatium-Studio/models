# Monatium Studio 모델

**한국어** · [English](README.en.md) · [日本語](README.ja.md)

트릭컬 리바이브 2차 창작 게임 「볼 오브 모나티엄 (BOL OF MONATIUM)」에 쓰는 3D 모델과, 모델을 만드는 Blender 스크립트 모음입니다.

## 구성

| 경로 | 내용 |
|---|---|
| `public/models/**.glb` | 게임이 읽는 완성 모델 (glTF 바이너리) |
| `art/blender/**.py` | 모델을 만드는 Blender 헤드리스 스크립트 (공용 도구는 `art/blender/lib`) |
| `docs/art/` | 아트 가이드와 모델별 설계 문서 (`ART_GUIDE.md`부터) |
| `public/ui/elf_logo_mono.svg` | 차량 데칼 스크립트가 읽는 입력 |

## 다시 만들기

Blender가 설치되어 있어야 합니다 (`blender`가 PATH에 있거나 macOS 기본 설치 위치).

```sh
npm run model -- art/blender/<분류>/<이름>.py
```

결과는 같은 이름의 `public/models/<분류>/<이름>.glb`에 쓰입니다.

## 라이선스

[MIT 라이선스](LICENSE). Monatium Studio가 만든 스크립트·모델 데이터·문서에 적용됩니다.

## 저작권

- 원작 「트릭컬 리바이브 (Trickcal: Revive)」의 캐릭터·세계관·디자인 등 원작에 대한 모든 권리는 **EPIDGames**에 있습니다. Trickcal Revive © EPIDGames Inc. All rights reserved.
- 이 저장소의 스크립트·모델 데이터·문서는 **Monatium Studio**가 만들었습니다. © 2026 Monatium Studio.
- MIT 라이선스는 Monatium Studio가 가진 권리에만 적용되며, 원작에 대한 권리를 부여하지 않습니다. 원작 캐릭터·디자인을 쓸 때는 EPIDGames의 2차 창작 가이드라인을 따르세요.
- 이 저장소는 트릭컬 리바이브의 비공식 2차 창작물이며, EPIDGames와 제휴하거나 EPIDGames의 승인을 받지 않았습니다.

## 상표

Trickcal, Trickcal: Revive(트릭컬, 트릭컬 리바이브) 및 기타 파생 브랜드는 EPIDGames의 등록상표입니다.

## 외부 자료

- 지구 지형 데이터: [Natural Earth](https://www.naturalearthdata.com/) (퍼블릭 도메인)
