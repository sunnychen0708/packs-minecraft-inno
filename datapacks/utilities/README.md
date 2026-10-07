# Utilities v3.7

> Source: **v3.7（尚未發布）** · Latest release: **utilities-v3.6** · Download: **utilities-v3.6.zip** · Previous package name: **整合_v3.2**.

遊戲內名稱「屁眼派對」：Minecraft Java 26.3 資料包，整合生存便利三合一、回家與自訂據點、座標顯示。

The actual pack source lives directly in this directory. Keep `pack.mcmeta` and `data/` here so Git can track individual changes.

## 核心功能

- 生存便利：自動補種、連鎖砍樹、礦脈挖掘（連鎖挖到的礦照原版給經驗）
- 座標顯示：Action Bar
- 固定據點：5 個（家、礦坑、村莊、傳送門、臨時點）
- 自訂據點：個人 8 個 + 共用 8 個
- 自訂據點命名與覆蓋位置
- `/trigger back`：返回上次傳送位置
- `/trigger deathloc`：返回最近死亡地點

## 指令

輸入 `/trigger help` 查看所有功能。

- 個人：/trigger plist；/trigger pset set 1；/trigger pgo set 1（slot 1～8）
- 共用：/trigger slist；/trigger sset set 1；/trigger sgo set 1（slot 1～8）
- 返回上次位置：/trigger back
- 最近死亡地點：/trigger deathloc

管理員／function API：

- /function nav:set_personal {slot:1,name:"名稱"}
- /function nav:set_shared {slot:1,name:"名稱"}
- /function nav:rename_personal {slot:1,name:"新名稱"}
- /function nav:rename_shared {slot:1,name:"新名稱"}
- /function nav:back
- /function nav:death

## 版本歷史

| 版本 | 主要更新 |
| --- | --- |
| **1.0** | 三個 Minecraft 資料包合一（`allinone` 統一調度）；新增 `/trigger help` 統一說明選單 |
| **1.1** | 新增臨時據點（`/trigger settemp`、`/trigger temp`）；完整固定據點系列（家、礦坑、村莊、傳送門、臨時點） |
| **1.2** | 刪除所有據點刪除/清除指令（`/trigger pdel`、`/trigger sdel`、`/trigger clearhome` 等）；新增 `[自訂名稱]` 對話框按鈕；移除 help 文字中的粗體符號 |
| **1.3** | **修正清單顯示 Bug**：1～8 列不顯示，改用 `/dialog show` 指令按鈕；help 改為純文字無任何符號修飾 |
| **1.4** | **完全移除 dialog 檔**（16 個檔案刪除）；`[自訂名稱]` 改為 `suggest_command`，點擊自動在聊天欄填好管理員指令 `/function nav:set_personal {slot:N,name:"名稱"}`，玩家只需修改「名稱」後送出 |
| **2.0** | 重新導入 **Dialog 名稱輸入介面**；個人／共用據點可直接點 `[自訂名稱]` 輸入名稱並設定位置，同時保留 `/function` 管理員指令方式；舊據點資料結構維持不變 |
| **2.1** | **升級至 Minecraft Java 26.3**；Data Pack 格式升至 121.0；修正 Loot Function／Predicate 26.3 語法；連鎖砍樹清單新增白楊木（挖掘事件漏接，於 v3.3 修正）；確保所有 26.2 舊座標、據點、名稱與設定可直接沿用 |
| **2.2** | 修正 `[自訂名稱]` 找不到 `minecraft:dialog` 元素的問題；名稱輸入改成 **inline Dialog**，不再依賴 Dialog registry 或重新登入 |
| **3.0** | 修正 `plist` 顯示；將**改名與改位置分離**；新增 `/trigger back` 返回上次位置、`/trigger deathloc` 返回最近死亡地點；共用據點暫時擴充至 16 格 |
| **3.1** | 共用據點恢復 8 格；`[改位置]` 改回 `[覆蓋]`；第一次設定據點可**同時命名＋儲存位置**；重新加入可點擊、自動填入的「指令教學」；保留 Back／死亡地點 |
| **3.2** | 正式刪除共用據點 9～16 的相關資料與功能；help 改為**指令教學在上、操作按鈕在下**；固定據點取消直接按鈕；Dialog 按鈕改白色；**Esc／取消不再送出任何指令**，只有確認設定／儲存才會修改資料 |
| **3.3** | 補齊 Poplar 原木挖掘事件及重置，修復三色 Poplar 連鎖砍樹；修正砍樹／挖礦共用耐久扣除、Unbreaking／Unbreakable 與工具耗盡停止；完成 26.3 相容性審核與官方伺服器回歸測試。 |
| **3.4** | 依使用者要求撤回 v3.3 的砍樹／挖礦耐久修正，完整恢復 v3.2 的工具耐久處理；保留 Poplar 挖掘事件與 26.3 相容性修正。v3.2、v3.3 release 保持不變。 |
| **3.5** | 拿掉載入時與玩家第一次加入時的聊天訊息（「[屁眼派對] 已載入」「[傳送系統] 已啟用」「自動補種、連鎖砍樹、礦脈挖掘已預設開啟」）；功能說明仍可用 `/trigger help` 查看。 |
| **3.6** | 礦脈挖掘連鎖挖到的礦會照原版掉經驗：煤 0～2、青金石 2～5、紅石 1～5、鑽石 3～7、綠寶石 3～7、石英 2～5、地獄金礦 0～1；鐵、銅、金礦與遠古遺骸原版不掉經驗，維持不給。用絲綢之觸挖不給經驗，和原版相同。工具耐久處理不變。 |
| **3.7** | 礦脈挖掘檢查鎬的等級：連鎖中的每一顆礦都先確認主手的鎬能採這種礦（依原版 `incorrect_for_*_tool` 方塊標籤，例如鑽石／綠寶石／金／紅石礦要鐵鎬以上、遠古遺骸要鑽石鎬以上），等級不夠就整條停止，不掉落、不給經驗、不扣耐久，礦留在原地。原版用等級不夠的鎬挖第一顆本來就不會觸發連鎖；v3.6 以前的漏洞是挖完第一顆後在同一刻換成低階鎬，連鎖仍會用低階鎬挖出鑽石等掉落物與經驗（`loot … mine` 本身不檢查等級）。另修正所有據點傳送（家、礦坑、村莊、傳送門、臨時點、個人／共用據點、Back、死亡地點）落點偏半格：原本會傳到四塊方塊的交角，旁邊有牆時會卡進牆裡，現在一律落在方塊正中央（主世界、地獄、終界皆同）。 |

## 安裝與更新

目前最新正式版是 [utilities-v3.6.zip](https://github.com/sunnychen0708/packs-minecraft-inno/releases/download/utilities-v3.6/utilities-v3.6.zip)；v3.7 目前只有 `main` 原始碼，尚未建立 tag／Release。安裝正式版時，移除世界 `datapacks/` 中的舊 Utilities ZIP（utilities-v3.5.zip、utilities-v3.4.zip、utilities-v3.3.zip、utilities-v3.2.zip、整合_v3.2.zip 或 vanilla-utilities-v3.2.zip），ZIP 不用解壓直接放入，再執行 `/reload`。不要同時載入兩份。

蹲下並持斧頭挖掉 Poplar 原木即可觸發；紅／橙／黃葉皆支援。單次最多連鎖 64 根，仍需附近有樹葉；無葉倒木及建築木材不會因這次更新取消保護。

工具耐久處理已恢復為 v3.2 行為；v3.3 新增的逐塊扣耐久與耗盡停止邏輯已撤回。

礦脈挖掘時，你親手挖的第一顆照原版給經驗；連鎖挖掉的每一顆會在原位置掉一顆經驗球，數值照原版該礦的隨機範圍。抽到 0 時不掉經驗球。

礦脈挖掘只連鎖主手鎬等級採得到的礦（鑽石／綠寶石／金／紅石礦要鐵鎬以上，鐵／銅／青金石礦要石鎬或銅鎬以上，遠古遺骸要鑽石鎬以上）；等級不夠時整條礦脈不動。

## 舊資料相容

- 家、礦坑、村莊、傳送門、臨時點、個人據點 1～8、共用據點 1～8、名稱、功能開關全部沿用。
- storage ID 與既有 scoreboard objective 名稱不更動。

## 注意

- 名稱輸入視窗送出時仍由 Vanilla dynamic/run_command 呼叫 function；若伺服器限制一般玩家執行 function，可能受權限規則影響。
- Esc／取消不會執行該 dynamic/run_command。
- back／死亡地點與原傳送系統支援主世界、地獄、終界。
- Data Pack 格式：121.0（Minecraft Java 26.3）。

詳見 [26.3 相容性審核與測試](COMPATIBILITY-26.3.md)。

## Release naming

Use `utilities-v<version>` for release tags and `utilities-v<version>.zip` for downloads.

[Utilities v3.2](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/utilities-v3.2) replaces the former `vanilla-utilities-v3.2` release name. This naming-only re-release preserves v3.2 gameplay and saved data; the original Git tag remains as a historical alias. Replace the old ZIP rather than loading both copies.

Example: `utilities-v3.7`
