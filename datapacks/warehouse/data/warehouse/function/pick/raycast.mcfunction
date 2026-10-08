scoreboard players set #pick_pass wh_tmp 0
execute if block ~ ~ ~ #minecraft:air run scoreboard players set #pick_pass wh_tmp 1
execute if block ~ ~ ~ minecraft:water run scoreboard players set #pick_pass wh_tmp 1
execute if block ~ ~ ~ minecraft:lava run scoreboard players set #pick_pass wh_tmp 1
execute if block ~ ~ ~ minecraft:bubble_column run scoreboard players set #pick_pass wh_tmp 1
execute unless score #pick_pass wh_tmp matches 1 run return run function warehouse:pick/hit
scoreboard players add @s wh_ray 1
execute if score @s wh_ray matches ..23 positioned ^ ^ ^0.25 run return run function warehouse:pick/raycast
tellraw @s [{"text":"[Warehouse] ","color":"gold"},{"text":"Pick 找不到準星指向的方塊。","color":"yellow"}]
return fail
