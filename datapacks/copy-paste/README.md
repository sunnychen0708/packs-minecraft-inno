# Minecraft Copy/Paste Datapack v1.0

適用：Minecraft Java Edition 26.3（Data Pack 121.0）

純 Vanilla datapack。操作使用 Trigger，不依賴 Warehouse 或其他資料包。

## v1.0 核心流程

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

瞄準箱子後：

```mcfunction
/trigger matbox
```

註冊材料來源。可重複註冊，**沒有寫死固定數量上限**。實際可用數量只受世界資料量與掃描時間影響。

支援：

- 箱子 / 陷阱箱
- 26.3 的各種銅箱
- 木桶
- 大箱子會自動把兩半都註冊

取消瞄準中的材料來源：

```mcfunction
/trigger matremove
```

查看目前註冊紀錄數：

```mcfunction
/trigger matlist
```

施工時每 tick 分批掃描材料來源，不會把所有箱子硬塞進同一 tick。

## Copy / Blueprint / Build

```mcfunction
/trigger pos1
/trigger pos2
/trigger anchor
/trigger c
/trigger v
```

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

系統先建立 BOM（Bill of Materials），再掃描所有已註冊材料來源。只有所有材料都足夠才進入扣料與施工。

材料不足時會顯示例如：

```text
[Copy/Paste] 材料不足，未施工；Blueprint 已保留。
缺少材料：
  minecraft:stone_bricks ×12
  minecraft:lantern ×3
共缺少 2 種、15 個物品。
```

目前缺料名稱使用精確 Minecraft item ID，因此不受客戶端語言影響。

## 生存安全

v1.0 不會把 Copy 當成免費 Clone：

- 施工只消耗已註冊容器中的一般、無自訂 components 的物品堆疊。
- Block Entity 的物品內容在 Blueprint buffer 中會被移除；箱子、熔爐、木桶、潛影盒等不會複製內含物。
- 沒有可對應生存材料、或會把儲存資源狀態直接複製出來的方塊會拒絕施工。
- 材料不足時完全不修改目標世界，也不扣除任何材料。
- 若扣料期間材料箱被其他人改動，施工會取消，已扣的普通材料會退還給施工玩家。

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

Build 的 Undo/Redo 會連材料交易一起處理：Undo 在施工區仍與 Build 完成狀態一致時，還原世界並退回該次實際消耗的材料；Redo 會重新掃描已註冊材料來源，材料全部足夠才再次扣料並恢復建築。若 Build 後施工區曾被修改且目前狀態不再吻合，材料型 Undo 會拒絕執行，以避免退款造成資源複製。

## 多人

- 每位玩家有獨立 Clipboard、Blueprint、BOM、材料箱註冊表與 5 層 Undo/Redo。
- Blueprint display 所有附近玩家都看得到。
- 材料來源註冊屬於玩家自己；不同玩家可以註冊同一個實體箱子。
- 如果多人同時從同一材料箱施工，第二階段會重新實際扣料並檢查，材料被搶走時不會免費施工。

## 限制

- Raycast：128 格。
- 一般 Copy / Cut：每軸最多 128 格，總體積受 `minecraft:max_block_modifications` 限制。
- Rotate / Mirror Structure Template：每軸 ≤ 48。
- Material box 數量沒有固定硬上限，但越多箱子檢查時間越長；目前每位玩家每 tick 最多處理 4 個註冊來源。
- Blueprint exact-state matcher覆蓋 Java 26.3 的 1,283 種非空氣 block IDs、35,720 個 block states。
- 實體不包含在 Copy/Cut/Blueprint 中。

## 驗證

```console
python3 scripts/validate-datapack.py copy-paste
python3 scripts/test-copy-paste.py
```

CI 另外會使用官方 Minecraft 26.3 server 執行 runtime smoke test；v1.0 tag 只有在 main 的驗證通過後才自動建立並交給 release workflow 發布 ZIP。
