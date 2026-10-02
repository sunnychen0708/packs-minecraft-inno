function mcc:materials/capture_here
execute store result storage mcc:temp box.pid int 1 run scoreboard players get @s mcc_id
function mcc:materials/register_do with storage mcc:temp box
return 1
