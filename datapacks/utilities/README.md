# Utilities v3.8

Minecraft Java 26.3（Data Pack 121.0）。最新 Release：[utilities-v3.8.zip](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/utilities-v3.8)；舊版名稱曾為「整合_v3.2」。

提供傳送與據點、座標顯示、連鎖砍樹、礦脈挖掘與自動補種。遊戲內輸入 **`/trigger help`** 可查看指令教學。

## 玩家指令

| 用途 | 指令 |
| --- | --- |
| 功能教學／座標顯示 | `/trigger help`、`/trigger coords` |
| 個人據點（1–8） | `/trigger plist`、`/trigger pset set 1`、`/trigger pgo set 1` |
| 共用據點（1–8） | `/trigger slist`、`/trigger sset set 1`、`/trigger sgo set 1` |
| 返回上次傳送位置／死亡地點 | `/trigger back`、`/trigger deathloc` |
| 生存便利開關 | `/trigger treecap`、`/trigger veinmine`、`/trigger replant` |

將例子中的 `1` 換成 1–8。固定據點包含家、礦坑、村莊、傳送門、臨時點；所有據點傳送都落在方塊中央，支援主世界、地獄與終界。

連鎖砍樹需蹲下、持斧頭，附近要有樹葉；單次最多 64 根，支援 Poplar 三色樹葉。礦脈挖掘照原版礦石給經驗，絲綢之觸不給；鎬的材質等級不足則不會連鎖挖取。自動補種需有可用種子。

## 管理與資料相容

據點名稱可透過遊戲內 Dialog 管理；管理員也可用：

```mcfunction
/function nav:set_personal {slot:1,name:"名稱"}
/function nav:rename_personal {slot:1,name:"新名稱"}
/function nav:set_shared {slot:1,name:"名稱"}
/function nav:rename_shared {slot:1,name:"新名稱"}
```

**v3.8 不更換**既有 storage／scoreboard ID；固定、個人／共用據點、名稱、玩家開關可延用。舊 world v3.7 → v3.8 已在 innotest 驗證 PASS，證據見 [覆蓋表](../../docs/innotest-coverage.md)。

重要的既有設計：**v3.4 撤回了 v3.3 工具逐塊扣耐久的修正，恢復 v3.2 的耐久處理**（包含舊的工具修復行為）；沒有在新版偷偷重新引入逐塊扣耐久。新增 Poplar mined objective 與 26.3 相容修正保留。資料包對應原版 Java 26.3 格式 `[121,0]`。

## 版本重點

| 版本 | 更新 |
| --- | --- |
| v1.x–v2.x | 三包整合、5 種固定與個人／共用據點、Dialog 命名、升級 Minecraft 26.3 |
| v3.0–v3.2 | Back／死亡點、各 8 格據點、清理無用功能與介面 |
| v3.3–v3.4 | 補上 Poplar 挖掘事件；撤回耐久改動，保持 v3.2 行為 |
| v3.5 | 移除載入與首次加入的多餘聊天訊息 |
| v3.6 | 礦脈連鎖掉落的原版 XP（煤、青金石、紅石、鑽石、綠寶石、石英、地獄金礦） |
| v3.7 | 礦脈鎬階檢查，防止等級不足的鎬取得高階礦掉落 |
| **v3.8** | 修正所有傳送點落在方塊交角的問題；樹葉檢查改為近到遠、找到即停 |

## 安裝與驗證

移除舊 Utilities ZIP（含 `整合_v3.2.zip`／`vanilla-utilities-v3.2.zip`），只放入目前版本的 ZIP 至世界 `datapacks/`，再依情況 `/reload`；**勿同時載入兩份**。使用 Dialog 時，變更 registry JSON 可能需要重入世界。

```bash
python3 scripts/validate-datapack.py utilities
python3 scripts/test-utilities.py
python3 scripts/test-utilities.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
```

官方 26.3 runtime 檢查 Poplar、無葉保護、砍樹／挖礦、鎬階、XP、耐久、補種與舊據點資料；但它不取代 [innotest 功能覆蓋](../../docs/innotest-coverage.md)，真人 UI 也要獨立驗證。舊 Release Tag 與歷史仍在 GitHub Releases。
