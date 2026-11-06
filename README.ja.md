# Monatium Studio モデル

[한국어](README.md) · [English](README.en.md) · **日本語**

モナティウム・スタジオが制作するトリッカル・リバイブ二次創作ゲームの制作に使用したモデルおよびBlenderスクリプトをまとめたリポジトリです。詳しい利用条件は、下記の[ライセンス](#ライセンス)および[著作権](#著作権)の項目をご参照ください。

## 構成

| パス | 内容 |
|---|---|
| `public/models/**.glb` | ゲームが読み込む完成モデル (glTFバイナリ) |
| `art/blender/**.py` | モデルを生成するBlenderヘッドレススクリプト (共通ツールは `art/blender/lib`) |
| `docs/art/` | アートガイドとモデルごとの設計文書 (`ART_GUIDE.md` から) |
| `public/ui/elf_logo_mono.svg` | 車両デカールのスクリプトが読み込む入力 |
| `index.html`, `viewer.ts`, `vite.config.ts` | モデルビューア（下記 [モデルビューア](#モデルビューア)） |

## 再生成

Blenderが必要です (`blender` がPATHにあるか、macOSの標準インストール先)。

```sh
npm run model -- art/blender/<分類>/<名前>.py
```

結果は同じ名前の `public/models/<分類>/<名前>.glb` に書き出されます。

## モデルビューア

`public/models` 以下のモデルをブラウザで見られます。ビューアは [strawberry-cake-engine](https://github.com/Monatium-Studio/strawberry-cake-engine) のモデルビューアを使います。
Node.js 20.19 以上（または 22.12 以上）が必要です。

```sh
npm install              # 初回のみ（エンジンと Vite を取得します）
npm run viewer           # 開発サーバー → http://127.0.0.1:5180/
```

静的サイトとしてビルドすることもできます。モデルを含む成果物が `dist/` に出力され、どのパスに置いても動きます。

```sh
npm run viewer:build     # dist/ にビルド
npm run viewer:preview   # ビルド結果を確認 → http://127.0.0.1:5181/
```

**操作**

| 操作 | 方法 |
|---|---|
| モデルを選ぶ | 左のリストをクリックします。ページを読み込み直さず、その場で切り替わります |
| 検索 | `/` または Ctrl・Cmd+K で検索欄に入ります。空白で区切った語をすべて含むパスのモデルだけが残ります。↑↓で選び、Enter で開き、Esc で消去します |
| 前後のモデル | リストをクリックしてフォーカスし、↑↓を押します |
| 回して見る | ドラッグで回転、ホイールで拡大・縮小、右ドラッグで移動 |
| アドレス | 表示中のモデルは `?model=<分類>/<名前>.glb` としてアドレスに残ります。再読み込み・戻る・リンク共有ができます |
| ほっぺリグ | ほっぺのボーンがあるキャラクターは右下に操作パネルが出ます：P ふくらませる、S つぶす、L・R・B 引っぱる、Space 離す、H 揺らす、J 走る |

`npm run model` でモデルを作り直したら、リストで選び直すか再読み込みすると新しいファイルが表示されます。

## AI生成物

このリポジトリのBlenderスクリプトと文書はAI(AnthropicのClaude)を活用して作成され、モデル(glb)はそのスクリプトで生成されました。Monatium Studioが方針を決め、結果を確認しました。

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
