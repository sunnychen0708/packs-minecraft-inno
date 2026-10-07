# 工作規則

適用整個 repo，所有貢獻者、agent、自動化流程與 reviewer 都要遵守。

## inno 寫入

- 任何寫入 inno 的動作都要使用者明確下指令才可以做，包括安裝或更新 datapack、改檔案、執行指令、啟動／關閉／重啟、UUID maintenance 的 apply。每次都要，之前的同意不能沿用。
- 讀取 inno 不用問，直接讀。

## 測試

- 一律直接在 `innotest` 測（`exaroton innotest control` workflow；需要玩家時用 Mineflayer bots）。
- 不要在本機、暫存資料夾、另建的世界或 MCC-Test 測，除非使用者指定。
- CI 照常跑，但只有 innotest 的結果才算驗過；回報時附上跑了什麼、workflow run 與結果。

## innotest 保持開機

- 測完不關機；清測試狀態不等於關機。
- 只有安裝必須重啟時才重啟，完成後保持開機。使用者要求才關機。

## 正式環境（inno）資料相容

`inno` 有真實的玩家與世界資料。已部署到 inno 的 pack（目前是 Warehouse、Utilities），只要改動可能影響存檔資料（storage／scoreboard 格式、migration、箱子註冊、玩家設定與統計、會搬動或改寫物品的程式等），新版裝到 inno 之前必須：

1. 複製目前的 inno 世界到 innotest；
2. 在上面套用新版本，確認既有資料升級正確（有 migration 時也要確認重跑不出錯）；
3. 通過後，等使用者明確下指令才可以把新版裝到 inno。

- 乾淨世界的測試不能代替這一步。不確定會不會影響資料時，當作會。
- 不要在 inno 上直接實驗；能不改資料格式就不改，優先選不需要 migration 的做法。
- Copy/Paste 尚未部署到 inno，這條暫時不適用，部署後再套用。
- review 或實作有風險的改動時，說明：是否改到存檔資料、是否需要 migration、做了哪個 inno 副本測試。

## Datapack 效能優先順序

1. 每 tick／高頻路徑的時間複雜度與成本最優先。
2. 其次是每次執行的指令數（含失敗的條件判斷、selector 掃描、多餘的 function 呼叫）。
3. server 記憶體只有在狀態很大、會無限成長或產生大量實體時才優先考慮；少量固定的 scoreboard／storage 換到明顯較少的 tick 成本是可以接受的。

比較或提出演算法時，列出前後的熱路徑指令數、時間複雜度與額外空間；能實測就實測。
