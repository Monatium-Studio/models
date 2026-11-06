# Monatium Studio モデル

[한국어](README.md) · [English](README.en.md) · **日本語**

トリッカル・リバイブの二次創作ゲーム『ボル・オブ・モナティウム (BOL OF MONATIUM)』で使う3Dモデルと、モデルを生成するBlenderスクリプト集です。

## 構成

| パス | 内容 |
|---|---|
| `public/models/**.glb` | ゲームが読み込む完成モデル (glTFバイナリ) |
| `art/blender/**.py` | モデルを生成するBlenderヘッドレススクリプト (共通ツールは `art/blender/lib`) |
| `docs/art/` | アートガイドとモデルごとの設計文書 (`ART_GUIDE.md` から) |
| `public/ui/elf_logo_mono.svg` | 車両デカールのスクリプトが読み込む入力 |

## 再生成

Blenderが必要です (`blender` がPATHにあるか、macOSの標準インストール先)。

```sh
npm run model -- art/blender/<分類>/<名前>.py
```

結果は同じ名前の `public/models/<分類>/<名前>.glb` に書き出されます。

## ライセンス

[MITライセンス](LICENSE)。Monatium Studioが制作したスクリプト・モデルデータ・文書に適用されます。

## クレジット表記

このリポジトリのモデルを直接使う場合は (ゲーム・動画・画像・他のプロジェクトへの組み込みや改変を含む)、クレジットを表記してください。クレジットや概要欄など、見る人が確認できる場所に次のように記載してください。

```
Models by Monatium Studio (https://github.com/Monatium-Studio/models), MIT License
```

## 著作権

- 原作『トリッカル・リバイブ (Trickcal: Revive)』のキャラクター・世界観・デザインなど、原作に関するすべての権利は **EPIDGames** に帰属します。Trickcal Revive © EPIDGames Inc. All rights reserved.
- このリポジトリのスクリプト・モデルデータ・文書は **Monatium Studio** が制作しました。© 2026 Monatium Studio.
- MITライセンスはMonatium Studioが持つ権利にのみ適用され、原作に関する権利を許諾するものではありません。原作のキャラクターやデザインを利用する際は、EPIDGamesの二次創作ガイドラインに従ってください。
- このリポジトリはトリッカル・リバイブの非公式二次創作物であり、EPIDGamesとは提携しておらず、承認も受けていません。

## 商標

Trickcal、Trickcal: Revive(トリッカル、トリッカル・リバイブ)およびその他の派生ブランドは、EPIDGamesの登録商標です。

## 外部データ

- 地球の地形データ: [Natural Earth](https://www.naturalearthdata.com/) (パブリックドメイン)
