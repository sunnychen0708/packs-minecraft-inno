# Utilities v3.3 — Minecraft Java 26.3 相容性審核

依據 [Minecraft 官方 26.3 更新說明](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3)，並以 Mojang 官方 26.3 server JAR 驗證。

## 審核結果

| 範圍 | 結果與處理 |
| --- | --- |
| Poplar 原木 | v3.2 已有 `natural_logs` 成員，但缺少挖掘事件。新增 `ml_poplar` objective、tick 觸發及事件歸零；既有世界 `/reload` 即建立新 objective。 |
| 紅／橙／黃 Poplar 葉 | 從官方 JAR 確認都包含在 `minecraft:leaves`；現有 `tree_foliage` 直接引用該標籤，無須另列硬編碼葉片。 |
| 倒木、Shelf Mushroom、Red Shrub、營地 | 維持附近樹葉檢查及自然原木白名單；沒有把蘑菇／灌木當成樹葉，也沒有加入木板或去皮木。無葉倒木不連鎖；附近有葉的人工原木仍可能通過既有啟發式檢查，並非完整建築辨識。 |
| Pack 格式 | `min_format`、`max_format` 原本已是 `[121,0]`，保留。 |
| Predicate／Loot Function 格式 | `is_sneaking`、`consume_one` 已使用 `type`；未使用已移除的 reference、block_state_property 或舊條件陣列格式。 |
| 耐久處理 | 實測發現既有 `set_damage: 1, add: true` 會修復工具，並非本次 26.3 新增的缺陷。一併改成讀取目前傷害、增加 1、寫回 `minecraft:damage`；保留其他元件，支援 Unbreaking、不毀、創造免耗與耗盡停止。砍樹和全部礦脈共用此修正。 |
| 自動補種 | 五種既有作物及扣種子 modifier 可繼續使用；新灌木與蘑菇不屬於既有自動補種功能。 |
| 據點、傳送、座標、Dialog | 保持所有原 storage／objective ID 與 8 個個人、8 個共用據點；只更新版本 metadata。既有函數與 macro 均以 26.3 解析。 |
| 其他 26.3 技術變動 | 本包未定義世界生成、藥水配方、探索地圖、告示牌或陶罐資料，不需相應遷移；新床、坐墊及樓梯／半磚未改變本包使用的功能。 |

## 驗證

- `python scripts/test-utilities.py`：JSON、格式、全部 12 種原木／菌柄的統計事件與重置、函數引用完整性。
- 官方 server JAR SHA-1：`33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c`，Java 25。
- 隔離測試世界完成 33 項 runtime assertions：三色 Poplar 連鎖、掉落與耐久、舊樹種／菌柄、無葉保護、非斧頭、64 根上限、工具耗盡、各材質斧頭、元件保留、不毀／耐久附魔、礦脈、扣種子、Poplar 事件只觸發一次、重載後個人／共用據點保留。
- 所有 function macros 另以測試參數實例化；未發現載入或 macro 解析錯誤。
- 這是原版伺服器 console／盔甲座測試，非真人玩家端操作；未自動驗證滑鼠砍樹、蹲下操作、Dialog 視覺與點擊流程。事件測試取用正式 tick 指令，替換玩家 selector 與觸發函數為測試替身。

重現方式（官方 JAR 和 Java 自備；測試只使用 `dist/` 下的新世界）：

```bash
python scripts/test-utilities.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
```

測試記錄保存在 `dist/utilities-test-*/console.log`，不會進入發布 ZIP。

## 版本保留

`utilities-v3.2` 使用原 release ID 更名，遊戲資料與先前 `vanilla-utilities-v3.2` 相同，僅調整文件與附件命名。`utilities-v3.3` 是獨立的新 release，v3.2 仍可下載。
