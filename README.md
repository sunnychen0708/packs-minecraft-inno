# Minecraft Inno Packs

Minecraft Java Datapacks 與 Resource Pack 專案；遊戲內名詞使用台灣常見譯名或 English。**正式規則**：[AGENTS.md](AGENTS.md)；**測試紀錄**：[innotest 覆蓋表](docs/innotest-coverage.md)。

## 版本與使用說明

| Pack | 最新 Release | 功能／教學 |
| --- | --- | --- |
| Utilities | [v3.8](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/utilities-v3.8) | [據點、傳送、連鎖砍樹／礦脈／補種與指令](datapacks/utilities/README.md) |
| Warehouse | [v4.7](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/warehouse-v4.7) | [自動分類、查詢、箱子管理、Pick、API](datapacks/warehouse/README.md) |
| Copy/Paste | [v1.8](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/copy-paste-v1.8) | [Blueprint、Build、Move、Rotate、Flip、Undo/Redo 與指令](datapacks/copy-paste/README.md) |
| cat-door-sounds | [v1.0](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/cat-door-sounds-v1.0) | [貓咪與門的音效](resourcepacks/cat-door-sounds/README.md) |

三包 Datapack 預設搭配 Minecraft Java 26.3。Warehouse 提供全服材料來源，Copy/Paste 的 Build 先用玩家背包，才向 Warehouse 扣料。

**安裝：** 到 [Releases](https://github.com/sunnychen0708/packs-minecraft-inno/releases) 下載 ZIP，Datapack 放 `<world>/datapacks/`、Resource Pack 放 `.minecraft/resourcepacks/`。更新時刪除同一包的舊 ZIP，**不能同時安裝兩版**。介面 registry JSON 變更時，退出世界再登入才能完整更新 Dialog；`/reload` 不能取代重新進入世界。

遊戲內入口：Warehouse 按 **G**；Copy/Paste 按 **G → 建築工具**，或 `/trigger cphelp` 查看指令；Utilities 用 `/trigger help`。

## 開發與操作文件

| 文件 | 內容 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | inno／innotest 安全規則、240 秒測試、Git 作者規範 |
| [Datapack 驗證與 Release](docs/datapack-validation.md) | CI／runtime／live／真人 client 的差異、發佈條件、證據 |
| [innotest 功能覆蓋表](docs/innotest-coverage.md) | 三包各功能的已驗／未驗、live run |
| [exaroton 操作](docs/exaroton-operations.md) | 伺服器權限、Mineflayer、UUID 遷移、request 與最後確認狀態 |

原始碼：`datapacks/{utilities,warehouse,copy-paste}/`、`resourcepacks/cat-door-sounds/`；共用腳本在 `scripts/`，GitHub Actions 在 `.github/workflows/`，一次性遠端 request 在 `ops/`（平時都應是 `noop`）。ZIP 由 `scripts/build-pack.sh` 輸出到已忽略的 `dist/`，不直接提交產物。

```bash
# 建置
./scripts/build-pack.sh utilities v3.8
./scripts/build-pack.sh warehouse v4.7
./scripts/build-pack.sh copy-paste v1.8

# 靜態驗證
python3 scripts/validate-datapack.py utilities
python3 scripts/validate-datapack.py warehouse
python3 scripts/validate-datapack.py copy-paste
python3 scripts/test-datapack-compatibility.py
```

官方 runtime、innotest live 與真人 client 驗證方式見 [驗證文件](docs/datapack-validation.md)；**CI PASS 不代表 innotest live PASS**。遠端測試預設三位非 SunnyChen bot，例行結束不關機；每次測試最多 **4 分鐘／240 秒**，完整 coverage 須拆 shard。

一般 Release 由 `release-pack.yml` 驗證並以 `<pack>-v<major>.<minor>` 發佈；只有使用者明確要求才可走 direct/no-gate，跳過部分不可聲稱 PASS。2026-10-08 壓縮 Git 歷史後，Release notes 改以 `scripts/generate-release-notes.py` 比較同一 Pack 前後版本的**檔案內容**，不依賴共同 commit 祖先。
