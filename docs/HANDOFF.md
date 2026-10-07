# 交接（2026-10-08）

> 給下一位接手的人。請一律用**繁體中文**與使用者溝通；技術規則以 `AGENTS.md` 為準，本文件只記目前狀態與最近證據。

## 目前版本

| Pack | Source | Latest release |
| --- | --- | --- |
| Utilities | v3.8 | `utilities-v3.8` |
| Warehouse | v4.7 | `warehouse-v4.7` |
| Copy/Paste | v1.8 | `copy-paste-v1.8` |
| cat-door-sounds | v1.0 | `cat-door-sounds-v1.0` |

三個 datapack 的 source 與最新 GitHub Release 已對齊。

## Production inno

2026-10-08 的 offline deploy 已把 production `world/datapacks` 整理成：

- `utilities-v3.8.zip`
- `warehouse-v4.7.zip`
- `copy-paste-v1.8.zip`

舊的 `Minecraft_Warehouse_26.3_v4.0.zip` 與 `utilities-v3.4.zip` 已移除。部署 job 驗證三個 release asset checksum 後上傳，結果 `PASS` 且 `server_remains_offline: true`；之後唯讀 `inno-storage-status` 再確認三個 ZIP 都存在（run 37659192281）。

**不要自行啟動 inno。** 任何 inno 寫入、開關機、指令或 maintenance apply 都要使用者每次明確下令；唯讀檢查可直接做。

## 最新 live 驗證

### Utilities v3.8

- innotest live suite 已 PASS。
- v3.7 舊世界資料載入 v3.8 後保留：`v3.7_world_data_survives_v3.8_load` PASS。
- 主要證據：run 37642068254。
- 詳細功能 coverage 見 `docs/innotest-coverage.md`。

### Warehouse v4.7

- v4.6 的分類、Pick、API、forceload、migration、滿箱／溢位、背景 Compact、G 主畫面 release gates 已 PASS。
- v4.7 另外完成跨維度 Compact／merge regression：主世界、地獄、終界共 27 checkpoints PASS，並確認 recovery PASS。
- 證據：run 37656341833。
- v4.7 在這次 live validation 後重新發布。

### Copy/Paste v1.8

- **最後一次完整 3D-house innotest live regression 是 v1.7**：run 37644325643。
- 該 run 所有 `MCCMP_CHECK` PASS，包含：完整 Blueprint state、Build/BOM、六方向 Move、Rotate 90/left/180、兩軸 Flip、Blueprint 位移／轉向／翻面／reset、Undo/Redo guard、Cut/Paste、A/B isolation。
- v1.8 只修正新的 Copy／Cut，以及 Cut → Undo → Redo 重建 Clipboard 時，會把方向重設為 0°、未翻面。
- v1.8 當時依使用者要求**直接發布/部署、不再重跑完整 live suite**。所以不要把 v1.7 的完整 PASS 寫成「v1.8 exact build 已 live PASS」。
- 兩個真人 client 同時點 UI 仍沒有正式 evidence。

## innotest / Mineflayer

- `innotest` 測完保持 ONLINE；只有使用者要求才關機。
- Mineflayer 預設使用 `penguin0531`、`geena0701`、`Felicitypeng` 三個 bot，保留 `SunnyChen` 給真人登入監督或 Computer Use。
- persistent bot session 可重用，不要每個測試都重開；只有需要 SunnyChen bot 時才用四人模式。
- Copy/Paste 正式 live regression 使用 `scripts/build-copy-paste-multiplayer-test.py` 的 3D house；舊 2×2 / 舊 Trigger harness 不再算正式驗證。
- Utilities / Warehouse 使用 `run-live-suite`；詳細操作見 `docs/exaroton-operations.md`。

## ops request baseline

repo 乾淨狀態時，以下 request 一律是 `noop`：

- `ops/exaroton-request.json`
- `ops/mineflayer-request.json`
- `ops/inno-maintenance-request.json`
- `ops/release-request.json`

request 是一次性 trigger，不是待辦事項；操作完成後要回 `noop`。

## Release / validation 規則

- 一般 release 走 gated release。
- 只有使用者明確要求「直接 release / 不再驗」時，才使用 direct/no-gate 路徑；跳過哪一層就要明講，不能把 skipped/failing 寫成 PASS。
- 能不跑 workflow 就不跑；GitHub Secret / 遠端 innotest 操作需要時才跑，完整 CI 留到階段完成或 release 前。
- static、official server runtime、Mineflayer live、Windows real client 是不同證據層級，不能互相冒充。

## Git / PR 狀態

- 舊 PR #54（`claude/innotest-house-regression`）已關閉。
- 有價值的 live-regression infrastructure 已整理後由 PR #70 合進 `main`，沒有把舊 v1.7/v4.6 datapack 本體倒灌。
- #70 初次 merge 帶入一個 runner dispatch 的字面 `\\n` SyntaxError；本次 repo consistency 整理會修掉並要求 CI 綠燈後再合。
- 新 branch 不用 `claude/` 前綴；commit 作者/committer 與署名規則見 `AGENTS.md`。

## 合作偏好

- 使用者要「做／修／驗」時直接做，不要只給步驟。
- Minecraft 名詞用台灣常用譯名或英文；避免中國大陸用語。
- Warehouse 測試一定尊重玩家自訂分類，不假設 default rule 就是真實分類。
- 介面偏好 Dialog、按鈕少且乾淨；不要加多餘狀態文字。
- 玩家開 Copy/Paste 介面寫「按 G → 建築工具」，不要叫玩家打 `/trigger copypaste`。
- 大型行為設計或有多種合理產品選擇時問使用者；明顯 bug、過期文件、測試基礎設施錯誤直接修。
