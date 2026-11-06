# Monatium Studio Models

[한국어](README.md) · **English** · [日本語](README.ja.md)

3D models and the Blender scripts that build them, made for *BOL OF MONATIUM*, a fan game based on Trickcal: Revive.

## Contents

| Path | What |
|---|---|
| `public/models/**.glb` | Finished models loaded by the game (glTF binary) |
| `art/blender/**.py` | Headless Blender scripts that build the models (shared tools in `art/blender/lib`) |
| `docs/art/` | Art guide and per-model design notes (start with `ART_GUIDE.md`) |
| `public/ui/elf_logo_mono.svg` | Input read by the vehicle decal scripts |

## Rebuilding

Requires Blender (`blender` on PATH, or the default macOS install location).

```sh
npm run model -- art/blender/<category>/<name>.py
```

The result is written to `public/models/<category>/<name>.glb`.

## License

[MIT License](LICENSE). It covers the scripts, model data and documents made by Monatium Studio.

## Attribution

If you use the models from this repository directly (in a game, video, image or another project, as is or modified), please credit them. Put a line like the following somewhere viewers can see it, such as the credits or a description:

```
Models by Monatium Studio (https://github.com/Monatium-Studio/models), MIT License
```

## Copyright

- All rights to the original work *Trickcal: Revive*, including its characters, world and designs, belong to **EPIDGames**. Trickcal Revive © EPIDGames Inc. All rights reserved.
- The scripts, model data and documents in this repository were made by **Monatium Studio**. © 2026 Monatium Studio.
- The MIT License applies only to the rights held by Monatium Studio and grants no rights to the original work. When using original characters or designs, follow EPIDGames' fan-creation guidelines.
- This repository is an unofficial fan work based on Trickcal: Revive. It is not affiliated with or endorsed by EPIDGames.

## Trademarks

Trickcal, Trickcal: Revive and other derived brands are registered trademarks of EPIDGames.

## Third-party data

- Earth terrain data: [Natural Earth](https://www.naturalearthdata.com/) (public domain)
