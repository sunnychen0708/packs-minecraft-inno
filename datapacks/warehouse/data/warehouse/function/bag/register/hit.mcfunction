data modify storage warehouse:bags candidate set value {registered:1b}
execute store result storage warehouse:bags candidate.x int 1 run data get block ~ ~ ~ x
execute store result storage warehouse:bags candidate.y int 1 run data get block ~ ~ ~ y
execute store result storage warehouse:bags candidate.z int 1 run data get block ~ ~ ~ z
execute if dimension minecraft:overworld run data modify storage warehouse:bags candidate.dimension set value "minecraft:overworld"
execute if dimension minecraft:the_nether run data modify storage warehouse:bags candidate.dimension set value "minecraft:the_nether"
execute if dimension minecraft:the_end run data modify storage warehouse:bags candidate.dimension set value "minecraft:the_end"
execute unless data storage warehouse:bags candidate.dimension run return 0
scoreboard players set @s wh_bag_dup 0
function warehouse:bag/register/check_duplicates with storage warehouse:bags candidate
execute if score @s wh_bag_dup matches 1 run return run tellraw @s {"text":"[Warehouse] 這個箱子已被其他 Warehouse 編號註冊。","color":"red"}
execute if score @s wh_bag_target matches 2.. if data storage warehouse:bags candidate run function warehouse:bag/register/check_buffer
execute if score @s wh_bag_ok matches 0 run return 0
execute if score @s wh_bag_target matches 1 run function warehouse:bag/register/save/01a
execute if score @s wh_bag_target matches 2 run function warehouse:bag/register/save/01b
execute if score @s wh_bag_target matches 3 run function warehouse:bag/register/save/02a
execute if score @s wh_bag_target matches 4 run function warehouse:bag/register/save/02b
execute if score @s wh_bag_target matches 5 run function warehouse:bag/register/save/03a
execute if score @s wh_bag_target matches 6 run function warehouse:bag/register/save/03b
execute if score @s wh_bag_target matches 7 run function warehouse:bag/register/save/04a
execute if score @s wh_bag_target matches 8 run function warehouse:bag/register/save/04b
execute if score @s wh_bag_target matches 9 run function warehouse:bag/register/save/05a
execute if score @s wh_bag_target matches 10 run function warehouse:bag/register/save/05b
tag @s remove wh_bag_reg_pending
scoreboard players set @s wh_bag_target 0
function warehouse:chunks/refresh
tellraw @s {"text":"[Warehouse] 背包箱註冊已更新；箱內物品沒有移動。","color":"yellow"}
