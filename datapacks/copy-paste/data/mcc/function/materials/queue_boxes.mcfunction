execute store result storage mcc:temp pid int 1 run scoreboard players get @s mcc_id
scoreboard players set @s mcc_matleft 0
function mcc:materials/queue_boxes_do with storage mcc:temp
return 1
