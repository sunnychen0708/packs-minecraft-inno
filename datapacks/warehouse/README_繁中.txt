Minecraft Java 26.3 自動分類倉庫 v4.4.1

目前版本／發布
- 原始碼版本：v4.4.1（尚未發布）
- 最新 Release：warehouse-v4.4
- Data Pack 格式：121.0（Minecraft Java 26.3）

安裝／升級
1. 移除舊版 Minecraft_Warehouse_26.2_v*.zip、Minecraft_Warehouse_26.3_v*.zip 或舊 warehouse-v*.zip；不要同時載入兩份。
2. 將 warehouse-v4.4.zip 放入世界 datapacks 資料夾。
3. 執行 /reload。
4. 既有 61 箱註冊、玩家分類覆寫、自訂箱名、scoreboard 與其他世界資料會沿用；v4.4 migration 不會重設這些資料。

v4.4.1：清理
- 移除已沒有入口的舊版「讀取箱子」流程（已由「查看倉庫」取代），玩家可見行為不變。
- 新增 v4.4.1 版本 marker；不會修改既有世界資料。
- 官方 26.3 runtime regression 補上自動分類、溢位、合併、玩家覆寫、自動堆疊、改分類搬移、搜尋、查看、Highlight 與刪除註冊。

v4.4：Pick
- 新增 /trigger pick 與 Warehouse 主 Dialog 的「Pick 一組」。
- 準星最遠約 6 格，忽略空氣、水、岩漿等流體。
- warehouse:api/resolve_block 以 Silk Touch loot 模擬把方塊解析成可取得的生存物品，不破壞原方塊。
- Pick 共用 Warehouse count_item / take_item；一次最多取該物品的原版最大堆疊數，庫存不足一組時取現有數量。
- 無正常生存掉落對應的方塊會拒絕，不會憑空產生物品。
- 物品查詢結果頁也能直接「取一組」，共用同一套扣料路徑。

v4.3：共用 API、Highlight、Copy/Paste 整合
- 提供最多 64 個去重材料來源的共用 API；目前 Warehouse 既有布局只有 61 個註冊槽。
- count_item：統計所有有效來源中的普通 item stack。
- take_item：先完整 preflight，再 all-or-nothing 扣除；庫存不足或來源失效時不會部分扣料。
- refund_item：退款統一送回入口箱 c00；入口箱塞不下或暫時不可用時，剩餘退款會進 pending_refunds 持久 queue，之後逐 tick 重試。
- API 只處理無自訂 components 的普通堆疊，避免拿走命名／容器／custom-data 變體。
- Highlight 直接使用既有 warehouse:chests 註冊資料，以 end_rod 粒子顯示目標箱；搜尋 → 分類結果 → Highlight 共用同一路徑。
- Warehouse 主頁可以進入 Copy/Paste 建築工具；Copy/Paste 的材料施工、Undo 退款與 Redo 重新扣料直接使用 Warehouse API。

v4.2：搜尋索引
- 修正新世界／升級時一次建立搜尋索引超過 65,536 command-chain 上限的問題。
- 26.3 搜尋索引拆成 72 個 shard，每 tick 建 1 份；完成前搜尋不會被當成 ready。
- 避免物品名稱表重複初始化。

v4.1：reset registrations hotfix
- 修正 warehouse:admin/reset_registrations 使用不完整 data remove 指令、導致 function 無法載入的問題。
- Reset 只清除 61 個箱位的 registered / valid；分類覆寫、自訂箱名與註冊 metadata 不會被整包刪掉。

v4.0：Minecraft 26.3 內容
- 加入 26.3 正式版 121 個新物品的自動分類、搜尋與持有物品分類設定支援。
- 修正 26.3 minecraft:any_block_use 的 location predicate 格式變更。
- 查詢結果維持同頁可捲動單欄；各 3×3 箱位頁與一般 action / 返回按鈕縮窄，避免超出畫面。

查詢／分類設定
- G →「查詢物品」，或「分類設定」→「打字選擇物品」。
- 支援繁中名稱、分類名稱、Minecraft ID；一個中文字也可搜尋。
- 查詢結果會顯示目前分類箱與有庫存／無庫存／箱未註冊／箱失效狀態。
- 點結果可新增、移動或移除分類，並可直接 Highlight 或取一組。
- 修改分類後，舊主分類箱內相同 base item ID 的既有庫存會背景搬往新分類箱。
- 搬移沿用主箱 → 同區溢位箱 → 放不下保留來源的安全搬運邏輯。
- 每次搜尋最多採用前 30 筆結果。
- 自由文字 Dialog 仍會出現 Minecraft 原版高權限確認頁，純 Vanilla 無法取消。

自動整理控制（需 OP）
/function warehouse:system/on
/function warehouse:system/off
/function warehouse:system/toggle
預設開啟。

舊資料相容性
- 可從 Minecraft 26.2 v3.2、26.3 v3.3/v3.4、Warehouse v4.0～v4.3 直接升級。
- 不重設 warehouse:chests：61 箱座標、dimension 與其他既有註冊 metadata 保留。
- 不重設 warehouse:boxnames：玩家自訂箱名保留。
- 不重設 warehouse:rules overrides：玩家新增／移動／移除的分類覆寫保留。
- 不更名既有 scoreboard objectives；既有玩家與系統分數可繼續使用。
- v4.0～v4.4.1 migrations 都以可再生成資料或版本 marker 為主；目前 v4.4.1 marker 不會清空既有世界資料。
- 搜尋索引屬可重建資料；v4.2 起使用 72-shard 建立流程。

目前限制
- 尚未提供「依箱子瀏覽全部分類規則」與「一鍵清空該箱全部分類」。
- 尚未提供入口箱「未分類物品清單 → 直接批次設定」頁面。
- 尚未提供完整的滿箱／溢位滿／箱子失效通知中心與快速重新註冊提示。
- 一般背景整理本身不會永久自動管理所有倉庫 chunk 的 forceload；共用 API 呼叫只會暫時處理它需要的來源 chunk。
- 尚未正式支援自訂維度。
- 查看倉庫遇到名稱表之外的新物品時，可能顯示 Minecraft ID。
- 純 Vanilla Datapack 無法提供伺服器硬崩潰瞬間的資料庫級 transaction 保證。
- 真正的滑鼠中鍵事件無法由純 Vanilla datapack 可靠偵測，因此 Pick 使用 Trigger / Dialog。

Minecraft 26.3 新物品分類（v4.0 起）
- 28 交通運輸：楊木船、儲物箱楊木船。
- 35 沙岩建材：16 色混凝土階梯、16 色混凝土半磚。
- 36 原木木材：楊木原木、楊木塊、剝皮楊木原木、剝皮楊木塊、楊木材。
- 37 木製建材：楊木階梯、半磚、柵欄、柵欄門、按鈕、壓力板、門、地板門、告示牌、懸掛式告示牌、展示架。
- 41 探索導航：26.3 的 16 種獨立 Explorer Map 物品。
- 52 羊毛織染：16 色羊毛階梯、16 色羊毛半磚、16 色坐墊、乾草床。
- 56 林地生態：楊木樹苗、紅／橙／黃楊木樹葉、層孔菇、紅灌木。

驗證
- python3 scripts/validate-datapack.py warehouse
- python3 scripts/test-warehouse.py
- python3 scripts/test-datapack-compatibility.py
- CI 會使用官方 Minecraft 26.3 server 跑 Warehouse 專用 runtime regression。
- CI 也會把 Utilities + Warehouse + Copy/Paste 三包同時載入，跑 all-datapacks compatibility regression。
- warehouse-v4.4 release 已使用目前的版本／runtime gate 發布。
