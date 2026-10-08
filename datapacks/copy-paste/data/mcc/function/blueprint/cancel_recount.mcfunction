# Stop a pending overlap recount and release the forceload recount_start added.
# Callers must run this before the Blueprint buffer bounds (mcc_bpsx0..mcc_bpsz2) change.
execute store result storage mcc:temp x1 int 1 run scoreboard players get @s mcc_bpsx0
execute store result storage mcc:temp z1 int 1 run scoreboard players get @s mcc_bpsz0
execute store result storage mcc:temp x2 int 1 run scoreboard players get @s mcc_bpsx2
execute store result storage mcc:temp z2 int 1 run scoreboard players get @s mcc_bpsz2
function mcc:blueprint/forceload_remove with storage mcc:temp
scoreboard players set @s mcc_bpover_scan 0
return 1
