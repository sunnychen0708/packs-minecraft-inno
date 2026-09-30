execute unless score @s mcc_redo matches 1 run tellraw @s [{"text":"[Copy/Paste] 沒有可 Redo 的狀態。","color":"red"}]
execute unless score @s mcc_redo matches 1 run return fail

# Save the current (post-Undo) world back into Undo so Z/Y style toggling is reversible.
scoreboard players operation @s mcc_fsx = @s mcc_rx2
scoreboard players operation @s mcc_fsx -= @s mcc_rx
scoreboard players add @s mcc_fsx 1
scoreboard players operation @s mcc_fsz = @s mcc_rz2
scoreboard players operation @s mcc_fsz -= @s mcc_rz
scoreboard players add @s mcc_fsz 1
scoreboard players operation @s mcc_sy = @s mcc_ry2
scoreboard players operation @s mcc_sy -= @s mcc_ry
scoreboard players add @s mcc_sy 1
function mcc:undo/setup_buffer

execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_rx
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_ry
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_rz
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_rx2
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_ry2
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_rz2
execute store result storage mcc:temp ubx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp ubx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp uby2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp ubz2 int 1 run scoreboard players get @s mcc_ubz2
scoreboard players set @s mcc_ok 0
execute if score @s mcc_rdim matches 1 run function mcc:undo/backup_from_overworld with storage mcc:temp
execute if score @s mcc_rdim matches 2 run function mcc:undo/backup_from_nether with storage mcc:temp
execute if score @s mcc_rdim matches 3 run function mcc:undo/backup_from_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Redo 前重建 Undo 快照失敗，沒有執行 Redo。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

scoreboard players operation @s mcc_udim = @s mcc_rdim
scoreboard players operation @s mcc_ux = @s mcc_rx
scoreboard players operation @s mcc_uy = @s mcc_ry
scoreboard players operation @s mcc_uz = @s mcc_rz
scoreboard players operation @s mcc_ux2 = @s mcc_rx2
scoreboard players operation @s mcc_uy2 = @s mcc_ry2
scoreboard players operation @s mcc_uz2 = @s mcc_rz2
scoreboard players set @s mcc_usel 0
execute if score @s mcc_rsel matches 1 run function mcc:undo/snapshot_selection

# Restore Redo world.
function mcc:redo/setup_buffer
execute store result storage mcc:temp rbx int 1 run scoreboard players get @s mcc_rbx
execute store result storage mcc:temp rbx2 int 1 run scoreboard players get @s mcc_rbx2
execute store result storage mcc:temp rby2 int 1 run scoreboard players get @s mcc_rby2
execute store result storage mcc:temp rbz2 int 1 run scoreboard players get @s mcc_rbz2
execute store result storage mcc:temp dstx int 1 run scoreboard players get @s mcc_rx
execute store result storage mcc:temp dsty int 1 run scoreboard players get @s mcc_ry
execute store result storage mcc:temp dstz int 1 run scoreboard players get @s mcc_rz
scoreboard players set @s mcc_ok 0
execute if score @s mcc_rdim matches 1 run function mcc:redo/restore_overworld with storage mcc:temp
execute if score @s mcc_rdim matches 2 run function mcc:redo/restore_nether with storage mcc:temp
execute if score @s mcc_rdim matches 3 run function mcc:redo/restore_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Redo 還原失敗。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail
execute if score @s mcc_rsel matches 1 run function mcc:redo/restore_selection
scoreboard players set @s mcc_redo 0
scoreboard players set @s mcc_undo 1
tellraw @s [{"text":"[Copy/Paste] Redo 完成。可再次 /trigger undo。","color":"green"}]
return 1
