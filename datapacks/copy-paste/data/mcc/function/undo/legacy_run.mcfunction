execute unless score @s mcc_undo matches 1 run tellraw @s [{"text":"[Copy/Paste] 沒有可 Undo 的上一次世界修改。","color":"red"}]
execute unless score @s mcc_undo matches 1 run return fail

# Save the current (post-operation) world into the per-player Redo buffer.
scoreboard players operation @s mcc_fsx = @s mcc_ux2
scoreboard players operation @s mcc_fsx -= @s mcc_ux
scoreboard players add @s mcc_fsx 1
scoreboard players operation @s mcc_fsz = @s mcc_uz2
scoreboard players operation @s mcc_fsz -= @s mcc_uz
scoreboard players add @s mcc_fsz 1
scoreboard players operation @s mcc_sy = @s mcc_uy2
scoreboard players operation @s mcc_sy -= @s mcc_uy
scoreboard players add @s mcc_sy 1
function mcc:redo/setup_buffer

execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_ux
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_uy
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_uz
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_ux2
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_uy2
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_uz2
execute store result storage mcc:temp rbx int 1 run scoreboard players get @s mcc_rbx
execute store result storage mcc:temp rbx2 int 1 run scoreboard players get @s mcc_rbx2
execute store result storage mcc:temp rby2 int 1 run scoreboard players get @s mcc_rby2
execute store result storage mcc:temp rbz2 int 1 run scoreboard players get @s mcc_rbz2
scoreboard players set @s mcc_ok 0
execute if score @s mcc_udim matches 1 run function mcc:redo/backup_from_overworld with storage mcc:temp
execute if score @s mcc_udim matches 2 run function mcc:redo/backup_from_nether with storage mcc:temp
execute if score @s mcc_udim matches 3 run function mcc:redo/backup_from_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Undo 前建立 Redo 快照失敗，沒有執行 Undo。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

scoreboard players operation @s mcc_rdim = @s mcc_udim
scoreboard players operation @s mcc_rx = @s mcc_ux
scoreboard players operation @s mcc_ry = @s mcc_uy
scoreboard players operation @s mcc_rz = @s mcc_uz
scoreboard players operation @s mcc_rx2 = @s mcc_ux2
scoreboard players operation @s mcc_ry2 = @s mcc_uy2
scoreboard players operation @s mcc_rz2 = @s mcc_uz2
scoreboard players set @s mcc_rsel 0
execute if score @s mcc_usel matches 1 run function mcc:redo/snapshot_selection

# Restore the pre-operation world from Undo.
function mcc:undo/setup_buffer
execute store result storage mcc:temp ubx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp ubx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp uby2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp ubz2 int 1 run scoreboard players get @s mcc_ubz2
execute store result storage mcc:temp dstx int 1 run scoreboard players get @s mcc_ux
execute store result storage mcc:temp dsty int 1 run scoreboard players get @s mcc_uy
execute store result storage mcc:temp dstz int 1 run scoreboard players get @s mcc_uz
scoreboard players set @s mcc_ok 0
execute if score @s mcc_udim matches 1 run function mcc:undo/restore_overworld with storage mcc:temp
execute if score @s mcc_udim matches 2 run function mcc:undo/restore_nether with storage mcc:temp
execute if score @s mcc_udim matches 3 run function mcc:undo/restore_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Undo 還原失敗；原 Undo 資料仍保留。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail
execute if score @s mcc_usel matches 1 run function mcc:undo/restore_selection
scoreboard players set @s mcc_undo 0
scoreboard players set @s mcc_redo 1
tellraw @s [{"text":"[Copy/Paste] Undo 完成。可用 /trigger redo 回到 Undo 前。","color":"green"}]
return 1
