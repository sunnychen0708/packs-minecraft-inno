# innotest 功能驗證清單

規則（AGENTS.md）：每個 datapack 的每個功能都要在 `innotest` 驗過；CI 與 headless runtime 只算輔助。這份清單列出所有功能、在 innotest 怎麼驗、目前狀態。新增或改功能時一起更新。

狀態：

- **未驗**：innotest 上還沒有測試，或測試還沒跑過。
- **已寫未跑**：innotest 測試已寫好，還沒在 innotest 跑過。
- **PASS（日期、run）**：在 innotest 跑過且通過，附 workflow run。

Utilities 的測試是 `scripts/build-utilities-live-test.py`，用 `exaroton innotest control` 的 `run-live-suite`（pack 選 `utilities`）跑；實際只需要 `penguin0531`、`geena0701`，Mineflayer workflow 預設讓三個非 SunnyChen bot 在線。預設是重點版（約 4 分鐘，315 步）：固定據點每個維度一個（家、礦坑、村莊）加 Back，個人／共用據點各測第 1、8 格（設定、傳送、列表、改名、覆蓋、無效編號、兩人隔離），死亡點；砍樹只測橡木，加不蹲、關閉、無葉、64 上限；礦脈測深板岩鑽石（有經驗）與遠古遺骸（無經驗），鎬等級各一組合格／不合格，加絲綢之觸、不蹲、關閉；補種測小麥與關閉。`--full`（733 步，約 40 分鐘）跑全部原木、礦物、等級組合、作物、5 個固定據點與 8 格據點，改到這些功能本身時才需要。

驗法欄裡的「bot」預設指 `penguin0531`、`geena0701`、`Felicitypeng`；`SunnyChen` 保留給真人登入監督或 Computer Use，只有確實需要第 4 位玩家時才由 bot 使用。bot 由測試 datapack 用 `tellraw` 下指令，自己送出 `/trigger`、挖方塊、蹲下（`scripts/mineflayer26/keepalive.js` 的 driver），不是用 `execute as` 代替玩家。測試動到的玩家背包、經驗、遊戲模式、手上物品、世界方塊與 Warehouse 庫存，結束時都要還原。

時間上限：每個 pack 的 innotest 測試都要在 4 分鐘內跑完。已在 innotest 通過的項目不重跑：`--recheck` 只跑還沒通過的項目（`run-live-suite` 的 pack 填 `utilities-recheck`／`warehouse-recheck`；Copy/Paste 的 command 填 `recheck`）。只有 server 在跑的段落用 `tick rate 10000`（最快）；要等 bot 回應或等 chunk 載入的段落用 20 tps；結束與清理一律調回 20。

Warehouse 的測試是 `scripts/build-warehouse-live-test.py`（`run-live-suite`，pack 選 `warehouse`）：用 inno 地圖上真的倉庫與玩家自訂分類，測試物品帶 `custom_data {wtest:1b}`，結束後從每一箱移除；分類、規則修改與移除、查詢、Pick、共用 API、檢視、改名、右鍵註冊／刪除註冊、chunk forceload、系統開關、load/migration 重跑都有。溢位箱只在主箱滿時記錄 `WTEST_NOTE`，沒有主動塞滿主箱測。

Copy/Paste 的測試是 `scripts/build-copy-paste-multiplayer-test.py`（`run-copy-paste-multiplayer-test`），全程用最快 tick。

## Utilities

| 功能 | innotest 驗法 | 狀態 |
| --- | --- | --- |
| `/trigger help` 功能總覽 | bot 送出 trigger，確認收到總覽訊息 | PASS（2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 座標顯示 `/trigger coords` 開關 | bot 切換，確認每位玩家各自的開關狀態 | PASS（2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 固定據點：家、礦坑、村莊、傳送門、臨時點（設定＋傳送） | bot 在已知位置設定，移到別處後傳送，比對落點是方塊正中央、維度正確 | PASS（家、礦坑、村莊；傳送門、臨時點只在 --full，2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 個人據點 1～8（`pset`／`pgo`／`plist`）與命名、改名、覆蓋 | 8 格全部設定、傳送、改名、覆蓋位置；兩位 bot 互不影響 | PASS（第 1、8 格，2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 共用據點 1～8（`sset`／`sgo`／`slist`）與命名、改名、覆蓋 | 8 格全部設定、另一位 bot 傳送到同一點 | PASS（第 1、8 格，2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| `/trigger back` | 每種傳送後 back 回到傳送前位置；主世界、地獄、終界 | PASS（2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| `/trigger deathloc` | keepInventory 下讓 bot 死亡、重生後回到死亡地點；結束還原 gamerule | PASS（2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 落點置中（v3.8） | 所有傳送比對 x/z 是 .5，旁邊有牆不卡牆 | PASS（2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 連鎖砍樹（蹲下＋斧頭） | 真的種一棵有葉子的樹，bot 蹲下用斧頭挖最下面的原木；全部原木掉落、無葉倒木不連鎖、64 根上限、Poplar 三色 | PASS（橡木，2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 礦脈挖掘 | 每種礦一條礦脈，bot 用鎬真的挖第一顆；整條挖完、掉落、經驗範圍、絲綢之觸不給經驗 | PASS（深板岩鑽石、遠古遺骸，2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 礦脈鎬等級檢查（v3.7） | 等級不夠的鎬：整條不動、不掉落、不給經驗；最低合格等級可以連鎖（耐久還沒驗） | PASS（2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 自動補種 | 成熟作物（小麥、胡蘿蔔、馬鈴薯、甜菜根、地獄疙瘩等）被 bot 採收後原地補種 | PASS（小麥，2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| `treecap`／`veinmine`／`replant` 個人開關 | 關閉後同樣動作不連鎖／不補種，打開後恢復；每位玩家各自 | PASS（2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 名稱輸入 Dialog（`nav:set_*`、`nav:rename_*`） | bot 送出 Dialog 會送的同一個指令，比對名稱與位置 | PASS（2026-10-07，重點版 [37621164714](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37621164714)＋recheck [37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)） |
| 舊資料沿用 | inno 地圖上既有據點、名稱、開關在新版載入後不變 | 未驗 |

## Warehouse

| 功能 | innotest 驗法 | 狀態 |
| --- | --- | --- |
| 自動分類（入口箱 → 分類箱） | 把已知物品放進 inno 地圖上真的入口箱，依當下的玩家自訂分類（`warehouse:rules overrides`，沒有才用預設）比對每樣物品落在哪一箱；結束把放進去的物品原數收回 | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| 溢位箱、滿箱保留來源 | 主箱塞滿後放入同類物品，確認進溢位箱；都滿時留在入口箱 | 未驗 |
| 箱子註冊、刪除註冊、重設、重複註冊提示 | bot 看著箱子用 trigger 註冊／刪除；結束從備份還原 `warehouse:chests` | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| 自訂箱名 | bot 改名，比對 `warehouse:boxnames`；結束還原 | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| 查詢物品（中文、分類名、Minecraft ID、一個字、前 30 筆） | bot 送出查詢，比對結果與庫存狀態 | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| 分類設定：新增、移動、移除分類；舊主箱庫存背景搬移 | bot 改分類後確認 override 與實際搬移；結束還原 override 與物品位置 | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| Highlight | bot 觸發，確認粒子位置與聊天訊息；未註冊／失效箱拒絕 | 已寫未跑 |
| Pick（`/trigger pick`、查詢結果「取一組」） | bot 看著方塊 pick，比對拿到的數量與倉庫減少的數量；結束歸還 | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| 倉庫瀏覽（`wh_view`、分頁） | bot 開各頁，確認收到 Dialog 且沒有錯誤 | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| 共用 API：`count_item`、`take_item`、`refund_item`、`material_sources`、`highlight`、`resolve_block`、pending refund | 在真的倉庫上呼叫，比對結果與箱子內容；結束還原 | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| Compact（整理合併堆疊） | 在一箱放不滿的同類堆疊，確認被合併、總數不變 | 部分（`run-warehouse-compact-live-test` 只驗直接呼叫） |
| 倉庫 chunk 常駐 forceload（v4.6） | 確認 61 箱所在 chunk 都 forceload；別人加的 forceload 不被移除；`chunks/release` 只移除自己的 | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| 自動整理開關（`system/on|off|toggle`） | 關閉時入口箱不動，打開後恢復 | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| Migration（v4.0～v4.6）重跑 | 在 inno 地圖資料上載入新版，61 箱註冊、override、箱名、scoreboard 不變；重跑不出錯 | PASS（2026-10-07，[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)＋recheck [37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)） |
| G 主畫面與各 Dialog | bot 開啟主畫面與各子頁，確認收到 Dialog 且沒有錯誤 | 未驗 |

## Copy/Paste

全部用 3D 測試房子（`scripts/mcc_house.py`）。

| 功能 | innotest 驗法 | 狀態 |
| --- | --- | --- |
| Pos1／Pos2 選取（真的 raycast） | 兩位 bot 同時選取房子 | PASS（2026-10-07，[37625064435](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37625064435)） |
| Copy → V Blueprint | 每格都有預覽、數量對、世界沒動 | PASS（2026-10-07，[37625064435](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37625064435)） |
| Build（背包材料） | 逐格比對、剛好扣一份 BOM | PASS（2026-10-07，[37625064435](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37625064435)） |
| Build（Warehouse 材料、背包＋Warehouse 混用、材料不足不施工） | 真的倉庫扣料，比對扣掉的數量；結束歸還 | 未驗 |
| 覆蓋保護（第一次 build 只警告） | 目標區有方塊時第一次 build 不動世界 | 未驗 |
| Blueprint 微調：移動、轉向、翻面、reset | 每一步逐格比對預覽位置與方塊狀態 | 未驗 |
| `/trigger materials` 材料檢查 | 只列材料、不施工不扣料 | 未驗 |
| Move（上下左右前後） | 已驗上移；其他方向未驗 | PASS（上移，2026-10-07，[37625064435](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37625064435)） |
| 直接 Rotate（右轉、左轉、180） | 已寫右轉；左轉、180 未驗 | FAIL（2026-10-07，[37625064435](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37625064435)、recheck [37630606793](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630606793)：B 同時 Rotate 少了屋頂 y=253 那層，之後的 Undo 拆掉 B 的房子；A 相同操作 PASS） |
| 直接 Flip（左右、前後） | 已寫左右；前後未驗 | FAIL（2026-10-07，[37625064435](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37625064435)、recheck [37630606793](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630606793)，Rotate 失敗後連帶失敗） |
| Cut → V | 逐格比對 | FAIL（2026-10-07，[37625064435](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37625064435)、recheck [37630606793](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630606793)，Rotate 失敗後連帶失敗） |
| Undo／Redo（含材料退還、五層歷史） | 已寫部分；五層與材料退還到 Warehouse 未驗 | 已寫未跑（部分） |
| Anchor、貼上模式（取代／遮罩） | 逐格比對 | 未驗 |
| 地獄、終界 | 在三個維度各做一次 Copy/Paste | 未驗 |
| 多人隔離 | 兩位 bot 同時操作，互不影響 | FAIL（2026-10-07，[37625064435](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37625064435)、recheck [37630606793](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630606793)，Rotate 失敗後連帶失敗） |
| `/trigger copypaste` Dialog、`cphelp` | bot 開啟，確認收到 Dialog／教學訊息 | 未驗 |

## cat-door-sounds（resource pack）

資源包在 client 端，innotest 的 bot 不會載入；只能用真人 client 驗。目前沒有 innotest 驗法。
