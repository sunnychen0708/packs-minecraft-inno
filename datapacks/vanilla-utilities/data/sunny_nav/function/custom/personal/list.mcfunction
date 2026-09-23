
scoreboard players set @s plist 0
execute store result storage sunny_nav:ctx id int 1 run scoreboard players get @s sunny_id
tellraw @s {"text":"────── 我的自訂據點 ──────","color":"green"}
tellraw @s {"text":"未設定：[設定] 會讓你輸入名稱；已設定：[覆蓋] 只換位置，[自訂名稱] 只改名稱。","color":"gray"}
function sunny_nav:custom/personal/list_slots with storage sunny_nav:ctx
tellraw @s [{"text":"[返回主選單]","color":"gold","click_event":{"action":"run_command","command":"/trigger help"}}]
