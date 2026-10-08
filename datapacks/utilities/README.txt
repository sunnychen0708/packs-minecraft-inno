屁眼派對 — Minecraft Java 26.3（整合版 v3.2）
（整合：生存便利三合一＋回家與自訂據點＋座標顯示）

安裝／更新：
1. 以「整合_v3.2.zip」取代舊版資料包，不要刪除世界資料。
2. ZIP 不用解壓，放進世界的 datapacks 資料夾。
3. 進入世界後輸入 /reload。
4. 輸入 /trigger help 查看功能。

v3.2 主要變更：
- 共用據點固定為 8 格；v3.0 曾預留的 9～16 格已從資料包移除，載入時也會清掉 sunny_nav:shared 的 s9～s16 舊欄位。
- /trigger help 改為「先指令教學、再操作按鈕」。
- 固定據點（家／礦坑／村莊／傳送門／臨時點）不再顯示直接執行按鈕，只保留可點擊並自動填入的指令教學。
- 個人／共用據點清單、功能開關、返回上次位置與死亡地點仍保留操作按鈕。
- 名稱輸入 Dialog 的「設定／儲存名稱」按鈕文字改為白色。
- 名稱輸入 Dialog 改為確認型：按 Esc 或「取消」只會關閉視窗，不會送出任何指令、也不會儲存或改名。
- 按「設定／儲存名稱」才會執行原本的儲存動作。

舊資料相容：
- 家、礦坑、村莊、傳送門、臨時點、個人據點 1～8、共用據點 1～8、名稱、功能開關全部沿用。
- storage ID 與既有 scoreboard objective 名稱不更動。

據點指令：
- 個人：/trigger plist；/trigger pset set 1；/trigger pgo set 1（slot 1～8）
- 共用：/trigger slist；/trigger sset set 1；/trigger sgo set 1（slot 1～8）
- 返回上次位置：/trigger back
- 最近死亡地點：/trigger deathloc

管理員／function API：
- /function nav:set_personal {slot:1,name:"名稱"}
- /function nav:set_shared {slot:1,name:"名稱"}
- /function nav:rename_personal {slot:1,name:"新名稱"}
- /function nav:rename_shared {slot:1,name:"新名稱"}
- /function nav:back
- /function nav:death

注意：
- 名稱輸入視窗送出時仍由 Vanilla dynamic/run_command 呼叫 function；若伺服器限制一般玩家執行 function，可能受權限規則影響。
- Esc／取消不會執行該 dynamic/run_command。
- back／死亡地點與原傳送系統支援主世界、地獄、終界。
- Data Pack 格式：121.0（Minecraft Java 26.3）。
