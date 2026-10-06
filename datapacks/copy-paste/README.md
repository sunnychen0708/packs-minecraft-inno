# Minecraft Copy/Paste Datapack v1.3.1

適用：Minecraft Java Edition 26.3（Data Pack 121.0）

純 Vanilla datapack。操作使用 Trigger 或 Dialog。施工材料先從玩家背包（含副手）拿，不夠再從同 repo 的 Warehouse datapack 共用材料來源拿。

## 未發布

- 修正微調 Blueprint 後、覆蓋檢查還沒跑完就清除預覽（`previewclear`、Copy）或旋轉／翻面重建時，舊的覆蓋檢查不會停止：清除後仍會跑完並說「Blueprint 覆蓋檢查更新完成」，重建時可能留下舊暫存區的永久 forceload。現在清除或重建 Blueprint 會先取消進行中的覆蓋檢查並解除它的 forceload。

## v1.3.1

- 拿掉載入時與第一次使用時的聊天訊息；介面一律從 G →「建築工具」開啟。

## v1.3

- **修正「材料檢查」會直接扣料施工（v1.1 起）**：材料足夠時按 `/trigger materials`，原本會一路執行到扣料並蓋出建築；現在只列出材料表。材料不足時也不再多印「材料不足，未施工」。
- **施工也從玩家背包拿材料**：先用背包（主背包與副手）的一般物品，不夠再從 Warehouse 扣；改名、附魔等帶自訂 components 的物品不會被使用。Undo 時從背包扣的退回背包（塞不下的退 Warehouse，不會掉在地上），從 Warehouse 扣的退回 Warehouse。材料檢查會分開顯示「背包 N + Warehouse M」。
- **轉向／翻面指令改成以玩家面對的方向為準**，不再有 X/Z 與 `set 10/20/30/40` 代碼：Blueprint 用 `bpturnright`／`bpturnleft`／`bpflip`（左右翻）／`bpflipfb`（前後翻）／`bpreset`；直接改原本建築用 `turnright`／`turnleft`／`flip`／`flipfb`。舊指令仍可用。
- **控制面板精簡**：主畫面只剩 Pos1、Pos2、Copy、Cut、Paste、Build、Undo、「調整預覽…」、「更多…」；其他功能移到子頁。貼上模式按鈕直接顯示目前模式（完全取代／保留原方塊），切換後立即更新。所有頁面由 function 產生，`/reload` 即可更新。
- **材料清單顯示物品名稱**：缺料清單與材料檢查使用遊戲翻譯鍵，玩家看到自己語言的名稱（例如「橡木門」），滑鼠移上去顯示 item ID。
- `/trigger cphelp` 教學改成 1～5 步驟：選範圍 → 複製 → 放預覽 → 調預覽 → 蓋出來，另列「直接改原本的建築」。

- **防複製修正**：所有真實世界編輯（Cut、Move、Flip、Rotate、貼上、Build）的 Undo/Redo 都會先比對「操作完成後的世界快照」；只要該區域之後被改過（包含箱子內容物），就拒絕 Undo/Redo，避免把已拿走的物品還原回來。
- **Cut → Undo 會作廢目前的 Cut Clipboard**：來源被還原後，不能再用 `/trigger v` 把同一批方塊或箱子內容物貼第二次。
- **Cut → Undo → Redo 會重新建立原本的 Cut Clipboard**：即使 Undo 後做過別的 Copy，Redo 也會恢復當初 Cut 的內容，可再用 `/trigger v` 搬移。
- 修正 Rotate／Mirror 後的 Masked 貼上會退回 Replace：來源是空氣的格子不再覆蓋目標既有方塊。
- 修正有自訂 Anchor 時 Flip X/Z 會移動 Anchor 本身：現在 Anchor 固定不動，結構以 Anchor 所在平面為鏡像軸翻轉。
- 修正長距離 Move／外部 Anchor Rotate：來源加目的地的 Z 跨度超過 200 格時，搬過去的前幾排會被內部暫存區覆蓋而遺失。
- **有門的建築現在可以施工**：門上半部、床腳、雙格植物上半部不再被誤判成「無法換算材料」；材料算在另一半。
- **修正 Cut／Move／Flip／直接 Rotate 會複製物品**：清空來源與內部暫存不再觸發方塊更新，吊燈籠、門、牆上火把不會再掉成多出來的物品。
- 舊版沒有防複製快照的 Undo/Redo 歷史會被拒絕執行，並提示從下一次編輯開始建立新的安全歷史。
- 材料檢查／施工／材料型 Redo 進行中時按下的 Copy、Cut、V、Undo/Redo、Move/Flip/Rotate 與 Blueprint 微調，現在會提示「這個指令沒有執行」，不再無聲忽略。
- **Blueprint 預覽不再歪半格**：預覽方塊原本用整數座標召喚，Minecraft 會自動把 X/Z 置中加 0.5，整個預覽往斜角偏半格；現在精確對齊方塊格。
- `/trigger cphelp` 指令教學改成聊天室訊息（跟 Utilities 一樣），點指令會自動填入聊天欄，滑鼠移上去看說明；不再開 Dialog。

## v1.2.1

- 修正 active `/trigger copypaste` Dialog 缺少「清 Anchor」操作；現在可直接執行 `/trigger anchor set 2` 回到 Pos1 預設 Anchor。
- 驗證改為直接檢查實際使用中的 Dialog，不再拿未被主流程呼叫的 legacy `panel.mcfunction` 當玩家 UI 證據。
- v1.2 真人 Trigger harness 補上「可重新選新區域／未重選則持續使用目前選區」、外部 Anchor、清 Anchor、Pos1 非最小角的預設 Anchor、Warehouse Build。
- 官方 26.3 headless regression 補上選區外 Anchor 的 Blueprint 直接／旋轉／鏡像精確座標，並在同一個 server world 載入生成的真人 harness 以檢查所有測試 function 可被 Vanilla 解析。
- 明確區分 headless armor-stand regression 與真人 client 驗證；沒有真人 evidence 時不再宣稱「實機全部驗過」。

## v1.2

- 修正 Pos1/Pos2 重新選取後 Copy/Cut 必須使用目前選區，且未重新選取時選區持續可用。
- 修正預設 Anchor/Blueprint 精確定位，沒有自訂 Anchor 時固定以 Pos1 為 pivot。
- 自訂 Anchor 可位於選區外，支援繞外部 pivot 的大半徑 Rotate，並加入連續旋轉 runtime regression。
- 新增 `/trigger cphelp` 與遊戲內指令教學 Dialog。
- 擴充 Rotate/Mirror、Move、Flip、Cut、Undo/Redo 的官方 Minecraft 26.3 behavioral regression。
- 完成 Warehouse 共用材料 API 整合，不再維護 Copy/Paste 私有材料箱。
- Build 的 Undo/Redo 會同步退款／重新扣料，並保留防複製 guard 與持久退款 queue。
- Blueprint 支援六方向微調、只讀材料報表、覆蓋重算與二次施工確認。
- 加入 Dialog 控制面板，並可與 Warehouse 主頁互相導覽。
- Phase 3 路徑已納入官方 Minecraft 26.3 runtime regression。

## 核心流程

Copy 現在是「先 Blueprint、再用真實材料施工」：

```text
選取 → /trigger c → /trigger v
                    ↓
             Blueprint 預覽
                    ↓
          轉向 / 翻面 / 微調 / 重新 V 定位
                    ↓
              /trigger build
                    ↓
     背包 + Warehouse 材料來源
          ↙                 ↘
      全部足夠             有缺料
      扣除材料             不扣材料
      真正施工             不修改世界
      清除預覽             保留 Blueprint
                         精確列出缺少 ID × 數量
```

Cut、Move、直接轉向／翻面仍維持直接修改真實世界的方式。

## 材料來源

Copy/Paste 不再維護自己的材料箱註冊表。施工與材料型 Redo **先使用玩家自己背包（主背包 0～35 格與副手）裡的一般物品**，不夠的部分再使用 Warehouse 的共用材料來源。

Warehouse API 會從已註冊且有效的 Warehouse 容器建立最多 64 個材料來源；目前 Warehouse 既有配置為 61 個可能容器，因此不需要重複註冊。

`/trigger build` 會依 BOM 逐項計算「背包 + Warehouse」庫存；全部足夠後，逐項先從背包扣，再由 Warehouse API 原子扣除其餘。若 Warehouse 有失效的註冊來源，施工會停止，而不是把不完整的庫存統計當成可信結果。

## Copy / Blueprint / Build

```mcfunction
/trigger pos1
/trigger pos2
/trigger anchor
/trigger c
/trigger v
```

`anchor` 是選用的；**沒有手動設定 Anchor 時，Pos1 就是預設 Anchor**。執行 `v` 時，準星指向方塊旁邊的目標格代表「Anchor 要落在這一格」，因此預設情況就是讓 Pos1 對齊目標格；若有自訂 Anchor，則由自訂 Anchor 對齊。未旋轉／鏡像與已旋轉／鏡像都遵守同一套定位語意。

**自訂 Anchor 可以位於選取範圍外。** 它是同維度的空間 pivot，不是選區內的特殊方塊；因此可以把 Anchor 放在遠離建築的位置，讓 Blueprint 或直接 Rotate 繞外部中心做大半徑旋轉。重新設定 Pos1 或 Pos2 會清除舊的自訂 Anchor，並回到「Pos1 為預設 Anchor」；若要自訂 Anchor，請在目前選取範圍確定後再設定。

`v` 只建立或重定位 Blueprint，不會直接生成真實方塊。

Blueprint 建立完成後可以先調整方向（只動預覽，不動原本建築；左右前後以你面對的方向為準）：

```mcfunction
/trigger bpturnright   # 預覽向右轉 90°（順時針）
/trigger bpturnleft    # 預覽向左轉 90°（逆時針）
/trigger bpflip        # 預覽左右翻（像照鏡子）
/trigger bpflipfb      # 預覽前後翻
/trigger bpreset       # 回到原本方向
```

每次調整後聊天欄會顯示目前方向（例如「右轉 90°，並翻面」），預覽立即重建，不必重新 Copy。這個方向也套用到 Cut 之後的 `v`。舊的 `/trigger rotate`、`/trigger mirror` 仍可使用。

確認後：

```mcfunction
/trigger build
```

系統先建立 BOM（Bill of Materials），再計算玩家背包與 Warehouse 的庫存。只有所有材料都足夠才進入扣料與施工。

材料不足時會顯示例如：

```text
[Copy/Paste] 材料不足，未施工；Blueprint 已保留。
缺少材料：
  石磚 ×12
  燈籠 ×3
共缺少 2 種、15 個物品。
```

物品名稱使用遊戲翻譯鍵，每位玩家看到自己語言的名稱；滑鼠移到名稱上會顯示精確的 item ID。名稱與最大堆疊表由 `scripts/gen-item-names.py` 從 26.3 server reports 產生，換 Minecraft 版本時要重新產生。

## Phase 3：Blueprint 微調、材料報表與覆蓋保護

Blueprint 建立完成後，不必重新用 `v` 定位就能直接微調。左右／前後是以玩家目前面向為基準，上下則是世界 Y 軸：

```mcfunction
/trigger bpleft set <1..128>
/trigger bpright set <1..128>
/trigger bpforward set <1..128>
/trigger bpbackward set <1..128>
/trigger bpup set <1..128>
/trigger bpdown set <1..128>
```

微調只移動 Blueprint display 與施工目標，不會重新 Copy，也不會修改來源世界。每次微調後會分批重新計算目標區域可能覆蓋的既有非空氣方塊；覆蓋檢查尚未完成時，系統會暫停下一次微調與施工。

施工前可先做只讀檢查：

```mcfunction
/trigger materials
```

這會列出 Blueprint 每種材料的需求量、背包與 Warehouse 各有多少、缺少量，不會扣除任何物品，也不會施工，同時保留目前的覆蓋統計。

如果目前位置會覆蓋既有非空氣方塊，第一次 `/trigger build` 只顯示警告並要求再次確認，不會扣材料或修改世界；第二次施工才會進入正常材料檢查。只要 Blueprint 再次移動、旋轉、鏡像或覆蓋重算，確認狀態就會重置。

按 **G** →「建築工具」開啟 Dialog 控制面板（需要同時安裝 Warehouse；也可用 `/trigger copypaste`）。主畫面只有常用的 Pos1、Pos2、Copy、Cut、Paste、Build、Undo；「調整預覽…」（`/trigger copypaste set 2`）有轉向、翻面、移動預覽、清除預覽與材料檢查；「更多…」（`set 3`）有 Anchor、貼上模式、直接改原本建築（`set 4`）、Redo 與指令教學。若 Warehouse 同時安裝，也可以從 Warehouse 主頁（G）直接進入建築工具。

## 遊戲內指令教學

輸入：

```mcfunction
/trigger cphelp
```

會在聊天室列出指令教學（點指令自動填入聊天欄，滑鼠移上去看說明）；主控制面板也有「指令教學」按鈕。教學依步驟列出：選範圍 → 複製 → 放預覽 → 調預覽（轉向、翻面、移動）→ 蓋出來，以及「直接改原本的建築」（搬家、移動、轉向、翻面）與 Undo/Redo、Anchor、貼上模式。

## 生存安全

Copy/Paste 不會把 Copy 當成免費 Clone：

- 施工只消耗玩家背包與 Warehouse 共用材料來源中的一般、無自訂 components 的物品堆疊。
- Block Entity 的物品內容在 Blueprint buffer 中會被移除；箱子、熔爐、木桶、潛影盒等不會複製內含物。
- 沒有可對應生存材料、或會把儲存資源狀態直接複製出來的方塊會拒絕施工。
- 材料不足時完全不修改目標世界，也不扣除任何材料。
- 若 Warehouse 在檢查與扣料之間被其他玩家改動，施工會取消；已扣的普通材料仍沿用既有交易補償流程。

## Cut

```mcfunction
/trigger x
/trigger v
```

Cut 是搬移，不需要材料箱。來源先被真正移除，下一次 `v` 真正貼上，成功後 Cut Clipboard 被消耗。

## 直接移動 / 轉向 / 翻面

直接修改真實選取（左右前後以你面對的方向為準）：

```mcfunction
/trigger right set <1..128>
/trigger left set <1..128>
/trigger up set <1..128>
/trigger down set <1..128>
/trigger forward set <1..128>
/trigger backward set <1..128>

/trigger turnright     # 原地向右轉 90°
/trigger turnleft      # 原地向左轉 90°
/trigger rotate180     # 原地轉 180°
/trigger flip          # 原地左右翻
/trigger flipfb        # 原地前後翻
```

舊的 `/trigger flipx`、`flipz`、`rotate90`、`rotate270` 仍可使用。

## Undo / Redo

```mcfunction
/trigger undo
/trigger redo
```

每位玩家保留最近 5 次真實世界修改。Build 成功也會進入世界 Undo/Redo 歷史。

每筆 Undo/Redo 都附帶一份「操作完成時的世界快照」。執行 Undo/Redo 前會先比對目前世界；若該區域之後被修改過（包含箱子、木桶等容器的內容物），就不執行，以免把已經被拿走的物品還原回來。

Cut 的 Undo 會還原來源，同時作廢目前的 Cut Clipboard；Redo 會再次清除來源並重新建立原本的 Cut Clipboard，之後可以照常 `/trigger v`。

Build 的 Undo/Redo 會連材料交易一起處理：Undo 在施工區仍與 Build 完成狀態一致時，還原世界並退回該次實際消耗的材料：從玩家背包扣的退回背包（背包塞不下的部分改退 Warehouse），從 Warehouse 扣的退回 Warehouse `c00` 入口箱，再由 Warehouse 自動分類；若入口箱當下塞不下，Warehouse 會把剩餘退款持久化排隊並逐 tick 重試。Redo 會重新計算背包與 Warehouse，材料全部足夠才再次扣料（同樣先扣背包）並恢復建築。若 Build 後施工區曾被修改且目前狀態不再吻合，材料型 Undo 會拒絕執行，以避免退款造成資源複製。

## 多人

- 每位玩家有獨立 Clipboard、Blueprint、BOM 與 5 層 Undo/Redo；材料先用自己的背包，再用全伺服器共用的 Warehouse。
- Blueprint display 所有附近玩家都看得到。
- Warehouse 材料來源是共用財產；Copy/Paste 不再保存玩家私人材料箱座標。
- 多人同時施工時，每次 Build/Redo 都會重新扣料（背包，再透過 Warehouse API 原子扣除）；材料在前一次檢查後被其他玩家取走時，不會免費施工。

## 限制

- Raycast：128 格。
- 一般 Copy / Cut：每軸最多 128 格，總體積受 `minecraft:max_block_modifications` 限制。
- Rotate / Mirror Structure Template：每軸 ≤ 48；有自訂 Anchor 的 Flip X/Z 也走這條路徑，同樣每軸 ≤ 48。
- Move / 直接 Rotate 的 Undo 範圍（來源加目的地）每軸 ≤ 256。
- Warehouse 共用材料來源上限為 64；Copy/Paste 不再有自己的材料箱上限或註冊資料。
- Blueprint exact-state matcher覆蓋 Java 26.3 的 1,283 種非空氣 block IDs、35,720 個 block states。
- 實體不包含在 Copy/Cut/Blueprint 中。

## 驗證

本地靜態與 pack-specific regression：

```console
python3 scripts/validate-datapack.py copy-paste
python3 scripts/test-copy-paste.py
python3 scripts/test-datapack-compatibility.py
```

官方 Minecraft 26.3 行為 regression：

```console
python3 scripts/test-copy-paste-runtime.py \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

目前 CI 會同時跑 Copy/Paste 專用 26.3 runtime，以及 Utilities + Warehouse + Copy/Paste 三包一起載入的 26.3 compatibility gate。`copy-paste-v1.3` 經過同一組 release gate 後發布。更完整的覆蓋範圍與仍需真人 client 驗證的項目見 [LIVE-VALIDATION.md](LIVE-VALIDATION.md)；多人隔離設計與雙人測試方式見 [MULTIPLAYER-VALIDATION.md](MULTIPLAYER-VALIDATION.md)。

正式版本仍統一由 `<pack-name>-v<version>` tag 觸發 `release-pack.yml` 驗證、打包與發布 ZIP。
