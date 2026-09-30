execute if score @s mcc_bpscan matches 1 run function mcc:blueprint/cancel_scan
execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
function mcc:blueprint/kill_owner with storage mcc:temp
scoreboard players set @s mcc_bpscan 0
return 1
