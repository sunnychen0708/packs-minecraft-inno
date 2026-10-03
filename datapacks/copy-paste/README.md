# Minecraft Copy/Paste Datapack v1.2

適用：Minecraft Java Edition 26.3（Data Pack 121.0）

純 Vanilla datapack。操作使用 Trigger。材料施工依賴同 repo 的 Warehouse datapack，並直接使用 Warehouse 共用註冊資料與 API。

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
          rotate / mirror / 重新 V 定位
                    ↓
              /trigger build
                    ↓
     掃描所有已註冊材料來源
          ↙                 ↘
      全部足夠             有缺料
      扣除材料             不扣材料
      真正施工             不修改世界
      清除預覽             保留 Blueprint
                         精確列出缺少 ID × 數量
```

Cut、Move、Flip、直接 Rotate 仍維持原本直接修改真實世界的方式。

## 材料來源

Copy/Paste 不再維護自己的材料箱註冊表。施工與材料型 Redo 直接使用 Warehouse 的共用材料來源。

Warehouse API 會從已註冊且有效的 Warehouse 容器建立最多 64 個材料來源；目前 Warehouse 既有配置為 61 個可能容器，因此不需要重複註冊。

`/trigger build` 會依 BOM 逐項呼叫 Warehouse API 查庫存；全部足夠後，再逐項由 Warehouse API 原子扣除。若 Warehouse 有失效的註冊來源，施工會停止，而不是把不完整的庫存統計當成可信結果。

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

Blueprint 建立完成後可以先設定：

```mcfunction
/trigger rotate
/trigger rotate set 10
/trigger rotate set 20
/trigger rotate set 30
/trigger rotate set 40

/trigger mirror
/trigger mirror set 10
/trigger mirror set 20
/trigger mirror set 30
```

如果 Blueprint 已存在，改 Rotate / Mirror 會直接重建目前預覽，不必重新 Copy。

確認後：

```mcfunction
/trigger build
```

系統先建立 BOM（Bill of Materials），再透過 Warehouse API 檢查共用庫存。只有所有材料都足夠才進入扣料與施工。

材料不足時會顯示例如：

```text
[Copy/Paste] 材料不足，未施工；Blueprint 已保留。
缺少材料：
  minecraft:stone_bricks ×12
  minecraft:lantern ×3
共缺少 2 種、15 個物品。
```

目前缺料名稱使用精確 Minecraft item ID，因此不受客戶端語言影響。

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

這會列出 Blueprint 每種材料的需求量、Warehouse 可用量與缺少量，不會扣除任何物品，同時保留目前的覆蓋統計。

如果目前位置會覆蓋既有非空氣方塊，第一次 `/trigger build` 只顯示警告並要求再次確認，不會扣材料或修改世界；第二次施工才會進入正常材料檢查。只要 Blueprint 再次移動、旋轉、鏡像或覆蓋重算，確認狀態就會重置。

`/trigger copypaste` 會開啟 Dialog 控制面板，包含 Pos1/Pos2/Anchor、Copy/Cut、Blueprint 六方向微調、Rotate/Mirror、材料／覆蓋檢查、施工與 Undo/Redo。若 Warehouse 同時安裝，也可以從 Warehouse 主頁直接進入建築工具。

## 遊戲內指令教學

輸入：

```mcfunction
/trigger cphelp
```

會開啟遊戲內「Copy/Paste 指令教學」Dialog；主控制面板也有「指令教學」按鈕。教學包含 Pos1/Pos2/Anchor、Copy/Blueprint/Build、Cut、Blueprint 微調、Rotate/Mirror、Move/Flip、Undo/Redo 等指令與目前的 Anchor/選區語意。

## 生存安全

Copy/Paste 不會把 Copy 當成免費 Clone：

- 施工只消耗 Warehouse 共用材料來源中的一般、無自訂 components 的物品堆疊。
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

## Move / Flip / Rotate

直接修改真實選取：

```mcfunction
/trigger right set <1..128>
/trigger left set <1..128>
/trigger up set <1..128>
/trigger down set <1..128>
/trigger forward set <1..128>
/trigger backward set <1..128>

/trigger flipx
/trigger flipz

/trigger rotate90
/trigger rotate180
/trigger rotate270
```

## Undo / Redo

```mcfunction
/trigger undo
/trigger redo
```

每位玩家保留最近 5 次真實世界修改。Build 成功也會進入世界 Undo/Redo 歷史。

Build 的 Undo/Redo 會連材料交易一起處理：Undo 在施工區仍與 Build 完成狀態一致時，還原世界並把該次實際消耗的材料統一退回 Warehouse `c00` 入口箱；若入口箱當下塞不下，Warehouse 會把剩餘退款持久化排隊並逐 tick 重試。Redo 會重新掃描 Warehouse 共用材料來源，材料全部足夠才再次扣料並恢復建築。若 Build 後施工區曾被修改且目前狀態不再吻合，材料型 Undo 會拒絕執行，以避免退款造成資源複製。

## 多人

- 每位玩家有獨立 Clipboard、Blueprint、BOM 與 5 層 Undo/Redo；材料來源則是全伺服器共用的 Warehouse。
- Blueprint display 所有附近玩家都看得到。
- Warehouse 材料來源是共用財產；Copy/Paste 不再保存玩家私人材料箱座標。
- 多人同時施工時，每次 Build/Redo 都會透過 Warehouse API 重新原子扣料；材料在前一次檢查後被其他玩家取走時，不會免費施工。

## 限制

- Raycast：128 格。
- 一般 Copy / Cut：每軸最多 128 格，總體積受 `minecraft:max_block_modifications` 限制。
- Rotate / Mirror Structure Template：每軸 ≤ 48。
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

目前 CI 會同時跑 Copy/Paste 專用 26.3 runtime，以及 Utilities + Warehouse + Copy/Paste 三包一起載入的 26.3 compatibility gate。`copy-paste-v1.2` release 會經過同一組 release gate。更完整的覆蓋範圍與仍需真人 client 驗證的項目見 [LIVE-VALIDATION.md](LIVE-VALIDATION.md)；多人隔離設計與雙人測試方式見 [MULTIPLAYER-VALIDATION.md](MULTIPLAYER-VALIDATION.md)。

正式版本仍統一由 `<pack-name>-v<version>` tag 觸發 `release-pack.yml` 驗證、打包與發布 ZIP。
