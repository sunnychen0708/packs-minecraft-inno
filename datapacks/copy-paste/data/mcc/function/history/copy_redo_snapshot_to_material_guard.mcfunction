scoreboard players operation @s mcc_hslot = @s mcc_txslot
function mcc:history/setup_redo_z
function mcc:redo/setup_buffer
execute store result storage mcc:temp cp.sx int 1 run scoreboard players get @s mcc_rbx
execute store result storage mcc:temp cp.sx2 int 1 run scoreboard players get @s mcc_rbx2
execute store result storage mcc:temp cp.sy2 int 1 run scoreboard players get @s mcc_rby2
execute store result storage mcc:temp cp.sz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp cp.sz2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players operation @s mcc_hslot = @s mcc_hnext
function mcc:history/setup_material_z
function mcc:undo/setup_buffer
execute store result storage mcc:temp cp.dx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp cp.dx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp cp.dz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp cp.dz2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players set @s mcc_ok 0
function mcc:history/copy_hidden with storage mcc:temp cp
return 1
