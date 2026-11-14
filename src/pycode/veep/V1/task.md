# TODO: HIVE WAV SHELF (VEEP Project Tasks)

## 📌 Project: VEEP (Vinyl Bee Beep Player)

### ⏹️ ACTIVE TASK: HIVE WAV SHELF
蜂の巣状（Hexagonal）のレイアウトを採用した、WAVファイルのライブラリ/管理シェルフ。

---

### 1. Visual Concepts (HIVE)
- [ ] **Hexagonal Grid**: ファイル一覧を六角形のタイルで表示。
- [ ] **Honeycomb Layout**: 各タイル（セル）がミツバチの巣のように隙間なく並ぶグリッドシステム。
- [ ] **Cell Feedback**: ホバー時にセルの縁がゴールドに発光するエフェクト。

### 2. Shelf Features (SHELF)
- [ ] **Multi-File Persistence**: 読み込んだ複数のWAVファイルを一時保持し、切り替え可能にする。
- [ ] **Active Cell**: 現在ロードされているファイル（セル）を特定の色（ハニーイエロー）で強調。
- [ ] **Quick Metadata**: セル内にファイル名の略称や演奏時間を表示。

### 3. Implementation Details
- [ ] **CSS Grid/Clip-path**: 六角形を描画するためのCSS定義。
- [ ] **WAV Storage**: IndexedDBまたはSession Storageを使用したファイル参照の管理。
- [ ] **Integration**: `veep.html` への統合とレコードプレーヤーとの連動。

### 4. Mobile & Overlay UI (Optimization)
- [ ] **Mobile Layout**: スマートフォン等の縦画面に対応したレスポンシブデザインの構築。
- [ ] **HIVE Overlay Mode**: モバイル環境では HIVE（シェルフ）をオーバーレイ表示（重ね合わせ）にし、スペースを有効活用する。
- [ ] **Touch Optimization**: レコードのスワイプ操作や六角形セルのタップ感の向上。

---
*Created by Antigravity*
