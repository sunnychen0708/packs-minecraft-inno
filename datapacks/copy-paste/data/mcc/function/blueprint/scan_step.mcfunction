execute store result storage mcc:temp sx int 1 run scoreboard players get @s mcc_bpsx
execute store result storage mcc:temp sy int 1 run scoreboard players get @s mcc_bpsy
execute store result storage mcc:temp sz int 1 run scoreboard players get @s mcc_bpsz
execute store result storage mcc:temp tx int 1 run scoreboard players get @s mcc_bptx
execute store result storage mcc:temp ty int 1 run scoreboard players get @s mcc_bpty
execute store result storage mcc:temp tz int 1 run scoreboard players get @s mcc_bptz
execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
function mcc:blueprint/scan_one with storage mcc:temp

scoreboard players add @s mcc_bpsx 1
scoreboard players add @s mcc_bptx 1
execute if score @s mcc_bpsx > @s mcc_bpsx2 run function mcc:blueprint/wrap_x
return 1
