execute store result storage mcc:temp cmp.cx int 1 run scoreboard players get @s mcc_rbx
execute store result storage mcc:temp cmp.cx2 int 1 run scoreboard players get @s mcc_rbx2
execute store result storage mcc:temp cmp.cy2 int 1 run scoreboard players get @s mcc_rby2
execute store result storage mcc:temp cmp.cz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp cmp.cz2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players operation @s mcc_hslot = @s mcc_uhead
function mcc:history/setup_material_z
function mcc:undo/setup_buffer
execute store result storage mcc:temp cmp.ex int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp cmp.ex2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp cmp.ey2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp cmp.ez int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp cmp.ez2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players set @s mcc_ok 0
function mcc:history/compare_hidden with storage mcc:temp cmp
return 1
