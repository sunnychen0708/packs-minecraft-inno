scoreboard players set @s su_init 1
scoreboard players set @s su_tree 1
scoreboard players set @s su_vein 1
scoreboard players set @s su_plant 1
scoreboard players set @s su_crop 0
scoreboard players set @s su_ctime 0
tellraw @s [{"text":"[屁眼派對] ","color":"gold"},{"text":"自動補種、連鎖砍樹、礦脈挖掘已預設開啟。輸入 ","color":"green"},{"text":"/trigger help","color":"aqua","click_event":{"action":"run_command","command":"/trigger help"},"hover_event":{"action":"show_text","value":{"text":"點擊開啟功能總覽","color":"yellow"}}},{"text":" 查看全部功能與開關。","color":"green"}]
