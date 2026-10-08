execute unless block ~ ~ ~ #minecraft:air run return run function mcc:ray/hit
scoreboard players add @s mcc_ray 1
execute if score @s mcc_ray matches ..1023 positioned ^ ^ ^0.125 run return run function mcc:ray/step
tellraw @s [{"text":"[Copy/Paste] 128 格內沒有瞄準到方塊。","color":"red"}]
return fail
