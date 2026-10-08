kill @e[type=minecraft:marker,tag=mcc_temp_hit]
execute align xyz run summon minecraft:marker ~ ~ ~ {Tags:["mcc_temp_hit"]}

execute store result score @s mcc_anx run data get entity @e[type=minecraft:marker,tag=mcc_temp_hit,limit=1] Pos[0] 1
execute store result score @s mcc_any run data get entity @e[type=minecraft:marker,tag=mcc_temp_hit,limit=1] Pos[1] 1
execute store result score @s mcc_anz run data get entity @e[type=minecraft:marker,tag=mcc_temp_hit,limit=1] Pos[2] 1
scoreboard players set @s mcc_and 0
execute if dimension minecraft:overworld run scoreboard players set @s mcc_and 1
execute if dimension minecraft:the_nether run scoreboard players set @s mcc_and 2
execute if dimension minecraft:the_end run scoreboard players set @s mcc_and 3

kill @e[type=minecraft:marker,tag=mcc_temp_hit]
execute unless score @s mcc_and matches 1..3 run tellraw @s [{"text":"[Copy/Paste] 目前只支援主世界、地獄、終界。","color":"red"}]
execute unless score @s mcc_and matches 1..3 run return fail
scoreboard players set @s mcc_hasa 1
tellraw @s [{"text":"[Copy/Paste] Anchor 已設定。","color":"green"}]
return 1
