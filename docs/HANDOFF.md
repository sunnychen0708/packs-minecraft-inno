# 交接（2026-10-07）

> 給下一位接手的人。請一律用**繁體中文**與使用者溝通。

## 1. 目前狀態

| Pack | Source | Latest release |
| --- | --- | --- |
| Utilities | v3.8 | `utilities-v3.7` |
| Warehouse | v4.6 | `warehouse-v4.5` |
| Copy/Paste | v1.7 | `copy-paste-v1.6` |
| cat-door-sounds | v1.0 | `cat-door-sounds-v1.0` |

- Utilities v3.8（傳送落點置中修正）與 Warehouse v4.6（倉庫區塊常駐載入、查詢讀取未載入箱子的庫存）只有原始碼，尚未發布；其他原始碼版本都已發布。
- 發布：`.github/workflows/release-pack.yml` 會驗證、打包、建 Release。兩種觸發方式：在 `main` 推 `<pack>-v<版本>` tag；或手動執行這個 workflow（`workflow_dispatch`，ref 選 `main`，輸入 `tag` 例如 `utilities-v3.7`），全部 gate 通過後由 workflow 在該 `main` commit 建 annotated tag 再建 Release。雲端 session 不能推 tag，要用手動執行。**發布前要先問使用者。**
- 2026-10-06 曾改寫 `main` 的最後一段歷史，拿掉 AI 工具署名並刪除舊分支。改寫前完整備份在使用者電腦 `C:\Users\sunny\repo-backups\packs-minecraft-inno-before-rewrite-20261006.git`。
- **最新 CI 狀態**：Utilities、Warehouse、Copy/Paste 專用 26.3 runtime 與三包 together compatibility 都通過。
- **最新多人實機狀態**：2026-10-07 最後一輪 Copy/Paste assertions 在四個 Mineflayer 玩家在線時全部 PASS，最後 `MCCMP_RESULT PASS`；但同一份持久化 server log 也保留前面數次失敗（harness parser error、bot invalid move、Undo/Redo FAIL）。controller 已新增 current-session `/ERROR]:` gate；在 fresh run 再通過前，不要稱為 clean live validation。
- **最新伺服器狀態**：`innotest.exaroton.me` 已關機，最後讀到 `OFFLINE`、`0/10`、Vanilla 26.3。
- exaroton / bot / production maintenance 的操作細節集中在 [`docs/exaroton-operations.md`](exaroton-operations.md)。

## 2. 和使用者合作

- **繁體中文**，直接、簡短。使用者最在意「功能真的正確」，不要只看文字說明或 commit message。
- **不要加任何 AI 工具署名**：commit 不加 `Co-Authored-By`，PR／Release 說明不加 Generated with… 或工作階段連結。
- 使用者叫「做 / 修 / 驗」時要實際操作 repo / CI / 測試，不要只提供步驟。
- **真人 client 測試直接開始跑，不要先問**（通常是使用者不在用電腦時才會要求）。
- 驗證要分層說清楚：static、official server runtime、Mineflayer multiplayer、Windows real client 不是同一件事，不能互相冒充。
- Warehouse 玩家會**自訂分類**，測試不能假設預設分類。
- 介面：使用者偏好 Dialog（乾淨、按鈕少、置中），不要加多餘狀態文字區塊；只改要求的部分。
- 不要有載入訊息；叫玩家開介面時寫「按 G」，不要叫玩家打 `/trigger copypaste`。
- 大改動或設計選擇先問；小 bug、測試基礎設施 bug、明顯技術債直接修。
- **版本號一律兩段**（例如 v1.6、v4.5），不要新增三段式版本。

## 3. exaroton / inno / innotest

### `innotest.exaroton.me`

- 測試服，可由 repo automation 啟停、部署 datapack、下 command、跑多人 regression。
- 目前 `online-mode=false`，讓四個測試玩家不用 Microsoft 授權即可登入。
- 四個 bot 名稱固定為：`SunnyChen`、`penguin0531`、`geena0701`、`Felicitypeng`。
- 玩家資料的正確遷移方向是：**`inno` online-mode UUID -> `innotest` 同名 offline UUID**。
- 四人資料遷移入口會把 `players/data/*.dat`、`.dat_old`、`players/advancements/*.json`、`players/stats/*.json` 從 production online UUID 寫到 innotest offline UUID；同時改寫 copied player NBT 內部 UUID reference，並掃描 innotest 各維度 `entities/*.mca`，把寵物/坐騎等 entity 對四名玩家的 online UUID reference 改成同名 offline UUID。修改前會備份，寫後會驗證。
- Minecraft Java 26.3 的玩家資料路徑是 `world/players/...`，**不是**舊的 `world/playerdata` / `world/advancements` / `world/stats`。

### `inno.exaroton.me`

- Production 世界。
- **任何寫入 inno 都要使用者明確下指令**（裝 datapack、改檔、執行指令、開關機、UUID maintenance apply），每次都要；讀取不用問（見 `AGENTS.md`）。
- repo 內的 **offline UUID maintenance** 是寫入 inno 的入口，同樣要使用者明確下指令才能 apply；dry-run 只讀取。
- 特例 workflow：`.github/workflows/exaroton-inno-maintenance.yml` + `scripts/exaroton_inno_uuid_migrate.py`。
- Production maintenance 必須要求 `inno` 已經 OFFLINE，而且 maintenance 自己**不得啟動** production server。先 dry-run，再 apply。\n- Production offline/online stats 現在採 **sum-per-counter** 真正累加；`uuid-migration-stats-sum-state.json` 防止重跑時把同一份 offline 歷史再加一次。若偵測到舊 max-per-counter migration backup，會用 backup 還原 baseline，再保留之後新增的 online progress。
- Secret 只存在 GitHub Actions `EXAROTON_API_TOKEN`，不要寫進 repo、request JSON 或 log。

### ops baseline

`ops/` 裡的 request 檔案是操作觸發器，不是工作清單。正常乾淨狀態應該全部回到 `noop`：

```text
ops/exaroton-request.json
ops/mineflayer-request.json
ops/inno-maintenance-request.json
```

不要把最後一次 destructive / state-changing request 留在 `main` 當 baseline。

完整操作方式看 [`docs/exaroton-operations.md`](exaroton-operations.md)。

## 4. Mineflayer 26.3 現況

- 入口：`.github/workflows/mineflayer-innotest.yml`。
- bootstrap：`scripts/mineflayer26/bootstrap.py`。
- client：`scripts/mineflayer26/keepalive.js`。
- 目標 host 硬鎖 `innotest.exaroton.me`，只接受上面四個玩家名稱。
- 四 bot **依序登入**，上一個 spawn 完才建立下一個，避免 26.3 初始同步 race。
- physics 關閉；idle 測試 client 會抑制 client-originated movement packet，但保留 teleport confirm、keepalive 等必要流量。
- 原因：目前 patched Mineflayer 26.3 在 server-side teleport 後可能送出 invalid movement packet，先前會導致 `Invalid move player packet received` / `socketClosed`。
- 修正後四 bot 已完整 hold 5 分鐘並成功結束 workflow；可穩定提供 4/10 真實玩家實體給 datapack 多人 regression。
- 這套 client 適合 presence、trigger/state、多玩家 server-side regression；**不要假設目前已能當完整走路/操作世界的通用 client**。

## 5. Copy/Paste v1.7 重要設計

- **介面**：玩家按 G →「建築工具」（`/trigger copypaste` 仍可，但玩家提示統一叫按 G）。主畫面 `ui/show`、調整預覽 `ui/adjust`、更多 `ui/more`、直接改原本建築 `ui/edit`。聊天教學 `/trigger cphelp` 是步驟式。
- **Anchor**：預設 pos1；自訂 anchor 不限制必須在選區內，否則無法做大半徑旋轉。
- **轉向／翻面以玩家面向為準**：Blueprint 用 `bpturnright` / `bpturnleft` / `bpflip` / `bpflipfb` / `bpreset`；直接改建築用 `turnright` / `turnleft` / `flip` / `flipfb`。
- **Undo/Redo**：多人狀態分 lane；目前 live multiplayer regression 已驗同 tick Move、Undo、Redo、Rotate、Cut/Paste 與 A/B 各自 Undo/Redo 不互相污染。
- **扣料**：先扣玩家背包 0～35 格與副手，再扣 Warehouse。Undo／扣料失敗時依來源退料。
- **物品名稱**：`scripts/gen-item-names.py` 從 26.3 server reports 產生名稱與最大堆疊表。Minecraft 版本更新時要重跑。
- 材料檢查只報告，不扣料；Build 才真正扣料與施工。

## 6. Warehouse v4.5 重要設計

- 主畫面是 `dialog/main.json`；G 和「回主選單」一致。
- 箱子詳細頁返回原本清單頁，依 `wh_back` / `ui/back_from_code` 邏輯返回。
- 頁面寬度維持 ≤ 390；三欄按鈕 120 寬。
- Warehouse 是 Copy/Paste 與 Pick 共用的 shared storage backend。
- v4.6 起已註冊箱子的 chunk 常駐 forceload（`warehouse:chunks/ensure|refresh|release`，自己加的記在 `warehouse:forceload chunks`，別人加的不碰；每 10 秒補回）。Copy/Paste 的 `place_buffer` 會無條件 `forceload remove` 施工區，所以靠定期補回。移除 Warehouse 前先 `/function warehouse:chunks/release`。
- 玩家可能自訂分類；任何測試都不能假定物品一定在預設箱位。

## 7. Minecraft 26.3 的坑

- 玩家資料：`world/players/data`、`world/players/advancements`、`world/players/stats`。
- inline item modifier 用 `"type"`，不是 `"function"`；扣物品要用 `store success` 確認。
- `multi_action` Dialog 必須有按鈕，否則頁面打不開。
- Dialog JSON 是 registry：`/reload` 不會更新 `dialog/*.json`，要重新進世界；function 產生的 inline Dialog 不受此限制。
- `summon` 整數座標會置中 +0.5；`block_display` 要用 `X.0 Y.0 Z.0` 對格線。
- 清空來源用 `fill ... air strict`；`clone` 的 `strict` 位置要正確，避免附著方塊掉落。
- macro 行少 `$` 會把 `$(var)` 當 literal；validator 會擋。
- exaroton test server 在高負載時可能 `Can't keep up`；live regression **不能用固定 sleep 決定完成**，要等該次 run 的 unique marker + `MCCMP_RESULT`。

## 8. 怎麼跑測試

### 靜態 / CI

```bash
for p in warehouse copy-paste utilities; do
  python3 scripts/validate-datapack.py "$p"
  python3 "scripts/test-$p.py"
done
python3 scripts/test-datapack-compatibility.py
```

### 官方 26.3 server runtime

需要 Java 25 + official server.jar：

```bash
python3 scripts/test-copy-paste-runtime.py --java $J --server-jar $S --accept-eula
python3 scripts/test-utilities.py          --java $J --server-jar $S --accept-eula
python3 scripts/test-warehouse-runtime.py  --java $J --server-jar $S --accept-eula
python3 scripts/test-datapack-compatibility.py --java $J --server-jar $S --accept-eula
```

Copy/Paste runtime 失敗時會印 `MCCST_DIAG_DROP_<步驟>` / `MCCST_DIAG_DIFF_<步驟>`。

### innotest 四人 multiplayer live regression

當 Copy/Paste 有多人 state / trigger / Undo / clipboard / Blueprint 相關改動時，除了 CI 還要跑：

1. 確認 / 啟動 `innotest`。
2. `ops/mineflayer-request.json` 觸發四 bot 300000 ms。
3. 等 `READY 4/4`。
4. `ops/exaroton-request.json` 觸發 `run-copy-paste-multiplayer-test`。
5. 要看到 `COPY_PASTE_MULTIPLAYER_LIVE_TEST=PASS` 與 `MCCMP_RESULT PASS`。
6. 測完關 `innotest`，再讀 status 確認 `OFFLINE` / `0/10`。
7. 三個 ops request 全部 reset 成 `noop`。

2026-10-07 最後一輪 assertions 全部 PASS，涵蓋：independent selection、clipboard、unique `mcc_id`、Blueprint、Move、work/undo lane、Undo/Redo、Rotate、Cut/Paste、A/B isolated Undo/Redo。不過同一 server log 有前面失敗的歷史紀錄；新的 current-session server-error gate 尚未在 fresh innotest session 重跑，所以目前只能稱為 final assertion pass，不是 clean live validation。

## 9. 真人 client 工具（`scripts/real-client/`，Windows）

- `mcdrive.py`：Win32 `SendInput` 送鍵盤／滑鼠；Minecraft 不在前景時拒絕送輸入。
- `realplay.py`：`trig()` 必須看到遊戲自己的 trigger confirmation；`reload_packs()` 要看到 reload + `/datapack list enabled`。
- `mcworld.py` 讀存檔；`defaults.json` 補 26.3 palette 預設屬性；`xform.py` 算 transform 後 blockstate。
- `stage1`～`stage13` 覆蓋 Warehouse 註冊/分類、Copy/Paste 主流程、材料、轉向翻面、Dialog、三包一起、Utilities vein XP 等。
- Dialog JSON 改動仍要重新進世界才能驗。

使用者電腦注意：

- `options.txt`：攻擊=滑鼠右鍵、使用=滑鼠左鍵、蹲下=左 Ctrl。不要假定 vanilla 預設，也不要改使用者設定。
- 開箱／註冊要送左鍵；右鍵在創造可能直接打掉箱子。
- 點 Dialog 前準星看天空，避免滑鼠事件掉回遊戲。
- Dialog 開著時聊天欄通常打不開，先關 UI 或直接點按鈕。
- Blueprint rotate/mirror 設定會跨 Copy 保留，測試前先 `bpreset`。

## 10. MCC-Test 本機測試世界

> 測試一律直接在 innotest 跑（見 `AGENTS.md`）。MCC-Test 只有使用者明確要求時才用。

- 只改 `%APPDATA%\.minecraft\saves\MCC-Test`，不要碰使用者其他世界；改 datapack 前先備份。
- 世界開著時 datapack ZIP 可能被鎖，不能刪 / 改名；要換檔名先退出世界。
- Warehouse 存量會隨測試變動，固定存量測試前要補齊或用 stage 自己重建 fixture。
- 使用者也會在這個世界自己玩；跑 stage 前先確認 fixture 狀態，不要假定前一次測試結束時的建築與箱子還在原位。

## 11. 目前仍未覆蓋 / 不要誤稱已驗

- **兩個 Windows 真人 client 同時操作**仍未測。現在通過的是四個 Mineflayer 真玩家實體 + 兩人同 tick server-side multiplayer regression，不等於兩個真人 UI client。
- GitHub CI 不跑 `scripts/real-client/`；CI 綠燈不代表 G、Dialog 點擊、crosshair raycast、真人 `/trigger` 全部正常。
- Blueprint 覆蓋檢查取消等部分 UI / client 行為仍需對應 real-client stage 才能叫「真人實機驗過」。
- Utilities v3.7 工具等級檢查與部分 Copy/Paste legacy trigger cleanup 主要由 headless runtime 覆蓋；若改玩家可見行為要補真人 client 驗證。
- `build-copy-paste-live-test.py` 是舊 Trigger harness，不能取代 `scripts/real-client/`；多人 state 則以新的 `build-copy-paste-multiplayer-test.py` + innotest live runner 為準。
- 真實世界 paste 的 clone 仍會產生正常 block update，這是為了讓柵欄、紅石等邊界連接正確。
