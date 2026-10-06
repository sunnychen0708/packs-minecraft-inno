# 交接（2026-10-06）

> 給下一位接手的人。請一律用**繁體中文**與使用者溝通。

## 1. 目前狀態

| Pack | 版本 | Release |
| --- | --- | --- |
| Utilities | v3.4.1 | `utilities-v3.4.1` |
| Warehouse | v4.4.2 | `warehouse-v4.4.2` |
| Copy/Paste | v1.3.1 | `copy-paste-v1.3.1` |
| cat-door-sounds | v1.0 | `cat-door-sounds-v1.0` |

- 所有原始碼版本都已發布，遠端只剩 `main` 分支，沒有進行中的 PR。
- 發布：在 `main` 推 `<pack>-v<版本>` tag，`.github/workflows/release-pack.yml` 會驗證、打包、建 Release。**打 tag 前要先問使用者。**
- 2026-10-06 改寫過 `main` 的最後一段歷史，拿掉所有 AI 工具署名，並刪除所有舊分支。改寫前的完整備份（含所有舊分支）在使用者電腦 `C:\Users\sunny\repo-backups\packs-minecraft-inno-before-rewrite-20261006.git`。

## 2. 和使用者合作

- **繁體中文**，直接、簡短。使用者沒耐心，最在意「功能真的正確」。
- **不要加任何 AI 工具署名**：commit 不加 `Co-Authored-By` 行，PR／Release 說明不加「Generated with …」或工作階段連結，作者一律是使用者的 git 身分。
- **真人 client 測試直接開始跑，不要先問**（使用者不在用電腦時才會叫你做）。
- 驗證要用**真實情境**：3D、多種方塊、真的從 Warehouse／背包扣料、真的點 Dialog；結果讀存檔判定，不看 log 的 PASS。不要把「headless server 通過」說成「實機驗過」。
- Warehouse 玩家會**自訂分類**，測試不能假設預設分類。
- 介面：使用者偏好 Dialog（要乾淨、按鈕少、置中），不要加狀態文字區塊；只改使用者要求的部分。
- 不要有載入訊息；要叫玩家開介面時寫「按 G」，不要叫玩家打 `/trigger copypaste`。
- 大改動或設計選擇先問（可用選項讓使用者選）；小 bug 直接修。

## 3. 重要設計

### Copy/Paste v1.3.1
- **介面**：玩家按 G →「建築工具」（`/trigger copypaste` 也可，但訊息一律叫玩家按 G）。全部是 function 產生的 inline Dialog，`/reload` 就會更新：主畫面 `ui/show`（9 顆）、`set 2` 調整預覽 `ui/adjust`、`set 3` 更多 `ui/more`、`set 4` 直接改原本建築 `ui/edit`。聊天教學 `/trigger cphelp` 是 1～5 步驟式。
- **轉向／翻面以玩家面向為準**：只動預覽 `bpturnright`／`bpturnleft`／`bpflip`／`bpflipfb`／`bpreset`（翻面換算在 `state/bp_flip_axis`：F·R(k)·M = R(−k)·(F·M)）；直接改建築 `turnright`／`turnleft`／`flip`／`flipfb`。舊的 `rotate`、`mirror`、`rotate90..270`、`flipx/z` 仍可用但不宣傳。
- **扣料**：先扣玩家背包 0～35 格與副手（有 components 的物品不用），再扣 Warehouse。Undo／扣料失敗退料時，背包扣的退回背包（依最大堆疊算空間，塞不下退 Warehouse），Warehouse 扣的退 Warehouse 入口箱再自動分類。記錄在 `bom/items` 的 `.inv` 與 `.taken`。
- **物品名稱**：`scripts/gen-item-names.py` 從 26.3 server `--reports` 產生 `function/names/load.mcfunction`（翻譯鍵與最大堆疊表）。**換 Minecraft 版本要重跑。**
- 材料檢查（job 2）只報告，不扣料（`materials/check_done`；v1.1～v1.2 曾經會直接施工）。

### Warehouse v4.4.2
- 主畫面一律是 `dialog/main.json`（G 和「回主選單」相同）。
- 選了某個箱子之後的頁面，返回會回到選它的那一頁：選箱時 `ui/back_from_code` 記到 `wh_back`，按鈕送 `wh_nav set 9` → `ui/back`；入口箱頁是 nav 17／37／57／67。`wh_back` 在 `load` 每次建立。
- 頁面寬度一律 ≤ 390（太寬會讓整頁偏右）；三欄按鈕 120 寬。

## 4. Minecraft 26.3 的坑

- **inline item modifier 用 `"type"`，不是 `"function"`**。巨集裡寫錯會無聲失敗（曾因此造成物品複製）；扣物品要用 `store success` 確認。
- **`multi_action` Dialog 一定要有按鈕**，否則整頁打不開（驗證器會擋）。
- **Dialog JSON 是註冊表**：`/reload` 不會更新 `dialog/*.json`，要退出再進世界。function 產生的 inline Dialog 不受影響。
- `summon` 整數座標會置中 +0.5；`block_display` 要用 `X.0 Y.0 Z.0` 才會對齊方塊格。
- 清空來源要用 `fill ... air strict`；`clone` 語法是 `... <dest> strict replace force`（`strict` 在模式前面），否則附著方塊會掉成物品。
- 巨集行少了 `$` 會把 `$(var)` 原樣印出（驗證器會擋）。

## 5. 怎麼跑測試

```bash
# 靜態
for p in warehouse copy-paste utilities; do python3 scripts/validate-datapack.py $p; python3 scripts/test-$p.py; done
python3 scripts/test-datapack-compatibility.py

# 官方 26.3 server（需要 Java 25 + server.jar，SHA1 33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c）
python3 scripts/test-copy-paste-runtime.py --java $J --server-jar $S --accept-eula
python3 scripts/test-warehouse-runtime.py  --java $J --server-jar $S --accept-eula
python3 scripts/test-datapack-compatibility.py --java $J --server-jar $S --accept-eula
```

使用者電腦上：server.jar 在 `C:\Users\sunny\mcai_data\local_server\server.jar`；Java 25 是啟動器內建的 `...Packages\Microsoft.4297127D64EC6_8wekyb3d8bbwe\LocalCache\Local\runtime\java-runtime-epsilon\windows-x64\java-runtime-epsilon\bin\java.exe`。本機沒有 `zip`，`build-pack.sh` 會失敗，改用 Python `zipfile` 以 pack 目錄為根打包。

Copy/Paste runtime 失敗時會印出 `MCCST_DIAG_DROP_<步驟>`（掉了什麼）、`MCCST_DIAG_DIFF_<步驟>`（哪一格不對）。

## 6. 真人 client 工具（`scripts/real-client/`，Windows）

- `mcdrive.py`：Win32 `SendInput` 送鍵盤／滑鼠。打指令會先清空聊天框；指令變成一般聊天或被拒絕就丟例外。Minecraft 不在前景時拒絕送輸入。
- `realplay.py`：`trig()` 必須看到遊戲回的「已觸發 [名稱]」；`reload_packs()` 要看到遊戲的「重新載入中！」並用 `/datapack list enabled` 確認每個 pack 都在；`join_world()` 等「加入了遊戲」，並自動按掉實驗性設定警告頁；存檔用「按 Esc 暫停」（單人不能 `/save-all`）。
- `mcworld.py` 讀存檔；`defaults.json` 補上 26.3 palette 省略的預設屬性。`xform.py` 算 rotate／mirror 後的預期 blockstate。
- `stage1`～`stage12`：場地、註冊、Copy/Paste 主流程、缺料、多箱、轉向翻面、選單、名稱、只檢查、背包扣料、Warehouse 返回按鈕、三包一起。`realplay.leave_world()`／`join_world()` 會退出／重進世界（含實驗性設定警告頁）。各腳本測什麼見 `datapacks/copy-paste/LIVE-VALIDATION.md`。
- 要重進世界（讓 Dialog JSON 生效）：Esc →「儲存並回到標題畫面」→「單人遊戲」→ 選 MCC-Test →「進入所選的世界」。視窗 870×519 時座標約為 (433,379)、(433,267)、(283,147)、(276,427)，先截圖確認。

**使用者電腦的坑：**
- `options.txt` 把**攻擊設為滑鼠右鍵、使用設為左鍵**。開箱子／註冊要送**左鍵**；送右鍵會在創造模式直接打掉箱子。不要改使用者的設定。
- 點 Dialog 按鈕前讓準星看天空（`tp @s ~ ~ ~ 0 -90`），否則滑鼠按下會被帶回遊戲。
- 有 Dialog 開著時聊天欄打不開，要先關畫面或直接用滑鼠點按鈕。
- 聊天欄最多 256 字；長的 `data modify ... Items` 要拆成多條 `item replace`。
- Blueprint 的旋轉／鏡像是玩家設定，會跨 Copy 保留；測試前先 `bpreset`。
- 世界難度不是和平，白天殭屍曬死會掉腐肉；掉落物檢查只算建築相關物品。

## 7. MCC-Test 測試世界

- 只能改 `%APPDATA%\.minecraft\saves\MCC-Test`（超平坦創造），不要碰其他世界；改 datapack 前先備份到 `.minecraft\backups\`。
- 現況：三包（Utilities、Warehouse、Copy/Paste）都已安裝；61 個大箱子已註冊到正確兩半、橡木板自訂分類到 11 號箱、小屋在原位（x1000 z1040）。使用者也會在這個世界自己玩（曾把小屋 Cut 走），測試前先確認小屋還在。Warehouse 存量隨測試變動，跑需要固定存量的段落前要先補（`stage5` 會自己重新配置）。
- 世界開著時 datapacks 裡的 ZIP 被鎖，不能刪或改名，只能覆蓋內容；要換檔名先 `leave_world()`。

## 8. 尚未處理

- 兩位真人 client 同時操作沒測過（`scripts/build-copy-paste-multiplayer-test.py`）。
- 舊 Trigger harness（`build-copy-paste-live-test.py`）的 Warehouse 段是假的（單箱＋直接寫 storage），正式驗證以 `scripts/real-client/` 為準。
- 貼上到真實世界的 `clone` 仍會觸發方塊更新（為了讓邊界的柵欄、紅石正常連接）；目前沒發現掉落問題。
