execute store result storage mcc:temp tx.id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp tx.src int 1 run scoreboard players get @s mcc_uhead
execute store result storage mcc:temp tx.dst int 1 run scoreboard players get @s mcc_hnext
function mcc:history/copy_undo_materials_to_redo_do with storage mcc:temp tx
return 1
