execute unless score @s mcc_bpactive matches 1 run tellraw @s [{"text":"[Copy/Paste] 目前沒有 Blueprint。","color":"red"}]
execute unless score @s mcc_bpactive matches 1 run return fail
execute unless score @s mcc_bpready matches 1 run tellraw @s [{"text":"[Copy/Paste] Blueprint 還在建立中，暫時不能微調。","color":"yellow"}]
execute unless score @s mcc_bpready matches 1 run return fail
scoreboard players operation @s mcc_bptx0 += @s mcc_dx
scoreboard players operation @s mcc_bpty0 += @s mcc_dy
scoreboard players operation @s mcc_bptz0 += @s mcc_dz
scoreboard players operation @s mcc_bpaimx += @s mcc_dx
scoreboard players operation @s mcc_bpaimy += @s mcc_dy
scoreboard players operation @s mcc_bpaimz += @s mcc_dz
scoreboard players set @s mcc_buildconfirm 0
execute store result storage mcc:temp nudge.id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp nudge.dx int 1 run scoreboard players get @s mcc_dx
execute store result storage mcc:temp nudge.dy int 1 run scoreboard players get @s mcc_dy
execute store result storage mcc:temp nudge.dz int 1 run scoreboard players get @s mcc_dz
function mcc:blueprint/nudge/entities with storage mcc:temp nudge
function mcc:blueprint/recount_start
tellraw @s [{"text":"[Copy/Paste] Blueprint 已微調；正在分批更新覆蓋檢查。","color":"gray"}]
return 1
