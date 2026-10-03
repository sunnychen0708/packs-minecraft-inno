# Commit one logical edit whose affected world is two disjoint regions:
# A = mcc_u*, B = mcc_u2*. Pre-A lives in Work; pre-B lives in Undo temp.
scoreboard players set @s mcc_rcnt 0
scoreboard players set @s mcc_rhead 0
scoreboard players set @s mcc_redo 0

scoreboard players operation @s mcc_hslot = @s mcc_uhead
scoreboard players add @s mcc_hslot 1
execute if score @s mcc_hslot matches ..0 run scoreboard players set @s mcc_hslot 1
execute if score @s mcc_hslot matches 6.. run scoreboard players set @s mcc_hslot 1

# Archive pre-edit region A from the immutable Work snapshot.
function mcc:work/setup_buffer
execute store result storage mcc:temp sparsecp.sx int 1 run scoreboard players get @s mcc_wbx
execute store result storage mcc:temp sparsecp.sx2 int 1 run scoreboard players get @s mcc_wbx2
execute store result storage mcc:temp sparsecp.sy2 int 1 run scoreboard players get @s mcc_wby2
execute store result storage mcc:temp sparsecp.sz int 1 run scoreboard players get #workz mcc_id
execute store result storage mcc:temp sparsecp.sz2 int 1 run scoreboard players get @s mcc_wbz2
function mcc:history_sparse/dims_u_a
function mcc:undo/setup_buffer
function mcc:history/setup_undo_z
execute store result storage mcc:temp sparsecp.dx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp sparsecp.dx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp sparsecp.dz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp sparsecp.dz2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players set @s mcc_ok 0
function mcc:history/copy_hidden with storage mcc:temp sparsecp
execute unless score @s mcc_ok matches 1 run return fail

# Archive pre-edit region B from the Undo temp snapshot.
function mcc:history_sparse/dims_u_b
function mcc:undo/setup_buffer
execute store result storage mcc:temp sparsecp.sx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp sparsecp.sx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp sparsecp.sy2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp sparsecp.sz int 1 run scoreboard players get #ubz mcc_id
execute store result storage mcc:temp sparsecp.sz2 int 1 run scoreboard players get @s mcc_ubz2
function mcc:history_sparse/setup_undo_z_b
execute store result storage mcc:temp sparsecp.dx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp sparsecp.dx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp sparsecp.dz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp sparsecp.dz2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players set @s mcc_ok 0
function mcc:history/copy_hidden with storage mcc:temp sparsecp
execute unless score @s mcc_ok matches 1 run return fail

# Guard A: exact post-edit live world.
function mcc:history_sparse/dims_u_a
function mcc:undo/setup_buffer
function mcc:history/setup_material_z
execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_ux
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_uy
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_uz
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_ux2
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_uy2
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_uz2
execute store result storage mcc:temp bx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp bx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp by2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp hz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp hz2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players set @s mcc_ok 0
execute if score @s mcc_udim matches 1 run function mcc:history/backup_overworld with storage mcc:temp
execute if score @s mcc_udim matches 2 run function mcc:history/backup_nether with storage mcc:temp
execute if score @s mcc_udim matches 3 run function mcc:history/backup_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run return fail

# Guard B.
function mcc:history_sparse/dims_u_b
function mcc:undo/setup_buffer
function mcc:history_sparse/setup_guard_z_b
execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_u2x
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_u2y
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_u2z
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_u2x2
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_u2y2
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_u2z2
execute store result storage mcc:temp bx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp bx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp by2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp hz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp hz2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players set @s mcc_ok 0
execute if score @s mcc_udim matches 1 run function mcc:history/backup_overworld with storage mcc:temp
execute if score @s mcc_udim matches 2 run function mcc:history/backup_nether with storage mcc:temp
execute if score @s mcc_udim matches 3 run function mcc:history/backup_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run return fail

scoreboard players set @s mcc_usparse 1
scoreboard players set @s mcc_histguard 1
scoreboard players set @s mcc_histcut 0
scoreboard players set @s mcc_histmat 0
execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp slot int 1 run scoreboard players get @s mcc_hslot
function mcc:history/save_undo_meta with storage mcc:temp
scoreboard players operation @s mcc_uhead = @s mcc_hslot
execute if score @s mcc_ucnt matches ..4 run scoreboard players add @s mcc_ucnt 1
scoreboard players set @s mcc_histguard 0
scoreboard players set @s mcc_histcut 0
scoreboard players set @s mcc_histmat 0
scoreboard players set @s mcc_undo 1
return 1
