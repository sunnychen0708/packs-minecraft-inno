# exaroton 與伺服器操作

> 規則以 [AGENTS.md](../AGENTS.md) 為準；本頁保留必要的操作方式與 **2026-10-08 最後確認**的狀態，並非即時伺服器狀態。

## 伺服器與權限

| Server | 用途 | 規則 |
| --- | --- | --- |
| `inno.exaroton.me` | 正式世界 | 唯讀可直接查；**寫入、下指令、開／關／重啟、UUID apply、安裝**每次都需使用者明確授權。不要自行開機。 |
| `innotest.exaroton.me` | 測試服 | 可依測試需求操作；**測完保持開機**，只有使用者明確要求才關機。必要重啟完成後仍須保持開機。 |

API Token 只放 GitHub Actions Secret `EXAROTON_API_TOKEN`，不得寫進 repo 或 request。所有 `ops/*-request.json` 都是一次性操作，執行完恢復 `noop`，不是待辦清單。

| Request | Workflow | 功能 |
| --- | --- | --- |
| `ops/exaroton-request.json` | `exaroton-innotest.yml` | innotest 狀態、部署、指令與 live suite |
| `ops/mineflayer-request.json` | `mineflayer-innotest.yml` | 測試玩家連線 |
| `ops/inno-maintenance-request.json` | `exaroton-inno-maintenance.yml` | inno 唯讀／離線 UUID 維護 |
| `ops/release-request.json` | `release-request.yml` | 版本發佈 |

## Discord 貓／狼收集進度榜（只支援手動更新）

- Workflow：[inno animal collection (read only)](../.github/workflows/inno-animal-progress.yml)，只有 `workflow_dispatch`，**沒有** push／cron／定時更新。
- 設定：在 Discord 頻道 **編輯頻道 → 整合 → Webhook**（或伺服器設定 → 整合 → Webhooks）建立一個 Webhook；將完整 URL 存到此 GitHub repo 的 **Settings → Secrets and variables → Actions → Repository secrets**，名稱為 `DISCORD_WEBHOOK_URL`。不可把 URL 貼進 Issue、workflow、原始碼或 Actions 日誌。`EXAROTON_API_TOKEN` 沿用既有 Secret。
- 更新：GitHub **Actions → inno animal collection (read only) → Run workflow → 選 main → Run workflow**。首次執行建立一則 Discord Embed；以後手動執行只編輯這一則，避免洗版（建議在 Discord 將它釘選）。
- 為了記住 Discord 訊息，首次成功發送後 workflow 會透過 GitHub API 在 `main` 建立 `ops/discord-animal-message.json`，**僅包含公開數字識別碼** `webhook_id` 和 `message_id`，不含 token。訊息若已被刪除或 Webhook 更換，下次執行才發新訊息並更新檔案。此狀態檔由 `GITHUB_TOKEN` 的 `contents: write` 權限維護；若 GitHub 分支保護阻止 workflow 寫入，需先調整允許方式，否則新訊息可能已送出但狀態寫入失敗。
- 執行期間僅使用 exaroton **GET** 讀取正式 `inno` 玩家 `world/players/advancements/<online-uuid>.json`；不開機、不操作 Minecraft 指令、不寫入世界。資料為**各玩家曾經馴服過的變種**，不是目前活著的寵物數量，離線也能查最後儲存的進度。
- 四位玩家固定是 `SunnyChen`、`penguin0531`、`geena0701`、`Felicitypeng`。只要有一位玩家存檔讀取失敗／內容不完整，整個發送流程失敗，不會發布不完整清單。
- 若 Secret 未設定，workflow 會在開始讀取前給明確錯誤；需使用者自行到 Discord 建立 Webhook 並填入 GitHub Secret。此 workflow 不會自動建立 Discord 頻道或 Webhook。

## 玩家身分與資料遷移

- `innotest` 為 `online-mode=false`。預設使用 `penguin0531`、`geena0701`、`Felicitypeng` 三個 Mineflayer bot；**`SunnyChen` 留給使用者真人登入**，必要時才作第四個 bot。
- 正確資料遷移方向是 **inno 的 online UUID → innotest 的 offline UUID**；offline UUID 由 `OfflinePlayer:<name>` 的 UUIDv3 規則產生，不是直接搬舊的 production offline 玩家檔。
- Java 26.3 玩家資料路徑是 `world/players/data/<uuid>.dat`（含 `.dat_old`）、`world/players/advancements/<uuid>.json`、`world/players/stats/<uuid>.json`；不是舊的 `world/playerdata`、`world/advancements`、`world/stats`。
- `migrate-inno-online-to-innotest-offline` 會複製玩家檔、改寫確切 UUID 參照、處理 entity region owner UUID、更新白名單與 OP UUID，並保留備份及驗證結果。
- Production UUID maintenance 僅由獨立的 `exaroton-inno-maintenance.yml` 進行；`uuid-migrate-dry-run` 唯讀，`uuid-migrate-apply` 必須得到當次明確授權且確認 **inno OFFLINE**，不得因此啟動 inno。合併 online/offline stats 時，數字計數器**相加**，用 `uuid-migration-stats-sum-state.json` 避免重複加入。

## Mineflayer 與實機驗證

`scripts/mineflayer26/bootstrap.py`、`scripts/mineflayer26/keepalive.js` 支援 26.3 測試身分；只允許四個名稱，且鎖定 innotest。連線會序列化，閒置 bot 停用自主物理並抑制部分移動封包以避開 26.3 相容問題。因此它們適合測**玩家在線、Trigger、多人狀態隔離**，不能假裝是可正常走動、滑鼠操作的真人 client。

Copy/Paste 正式多人回歸用 `scripts/build-copy-paste-multiplayer-test.py` 產生 3D 房屋測試包，再由 innotest controller 執行 `run-copy-paste-multiplayer-test`。A、B 分別為 `penguin0531`／`geena0701`；等指定玩家穩定在線，檢查**本次**唯一 run marker 與全部 `MCCMP_CHECK`，只在收到 `MCCMP_RESULT PASS` 後判成功，不得重用舊 log 或用固定 sleep 當完成依據。

- 使用精確的三包來源，不要保留同一 pack 的兩個 ZIP（重複載入會干擾測試）。
- 清除測試建築、暫存 harness、tag、scoreboard、測試用 forceload，還原玩家及倉庫資料；需要 `/reload` 時只在清理／部署範圍內操作。
- **每次 innotest 測試最多 240 秒**；完整 coverage 切成獨立 shard，不可因時限少驗。Utilities／Warehouse 用 `run-live-suite`；重查可用 `utilities-recheck`、`warehouse-recheck`，Copy/Paste 用 `recheck`。
- 把 parser、bot disconnect、chunk 未載入、timeout 與真正的 datapack assertion FAIL 分開處理。CI／Mineflayer PASS 不代表真人 G 鍵、Dialog 或準星操作 PASS。

詳細測試層級與證據見 [驗證方式](datapack-validation.md) 和 [功能覆蓋表](innotest-coverage.md)。

## 最後確認的部署與狀態（2026-10-08）

- **inno**：正式世界的 `world/datapacks` 已安裝 `utilities-v3.8.zip`、`warehouse-v4.7.zip`、`copy-paste-v1.8.zip`，舊 ZIP 已移除。當次 checksum／部署及唯讀查核 PASS（run `37659192281`），**當次保持 OFFLINE**。
- **innotest**：Copy/Paste 驗證完成後，使用者當次明確要求關機；最後 `OFFLINE`、0 players（[run 37719692728](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37719692728)）。這是**歷史快照**，下次操作前要再讀即時狀態；不是「一般測完要關機」。
- **現行版本**：Utilities v3.8、Warehouse v4.7、Copy/Paste v1.8；詳細驗證結果見 [功能覆蓋表](innotest-coverage.md)。
