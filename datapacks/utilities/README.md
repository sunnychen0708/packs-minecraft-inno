# Utilities v3.2

> Original package name: **整合_v3.2**

Minecraft Java 26.3 data pack combining survival utilities, teleport/home and custom waypoints, and coordinate display.

The actual pack source lives directly in this directory. Keep `pack.mcmeta` and `data/` here so Git can track individual changes.

## 核心功能

- 生存便利：自動補種、連鎖砍樹、礦脈挖掘
- 座標顯示：Action Bar
- 固定據點：5 個（家、礦坑、村莊、傳送門、臨時點）
- 自訂據點：個人 8 個 + 共用 8 個
- 自訂據點命名與覆蓋位置
- `/trigger back`：返回上次傳送位置
- `/trigger deathloc`：返回最近死亡地點

## 版本歷史

| 版本 | 主要更新 |
| --- | --- |
| **1.0** | 三個 Minecraft 資料包合一（`allinone` 統一調度）；新增 `/trigger help` 統一說明選單 |
| **1.1** | 新增臨時據點（`/trigger settemp`、`/trigger temp`）；完整固定據點系列（家、礦坑、村莊、傳送門、臨時點） |
| **1.2** | 刪除所有據點刪除/清除指令（`/trigger pdel`、`/trigger sdel`、`/trigger clearhome` 等）；新增 `[自訂名稱]` 對話框按鈕；移除 help 文字中的粗體符號 |
| **1.3** | **修正清單顯示 Bug**：1～8 列不顯示，改用 `/dialog show` 指令按鈕；help 改為純文字無任何符號修飾 |
| **1.4** | **完全移除 dialog 檔**（16 個檔案刪除）；`[自訂名稱]` 改為 `suggest_command`，點擊自動在聊天欄填好管理員指令 `/function nav:set_personal {slot:N,name:"名稱"}`，玩家只需修改「名稱」後送出 |
| **2.0** | 重新導入 **Dialog 名稱輸入介面**；個人／共用據點可直接點 `[自訂名稱]` 輸入名稱並設定位置，同時保留 `/function` 管理員指令方式；舊據點資料結構維持不變 |
| **2.1** | **升級至 Minecraft Java 26.3**；Data Pack 格式升至 121.0；修正 Loot Function／Predicate 26.3 語法；連鎖砍樹新增白楊木；確保所有 26.2 舊座標、據點、名稱與設定可直接沿用 |
| **2.2** | 修正 `[自訂名稱]` 找不到 `minecraft:dialog` 元素的問題；名稱輸入改成 **inline Dialog**，不再依賴 Dialog registry 或重新登入 |
| **3.0** | 修正 `plist` 顯示；將**改名與改位置分離**；新增 `/trigger back` 返回上次位置、`/trigger deathloc` 返回最近死亡地點；共用據點暫時擴充至 16 格 |
| **3.1** | 共用據點恢復 8 格；`[改位置]` 改回 `[覆蓋]`；第一次設定據點可**同時命名＋儲存位置**；重新加入可點擊、自動填入的「指令教學」；保留 Back／死亡地點 |
| **3.2** | 正式刪除共用據點 9～16 的相關資料與功能；help 改為**指令教學在上、操作按鈕在下**；固定據點取消直接按鈕；Dialog 按鈕改白色；**Esc／取消不再送出任何指令**，只有確認設定／儲存才會修改資料 |

## Release naming

Use `utilities-v<version>` for future release tags.

Example: `utilities-v3.3`
