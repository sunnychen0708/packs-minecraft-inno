# Rebuild a Cut clipboard from the dedicated Redo archive before mutating the
# real world. Leave mcc_clip disabled until Redo itself succeeds.
execute unless score @s mcc_rsel matches 1 run scoreboard players set @s mcc_ok 0
execute unless score @s mcc_rsel matches 1 run return fail

execute if score @s mcc_matjob matches 1 run scoreboard players operation @s mcc_hslot = @s mcc_txslot
execute unless score @s mcc_matjob matches 1 run scoreboard players operation @s mcc_hslot = @s mcc_rhead
function mcc:history/setup_cutredo_z
function mcc:undo/setup_buffer
execute store result storage mcc:temp cutcp.sx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp cutcp.sx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp cutcp.sy2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp cutcp.sz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp cutcp.sz2 int 1 run scoreboard players get @s mcc_hz2

scoreboard players operation @s mcc_cbx = @s mcc_id
scoreboard players operation @s mcc_cbx *= #slot mcc_id
scoreboard players operation @s mcc_cbx += #base mcc_id
scoreboard players operation @s mcc_cbx2 = @s mcc_cbx
scoreboard players operation @s mcc_cbx2 += @s mcc_fsx
scoreboard players remove @s mcc_cbx2 1
scoreboard players operation @s mcc_cby2 = @s mcc_sy
scoreboard players remove @s mcc_cby2 1
scoreboard players operation @s mcc_cbz2 = #cbz mcc_id
scoreboard players operation @s mcc_cbz2 += @s mcc_fsz
scoreboard players remove @s mcc_cbz2 1
execute store result storage mcc:temp cutcp.dx int 1 run scoreboard players get @s mcc_cbx
execute store result storage mcc:temp cutcp.dx2 int 1 run scoreboard players get @s mcc_cbx2
execute store result storage mcc:temp cutcp.dz int 1 run scoreboard players get #cbz mcc_id
execute store result storage mcc:temp cutcp.dz2 int 1 run scoreboard players get @s mcc_cbz2

scoreboard players set @s mcc_clip 0
scoreboard players set @s mcc_cliptype 0
scoreboard players set @s mcc_ok 0
function mcc:history/copy_hidden with storage mcc:temp cutcp
execute unless score @s mcc_ok matches 1 run return fail

scoreboard players operation @s mcc_sx = @s mcc_fsx
scoreboard players operation @s mcc_sz = @s mcc_fsz
# mcc_sy is already the Redo region height.

scoreboard players operation @s mcc_offx = @s mcc_rp1x
scoreboard players operation @s mcc_offy = @s mcc_rp1y
scoreboard players operation @s mcc_offz = @s mcc_rp1z
execute if score @s mcc_rhasa matches 1 run scoreboard players operation @s mcc_offx = @s mcc_ranx
execute if score @s mcc_rhasa matches 1 run scoreboard players operation @s mcc_offy = @s mcc_rany
execute if score @s mcc_rhasa matches 1 run scoreboard players operation @s mcc_offz = @s mcc_ranz
scoreboard players operation @s mcc_offx -= @s mcc_rx
scoreboard players operation @s mcc_offy -= @s mcc_ry
scoreboard players operation @s mcc_offz -= @s mcc_rz
scoreboard players set @s mcc_rot 0
scoreboard players set @s mcc_mir 0
scoreboard players operation @s mcc_canchor = @s mcc_rhasa
function mcc:state/bp_offset_init
return 1
