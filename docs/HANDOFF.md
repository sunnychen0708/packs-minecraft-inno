# 交接（2026-10-08）

> 給下一位接手的人。請一律用**繁體中文**與使用者溝通；技術規則以 `AGENTS.md` 為準，本文件只記目前狀態與最新證據。

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

舊的 `Minecraft_Warehouse_26.3_v4.0.zip` 與 `utilities-v3.4.zip` 已移除。部署 job 驗證 release asset checksum 後上傳，結果 PASS 且 `server_remains_offline: true`；唯讀 `inno-storage-status` 再確認三個 ZIP 都存在（run 37659192281）。

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

- **v1.8 exact build 的完整 3D-house innotest multiplayer regression 已 PASS**：run [37718900567](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37718900567)。
- 所有 `MCCMP_CHECK` PASS，包含：獨立選區／Clipboard／mcc_id、完整 Blueprint state、Build/BOM、六方向 Move、Rotate 90/left/180、兩軸 Flip、Blueprint 六方向微調／轉向／翻面／reset、Undo/Redo guard、Cut/Paste、A/B isolation。
- v1.8 新行為也有直接 assertion：新的 Copy／Cut，以及 Cut → Undo → Redo 重建 Clipboard 後方向回到 0°、未翻面。
- Java 26.3 Blueprint matcher 全量 live gate 已 PASS：run [37719130915](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37719130915)，`states=35724 expected=35724 fail=0 air_ret=0`；35724 = 35,720 個合法 state + 4 個重複 regression case。
- v1.8 **發布當時**依使用者要求走 direct/no-gate；這只代表 release-time gate 被跳過，不能再寫成「v1.8 尚未 live 驗證」。
- 兩個真人 client 同時點 UI 仍沒有正式 evidence；Issue #49 的真人 UI 是較早的歷史證據。

## innotest / Mineflayer

- 例行規則仍是：測完保持 ONLINE；只有使用者要求才關機。
- **目前狀態是 OFFLINE / 0 players**：2026-10-08 Copy/Paste 完整驗證後，使用者明確要求關機；最後確認 run [37719692728](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37719692728)。
- Mineflayer 預設使用 `penguin0531`、`geena0701`、`Felicitypeng` 三個 bot，保留 `SunnyChen` 給真人登入監督或 Computer Use。
- Copy/Paste 正式 live regression 使用 `scripts/build-copy-paste-multiplayer-test.py` 的 3D house；目前 actor A/B 是 `penguin0531` / `geena0701`，第三個 bot 可保持在線，SunnyChen 不需要參與。
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

- PR #54（`claude/innotest-house-regression`）已關閉，不合併舊 datapack 本體。
- 有價值的 live-regression infrastructure 已由 PR #70 整理進 `main`。
- repo consistency 修正已由 PR #71 合併；#70 帶入的 runner dispatch 字面 `\\n` SyntaxError 也已修正並通過 CI。
- 目前沒有 open PR。
- 這次 repo cleanup 會把 #71 之後可合併的測試／ops 歷史壓成單一 commit，並把仍存在的舊工作 branch ref 對齊最新 `main`；branch 名稱本身若無可用 delete-ref API，保留名稱不代表還有未合併內容。
- 新 branch 不用 `claude/` 前綴；commit 作者/committer 與署名規則見 `AGENTS.md`。

## 合作偏好

- 使用者要「做／修／驗」時直接做，不要只給步驟。
- Minecraft 名詞用台灣常用譯名或 English；避免中國大陸用語。
- Warehouse 測試一定尊重玩家自訂分類，不假設 default rule 就是真實分類。
- 介面偏好 Dialog、按鈕少且乾淨；不要加多餘狀態文字。
- 玩家開 Copy/Paste 介面寫「按 G → 建築工具」，不要叫玩家打 `/trigger copypaste`。
- 大型行為設計或有多種合理產品選擇時問使用者；明顯 bug、過期文件、測試基礎設施錯誤直接修。
