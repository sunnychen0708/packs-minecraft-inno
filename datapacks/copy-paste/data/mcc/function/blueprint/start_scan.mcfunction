execute store result storage mcc:temp x1 int 1 run scoreboard players get @s mcc_bpsx0
execute store result storage mcc:temp z1 int 1 run scoreboard players get @s mcc_bpsz0
execute store result storage mcc:temp x2 int 1 run scoreboard players get @s mcc_bpsx2
execute store result storage mcc:temp z2 int 1 run scoreboard players get @s mcc_bpsz2
function mcc:blueprint/forceload_add with storage mcc:temp
return run function mcc:blueprint/start_scan_loaded
