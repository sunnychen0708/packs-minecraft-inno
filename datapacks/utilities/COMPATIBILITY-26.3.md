# Utilities v3.6 — Minecraft Java 26.3 相容性審核

依據 [Minecraft 官方 26.3 更新說明](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3)，並以 Mojang 官方 26.3 server JAR 驗證。

## 審核結果

| 範圍 | 結果與處理 |
| --- | --- |
| Poplar 原木 | v3.2 已有 `natural_logs` 成員，但缺少挖掘事件。新增 `ml_poplar` objective、tick 觸發及事件歸零；既有世界 `/reload` 即建立新 objective。 |
| 紅／橙／黃 Poplar 葉 | 從官方 JAR 確認都包含在 `minecraft:leaves`；現有 `tree_foliage` 直接引用該標籤，無須另列硬編碼葉片。 |
| 倒木、Shelf Mushroom、Red Shrub、營地 | 維持附近樹葉檢查及自然原木白名單；沒有把蘑菇／灌木當成樹葉，也沒有加入木板或去皮木。無葉倒木不連鎖；附近有葉的人工原木仍可能通過既有啟發式檢查，並非完整建築辨識。 |
| Pack 格式 | `min_format`、`max_format` 原本已是 `[121,0]`，保留。 |
| Predicate／Loot Function 格式 | `is_sneaking`、`consume_one` 已使用 `type`；未使用已移除的 reference、block_state_property 或舊條件陣列格式。 |
| 耐久處理 | 依使用者要求，v3.4 撤回 v3.3 的耐久修正。砍樹、全部 11 種礦脈 break 函數及 `damage_one` modifier 完整還原 v3.2 原始碼（`set_damage: 1, add: true`）；移除 v3.3 新增的 tool helper。此行為會將工具修復至全滿，依要求保留。 |
| 礦脈經驗（v3.6） | 連鎖挖掉的礦原本用 `loot spawn … mine` 掉落、`setblock air` 移除，兩者都不產生經驗。v3.6 在 7 種有經驗的礦的 `break` 函數加入 `vein/xp`，用 `random value` 抽原版範圍並以巨集 `summon experience_orb {Value:…}` 生成；主手有絲綢之觸時跳過。已在官方 26.3 server 驗證經驗球數量、數值範圍、0 不生成、絲綢之觸與鐵礦不生成。 |
| 自動補種 | 五種既有作物及扣種子 modifier 可繼續使用；新灌木與蘑菇不屬於既有自動補種功能。 |
| 據點、傳送、座標、Dialog | 保持所有原 storage／objective ID 與 8 個個人、8 個共用據點；只更新版本 metadata。既有函數與 macro 均以 26.3 解析。 |
| 其他 26.3 技術變動 | 本包未定義世界生成、藥水配方、探索地圖、告示牌或陶罐資料，不需相應遷移；新床、坐墊及樓梯／半磚未改變本包使用的功能。 |

## 驗證

- `python scripts/test-utilities.py`：JSON、格式、全部 12 種原木／菌柄的統計事件與重置、函數引用完整性。
- 官方 server JAR SHA-1：`33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c`，Java 25。
- 隔離測試世界完成 37 項 runtime assertions：三色 Poplar 連鎖、掉落與耐久、舊樹種／菌柄、無葉保護、非斧頭、64 根上限、瀕壞工具持續連鎖、各材質斧頭恢復原版耐久行為、元件與耐久附魔保留、不毀工具舊行為、礦脈、扣種子、Poplar 事件只觸發一次、重載後個人／共用據點保留、礦脈經驗（鑽石數值範圍、煤礦 0 不生成、絲綢之觸與鐵礦不生成）。
- 所有 function macros 另以測試參數實例化；未發現載入或 macro 解析錯誤。
- 以上是原版伺服器 console／盔甲座測試，非真人玩家端操作；未自動驗證滑鼠砍樹、Dialog 視覺與點擊流程。
- 礦脈經驗另在真人 client 驗證（2026-10-07，`scripts/real-client/stage13_vein_xp.py`，讀玩家存檔的經驗值）：生存模式按住蹲下、只用滑鼠挖第一顆，4 顆鑽石礦整條挖掉並得到 22 點經驗（範圍 12～28，只挖一顆最多 7 點）；絲綢之觸挖鑽石礦、普通鎬挖鐵礦都整條挖掉且 0 經驗。同一輪 `stage12_all_packs` 三包一起安裝（Utilities v3.6、Warehouse v4.5、Copy/Paste v1.5）7 項全過。事件測試取用正式 tick 指令，替換玩家 selector 與觸發函數為測試替身。

重現方式（官方 JAR 和 Java 自備；測試只使用 `dist/` 下的新世界）：

```bash
python scripts/test-utilities.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
```

測試記錄保存在 `dist/utilities-test-*/console.log`，不會進入發布 ZIP。

## 版本保留

`utilities-v3.2` 使用原 release ID 更名，遊戲資料與先前 `vanilla-utilities-v3.2` 相同，僅調整文件與附件命名。`utilities-v3.4` 是獨立的新 release；v3.2 與 v3.3 的 release、標籤及附件保持不變，仍可下載。
