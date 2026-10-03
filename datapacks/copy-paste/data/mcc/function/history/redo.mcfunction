# Load newest Redo metadata.
scoreboard players operation @s mcc_hslot = @s mcc_rhead
execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp slot int 1 run scoreboard players get @s mcc_hslot
function mcc:history/load_redo_meta with storage mcc:temp
execute if score @s mcc_rsparse matches 1 run return run function mcc:history_sparse/redo_loaded

execute if score @s mcc_rmat matches 1 if score @s mcc_bpactive matches 1 run tellraw @s [{"text":"[Copy/Paste] 材料型 Redo 前請先清除或完成目前的 Blueprint，避免覆蓋它的材料表。","color":"red"}]
execute if score @s mcc_rmat matches 1 if score @s mcc_bpactive matches 1 run return fail
execute if score @s mcc_rmat matches 1 run return run function mcc:materials/redo_start
return run function mcc:history/redo_apply
