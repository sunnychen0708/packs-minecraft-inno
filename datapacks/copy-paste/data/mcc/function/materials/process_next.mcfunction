execute store result storage mcc:temp pid int 1 run scoreboard players get @s mcc_id
function mcc:materials/process_next_do with storage mcc:temp
scoreboard players remove @s mcc_matleft 1
return 1
