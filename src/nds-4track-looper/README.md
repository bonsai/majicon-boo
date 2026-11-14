# 4-Track Voicer / Looper (NDS)

NDS実機向けの4トラック・自動ボイパ・ルーパーの雛形です。  
通信機能は未実装。devkitPro (C言語 / libnds) でビルドします。

## 必要環境

- [devkitPro](https://devkitpro.org/wiki/Getting_Started)（devkitARM + libnds）
- Windows の場合は **devkitPro MSYS** で `make` が使えること

## ビルド

### PowerShell（Windows）

```powershell
.\build.ps1
```

クリーンビルド:

```powershell
.\build.ps1 -Clean
.\build.ps1
```

`DEVKITARM` が未設定の場合は、既定で `C:\devkitPro\devkitARM` を参照します。

### MSYS / シェル

```bash
export DEVKITARM=/c/devkitPro/devkitARM   # 環境に合わせて
make
```

## 操作（設計）

- **下画面**: 上段4パッド = REC1〜4（タッチしている間だけ録音）、その下 = 再生
- **L**: 全トラックをループ再生
- **R**: 全トラック停止
- **START**: 終了

## 構成

| ファイル | 役割 |
|----------|------|
| `main.c` | 初期化・メインループ |
| `audio.c/h` | マイク録音・4トラックバッファ・再生 |
| `sequencer.c/h` | BPM・ループタイミング |
| `ui.c/h` | タッチ・2画面表示 |

サンプリング: 16kHz / 16bit モノ、1トラックあたり10秒まで。
