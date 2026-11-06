# Monatium Studio 모델

Monatium Studio 게임의 3D 모델 모음 (비공개).

- `public/models/**.glb`: 게임이 읽는 완성 모델 (glTF 바이너리)
- `art/blender/**.py`: 모델을 만드는 Blender 헤드리스 스크립트 (공용 도구는 `art/blender/lib`)
- `docs/art/`: 아트 가이드와 모델별 설계 문서 (`ART_GUIDE.md`부터)
- `public/ui/elf_logo_mono.svg`: 차량 데칼 스크립트가 읽는 입력

## 다시 만들기

Blender가 설치되어 있어야 한다 (`blender`가 PATH에 있거나 macOS 기본 설치 위치).

```sh
npm run model -- art/blender/<분류>/<이름>.py
```

결과는 같은 이름의 `public/models/<분류>/<이름>.glb`에 쓰인다.

## 주의

원작 이미지 등 외부 레퍼런스 자료는 이 저장소에 넣지 않는다.
