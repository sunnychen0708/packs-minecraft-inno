# 工作規則

適用整個 repo，所有貢獻者、agent、自動化流程與 reviewer 都要遵守。

## inno 寫入

- 任何寫入 inno 的動作都要使用者明確下指令才可以做，包括安裝或更新 datapack、改檔案、執行指令、啟動／關閉／重啟、UUID maintenance 的 apply。每次都要，之前的同意不能沿用。
- 讀取 inno 不用問，直接讀。

## Git 與 GitHub

- commit 作者與 committer 一律用 `陳譯晴 <144662040+sunnychen0708@users.noreply.github.com>`，不用 Claude 或其他 agent 的名義。
- commit 訊息、PR 標題與內文、comment 都不加 `Co-Authored-By: Claude`、`Claude-Session`、「Generated with Claude Code」之類的署名。
- 新分支不用 `claude/` 開頭。

## 測試

- 一律直接在 `innotest` 測（`exaroton innotest control` workflow；需要玩家時用 Mineflayer bots）。
- Mineflayer 測試預設只用 `penguin0531`、`geena0701`、`Felicitypeng`，保留 `SunnyChen` 給使用者真人登入監督或 Computer Use。只有測試確實需要第 4 位玩家，或使用者明確要求，才讓 `SunnyChen` bot 上線。
- 不要在本機、暫存資料夾、另建的世界或 MCC-Test 測，除非使用者指定。
- 每個 datapack 的每個功能都要在 innotest 驗過，不是只有改到的那個 pack 或 Copy/Paste。功能清單與目前覆蓋狀態見 `docs/innotest-coverage.md`；新增或改功能時一起更新。
- 測試要用接近真實使用的情境，結果要逐項比對，不能只抽查一兩格或只看有沒有報錯。只放幾個完整方塊（例如 2×2 金／鑽石塊）的測試不算驗過。
  - Copy/Paste：用 3D 測試房子（`scripts/mcc_house.py`：門、台階、樓梯、原木軸向、玻璃片、火把、燈籠、箱子），每一步逐格比對完整 blockstate。
  - Utilities：玩家真的挖／採收（連鎖砍樹、礦脈、補種），每個據點與 Back／死亡點都實際傳送並比對落點。
  - Warehouse：用 inno 地圖上真的倉庫與玩家自訂分類，不假設預設分類；分類、查詢、Pick、共用 API 都要比對實際箱子內容。
- **任何單次 innotest 測試都必須在 4 分鐘（240 秒）內完成。** 完整 coverage 若超過 4 分鐘，必須拆成多個互相獨立、各自 ≤240 秒的 shard；不能用「full suite」當理由跑 40 分鐘，也不能為了塞進 4 分鐘而少驗案例。每個 shard 都要能獨立 PASS/FAIL、清理並還原測試狀態。
- CI／官方 server 僅是輔助證據；只有 innotest live 才算本專案實機驗證。能不額外觸發 workflow 就不跑：需要 GitHub Secret／遠端 innotest 時才使用 workflow，完整 CI 留在階段完成或 Release 前；回報實際跑過的測試、workflow run 與結果，未跑不可寫 PASS。

## innotest 保持開機

- 測完不關機；清測試狀態不等於關機。
- 只有安裝必須重啟時才重啟，完成後保持開機。使用者要求才關機。

## 正式環境（inno）資料相容

`inno` 有真實的玩家與世界資料。已部署到 inno 的 pack（目前三個 datapack：Warehouse、Utilities、Copy/Paste），只要改動可能影響存檔資料（storage／scoreboard 格式、migration、箱子註冊、玩家設定與統計、會搬動或改寫物品的程式等），新版裝到 inno 之前，先在 innotest（有 inno 的地圖）裝新版，確認既有資料升級正確（有 migration 時也要確認重跑不出錯）；通過後，等使用者明確下指令才可以裝到 inno。

- 不確定會不會影響資料時，當作會。
- 不要在 inno 上直接實驗；能不改資料格式就不改，優先選不需要 migration 的做法。
- review 或實作有風險的改動時，說明：是否改到存檔資料、是否需要 migration、在 innotest 做了哪些測試。

## Datapack 效能優先順序

1. 每 tick／高頻路徑的時間複雜度與成本最優先。
2. 其次是每次執行的指令數（含失敗的條件判斷、selector 掃描、多餘的 function 呼叫）。
3. server 記憶體只有在狀態很大、會無限成長或產生大量實體時才優先考慮；少量固定的 scoreboard／storage 換到明顯較少的 tick 成本是可以接受的。

比較或提出演算法時，列出前後的熱路徑指令數、時間複雜度與額外空間；能實測就實測。

## 文件與玩家介面

- 玩家指令集中維護在各 Pack 的 `README.md`；版本與入口總覽見根目錄 `README.md`，實機功能覆蓋與未驗項目只維護在 `docs/innotest-coverage.md`。不要在多份文件複製大量過期測試狀態。
- 文件、玩家提示優先用繁體中文、台灣 Minecraft 常用譯名或 English，不用中國大陸用語。Copy/Paste 玩家入口寫「按 G → 建築工具」，不要要求玩家使用過期 Trigger。
