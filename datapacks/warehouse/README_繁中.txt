Minecraft Java 26.3 自動分類倉庫 v4.0

安裝／升級
1. 移除舊版 Minecraft_Warehouse_26.2_v*.zip／Minecraft_Warehouse_26.3_v*.zip。
2. 將 v4.0 zip 放入世界 datapacks 資料夾。
3. 執行 /reload。
4. 既有箱子註冊、玩家分類覆寫、自訂箱名與搜尋索引會保留。

v4.0 更新
- Minecraft Java 26.3（Data Pack 121.0）。
- 新增 26.3 正式版 121 個新物品的自動分類、搜尋與持有物品分類設定支援。
- 修正 26.3 對 advancement `minecraft:any_block_use` 的 location predicate 格式變更。
- 保留 v3.2 的所有倉庫功能、註冊資料、分類覆寫與自訂箱名相容性。
- 查詢結果維持同頁可捲動單欄，但結果按鈕縮窄，不再橫跨大部分畫面。
- 所有區域 3×3 主箱頁統一使用最小尺寸：每顆按鈕 width 150、頁面說明 width 最多 330。
- 新增註冊、刪除註冊、目前註冊、命名、查看與分類選箱的 3×3 介面尺寸一致。
- 雙欄頁面的過大 action 按鈕收斂到 compact width 150；返回鍵統一 width 200。

查詢／分類設定
- G →「查詢物品」，或「分類設定」→「打字選擇物品」。
- 支援繁中名稱、分類名稱、Minecraft ID；一個中文字也可搜尋。
- 結果格式例如：鐵礦 → 14・無庫存。
- 若玩家改過分類，例如移到 19：鑽石 → 19・有庫存（預設 11）。
- 點結果可直接新增、移動或移除分類。
- 文字搜尋仍會出現 Minecraft 26.3 原版的高權限指令確認頁。

既有功能保留
- 查詢結果會標示目前分類箱：有庫存／無庫存／箱未註冊／箱失效。
- 修改物品分類後，舊主分類箱內相同 base item ID 的既有庫存會背景搬往新分類箱。
- 搬移沿用主箱 → 同區溢位箱 → 放不下保留來源的安全搬運邏輯。
- 查看箱子內容仍採分頁，避免最多 54 種物品時超出畫面。
- 只有區域內 9 個主箱使用 3×3 按鈕；其他選單為單欄或雙欄。

自動整理控制（需 OP）
/function warehouse:system/on
/function warehouse:system/off
/function warehouse:system/toggle
預設開啟。

目前仍未實現／限制
- 尚未提供「依箱子瀏覽全部分類規則」與「一鍵清空該箱全部分類」。
- 尚未提供入口箱「未分類物品清單 → 直接批次設定」頁面。
- 尚未提供完整的滿箱／溢位滿／箱子失效通知中心與快速重新註冊提示。
- 尚未自動管理 forceload；倉庫區塊未載入時不保證持續整理或搬移。
- 尚未正式支援自訂維度。
- 查看倉庫遇到名稱表之外的新物品時，可能顯示 Minecraft ID。
- 每次搜尋最多採用前 30 筆結果。
- 自由文字 Dialog 會出現 Minecraft 原版高權限確認頁，純 Vanilla 無法取消。
- 純 Vanilla Datapack 無法提供伺服器硬崩潰瞬間的資料庫級 transaction 保證。

v4.0 舊資料相容性
- 可直接沿用 Minecraft 26.2 v3.2 / 26.3 v3.3 的世界資料。
- 不重設 warehouse:chests：既有 61 箱註冊座標、維度、registered 狀態保留。
- 不重設 warehouse:boxnames：玩家自訂箱名保留。
- 不重設 warehouse:rules overrides：玩家新增／移動／移除的分類覆寫保留。
- 不更名既有 scoreboard objectives；玩家與系統分數紀錄可繼續使用。
- v3.4 migration 仍保留；v4.0 另新增 warehouse:meta v40 標記。
- v4.0 migration 只重建可再生成的搜尋索引並寫入 v40 標記，不修改 warehouse:chests、warehouse:boxnames、warehouse:rules 或既有玩家資料。
- 已加入 Minecraft 26.3 正式版新增的 121 個物品。


v4.0：Minecraft 26.3 新物品分類
- 28 交通運輸：楊木船、儲物箱楊木船。
- 35 沙岩建材：16 色混凝土階梯、16 色混凝土半磚。
- 36 原木木材：楊木原木、楊木塊、剝皮楊木原木、剝皮楊木塊、楊木材。
- 37 木製建材：楊木階梯、半磚、柵欄、柵欄門、按鈕、壓力板、門、地板門、告示牌、懸掛式告示牌、展示架。
- 41 探索導航：26.3 的 16 種獨立 Explorer Map 物品。
- 52 羊毛織染：16 色羊毛階梯、16 色羊毛半磚、16 色坐墊、乾草床。
- 56 林地生態：楊木樹苗、紅／橙／黃楊木樹葉、層孔菇、紅灌木。
