scoreboard players add @s sunny_deaths 0
scoreboard players operation @s sunny_dseen = @s sunny_deaths
scoreboard players add #next sunny_id 1
scoreboard players operation @s sunny_id = #next sunny_id
tellraw @s [{"text":"[傳送系統] ","color":"gold"},{"text":"已啟用。輸入 ","color":"white"},{"text":"/trigger help","color":"aqua","click_event":{"action":"run_command","command":"/trigger help"},"hover_event":{"action":"show_text","value":{"text":"點擊開啟功能總覽","color":"yellow"}}},{"text":" 查看用法。","color":"white"}]
