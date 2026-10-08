# Datapack 驗證與 Release

> **測試規則與限制**以 [AGENTS.md](../AGENTS.md) 為準。這裡說明層級、工具、證據與發佈條件；不要把不同層級的 PASS 混為一談。

## 驗證層級

| 層級 | 工具 | 能證明的事 |
| --- | --- | --- |
| 靜態與回歸 | `scripts/validate-datapack.py <pack>`、`scripts/test-<pack>.py` | JSON／function／macro／Dialog 語法、已知 Bug 回歸、版本標籤及 ZIP 結構 |
| 跨包相容 | `scripts/test-datapack-compatibility.py` | 三包 namespace、scoreboard、storage、load/tick 互不衝突 |
| 官方 Java 26.3 runtime | 下方專用 harness（`--java`、`--server-jar`、`--accept-eula`） | 真的在原版伺服器上載入、執行函式、比對方塊／資料 |
| **innotest live** | `exaroton-innotest.yml`、Mineflayer、live harness | 真玩家身分、世界資料、多人隔離、實際操作流程 |
| **真人 client** | `scripts/real-client/`（Windows） | G 鍵、實際 Dialog 點擊／版面、滑鼠準星、client 行為 |

測試原則：修 Bug 時盡可能補回歸；不以「成功載入／沒報錯」代替功能驗證。CI／官方 server 測試是輔助，**只有 innotest 的結果才算符合本專案實機驗證**。以測試腳本自行產生的 PASS 訊息作佐證時，也要核對真實世界結果。

常用指令（`<pack>` = `utilities`、`warehouse`、`copy-paste`）：

```bash
python3 scripts/validate-datapack.py <pack>
python3 scripts/test-<pack>.py
python3 scripts/test-datapack-compatibility.py

# 官方 Minecraft 26.3 server；替換成環境中的路徑
python3 scripts/test-utilities.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
python3 scripts/test-warehouse-runtime.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
python3 scripts/test-copy-paste-runtime.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
python3 scripts/test-datapack-compatibility.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
```

以上官方 runtime 會建立獨立測試世界，只能說明該層已驗，**不能取代 innotest**。如果使用者要求直接 release/no-gate，必須如實標示跳過哪些 gates。

## innotest 必守事項

- **每次測試 4 分鐘（240 秒）內**；長套件切成可各自 PASS／FAIL、清理及還原資料的 shard。完整覆蓋不能因時限縮水，也不能用單次 40 分鐘 `--full`。
- 先讀 server 狀態；用非 SunnyChen 三 bot，保留 SunnyChen 給真人；不要用 `execute as` 冒充玩家操作。
- Copy/Paste 使用 `scripts/mcc_house.py` 3D house（樓梯、門、台階、箱子、blockstate）逐格比對，不再用少量方塊當完整回歸。Utilities 真挖礦／砍樹／補種；Warehouse 必須依 **inno 地圖上的玩家自訂分類**驗真實箱子與庫存。
- 操作後還原世界、玩家、Warehouse 與測試檔案。測完**不關機**，除非使用者另有指示。
- 每項功能驗法、已驗／未驗及證據只維護在 [innotest 覆蓋表](innotest-coverage.md)，版本更新要同步維護。

## 已知證據與限制

| 版本 | 已驗證的範圍 | 證據 |
| --- | --- | --- |
| Utilities v3.8 | innotest 功能回歸；v3.7 世界據點／設定載入新版 | [37642068254](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37642068254)，及 [覆蓋表](innotest-coverage.md) |
| Warehouse v4.7 | 真倉庫、滿箱溢位、背景 Compact、G 導航；跨主世界／地獄／終界 27 checkpoints | [37641685439](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37641685439)、[37656341833](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37656341833) |
| Copy/Paste v1.8 | **完整 3D house 兩玩家**、新 Copy/Cut 方向歸零、Undo/Redo、Flip/Rotate 等 `MCCMP_CHECK` 全過 | [37718900567](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37718900567) |
| Copy/Paste v1.8 | 全部 35,720 種合法 Java 26.3 block state + 4 個重複案例：`states=35724 expected=35724 fail=0 air_ret=0` | [37719130915](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37719130915) |

**尚未證明**：Copy/Paste v1.8 兩位真人 client 同時點 UI；部分 Warehouse Highlight 視覺結果、Copy/Paste Warehouse 混合材料等 live 流程也仍須補（見覆蓋表）。v1.8 **發佈當下**是使用者要求的 direct/no-gate，後來補跑 exact-build live PASS；不能把當時跳過的 release-time gate 寫成 PASS，也不能寫成「v1.8 尚未 live 驗」。

Issue #49／PR #52 的歷史證據：v1.7 matcher [37599912705](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37599912705) 全 state PASS；[37600389867](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37600389867) 為 18/18 多人 PASS。更早的 Windows 真人 UI 只證明當時能按 G、選 Pos1／Pos2／Copy／Paste、旋轉 `oak_stairs` 的 `facing` 並保留其他 property；**不代表 v1.8 UI 已重測**。CI 的 ID tree matcher 會驗每種合法 property 組合，並非只比對總數。歷史 log 中的舊 commit SHA 可能因 Git 歷史壓縮而與目前 main 不同，workflow run URL 仍可追溯。

## Release 規則

一般使用 `.github/workflows/release-pack.yml`：驗證 source 版號與 tag 一致、執行靜態及三包共存 runtime，以及適用的各包 runtime，通過後打包並發佈。只有使用者明確要求直接發佈，才使用 `release-direct`；**跳過驗證不等於 PASS**。

Tag 格式：`<pack>-v<major>.<minor>`；Release ZIP 為 `dist/<pack>-v<version>.zip`。

**2026-10-08 Git 歷史壓縮後**，舊 Release Tag 不移動。一般與 direct Release **都**使用 `scripts/generate-release-notes.py`，直接比較同一 pack 前一版本 tag 與新版的檔案 tree（新增／修改／刪除），不靠共同 commit 祖先或自動 PR 列表，因此舊歷史分岔不會污染更新紀錄。此處是檔案變更摘要，**不是**未經驗證的功能宣稱。

詳細遠端操作見 [exaroton 操作](exaroton-operations.md)。
