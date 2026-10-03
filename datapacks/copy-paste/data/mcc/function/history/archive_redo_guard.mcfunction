# Archive the exact post-Undo world for the candidate Redo slot.
# mcc_hslot = candidate Redo slot; mcc_r* = world region after Undo.
function mcc:history/setup_redo_guard_z
function mcc:undo/setup_buffer
execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_rx
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_ry
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_rz
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_rx2
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_ry2
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_rz2
execute store result storage mcc:temp bx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp bx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp by2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp hz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp hz2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players set @s mcc_ok 0
execute if score @s mcc_rdim matches 1 run function mcc:history/backup_overworld with storage mcc:temp
execute if score @s mcc_rdim matches 2 run function mcc:history/backup_nether with storage mcc:temp
execute if score @s mcc_rdim matches 3 run function mcc:history/backup_end with storage mcc:temp
return 1
