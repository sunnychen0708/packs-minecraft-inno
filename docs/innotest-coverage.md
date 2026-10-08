# innotest 功能覆蓋與證據

> 適用三個 Datapack；更新功能時請同步更新。僅標註**實際在 innotest 跑完**的項目。靜態／官方 server runtime PASS 不代表 live PASS。細則見 [驗證方式](datapack-validation.md) 和 [AGENTS.md](../AGENTS.md)。

**執行方式：** Utilities 用 `scripts/build-utilities-live-test.py`、Warehouse 用 `scripts/build-warehouse-live-test.py`，透過 `run-live-suite` 執行；Copy/Paste 用 `scripts/build-copy-paste-multiplayer-test.py` + `run-copy-paste-multiplayer-test`；缺口則用 `scripts/build-copy-paste-gap-live-test.py` 的獨立 `copy-paste-gap-{external,modes,dimensions,history,materials,ui-packets}` shards 執行 `run-live-suite`。必須以 `scripts/mcc_house.py` 的完整 3D 房屋逐格比對，Dialog 封包檢查不算真人 UI。預設三 bot 為 `penguin0531`／`geena0701`／`Felicitypeng`，不占用 SunnyChen。

**硬限制：每次 ≤240 秒**，較長的測試切 shard，各 shard 都要獨立 PASS/FAIL、清理／還原，不能砍覆蓋案例。舊 Utilities 40 分鐘 `--full` 不適用；重查已驗項目可用 `utilities-recheck`／`warehouse-recheck`、Copy/Paste `recheck`。必要時僅在 server 指令段使用加速 tick，bot 回應／chunk 載入用 20 tps，清理一律恢復 20。

狀態：「PASS」僅限表列實際範圍；「部分」表示其他變體尚未實機驗；「未驗」表示只有 CI／headless 或無證據。

## Utilities v3.8

主要證據：[功能重點及 recheck 37621164714／37630732909](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37630732909)；[舊資料升級 37642068254](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37642068254)。

| 功能 | innotest 實際覆蓋／未覆蓋 | 狀態 |
| --- | --- | --- |
| `help`、`coords` | Trigger 回應、玩家獨立開關 | PASS |
| 固定據點、Back／死亡點 | 家／礦坑／村莊、三維度落點與置中、Back、死亡點；傳送門／臨時點只存在舊 full 規劃 | 部分 |
| 個人／共用據點 1–8 | 第 1、8 格的設定、傳送、命名／改名、覆寫、兩人隔離；不是 1–8 每一格全跑 | 部分 |
| 連鎖砍樹 | 真玩家橡木、無葉、非蹲下、停用、64 根；三色 Poplar 及其他樹種未全量 live | 部分 |
| 礦脈與鎬等級 | 深板岩鑽石、遠古遺骸、XP／絲綢之觸、最低鎬階、停用；其他礦／耐久變體未全量 live | 部分 |
| 自動補種 | 小麥與停用路徑；其他作物未全量 live | 部分 |
| Dialog 名稱輸入 | `nav:set_*`、`nav:rename_*` 的等效指令 | PASS（非真人點擊） |
| v3.7 → v3.8 舊資料 | 玩家據點、名稱與設定保留 | PASS |

## Warehouse v4.7

功能與 recheck：[37624017827](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37624017827)、[37629667234](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37629667234)；release targeted gate [37641685439](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37641685439)；跨維度 [37656341833](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37656341833)。

| 功能 | innotest 實際覆蓋／未覆蓋 | 狀態 |
| --- | --- | --- |
| 自動分類／玩家自訂分類 | 真實入口箱、當下 `warehouse:rules overrides`、新增／搬移／刪除分類及庫存回收 | PASS |
| 箱子管理 | 註冊／解除、命名、查詢、瀏覽、分頁；恢復測試資料 | PASS |
| 滿箱／溢位／保留入口 | 主箱滿 → 溢位；都滿 → 留在入口箱 | PASS |
| Pick／共享材料 API | Count、Take、Refund、Material Sources、Resolve Block、pending refund 與 Pick | PASS |
| Compact／背景整理 | 自動 tick 合併 40+30→64+6、數量不變；跨三維度 27 checkpoints | PASS |
| Chunk forceload | 已註冊箱常駐，別人的 forceload 不受影響 | PASS |
| 開關／遷移 | system on/off、v4.0–v4.6 舊資料重跑 | PASS |
| G 主畫面／Dialog | bot 收到主畫面、管理、查詢、分類、說明及返回 | PASS（非真人點擊） |
| Highlight | 共用 `warehouse:api/highlight` 的 live API 路徑有 PASS；玩家可見粒子位置／訊息未跑 | **部分** |
| **Issue #72：個人背包 `bag`** | [innotest Run 37774242630](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37774242630) 驗證 02-A/02-B、J→Q→K→J 改綁交換；[完整實測 Run 37787701641](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37787701641) 第 1 組 27 格及 Item Components 逐格比對、來回交換 PASS（92.99 秒）。尚未驗所有玩家、快捷列／裝備／副手的完整逐格回歸。 | **部分 PASS** |
| **Issue #72：共用背包 `sbag`** | [完整實測 Run 37787701641](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37787701641) 第 3 組兩名 bot 競爭、占用互斥、占用者斷線、他人被拒、重新登入歸還、05-A 遭外部放物品時防覆寫／清空後歸還 PASS（186.08 秒）。尚未驗所有四名玩家的完整排列與真人介面。 | **部分 PASS** |
| **Issue #72：跨維度／無效箱防護** | [完整實測 Run 37787701641](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37787701641) 第 2 組：玩家在主世界、A 在地獄、B 在終界，來回交換與資料比對、B 非空拒絕、A 無效座標拒絕 PASS（154.44 秒）。其他玩家維度組合尚未逐一驗證。 | **部分 PASS** |
| **Issue #72：G → 背包箱註冊** | [Run 37799688068](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37799688068)：02–04 三名玩家各 14/14 PASS（42/42）；[Run 37803796428](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37803796428)：01 與 05 使用 SunnyChen 身分實機右鍵及 Trigger 分別 14/14、17/17 PASS，合計 31/31（30.6、30.9 秒），包含 A/B、B 非空拒絕、改綁不搬物品、其他玩家越權拒絕、取消註冊，以及共用背包使用中禁止重新註冊與取消 05。五組均完成測試資料／原 ZIP 還原和 bot 斷線確認；innotest 保持開機。**01–05 註冊權限及 Minecraft 原版右鍵流程已驗證；真人按 G 鍵、實際點選 Dialog 按鈕尚未驗證（已驗證 wh_nav 的 show_dialog 封包及按鈕指令映射）。** | **部分 PASS** |

## Copy/Paste v1.8

完整房屋多人 [37718900567](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37718900567) 所有 `MCCMP_CHECK` PASS；35,720 合法 blockstates + 4 重複 regression [37719130915](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37719130915)：`states=35724 expected=35724 fail=0 air_ret=0`。

| 功能 | innotest 實際覆蓋／未覆蓋 | 狀態 |
| --- | --- | --- |
| Pos1／Pos2、Copy、Clipboard | A/B 獨立選區、`mcc_id`、完整 3D house | PASS |
| Blueprint／Build | Blueprint 完整 state、背包材料 BOM、施工後逐格相同 | PASS（背包材料） |
| Blueprint 六向微調、Rotate、Flip、reset | 逐格核對；新 Copy、Cut、Cut→Undo→Redo 後方向歸 0°／未翻面 | PASS |
| 直接 Move／Rotate／Flip | 六方向 Move、90° 左／右與 180°、兩軸翻面、各自 Undo | PASS |
| Undo／Redo guard | 忽略同方塊 ID 的 state 改動；換 ID／箱內物品改動會拒絕並列差異 | PASS |
| Cut／Paste、多人隔離 | 兩位玩家同 tick、A/B 獨立 Undo、Cut/Redo 恢復 Clipboard | PASS |
| 35,720 種 block state matcher | 全量 + 4 重複案例 | PASS |
| Warehouse 混合材料／不足不施工 | 真實 innotest 的完整 3D 房屋：背包＋Warehouse 混合扣料、不足完全不施工、施工成功且背包份額精確消耗、Undo 退回背包及 Warehouse 8 種材料逐品項數量精確 PASS（[37737410514](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37737410514)）；測後復原倉庫註冊與測試玩家背包 | **PASS（已驗範圍）** |
| 覆蓋保護、`materials`、5 層完整 Undo／退款 | `materials` 只讀、目標已有方塊時先警告再施工、Undo 保留原有方塊、混合扣料後背包／Warehouse 精確退款 PASS（[37737410514](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37737410514)）；連續五次房屋 Move＋逐筆 Undo 完整狀態／筆數 PASS（[37736767886](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37736767886)）。**未堆疊五筆獨立材料 Build 後逐筆退款** | **部分** |
| 外部 Anchor、Replace／Masked | 外部 Anchor 真正 3D Rotate／Flip 與各自 Undo 逐格 PASS（[37736165012](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37736165012)）；Replace／Masked 各自剪下貼上 3D 房屋，含原目標方塊／來源空氣處理 PASS（[37736427722](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37736427722)）。**外部 Anchor Blueprint Build** 尚未 live 驗 | **部分** |
| 地獄／終界 Copy/Paste | 地獄／終界各自 3D 房屋 Copy、完整 Blueprint、Cut／Paste、來源清空與 Undo 還原逐格 PASS（[37736565101](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37736565101)）；跨維度搬運（例如主世界複製、地獄貼上）未另行驗證 | **部分** |
| G／Dialog／準星真人 UI | v1.8 兩名 bot 各自收到 Copy/Paste `show_dialog` 封包 PASS（[37737261488](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37737261488)）；**真人按 G、滑鼠點選 Dialog、準星手感與雙真人併發仍未驗** | **部分（非真人 UI）** |

## Resource Pack

`cat-door-sounds` 是 client-side Resource Pack，不會由 innotest 的 Mineflayer bot 載入；需真人 Minecraft client 驗證，不能標示 bot PASS。
