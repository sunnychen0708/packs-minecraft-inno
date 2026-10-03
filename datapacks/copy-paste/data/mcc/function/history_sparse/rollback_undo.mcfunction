# Restore the post-edit A/B snapshots already captured in candidate Redo slot.
function mcc:history_sparse/dims_u_a
function mcc:undo/setup_buffer
scoreboard players operation @s mcc_hslot = @s mcc_hnext
function mcc:history/setup_redo_z
execute store result storage mcc:temp bx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp bx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp by2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp hz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp hz2 int 1 run scoreboard players get @s mcc_hz2
execute store result storage mcc:temp dstx int 1 run scoreboard players get @s mcc_ux
execute store result storage mcc:temp dsty int 1 run scoreboard players get @s mcc_uy
execute store result storage mcc:temp dstz int 1 run scoreboard players get @s mcc_uz
execute if score @s mcc_udim matches 1 run function mcc:history/restore_overworld with storage mcc:temp
execute if score @s mcc_udim matches 2 run function mcc:history/restore_nether with storage mcc:temp
execute if score @s mcc_udim matches 3 run function mcc:history/restore_end with storage mcc:temp

function mcc:history_sparse/dims_u_b
function mcc:undo/setup_buffer
scoreboard players operation @s mcc_hslot = @s mcc_hnext
function mcc:history_sparse/setup_redo_z_b
execute store result storage mcc:temp bx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp bx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp by2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp hz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp hz2 int 1 run scoreboard players get @s mcc_hz2
execute store result storage mcc:temp dstx int 1 run scoreboard players get @s mcc_u2x
execute store result storage mcc:temp dsty int 1 run scoreboard players get @s mcc_u2y
execute store result storage mcc:temp dstz int 1 run scoreboard players get @s mcc_u2z
execute if score @s mcc_udim matches 1 run function mcc:history/restore_overworld with storage mcc:temp
execute if score @s mcc_udim matches 2 run function mcc:history/restore_nether with storage mcc:temp
execute if score @s mcc_udim matches 3 run function mcc:history/restore_end with storage mcc:temp
return fail
