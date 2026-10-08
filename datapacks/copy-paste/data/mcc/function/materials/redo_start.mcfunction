execute if score @s mcc_matphase matches 1.. run tellraw @s [{"text":"[Copy/Paste] 另一個材料交易仍在進行。","color":"red"}]
execute if score @s mcc_matphase matches 1.. run return fail
function mcc:materials/ensure_player
scoreboard players operation @s mcc_txslot = @s mcc_rhead
execute store result storage mcc:temp tx.id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp tx.slot int 1 run scoreboard players get @s mcc_txslot
function mcc:materials/load_redo_transaction with storage mcc:temp tx
function mcc:materials/reset_have_start
scoreboard players set @s mcc_matjob 1
scoreboard players set @s mcc_matphase 1
function mcc:materials/queue_boxes
tellraw @s [{"text":"[Copy/Paste] Redo：正在重新檢查施工材料…","color":"aqua"}]
execute if score @s mcc_matleft matches 0 run return run function mcc:materials/count_done
return 1
