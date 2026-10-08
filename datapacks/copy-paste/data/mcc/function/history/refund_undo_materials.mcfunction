data modify storage mcc:temp tx set value {}
execute store result storage mcc:temp tx.id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp tx.slot int 1 run scoreboard players get @s mcc_uhead
function mcc:history/refund_undo_materials_init with storage mcc:temp tx
return 1
