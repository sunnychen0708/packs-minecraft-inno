execute if score @s prename matches 1 run function sunny_nav:custom/personal/rename_prompt/1
execute if score @s prename matches 2 run function sunny_nav:custom/personal/rename_prompt/2
execute if score @s prename matches 3 run function sunny_nav:custom/personal/rename_prompt/3
execute if score @s prename matches 4 run function sunny_nav:custom/personal/rename_prompt/4
execute if score @s prename matches 5 run function sunny_nav:custom/personal/rename_prompt/5
execute if score @s prename matches 6 run function sunny_nav:custom/personal/rename_prompt/6
execute if score @s prename matches 7 run function sunny_nav:custom/personal/rename_prompt/7
execute if score @s prename matches 8 run function sunny_nav:custom/personal/rename_prompt/8
execute unless score @s prename matches 1..8 run function sunny_nav:custom/invalid_slot
scoreboard players set @s prename 0
