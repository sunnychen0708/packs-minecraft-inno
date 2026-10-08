execute unless score @s mcc_bpactive matches 1 run tellraw @s [{"text":"[Copy/Paste] 請先建立 Blueprint。","color":"red"}]
execute unless score @s mcc_bpactive matches 1 run return fail
execute unless score @s mcc_bpready matches 1 run tellraw @s [{"text":"[Copy/Paste] Blueprint 還在建立中。","color":"yellow"}]
execute unless score @s mcc_bpready matches 1 run return fail
execute if score @s mcc_matphase matches 1.. run tellraw @s [{"text":"[Copy/Paste] 另一個材料檢查正在進行。","color":"yellow"}]
execute if score @s mcc_matphase matches 1.. run return fail
execute if score @s mcc_bpover_scan matches 1 run tellraw @s [{"text":"[Copy/Paste] Blueprint 覆蓋檢查仍在更新，請稍候。","color":"yellow"}]
execute if score @s mcc_bpover_scan matches 1 run return fail
function mcc:materials/ensure_player
function mcc:materials/reset_have_start
scoreboard players set @s mcc_materr 0
scoreboard players set @s mcc_matjob 2
scoreboard players set @s mcc_matphase 1
function mcc:materials/queue_items
tellraw @s [{"text":"[Copy/Paste] 正在查詢 Warehouse 庫存…","color":"aqua"}]
execute if score @s mcc_matleft matches 0 run return run function mcc:materials/count_done
return 1
