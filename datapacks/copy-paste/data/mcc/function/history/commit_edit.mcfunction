scoreboard players set @s mcc_usparse 0
# A successful new world edit invalidates the Redo chain.
scoreboard players set @s mcc_rcnt 0
scoreboard players set @s mcc_rhead 0
scoreboard players set @s mcc_redo 0

# Recompute the Undo snapshot dimensions from its world bounds.
scoreboard players operation @s mcc_fsx = @s mcc_ux2
scoreboard players operation @s mcc_fsx -= @s mcc_ux
scoreboard players add @s mcc_fsx 1
scoreboard players operation @s mcc_fsz = @s mcc_uz2
scoreboard players operation @s mcc_fsz -= @s mcc_uz
scoreboard players add @s mcc_fsz 1
scoreboard players operation @s mcc_sy = @s mcc_uy2
scoreboard players operation @s mcc_sy -= @s mcc_uy
scoreboard players add @s mcc_sy 1

# Ring-buffer slot after the current newest Undo.
scoreboard players operation @s mcc_hslot = @s mcc_uhead
scoreboard players add @s mcc_hslot 1
execute if score @s mcc_hslot matches ..0 run scoreboard players set @s mcc_hslot 1
execute if score @s mcc_hslot matches 6.. run scoreboard players set @s mcc_hslot 1
function mcc:history/setup_undo_z

execute store result storage mcc:temp ubx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp ubx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp uby2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp ubz2 int 1 run scoreboard players get @s mcc_ubz2
execute store result storage mcc:temp hz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp hz2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players set @s mcc_ok 0
function mcc:history/archive_undo with storage mcc:temp
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_ucnt 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_uhead 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_undo 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_histmat 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_histguard 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_histcut 0
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Undo 歷史寫入失敗；為避免資源複製，本次操作不提供 Undo。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

scoreboard players operation @s mcc_uhead = @s mcc_hslot
execute if score @s mcc_ucnt matches ..4 run scoreboard players add @s mcc_ucnt 1

# Every world-edit history entry stores the exact expected post-edit world.
# Undo is allowed only while the live world still matches this guard snapshot.
scoreboard players set @s mcc_histguard 0
scoreboard players operation @s mcc_hslot = @s mcc_uhead
function mcc:history/archive_material_guard
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_ucnt 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_uhead 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_undo 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_histmat 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_histcut 0
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Undo 防複製快照建立失敗；為安全起見已清除目前 Undo 歷史。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail
scoreboard players set @s mcc_histguard 1

execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp slot int 1 run scoreboard players get @s mcc_uhead
function mcc:history/save_undo_meta with storage mcc:temp
scoreboard players set @s mcc_histmat 0
scoreboard players set @s mcc_histguard 0
scoreboard players set @s mcc_histcut 0
scoreboard players set @s mcc_undo 1
return 1
