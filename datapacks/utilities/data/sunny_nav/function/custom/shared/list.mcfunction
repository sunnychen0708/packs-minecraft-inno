
scoreboard players set @s slist 0
tellraw @s {"text":"────── 全服共用據點 ──────","color":"aqua"}
tellraw @s {"text":"共 8 格。未設定：[設定] 會讓你輸入名稱；已設定：[覆蓋] 只換位置，[自訂名稱] 只改名稱。","color":"gray"}
function sunny_nav:custom/shared/list_slots
tellraw @s [{"text":"[返回主選單]","color":"gold","click_event":{"action":"run_command","command":"/trigger help"}}]
