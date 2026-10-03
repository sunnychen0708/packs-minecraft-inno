# Re-load the Redo entry selected when the async material check started.
execute if score @s mcc_matjob matches 1 run scoreboard players operation @s mcc_hslot = @s mcc_txslot
execute unless score @s mcc_matjob matches 1 run scoreboard players operation @s mcc_hslot = @s mcc_rhead
execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp slot int 1 run scoreboard players get @s mcc_hslot
function mcc:history/load_redo_meta with storage mcc:temp
execute unless score @s mcc_rguard matches 1 run tellraw @s [{"text":"[Copy/Paste] 這筆舊 Redo 沒有防複製安全快照；為安全起見已拒絕執行。","color":"red"}]
execute unless score @s mcc_rguard matches 1 run return fail

# Region dimensions.
scoreboard players operation @s mcc_fsx = @s mcc_rx2
scoreboard players operation @s mcc_fsx -= @s mcc_rx
scoreboard players add @s mcc_fsx 1
scoreboard players operation @s mcc_fsz = @s mcc_rz2
scoreboard players operation @s mcc_fsz -= @s mcc_rz
scoreboard players add @s mcc_fsz 1
scoreboard players operation @s mcc_sy = @s mcc_ry2
scoreboard players operation @s mcc_sy -= @s mcc_ry
scoreboard players add @s mcc_sy 1

# Candidate Undo ring slot; do not commit the pointer until Redo succeeds.
scoreboard players operation @s mcc_hnext = @s mcc_uhead
scoreboard players add @s mcc_hnext 1
execute if score @s mcc_hnext matches ..0 run scoreboard players set @s mcc_hnext 1
execute if score @s mcc_hnext matches 6.. run scoreboard players set @s mcc_hnext 1
scoreboard players operation @s mcc_hslot = @s mcc_hnext
function mcc:history/setup_undo_z
function mcc:undo/setup_buffer

# Save the current post-Undo world into the candidate Undo history slot.
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
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Redo 前建立 Undo 歷史失敗，沒有執行 Redo。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

function mcc:history/check_redo_guard
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Undo 後的世界已被修改；為避免資源複製，未執行 Redo。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

scoreboard players operation @s mcc_udim = @s mcc_rdim
scoreboard players operation @s mcc_ux = @s mcc_rx
scoreboard players operation @s mcc_uy = @s mcc_ry
scoreboard players operation @s mcc_uz = @s mcc_rz
scoreboard players operation @s mcc_ux2 = @s mcc_rx2
scoreboard players operation @s mcc_uy2 = @s mcc_ry2
scoreboard players operation @s mcc_uz2 = @s mcc_rz2
scoreboard players set @s mcc_usparse 0
scoreboard players set @s mcc_usel 0
execute if score @s mcc_rsel matches 1 run function mcc:undo/snapshot_selection
scoreboard players operation @s mcc_histmat = @s mcc_rmat
scoreboard players set @s mcc_histguard 1
scoreboard players operation @s mcc_histcut = @s mcc_rcut
function mcc:history/copy_redo_snapshot_to_material_guard
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Redo 的防複製快照建立失敗；世界尚未修改。","color":"red"}]
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_histmat 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_histguard 0
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_histcut 0
execute unless score @s mcc_ok matches 1 run return fail
execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp slot int 1 run scoreboard players get @s mcc_hnext
function mcc:history/save_undo_meta with storage mcc:temp
scoreboard players set @s mcc_histmat 0
scoreboard players set @s mcc_histguard 0
scoreboard players set @s mcc_histcut 0

# Redoing a Cut must restore its movable clipboard as well as the post-Cut world.
# Prepare the hidden clipboard first; keep it disabled until the world restore succeeds.
execute if score @s mcc_rcut matches 1 run function mcc:history/prepare_cut_clipboard_from_redo
execute if score @s mcc_rcut matches 1 unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Cut Redo 的 Clipboard 還原失敗；世界尚未修改。","color":"red"}]
execute if score @s mcc_rcut matches 1 unless score @s mcc_ok matches 1 run return fail

# Restore the newest Redo snapshot from its history slot.
execute if score @s mcc_matjob matches 1 run scoreboard players operation @s mcc_hslot = @s mcc_txslot
execute unless score @s mcc_matjob matches 1 run scoreboard players operation @s mcc_hslot = @s mcc_rhead
function mcc:history/setup_redo_z
function mcc:redo/setup_buffer
execute store result storage mcc:temp bx int 1 run scoreboard players get @s mcc_rbx
execute store result storage mcc:temp bx2 int 1 run scoreboard players get @s mcc_rbx2
execute store result storage mcc:temp by2 int 1 run scoreboard players get @s mcc_rby2
execute store result storage mcc:temp hz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp hz2 int 1 run scoreboard players get @s mcc_hz2
execute store result storage mcc:temp dstx int 1 run scoreboard players get @s mcc_rx
execute store result storage mcc:temp dsty int 1 run scoreboard players get @s mcc_ry
execute store result storage mcc:temp dstz int 1 run scoreboard players get @s mcc_rz
scoreboard players set @s mcc_ok 0
execute if score @s mcc_rdim matches 1 run function mcc:history/restore_overworld with storage mcc:temp
execute if score @s mcc_rdim matches 2 run function mcc:history/restore_nether with storage mcc:temp
execute if score @s mcc_rdim matches 3 run function mcc:history/restore_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Redo 還原失敗；歷史資料仍保留。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail
execute if score @s mcc_rsel matches 1 run function mcc:redo/restore_selection
execute if score @s mcc_rcut matches 1 run scoreboard players set @s mcc_clip 1
execute if score @s mcc_rcut matches 1 run scoreboard players set @s mcc_cliptype 2
execute if score @s mcc_rcut matches 1 run tellraw @s [{"text":"[Copy/Paste] Cut Redo 完成；Cut Clipboard 已重新建立，可再次用 /trigger v 搬移。","color":"gray"}]

# Pop Redo and commit Undo.
scoreboard players remove @s mcc_rcnt 1
execute if score @s mcc_rcnt matches 0 run scoreboard players set @s mcc_rhead 0
execute if score @s mcc_rcnt matches 1.. run scoreboard players remove @s mcc_rhead 1
execute if score @s mcc_rcnt matches 1.. if score @s mcc_rhead matches ..0 run scoreboard players set @s mcc_rhead 5
scoreboard players operation @s mcc_uhead = @s mcc_hnext
execute if score @s mcc_ucnt matches ..4 run scoreboard players add @s mcc_ucnt 1
function mcc:history/sync_flags

tellraw @s [{"text":"[Copy/Paste] Redo 完成。Undo 可用 ","color":"green"},{"score":{"name":"@s","objective":"mcc_ucnt"},"color":"yellow"},{"text":"/5；Redo 剩餘 ","color":"green"},{"score":{"name":"@s","objective":"mcc_rcnt"},"color":"yellow"},{"text":"/5。","color":"green"}]
return 1
