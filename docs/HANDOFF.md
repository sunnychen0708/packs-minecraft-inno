# 交接：Copy/Paste v1.3 + Warehouse v4.4.1（2026-10-05）

> 給下一位接手的人（或 Claude）。請一律用**繁體中文**與使用者溝通。

## 1. 目前在哪裡

- 分支：`claude/lucid-brown-1zoaky` → PR [#25](https://github.com/sunnychen0708/packs-minecraft-inno/pull/25)（draft，base `main`）
- 舊 PR #23、#21 已留言關閉；#25 取代它們。
- 版本（**都還沒打 release tag**）：
  - Copy/Paste source **v1.3**（最新已發布 ZIP 仍是 v1.2）
  - Warehouse source **v4.4.1**（最新已發布 ZIP 仍是 v4.4）
- 發布方式：合併後推 tag `copy-paste-v1.3`、`warehouse-v4.4.1`，`.github/workflows/release-pack.yml` 會自動驗證、打包、建 Release。**要先問使用者再打 tag。**

## 2. 這個 PR 做了什麼

### Copy/Paste
1. **v1.2 的安全修正**（從 #23 接手）：所有世界編輯的 Undo/Redo 都有「操作後世界快照」防護（含容器內容物）；Cut → Undo 作廢 Cut Clipboard；旋轉後 Masked 貼上；外部 Anchor Flip。
2. **Cut → Undo → Redo 重建原本的 Cut Clipboard**。真正的 bug 是 `history/copy_hidden` macro 少傳 `dx2/dz2`，整段呼叫失敗。
3. **長距離 Move／外部 Anchor Rotate**：Undo 暫存 lane（≤256 深）壓到 Work lane；`#workz` 改為 20000500。
4. **有門的建築原本完全不能施工**：門上半部（還有床腳、雙格植物上半）絲綢之觸掉落為空 → 被判成「無法換算材料」。現在這些半格算 0 材料（`materials/bom_from_block` + `tags/block/material_free_upper_half.json`）。
5. **Cut／Move／Flip／直接 Rotate 會複製物品**：清空來源用會觸發更新的 `fill ... air replace`，燈籠、門、牆上火把掉成物品但建築仍完整。改成 `fill ... air strict`；所有寫入隱藏 lane 的 `clone` 也改 `strict`。注意語法是 `clone ... <dest> strict replace force`（`strict` 在模式**前面**）。
6. 材料檢查／施工進行中按其他指令會提示，不再無聲忽略（`materials/busy_notice`）。
7. **介面**：`/trigger copypaste` 改成「狀態式 Dialog」（`ui/open` 產生狀態字串 → `ui/show` macro Dialog），子頁 `dialog/nudge.json`、`dialog/edit.json`。舊的 `dialog/main.json`、`panel.mcfunction` 已刪。
   - **使用者還沒在遊戲裡看過新 Dialog**。他對舊介面非常不滿（太醜、難用）。

### Warehouse
- 刪除沒有入口的舊「讀取箱子」流程（`function/read/*`、`dialog/read/*`），行為不變。
- 新增只寫版本 marker 的 `migrate_v441`。
- runtime regression 補上核心功能（分類、溢位、合併、覆寫、components、16 堆疊、compact、改分類搬移、搜尋、查看、Highlight、刪除註冊）。

## 3. 驗證狀態（誠實版）

| 層級 | 狀態 |
| --- | --- |
| 靜態 + pack regression（三包） | 全過 |
| 官方 26.3 server：Copy/Paste runtime | **182 項全過**（含 3D 小屋：精確扣料、少一塊不施工、Undo 退料、Redo 再扣、旋轉 90°、Cut/Move/Flip/Rotate 逐格一致且無掉落物） |
| 官方 26.3 server：Warehouse runtime | 120 項全過 |
| 三包相容 runtime | 全過 |
| **真人 client harness** | **最新版尚未有人跑過**。上一次真人跑（舊 harness）是 44/47，3 個失敗是 harness 本身問題（地獄 chunk 未載入），已修。 |

3D 測試建築定義在 `scripts/mcc_house.py`（headless runtime 和真人 harness 共用）。

## 4. 下一步（照優先順序）

1. 等 PR #25 最新 commit 的 CI 綠（本機已全過）。
2. 請使用者跑**真人 harness**（下面指令），把 `MCCT PASS/FAIL/DONE` 結果拿回來。新版 harness 包含：
   - 跨維度修正
   - 真人玩家選取 3D 小屋 → Copy → V → 施工
   - Warehouse **全部 61 箱位註冊 + 一條自訂分類**（不假設預設分類；使用者明確要求）
   - 真實 tick 自動分類、Undo 退料再分類、Redo、Pick
   - 會備份並還原測試世界原本的註冊和分類
3. 請使用者實際看新 Dialog，依回饋調整。
4. 使用者同意後才合併、打 tag。

## 5. 怎麼跑測試

```bash
# 靜態
for p in warehouse copy-paste utilities; do python3 scripts/validate-datapack.py $p; python3 scripts/test-$p.py; done
python3 scripts/test-datapack-compatibility.py

# 官方 server（需要 Java 25 + server.jar）
#   雲端環境：apt-get update && apt-get install -y openjdk-25-jre-headless
#   server.jar: https://piston-data.mojang.com/v1/objects/33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c/server.jar
#   （SHA1 33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c；雲端環境需允許 piston-data.mojang.com）
J=/usr/lib/jvm/java-25-openjdk-amd64/bin/java; S=/path/server.jar
python3 scripts/test-copy-paste-runtime.py --java $J --server-jar $S --accept-eula
python3 scripts/test-warehouse-runtime.py --java $J --server-jar $S --accept-eula
python3 scripts/test-datapack-compatibility.py --java $J --server-jar $S --accept-eula
```

Copy/Paste runtime 失敗時會印出 `DIAGNOSTICS`：`MCCST_DIAG_DROP_<步驟>`（掉了什麼物品）、`MCCST_DIAG_DIFF_<步驟>`（哪一格不對）。

真人 harness（使用者在自己電腦、可丟棄的創造模式測試世界執行）：

```bash
python3 scripts/build-copy-paste-live-test.py   # → dist/mcc-live-test
./scripts/build-pack.sh warehouse v4.4.1 && ./scripts/build-pack.sh copy-paste v1.3
```

把兩個 ZIP 和 `dist/mcc-live-test` 放進測試世界 `datapacks/`，進遊戲 `/reload` → `/function mcc_test:start`，約 3 分鐘後出現 `MCCT DONE pass=… fail=…`；結果也在 `.minecraft/logs/latest.log`。

## 6. 和使用者合作要注意

- **繁體中文**。語氣直接，使用者沒耐心，最在意「功能真的正確」與速度。
- 大改動或設計選擇先問；小 bug 直接修。
- 驗證要用**真實情境**：3D、多種方塊、真的從 Warehouse 扣料；不要用 4 個方塊平面測試交差。
- Warehouse 玩家會**自訂分類**，測試不能假設預設分類。
- 不要把「headless server 通過」說成「實機驗過」。
- 介面：使用者偏好 Dialog（做得好的前提下），不行才用聊天室選單（Utilities 那種）。

## 7. 已知限制 / 尚未處理

- Warehouse 介面沒有重做（使用者這次只要求驗證）。
- 雙人同時操作的真人測試（`build-copy-paste-multiplayer-test.py`）沒跑過。
- 貼上到真實世界的 `clone` 仍會觸發方塊更新（為了讓邊界的柵欄、紅石等正常連接）；目前測試沒有發現掉落問題。
