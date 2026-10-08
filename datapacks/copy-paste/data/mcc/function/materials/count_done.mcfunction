execute if score @s mcc_materr matches 1 run tellraw @s [{"text":"[Copy/Paste] Warehouse 材料來源不完整或失效，未施工。請先修正 Warehouse 註冊狀態。","color":"red"}]
execute if score @s mcc_materr matches 1 run scoreboard players set @s mcc_matphase 0
execute if score @s mcc_materr matches 1 run scoreboard players set @s mcc_matjob 0
execute if score @s mcc_materr matches 1 run return fail
scoreboard players set @s mcc_matmiss 0
scoreboard players set @s mcc_matkind 0
scoreboard players set @s mcc_mattotal 0
execute store result storage mcc:temp pid int 1 run scoreboard players get @s mcc_id
function mcc:materials/eval_init with storage mcc:temp
# A material check (job 2) only reports: it must never fall through to taking materials and building.
execute if score @s mcc_matjob matches 2 run return run function mcc:materials/check_done
execute if score @s mcc_matmiss matches 1 if score @s mcc_matjob matches 0 run function mcc:materials/report_missing
execute if score @s mcc_matmiss matches 1 if score @s mcc_matjob matches 1 run function mcc:materials/report_missing_redo
execute if score @s mcc_matmiss matches 1 run scoreboard players set @s mcc_matphase 0
execute if score @s mcc_matmiss matches 1 run scoreboard players set @s mcc_matjob 0
execute if score @s mcc_matmiss matches 1 run return fail
function mcc:materials/remain_init_start
scoreboard players set @s mcc_matphase 2
function mcc:materials/queue_items
execute if score @s mcc_matleft matches 0 run return run function mcc:materials/take_done
return 1
