function mcc:materials/ensure_player
execute store result storage mcc:temp pid int 1 run scoreboard players get @s mcc_id
function mcc:materials/bom_reset_do with storage mcc:temp
return 1
