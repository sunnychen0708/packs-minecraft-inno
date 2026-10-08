execute if score @s srename matches 1 run function sunny_nav:custom/shared/rename_prompt/1
execute if score @s srename matches 2 run function sunny_nav:custom/shared/rename_prompt/2
execute if score @s srename matches 3 run function sunny_nav:custom/shared/rename_prompt/3
execute if score @s srename matches 4 run function sunny_nav:custom/shared/rename_prompt/4
execute if score @s srename matches 5 run function sunny_nav:custom/shared/rename_prompt/5
execute if score @s srename matches 6 run function sunny_nav:custom/shared/rename_prompt/6
execute if score @s srename matches 7 run function sunny_nav:custom/shared/rename_prompt/7
execute if score @s srename matches 8 run function sunny_nav:custom/shared/rename_prompt/8
execute unless score @s srename matches 1..8 run function sunny_nav:custom/invalid_slot
scoreboard players set @s srename 0
