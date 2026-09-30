# Minecraft Copy/Paste Datapack v0.5.0

適用：Minecraft Java Edition 26.3（Data Pack 121.0）

純 Vanilla datapack。操作使用 Trigger，不使用 G、ESC 或 Dialog。

## 核心原則

v0.5.0 開始把 **Copy** 和 **Cut** 明確分開：

- `/trigger c`：Copy。保存個人 Clipboard，但 `V` **不會生成真實方塊**；只建立所有玩家都看得到的 Blueprint 預覽。
- `/trigger x`：Cut。真正移除來源方塊；之後 `V` 會真正貼到目標位置，成功後 Cut Clipboard 立即消耗，不能重複貼上。
- Move / Flip / Rotate：仍然直接修改真實世界方塊。
- Undo / Redo：最近一次真實世界修改可在前後狀態來回切換。

因此 Copy 不再能用來複製鑽石方塊、信標、箱子內容等物資。

## 安裝

1. 把 ZIP 放進 `world/datapacks/`
2. 移除舊版 Copy/Paste ZIP
3. 重啟伺服器或執行 `/reload`
4. `/trigger copypaste` 顯示控制面板

## 選取

```mcfunction
/trigger pos1
/trigger pos2
/trigger anchor
/trigger anchor set 2
```

Pos1 / Pos2 / Anchor 都以準星看向的方塊設定。未自訂 Anchor 時使用 Pos1。

## Copy → Blueprint

```mcfunction
/trigger c
/trigger v
```

`c` 保存當下選取內容；`v` 看向目標方塊旁邊的位置後建立 Blueprint。

Blueprint：

- 使用 `block_display`，不會放置真實方塊。
- 保留 Minecraft 26.3 的原始 block state，包括樓梯方向、原木軸向、門狀態等。
- 所有附近玩家都看得到。
- 每位玩家各自最多保留一份目前的 Blueprint；再次 `v` 會替換自己的上一份。
- `/trigger previewclear` 清除自己的 Blueprint。
- Blueprint 建立分批執行，避免中小型建築一次生成大量 display entity 卡住伺服器。
- Copy 之後即使在 Blueprint 還沒畫完前又 Copy 其他東西，Blueprint 會使用自己的快照，不會混到新 Clipboard。

若 `rotate / mirror` 不是預設值，Blueprint 會先在隱藏 Work 區用 Vanilla Structure Template 轉換，再讀取轉換後的 block state，因此方向性方塊由 Minecraft 本身處理。

注意：Block Entity 的內容不會被 Blueprint 複製；例如箱子內容不會出現在預覽中。

## Cut

```mcfunction
/trigger x
/trigger v
```

`x` 取代舊的 `/trigger cut`。

Cut 會真正清除來源並把快照保存為 Cut Clipboard。下一次 `v` 會真正貼上；成功後 Clipboard 被消耗，所以不能連續 `v` 複製同一份材料。

## 直接移動真實選取

```mcfunction
/trigger right set <1..128>
/trigger left set <1..128>
/trigger up set <1..128>
/trigger down set <1..128>
/trigger forward set <1..128>
/trigger backward set <1..128>
```

水平四方向依玩家當下水平朝向；up/down 永遠是世界 Y 軸。Pos1、Pos2、Anchor 一起移動。

## 直接鏡像真實選取

```mcfunction
/trigger flipx
/trigger flipz
```

Flip 在原地修改真實方塊。自訂 Anchor 會跟著對稱變換。

## 直接旋轉真實選取

```mcfunction
/trigger rotate90
/trigger rotate180
/trigger rotate270
```

以自訂 Anchor 為中心；沒有自訂 Anchor 時以 Pos1 為中心。使用 Vanilla Structure Template，所以直接 Rotate 的 X/Y/Z 每軸上限為 48 格。

## Blueprint / Cut Paste 的旋轉與鏡像設定

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

設定值：

- Rotate：0° / 90° / 180° / 270°
- Mirror：無 / X / Z

這組設定只影響下一次 `v` 的 Blueprint 或 Cut Paste；要直接旋轉現有真實建築請用 `rotate90/180/270`。

## Undo / Redo

```mcfunction
/trigger undo
/trigger redo
```

目前是一層歷史：

1. 真實世界修改成功後建立 Undo
2. Undo 前會把「修改後」狀態保存到 Redo Buffer
3. Redo 前又會把「Undo 後」狀態重新保存回 Undo Buffer

因此可以像單層 Ctrl+Z / Ctrl+Y 一樣反覆：

```text
修改 → undo → redo → undo → redo
```

只要做了新的真實世界修改，舊 Redo 就失效。Copy、建立/清除 Blueprint 不修改世界，因此不會清除 Redo。

## 多人

- 每位玩家有獨立 `mcc_id`
- Clipboard / Undo / Redo / Work / Blueprint Buffer 都依玩家分離
- Clipboard 與 Undo 不會互相串到其他玩家
- Blueprint display 是共享可見，所有玩家都能一起看建築預覽
- 若兩個玩家刻意同時修改相同的真實世界方塊，最後結果仍依伺服器命令執行順序決定；目前不做區域鎖

## 限制

- Raycast：128 格
- 一般 Copy / Cut / 無變換資料：每軸最多 128 格，總體積受 `minecraft:max_block_modifications` 限制
- Rotate / Mirror Structure Template：每軸 ≤ 48
- Blueprint 目前針對中小型建築設計
- Blueprint exact-state matcher 覆蓋 Java 26.3 的 1,283 種非空氣 block IDs、35,720 個 block states
- 實體不包含在 Copy/Cut/Blueprint 中

## 驗證

```console
python3 scripts/validate-datapack.py copy-paste
python3 scripts/test-copy-paste.py
```

多人架構與測試方式見 [MULTIPLAYER-VALIDATION.md](MULTIPLAYER-VALIDATION.md)。v0.4.2 的實機基準結果保留在 [LIVE-VALIDATION.md](LIVE-VALIDATION.md)。
