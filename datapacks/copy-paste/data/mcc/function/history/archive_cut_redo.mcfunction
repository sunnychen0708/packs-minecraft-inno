# Preserve the original pre-Cut source from the Undo history slot in a
# dedicated candidate Redo clipboard lane. This survives intervening Copy use.
scoreboard players operation @s mcc_hslot = @s mcc_uhead
function mcc:history/setup_undo_z
function mcc:undo/setup_buffer
execute store result storage mcc:temp cutcp.sx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp cutcp.sx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp cutcp.sy2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp cutcp.sz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp cutcp.sz2 int 1 run scoreboard players get @s mcc_hz2

scoreboard players operation @s mcc_hslot = @s mcc_hnext
function mcc:history/setup_cutredo_z
function mcc:undo/setup_buffer
execute store result storage mcc:temp cutcp.dx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp cutcp.dz int 1 run scoreboard players get @s mcc_hz

scoreboard players set @s mcc_ok 0
function mcc:history/copy_hidden with storage mcc:temp cutcp
return 1
