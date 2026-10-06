# 交接：Copy/Paste v1.3 + Warehouse v4.4.1（2026-10-06 下午更新）

> 給下一位接手的人（或 Claude）。請一律用**繁體中文**與使用者溝通。

## 0b. Warehouse v4.4.2（分支 `fix/warehouse-v4.4.2-nav`）

使用者只要求：修按鈕被切掉、確認返回會回上一頁；**其他介面不要動**。
- 三欄箱子清單按鈕 150→120 寬（窄視窗右排原本超出畫面）。
- 選了某個箱子之後的頁面，返回／取消改回「選這個箱子的那一頁」：選箱時用 `ui/back_from_code` 記到 `wh_back`（register 11-16／17、view 31-36／37、unregister 51-56／57、boxname 61-66／67），按鈕送 `wh_nav set 9` → `ui/back`。靜態 Dialog（armed_00、input_xx、view error、not_registered）直接寫目標。`wh_back` 在 `load` 每次建立，舊世界也有。
- **順便發現的舊 bug**：箱子只有 1～8 種物品時「查看倉庫」內容頁打不開（26.3 不接受沒有按鈕的 multi_action）。改成 notice；`validate-datapack.py` 會擋沒有按鈕的 multi_action。
- 真人 client（`stage11_wh_back.py`，滑鼠實點）：所有改過的返回、實際註冊完成／解除完成後的返回、入口箱頁、以及沒改過的整條返回鏈都正確；52 解除後已重新註冊回原箱。**靜態 Dialog 要退出再進世界才會更新**，測試時有自動重進世界。

## 0a. 2026-10-06 下午：PR #26 真人驗證（先讀這段）

- 分支 `claude/lucid-brown-1zoaky` → PR [#26](https://github.com/sunnychen0708/packs-minecraft-inno/pull/26)（#25 已合併）。
- **PR #26 已在真人 client 驗證通過**（結果在 `dist/real-client-pr26/`，判定一律讀存檔）：
  - Blueprint 預覽：86 個 `block_display` 逐一落在目標格的**方塊角**、blockstate 完全一致；旋轉 90／180、鏡像 X 的預覽也 86/86 對齊，且施工結果與預覽一致。
  - Build／Undo 退料／Redo 再扣、0 掉落、Warehouse 精確扣一份：全過。
  - `/trigger cphelp` 聊天教學正常顯示（截圖 `cphelp.png`）。
  - **材料不足拒絕施工（stage4）**：Warehouse 石磚 0 → Build 被拒、世界與庫存都沒動；補 40 石磚 → 施工逐格正確、扣一份、0 掉落；Undo 後全額退回。全過。
- 這次發現並修掉的 bug：**Warehouse Pick 缺貨訊息印出字面上的 `$(item_id)`**（`pick/withdraw` 第 8 行少了 macro `$`）。`validate-datapack.py` 已加檢查：非 `$` 行出現 `$(var)` 就失敗（Dialog 的 `dynamic/run_command` template 除外）。真人 client 重測：訊息正確顯示 `minecraft:diamond_block`。
- 測試腳本修正：Blueprint 的旋轉／鏡像是**玩家設定，會跨 Copy 保留**；上次中斷殘留 `rotate=270`，害第一輪 Blueprint 檢查全錯。`stage3`/`stage4` 現在先 `reset_xform()`。PR #26 新加的 display 檢查原本把 `block_state` 當 dict（26.3 存檔是字串），已改用 `mcworld.fmt` 比對完整 state。
- **多箱扣料／退料分類（`stage5_multisource.py`，真人 client 全過）**：每種材料分散在 2～6 個箱子（分類箱兩半、溢位箱 10/30/60、玩家亂塞的 12/22/25…），沒有任何一箱夠一份 BOM。Build：逐格正確、每箱只減不增、總共剛好扣一份（石磚從 4 箱、木板從 3 箱扣）。Undo：退料經入口箱 → 真實分類，**每種材料剛好回到自己的分類箱**（木板依自訂規則回 11），其他箱子一格都沒變，入口箱清空。Redo 再扣一份、Undo 再退回。結果在 `dist/real-client-multisource/`。
- **介面**：`/trigger copypaste`（G → Warehouse → 建築工具）拿掉上方狀態文字（Pos/Anchor/剪貼簿/Blueprint/Undo 計數），只剩按鈕；旋轉／鏡像按鈕和教學註明「只轉 Blueprint，不動本體」，直接改世界的那行改叫「直接翻轉／旋轉本體」。
- **轉向／翻面指令重新設計（使用者選定）**：全部以「玩家面對的方向」為準，不再有 X/Z、`set 10/20/30/40` 代碼。
  - 只動預覽（也套用到 Cut 後的 V）：`bpturnright`／`bpturnleft`（順／逆時針 90°）、`bpflip`（左右翻）、`bpflipfb`（前後翻）、`bpreset`。翻面是「世界方向的翻轉疊加在目前方向上」，換算在 `state/bp_flip_axis`（F·R(k)·M = R(−k)·(F·M)）。
  - 直接改原本建築：`turnright`／`turnleft`（= rotate_edit r90/r270）、`flip`／`flipfb`（依面向選 flip/x 或 flip/z）。舊的 `rotate`、`mirror`、`rotate90/180/270`、`flipx/z` 仍可用，但不出現在教學和 Dialog。
  - 主 Dialog 按鈕：預覽右轉 90°／左轉 90°／左右翻／前後翻／回原方向；直接編輯子 Dialog：原地右轉／左轉／轉 180°／左右翻／前後翻。聊天教學改成 1～5 步驟式。
  - 真人 client 驗證（`stage6_orient.py`，預期值照玩家要求一步步用世界座標推出來，不讀 pack 內部分數）：面北／東／西三組組合的預覽 86/86、施工逐格一致、0 掉落；bpreset 回原方向；直接 turnright/turnleft/flip（北、東）/flipfb 全部逐格一致、箱子內容保留、Undo 精確還原。
  - **注意：Dialog JSON（`dialog/*.json`）是註冊表，`/reload` 不會更新，要退出再進世界。**
- 真人工具的坑：按 T 開聊天時 T 可能被打進輸入框（曾送出「t/reload」變一般聊天、沒 reload 就開跑）。`mcdrive.chat` 現在先清空輸入框，指令變成一般聊天或「未知」就丟例外；`trig()` 必須看到「已觸發 [名稱]」；`reload_packs()` 要等到「Copy/Paste v… 已載入」。
- **選單精簡（使用者嫌 G 進去按鈕太多）**：主畫面只剩 9 顆（Pos1、Pos2、Copy／Cut、V 放置、施工／Undo、調整預覽…、更多…）。子頁：`copypaste set 2` 調整預覽（轉向、翻面、清除、移動 1 格、材料檢查、施工）、`set 3` 更多（Anchor、清除 Anchor、貼上模式、直接改原本建築…、Redo、教學）、`set 4` 直接改原本建築。全部改成 function 產生的 inline Dialog（`ui/show|adjust|more|more_show|edit`），**`/reload` 就會更新**；`dialog/edit.json`、`nudge.json` 已刪。
- 貼上模式按鈕顯示**目前**模式（「貼上：完全取代」／「貼上：保留原方塊」，提示說明並寫「點一下改成…」），按下送 `mode set 2`：切換後馬上重開「更多」頁顯示新狀態。真人 client（`stage7_menu.py`）：四頁都打開、`mcc_mask` 0→1→0 從存檔確認、標籤跟著變。視窗窄時 3 欄 × 150 寬會超出畫面，一律用 120。
- 主畫面按鈕改名：「V 放置」→ **Paste**、「施工」→ **Build**（調整預覽頁的施工也是 Build）。
- **材料名稱改用翻譯鍵**：`scripts/gen-item-names.py` 從 26.3 server `--reports` 的 `components/item/*.json`（`minecraft:item_name`）產生 `function/names/load.mcfunction`（1658 個 id → key，載入到 `storage mcc:names key`）。缺料清單與材料檢查用 `{"translate":"$(key)","fallback":"$(id)"}`，滑鼠移上去顯示 id。玩家看到自己語言的名稱（zh_tw：橡木門、石磚、鑽石方塊…）。真人 client（`stage8_names.py`）從聊天日誌確認。**換 Minecraft 版本要重跑產生器。**
- **施工也從玩家背包扣料（使用者選定）**：順序是背包 0～35 格與副手 → Warehouse；有 components 的物品（改名、附魔…）不使用。Undo／扣料失敗退料時，**背包扣的退回背包**，依 `mcc:names max`（最大堆疊表，同一個產生器）算出背包還塞得下多少，用 `give` 給回；塞不下的和 Warehouse 扣的都退 Warehouse，不會掉地上。記錄在 `bom/items .inv`，總數仍是 `.taken`。材料檢查顯示「背包 N + Warehouse M」。程式：`materials/inv_*`、`refund_split`、`warehouse_take_one`、`history/refund_undo_materials_one`。
  - **26.3 的 inline item modifier 用 `"type"`，不是 `"function"`**。巨集裡寫錯會無聲失敗；第一版因此沒扣到背包、Undo 卻退料，**真人測試抓到物品複製**。現在每次扣除都 `store success`，失敗就不算已扣；server runtime 加了「真的從副手扣掉」測試。
  - 真人 client `stage10_inventory.py`：背包 10 石磚＋副手 5 木板先扣、改名的石磚不動、Warehouse 只扣其餘；Undo 背包拿回 10＋5、Warehouse 回到原狀；背包只剩 4 格空間時只退 4 個、其餘 16 進 Warehouse、0 掉落。
- 使用者說：**真人測試一律直接開始跑，不要問**（他不在用電腦）。
- **嚴重 bug（v1.1 起，已發布的 v1.1／v1.2 都有）**：材料足夠時按「材料檢查」會直接扣料並施工。`materials/count_done` 先把 `mcc_matjob` 歸零，才判斷 job 2 要提早結束，所以永遠不會結束，一路跑進扣料。缺料時則會多印「材料不足，未施工」。已修（`materials/check_done`）；runtime 新增「材料齊全時檢查不扣料不施工」兩項（舊碼確認 FAIL）；真人 client `stage9_checkonly.py`：材料齊全時檢查，目標仍是空氣、每個箱子不變。
- MCC-Test 目前狀態：乾淨。61 箱已註冊、Warehouse 剛好 2 倍 BOM、小屋與箱內物品在原位、旋轉／鏡像已重設、沒有殘留建築。備份：`backups\MCC-Test-before-e1eea6e-20261006`。
- 注意：世界難度不是和平，晚上會生怪；把時間調成白天時殭屍曬死會掉腐肉，`no_drops` 會誤報（rotten_flesh），不是 Copy/Paste 問題。

## 0. 2026-10-06 上午更新摘要

- **真人 client 驗證已完成**（使用者的 Windows 電腦、官方 26.3 client、可丟棄的 `MCC-Test` 超平坦創造世界）。做法見 §8：用作業系統層級的鍵盤／滑鼠輸入真的操作遊戲，**結果一律讀世界存檔逐格判定，不看 log 的 PASS**。
- 結果：Warehouse 61 箱真實註冊、自訂分類、Copy/Blueprint/Build 扣料、Undo 退料、Redo 再扣、旋轉 90/180/270 施工、X/Z 鏡像施工、Cut→V（含箱子內容物）、Move、Flip X/Z、直接 Rotate、Pick **全部通過，沒有發現 Copy/Paste 或 Warehouse 的 bug**。詳表見 §3。
- **舊真人 harness（`build-copy-paste-live-test.py`）的 Warehouse 段落不可信**：它用兩個 `setblock chest` 擺成兩個**單箱**，再直接寫 `warehouse:chests` storage 假裝註冊，沒有走玩家流程。使用者明確指出「箱子根本放錯」。它在真人世界跑出 `pass=92 fail=10`，10 個 FAIL 都是「剛分類完的 warehouse stock」計數。要嘛修 harness，要嘛直接以 §8 的工具為準。
- 尚未做：新 Dialog 的使用者主觀評價。（材料不足拒絕施工已於下午驗證，見 §0a。）

## 1. 目前在哪裡

- 分支：`claude/lucid-brown-1zoaky` → PR [#25](https://github.com/sunnychen0708/packs-minecraft-inno/pull/25)（base `main`）
- 舊 PR #23、#21 已留言關閉；#25 取代它們。
- 版本（**都還沒打 release tag**）：
  - Copy/Paste source **v1.3**（最新已發布 ZIP 仍是 v1.2）
  - Warehouse source **v4.4.1**（最新已發布 ZIP 仍是 v4.4）
- 發布方式：合併後推 tag `copy-paste-v1.3`、`warehouse-v4.4.1`，`.github/workflows/release-pack.yml` 會自動驗證、打包、建 Release。**要先問使用者再打 tag。**

## 2. 這個 PR 做了什麼

### Copy/Paste
1. **v1.2 的安全修正**（從 #23 接手）：所有世界編輯的 Undo/Redo 都有「操作後世界快照」防護（含容器內容物）；Cut → Undo 作廢 Cut Clipboard；旋轉後 Masked 貼上；外部 Anchor Flip。
2. **Cut → Undo → Redo 重建原本的 Cut Clipboard**。真正的 bug 是 `history/copy_hidden` macro 少傳 `dx2/dz2`，整段呼叫失敗。
3. **長距離 Move／外部 Anchor Rotate**：Undo 暫存 lane（≤256 深）壓到 Work lane；`#workz` 改為 20000500。
4. **有門的建築原本完全不能施工**：門上半部（還有床腳、雙格植物上半）絲綢之觸掉落為空 → 被判成「無法換算材料」。現在這些半格算 0 材料（`materials/bom_from_block` + `tags/block/material_free_upper_half.json`）。
5. **Cut／Move／Flip／直接 Rotate 會複製物品**：清空來源用會觸發更新的 `fill ... air replace`，燈籠、門、牆上火把掉成物品但建築仍完整。改成 `fill ... air strict`；所有寫入隱藏 lane 的 `clone` 也改 `strict`。注意語法是 `clone ... <dest> strict replace force`（`strict` 在模式**前面**）。
6. 材料檢查／施工進行中按其他指令會提示，不再無聲忽略（`materials/busy_notice`）。
7. **介面**：`/trigger copypaste` 改成「狀態式 Dialog」（`ui/open` 產生狀態字串 → `ui/show` macro Dialog），子頁 `dialog/nudge.json`、`dialog/edit.json`。舊的 `dialog/main.json`、`panel.mcfunction` 已刪。
   - **使用者還沒在遊戲裡看過新 Dialog**。他對舊介面非常不滿（太醜、難用）。

### Warehouse
- 刪除沒有入口的舊「讀取箱子」流程（`function/read/*`、`dialog/read/*`），行為不變。
- 新增只寫版本 marker 的 `migrate_v441`。
- runtime regression 補上核心功能（分類、溢位、合併、覆寫、components、16 堆疊、compact、改分類搬移、搜尋、查看、Highlight、刪除註冊）。

## 3. 驗證狀態（誠實版）

| 層級 | 狀態 |
| --- | --- |
| 靜態 + pack regression（三包） | 全過 |
| 官方 26.3 server：Copy/Paste runtime | **182 項全過**（含 3D 小屋：精確扣料、少一塊不施工、Undo 退料、Redo 再扣、旋轉 90°、Cut/Move/Flip/Rotate 逐格一致且無掉落物） |
| 官方 26.3 server：Warehouse runtime | 120 項全過 |
| 三包相容 runtime | 全過 |
| 本機 Windows 重跑（2026-10-06，HEAD `a1ae428`，Java 25.0.1） | 靜態全過；server：Copy/Paste 182、Warehouse 120、相容 10，全過 |
| 舊真人 harness（`mcc_test:start`） | `pass=92 fail=10`；但 Warehouse 段是假的（單箱 + 直接寫 storage），**不採信** |
| **真人 client，真實操作 + 讀存檔判定（§8）** | **全部通過**，見下表 |

真人 client 驗證明細（每一項都由 `scripts/real-client/` 讀 `.mca` region／entities／`command_storage.dat`／playerdata 判定）：

| 項目 | 結果 |
| --- | --- |
| 61 個真正大箱子（right+left 相連、朝南），用 `wh_register` Dialog → 滑鼠點「開始註冊」→ 真的對箱子按「使用」 | 61/61 註冊到正確的 A/B 兩半；沒有任何半箱被打掉 |
| 手持橡木板 `wh_rule set 1` → `wh_rule_dest set 11` | `rules.overrides` = `{oak_planks: 11}` |
| 2 倍小屋 BOM 放入入口箱 → 真實 tick 分類 | 入口箱清空；10 種材料數量全對；52 橡木板全部在 11 號箱 |
| Copy → V（Blueprint） | 目標 0 個真實方塊、86 個 `block_display`、來源不變 |
| Build | 196 格（含所有 blockstate）逐格一致；複製出的箱子是空的、來源箱子內容不變；Warehouse 剛好少一份 BOM；0 掉落物 |
| Build → Undo → Redo | Undo：目標回空氣、退料回入口箱並重新分類、庫存回 2 倍；Redo：再次逐格一致、再扣一份 |
| Blueprint 旋轉 90/180/270 → Build | 與原版 rotate 規則（門、樓梯、玻璃片連接、原木軸、牆上火把、箱子方向）逐格一致；0 掉落；Undo 後全額退料 |
| Blueprint 鏡像 X / Z → Build | 與原版 mirror 規則（含門 hinge 翻轉）逐格一致；0 掉落；全額退料 |
| Cut → V | 來源全空、0 掉落；目標逐格一致且箱子內容物跟著搬；Cut Clipboard 用一次就消耗；Undo×2 精確還原、內容物只回來一份 |
| Move right 3 / up 2、Flip X / Z、直接 Rotate 90/180/270 | 全部逐格一致、箱子內容物保留、0 掉落；每次 Undo 精確還原 |
| Pick（看著石磚） | 玩家拿到 40 個（倉庫只有 40），Warehouse 對應減少 |

3D 測試建築定義在 `scripts/mcc_house.py`（headless runtime、舊 harness、真人工具共用）。

## 4. 下一步（照優先順序）

1. ~~真人跑 stage4~~（已完成，§0a）。
2. 修舊真人 harness 的 Warehouse 段（改成真的大箱子；註冊盡量走玩家流程），或直接淘汰它、以 `scripts/real-client/` 為準。
3. 請使用者實際看新 Dialog，依回饋調整。
4. 打 release tag（`copy-paste-v1.3`、`warehouse-v4.4.1`）前**一定要先問使用者**。

## 5. 怎麼跑測試

```bash
# 靜態
for p in warehouse copy-paste utilities; do python3 scripts/validate-datapack.py $p; python3 scripts/test-$p.py; done
python3 scripts/test-datapack-compatibility.py

# 官方 server（需要 Java 25 + server.jar）
#   雲端環境：apt-get update && apt-get install -y openjdk-25-jre-headless
#   server.jar: https://piston-data.mojang.com/v1/objects/33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c/server.jar
#   （SHA1 33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c；雲端環境需允許 piston-data.mojang.com）
J=/usr/lib/jvm/java-25-openjdk-amd64/bin/java; S=/path/server.jar
python3 scripts/test-copy-paste-runtime.py --java $J --server-jar $S --accept-eula
python3 scripts/test-warehouse-runtime.py --java $J --server-jar $S --accept-eula
python3 scripts/test-datapack-compatibility.py --java $J --server-jar $S --accept-eula
```

Copy/Paste runtime 失敗時會印出 `DIAGNOSTICS`：`MCCST_DIAG_DROP_<步驟>`（掉了什麼物品）、`MCCST_DIAG_DIFF_<步驟>`（哪一格不對）。

真人 harness（使用者在自己電腦、可丟棄的創造模式測試世界執行）：

```bash
python3 scripts/build-copy-paste-live-test.py   # → dist/mcc-live-test
./scripts/build-pack.sh warehouse v4.4.1 && ./scripts/build-pack.sh copy-paste v1.3
```

把兩個 ZIP 和 `dist/mcc-live-test` 放進測試世界 `datapacks/`，進遊戲 `/reload` → `/function mcc_test:start`，約 3 分鐘後出現 `MCCT DONE pass=… fail=…`；結果也在 `.minecraft/logs/latest.log`。

## 6. 和使用者合作要注意

- **繁體中文**。語氣直接，使用者沒耐心，最在意「功能真的正確」與速度。
- 大改動或設計選擇先問；小 bug 直接修。
- 驗證要用**真實情境**：3D、多種方塊、真的從 Warehouse 扣料；不要用 4 個方塊平面測試交差。
- Warehouse 玩家會**自訂分類**，測試不能假設預設分類。
- 不要把「headless server 通過」說成「實機驗過」。
- 介面：使用者偏好 Dialog（做得好的前提下），不行才用聊天室選單（Utilities 那種）。

## 7. 已知限制 / 尚未處理

- 本機沒有 `zip` 指令，`build-pack.sh` 會失敗；用 Python `zipfile` 以 pack 目錄為根打包即可。
- Warehouse 介面沒有重做（使用者這次只要求驗證）。
- 雙人同時操作的真人測試（`build-copy-paste-multiplayer-test.py`）沒跑過。
- 貼上到真實世界的 `clone` 仍會觸發方塊更新（為了讓邊界的柵欄、紅石等正常連接）；目前測試沒有發現掉落問題。
- ~~MCC-Test 殘留~~（已於 §0a 清除）：真人驗證最後一段不小心把 stage 3 重跑了一半，留下一棟「Blueprint 旋轉 270° 施工」的建築（約在 x 1075..1081、z 1054..1060）沒有 Undo，Warehouse 也多了一份 2 倍 BOM。乾淨備份在 `%APPDATA%\.minecraft\backups\MCC-Test-before-a1ae428-20261006`（放入最新 datapack 之前）。下次驗證前建議先還原或另開新世界。
- 舊真人 harness 的 10 個「剛分類完 warehouse stock」FAIL 沒有在 §8 重現（§8 等 20 秒讓分類完成後讀存檔，數量完全正確）；推測是 harness 在分類尚未完成時就呼叫 `count_item`，加上它的假箱子設定，未深究。

## 8. 真人 client 驗證工具（`scripts/real-client/`，Windows）

目的：不靠 datapack 自己印的 PASS，而是**真的像玩家一樣操作**，再**讀世界存檔**判定。

- `mcdrive.py`：用 Win32 `SendInput` 對 Minecraft 視窗送鍵盤／滑鼠。指令用「按 T → Unicode 打字 → Enter」輸入（避開中文輸入法）；`screenshot()` 截圖；`in_game()` 用快捷欄清晰度判斷是否有 Dialog／選單開著；`close_screens()` 只在有畫面開著時才按 Esc。
- `mcworld.py`：唯讀 Anvil 讀取器（region、entities、block entity、command storage）。26.3 的 palette 會省略預設屬性，所以用 `defaults.json`（由 server.jar `--reports` 的 `blocks.json` 產生）補齊，才能逐格比對完整 blockstate。
- `xform.py`：依原版規則計算 rotate／mirror 後的 blockstate，作為預期值。
- `realplay.py`：場地配置與共用動作。存檔方式是「按 Esc 暫停」，讓 integrated server 存所有 chunk（單人遊戲不能用 `/save-all`）。
- `stage1_chests.py` → `stage2_register.py` → `stage3_house.py [rule stock house build rotbuild mirbuild cut direct pick]` → `stage4_shortage.py`。結果寫入 `dist/real-client/realplay-results.json`、`realplay.log` 和截圖。

**使用者電腦的坑（一定要看）：**
- 使用者的 `options.txt` 把 **攻擊設為滑鼠右鍵、使用設為滑鼠左鍵**。「打開／註冊箱子」要送**左鍵**；送右鍵會在創造模式直接把箱子打掉。不要改使用者的按鍵設定。
- 點 Dialog 按鈕會在 mouse-down 時關閉畫面，滑鼠狀態會被帶回遊戲。所以點按鈕前要先讓準星看天空（`tp … 180 -90`）。
- 聊天欄最多 256 字，長的 `data modify … Items set value [...]` 會被截斷，要拆成每格一條 `item replace`。
- 送輸入前一定要確認 Minecraft 是前景視窗。曾經有腳本在使用者切走視窗時，把指令打進了使用者的其他視窗。工具在無法取得焦點時會丟出例外；不要在使用者正在用電腦時跑。
- 匯入 `stage3_house` 會執行全部段落；只想用 helper 時要先把 `sys.argv` 設成 `['x', 'none']`（`stage4_shortage.py` 已這樣做）。
