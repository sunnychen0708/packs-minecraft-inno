# Load newest Undo metadata.
scoreboard players operation @s mcc_hslot = @s mcc_uhead
execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp slot int 1 run scoreboard players get @s mcc_hslot
function mcc:history/load_undo_meta with storage mcc:temp
execute unless score @s mcc_uguard matches 1 run tellraw @s [{"text":"[Copy/Paste] 這筆舊 Undo 沒有防複製安全快照；為安全起見已拒絕執行。","color":"red"}]
execute unless score @s mcc_uguard matches 1 run return fail

# Region dimensions.
scoreboard players operation @s mcc_fsx = @s mcc_ux2
scoreboard players operation @s mcc_fsx -= @s mcc_ux
scoreboard players add @s mcc_fsx 1
scoreboard players operation @s mcc_fsz = @s mcc_uz2
scoreboard players operation @s mcc_fsz -= @s mcc_uz
scoreboard players add @s mcc_fsz 1
scoreboard players operation @s mcc_sy = @s mcc_uy2
scoreboard players operation @s mcc_sy -= @s mcc_uy
scoreboard players add @s mcc_sy 1

# Candidate Redo ring slot; do not commit the pointer until Undo succeeds.
scoreboard players operation @s mcc_hnext = @s mcc_rhead
scoreboard players add @s mcc_hnext 1
execute if score @s mcc_hnext matches ..0 run scoreboard players set @s mcc_hnext 1
execute if score @s mcc_hnext matches 6.. run scoreboard players set @s mcc_hnext 1
scoreboard players operation @s mcc_hslot = @s mcc_hnext
function mcc:history/setup_redo_z
function mcc:redo/setup_buffer

# Save the current post-operation world into the candidate Redo history slot.
execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_ux
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_uy
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_uz
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_ux2
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_uy2
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_uz2
execute store result storage mcc:temp bx int 1 run scoreboard players get @s mcc_rbx
execute store result storage mcc:temp bx2 int 1 run scoreboard players get @s mcc_rbx2
execute store result storage mcc:temp by2 int 1 run scoreboard players get @s mcc_rby2
execute store result storage mcc:temp hz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp hz2 int 1 run scoreboard players get @s mcc_hz2
scoreboard players set @s mcc_ok 0
execute if score @s mcc_udim matches 1 run function mcc:history/backup_overworld with storage mcc:temp
execute if score @s mcc_udim matches 2 run function mcc:history/backup_nether with storage mcc:temp
execute if score @s mcc_udim matches 3 run function mcc:history/backup_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Undo 前建立 Redo 歷史失敗，沒有執行 Undo。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

function mcc:history/check_undo_material_guard
execute unless score @s mcc_ok matches 1 run return run function mcc:history/undo_guard_fail

scoreboard players operation @s mcc_rdim = @s mcc_udim
scoreboard players operation @s mcc_rx = @s mcc_ux
scoreboard players operation @s mcc_ry = @s mcc_uy
scoreboard players operation @s mcc_rz = @s mcc_uz
scoreboard players operation @s mcc_rx2 = @s mcc_ux2
scoreboard players operation @s mcc_ry2 = @s mcc_uy2
scoreboard players operation @s mcc_rz2 = @s mcc_uz2
scoreboard players set @s mcc_rsel 0
execute if score @s mcc_ucut matches 1 if score @s mcc_usel matches 1 run function mcc:history/copy_undo_selection_to_redo
execute unless score @s mcc_ucut matches 1 if score @s mcc_usel matches 1 run function mcc:redo/snapshot_selection
scoreboard players operation @s mcc_rmat = @s mcc_umat
scoreboard players set @s mcc_rguard 1
scoreboard players operation @s mcc_rcut = @s mcc_ucut

# A Redo of Cut must recreate the original Cut clipboard, not only clear the source.
# Archive that source from the immutable Undo history before restoring the world.
execute if score @s mcc_ucut matches 1 run function mcc:history/archive_cut_redo
execute if score @s mcc_ucut matches 1 unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_rguard 0

execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp slot int 1 run scoreboard players get @s mcc_hnext
function mcc:history/save_redo_meta with storage mcc:temp
execute if score @s mcc_umat matches 1 run function mcc:history/copy_undo_materials_to_redo

# Restore the newest Undo snapshot from its history slot.
scoreboard players operation @s mcc_hslot = @s mcc_uhead
function mcc:history/setup_undo_z
function mcc:undo/setup_buffer
execute store result storage mcc:temp bx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp bx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp by2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp hz int 1 run scoreboard players get @s mcc_hz
execute store result storage mcc:temp hz2 int 1 run scoreboard players get @s mcc_hz2
execute store result storage mcc:temp dstx int 1 run scoreboard players get @s mcc_ux
execute store result storage mcc:temp dsty int 1 run scoreboard players get @s mcc_uy
execute store result storage mcc:temp dstz int 1 run scoreboard players get @s mcc_uz
scoreboard players set @s mcc_ok 0
execute if score @s mcc_udim matches 1 run function mcc:history/restore_overworld with storage mcc:temp
execute if score @s mcc_udim matches 2 run function mcc:history/restore_nether with storage mcc:temp
execute if score @s mcc_udim matches 3 run function mcc:history/restore_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Undo 還原失敗；歷史資料仍保留。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail
execute if score @s mcc_usel matches 1 run function mcc:undo/restore_selection

# Snapshot the exact post-Undo world. Redo is exposed only if both this guard
# and (for Cut) the archived Cut clipboard succeeded.
scoreboard players operation @s mcc_hslot = @s mcc_hnext
execute if score @s mcc_rguard matches 1 run function mcc:history/archive_redo_guard
execute if score @s mcc_rguard matches 1 unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_rguard 0

execute if score @s mcc_umat matches 1 run function mcc:history/refund_undo_materials

# Undoing a Cut restores its source. Any still-live Cut clipboard must be consumed,
# otherwise source + clipboard can duplicate blocks or container contents.
execute if score @s mcc_ucut matches 1 if score @s mcc_cliptype matches 2 run scoreboard players set @s mcc_clip 0
execute if score @s mcc_ucut matches 1 if score @s mcc_cliptype matches 2 run scoreboard players set @s mcc_cliptype 0
execute if score @s mcc_ucut matches 1 run tellraw @s [{"text":"[Copy/Paste] Cut 已 Undo；對應的 Cut Clipboard 已作廢。","color":"gray"}]

# Pop Undo and commit Redo only when its safety guard exists.
scoreboard players remove @s mcc_ucnt 1
execute if score @s mcc_ucnt matches 0 run scoreboard players set @s mcc_uhead 0
execute if score @s mcc_ucnt matches 1.. run scoreboard players remove @s mcc_uhead 1
execute if score @s mcc_ucnt matches 1.. if score @s mcc_uhead matches ..0 run scoreboard players set @s mcc_uhead 5
execute if score @s mcc_rguard matches 1 run scoreboard players operation @s mcc_rhead = @s mcc_hnext
execute if score @s mcc_rguard matches 1 if score @s mcc_rcnt matches ..4 run scoreboard players add @s mcc_rcnt 1
execute unless score @s mcc_rguard matches 1 run scoreboard players set @s mcc_rhead 0
execute unless score @s mcc_rguard matches 1 run scoreboard players set @s mcc_rcnt 0
function mcc:history/sync_flags

execute unless score @s mcc_rguard matches 1 run tellraw @s [{"text":"[Copy/Paste] Undo 已完成，但 Redo 安全快照建立失敗，因此已清除 Redo 歷史。","color":"yellow"}]
tellraw @s [{"text":"[Copy/Paste] Undo 完成。Undo 剩餘 ","color":"green"},{"score":{"name":"@s","objective":"mcc_ucnt"},"color":"yellow"},{"text":"/5；Redo 可用 ","color":"green"},{"score":{"name":"@s","objective":"mcc_rcnt"},"color":"yellow"},{"text":"/5。","color":"green"}]
return 1
