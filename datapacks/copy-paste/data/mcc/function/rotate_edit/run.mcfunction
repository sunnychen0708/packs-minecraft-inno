execute store success score @s mcc_tmp run function mcc:selection/prepare
execute unless score @s mcc_tmp matches 1 run return fail
execute unless score @s mcc_selx matches 1..48 run tellraw @s [{"text":"[Copy/Paste] 原地 Rotate 時 X 長度必須 ≤ 48。","color":"red"}]
execute unless score @s mcc_selx matches 1..48 run return fail
execute unless score @s mcc_sely matches 1..48 run tellraw @s [{"text":"[Copy/Paste] 原地 Rotate 時 Y 長度必須 ≤ 48。","color":"red"}]
execute unless score @s mcc_sely matches 1..48 run return fail
execute unless score @s mcc_selz matches 1..48 run tellraw @s [{"text":"[Copy/Paste] 原地 Rotate 時 Z 長度必須 ≤ 48。","color":"red"}]
execute unless score @s mcc_selz matches 1..48 run return fail

execute store success score @s mcc_tmp run function mcc:work/snapshot_selection
execute unless score @s mcc_tmp matches 1 run tellraw @s [{"text":"[Copy/Paste] Rotate 暫存快照失敗，沒有修改世界。","color":"red"}]
execute unless score @s mcc_tmp matches 1 run return fail

scoreboard players operation @s mcc_sx = @s mcc_selx
scoreboard players operation @s mcc_sy = @s mcc_sely
scoreboard players operation @s mcc_sz = @s mcc_selz
scoreboard players operation @s mcc_offx = @s mcc_soffx
scoreboard players operation @s mcc_offy = @s mcc_soffy
scoreboard players operation @s mcc_offz = @s mcc_soffz
scoreboard players operation @s mcc_dstx = @s mcc_p1x
scoreboard players operation @s mcc_dsty = @s mcc_p1y
scoreboard players operation @s mcc_dstz = @s mcc_p1z
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_dstx = @s mcc_anx
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_dsty = @s mcc_any
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_dstz = @s mcc_anz

execute if score @s mcc_erot matches 1 if score @s mcc_emir matches 0 run function mcc:paste/prepare_r1_m0
execute if score @s mcc_erot matches 2 if score @s mcc_emir matches 0 run function mcc:paste/prepare_r2_m0
execute if score @s mcc_erot matches 3 if score @s mcc_emir matches 0 run function mcc:paste/prepare_r3_m0
execute if score @s mcc_erot matches 0 if score @s mcc_emir matches 1 run function mcc:paste/prepare_r0_m1
execute if score @s mcc_erot matches 0 if score @s mcc_emir matches 2 run function mcc:paste/prepare_r0_m2

scoreboard players operation @s mcc_dsty2 = @s mcc_psty
scoreboard players operation @s mcc_dsty2 += @s mcc_sy
scoreboard players remove @s mcc_dsty2 1

# Transform the Work snapshot in hidden space before touching the real world.
# The hidden target is cleared first so occupied real targets cannot suppress source blocks.
execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp wbx int 1 run scoreboard players get @s mcc_wbx
execute store result storage mcc:temp wbx2 int 1 run scoreboard players get @s mcc_wbx2
execute store result storage mcc:temp sx int 1 run scoreboard players get @s mcc_selx
execute store result storage mcc:temp sy int 1 run scoreboard players get @s mcc_sely
execute store result storage mcc:temp sz int 1 run scoreboard players get @s mcc_selz
execute store result storage mcc:temp wbz2 int 1 run scoreboard players get @s mcc_wbz2
function mcc:work/save_template with storage mcc:temp

execute store result storage mcc:temp old_wbx2 int 1 run scoreboard players get @s mcc_wbx2
execute store result storage mcc:temp old_wbz2 int 1 run scoreboard players get @s mcc_wbz2
execute store result storage mcc:temp wby2 int 1 run scoreboard players get @s mcc_wby2

# Translate the real placement origin so the transformed bounds start at the Work lane.
scoreboard players operation @s mcc_tmp = @s mcc_wbx
scoreboard players operation @s mcc_tmp -= @s mcc_bminx
scoreboard players operation @s mcc_tmp += @s mcc_pstx
execute store result storage mcc:temp spx int 1 run scoreboard players get @s mcc_tmp
scoreboard players operation @s mcc_tmp = #workz mcc_id
scoreboard players operation @s mcc_tmp -= @s mcc_bminz
scoreboard players operation @s mcc_tmp += @s mcc_pstz
execute store result storage mcc:temp spz int 1 run scoreboard players get @s mcc_tmp

scoreboard players operation @s mcc_wbx2 = @s mcc_bmaxx
scoreboard players operation @s mcc_wbx2 -= @s mcc_bminx
scoreboard players operation @s mcc_wbx2 += @s mcc_wbx
scoreboard players operation @s mcc_wbz2 = @s mcc_bmaxz
scoreboard players operation @s mcc_wbz2 -= @s mcc_bminz
scoreboard players operation @s mcc_wbz2 += #workz mcc_id
execute store result storage mcc:temp stage_wbx2 int 1 run scoreboard players get @s mcc_wbx2
execute store result storage mcc:temp stage_wbz2 int 1 run scoreboard players get @s mcc_wbz2

scoreboard players set @s mcc_ok 0
function mcc:rotate_edit/stage_work with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Rotate/Flip 轉換暫存失敗，沒有修改世界。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

# Union of source and rotated destination for one-step Undo/Redo.
scoreboard players operation @s mcc_uminx = @s mcc_minx
scoreboard players operation @s mcc_uminx < @s mcc_bminx
scoreboard players operation @s mcc_uminy = @s mcc_miny
scoreboard players operation @s mcc_uminy < @s mcc_psty
scoreboard players operation @s mcc_uminz = @s mcc_minz
scoreboard players operation @s mcc_uminz < @s mcc_bminz
scoreboard players operation @s mcc_umaxx = @s mcc_maxx
scoreboard players operation @s mcc_umaxx > @s mcc_bmaxx
scoreboard players operation @s mcc_umaxy = @s mcc_maxy
scoreboard players operation @s mcc_umaxy > @s mcc_dsty2
scoreboard players operation @s mcc_umaxz = @s mcc_maxz
scoreboard players operation @s mcc_umaxz > @s mcc_bmaxz
scoreboard players operation @s mcc_usx = @s mcc_umaxx
scoreboard players operation @s mcc_usx -= @s mcc_uminx
scoreboard players add @s mcc_usx 1
scoreboard players operation @s mcc_usy = @s mcc_umaxy
scoreboard players operation @s mcc_usy -= @s mcc_uminy
scoreboard players add @s mcc_usy 1
scoreboard players operation @s mcc_usz = @s mcc_umaxz
scoreboard players operation @s mcc_usz -= @s mcc_uminz
scoreboard players add @s mcc_usz 1
execute unless score @s mcc_usx matches 1..256 run tellraw @s [{"text":"[Copy/Paste] Rotate Undo 範圍 X 超過 256 格，已取消。","color":"red"}]
execute unless score @s mcc_usx matches 1..256 run return fail
execute unless score @s mcc_usy matches 1..256 run tellraw @s [{"text":"[Copy/Paste] Rotate Undo 範圍 Y 超過 256 格，已取消。","color":"red"}]
execute unless score @s mcc_usy matches 1..256 run return fail
execute unless score @s mcc_usz matches 1..256 run tellraw @s [{"text":"[Copy/Paste] Rotate Undo 範圍 Z 超過 256 格，已取消。","color":"red"}]
execute unless score @s mcc_usz matches 1..256 run return fail
scoreboard players operation @s mcc_uvol = @s mcc_usx
scoreboard players operation @s mcc_uvol *= @s mcc_usy
scoreboard players operation @s mcc_uvol *= @s mcc_usz
execute store result score @s mcc_lim run gamerule minecraft:max_block_modifications
execute if score @s mcc_uvol > @s mcc_lim run tellraw @s [{"text":"[Copy/Paste] Rotate Undo 範圍超過 minecraft:max_block_modifications，已取消。","color":"red"}]
execute if score @s mcc_uvol > @s mcc_lim run return fail

function mcc:move/setup_undo_buffer
execute store result storage mcc:temp x1 int 1 run scoreboard players get @s mcc_uminx
execute store result storage mcc:temp z1 int 1 run scoreboard players get @s mcc_uminz
execute store result storage mcc:temp x2 int 1 run scoreboard players get @s mcc_umaxx
execute store result storage mcc:temp z2 int 1 run scoreboard players get @s mcc_umaxz
execute if score @s mcc_p1d matches 1 run function mcc:move/forceload_add_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:move/forceload_add_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:move/forceload_add_end with storage mcc:temp

execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_uminx
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_uminy
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_uminz
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_umaxx
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_umaxy
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_umaxz
execute store result storage mcc:temp ubx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp ubx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp uby2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp ubz2 int 1 run scoreboard players get @s mcc_ubz2
scoreboard players set @s mcc_ok 0
execute if score @s mcc_p1d matches 1 run function mcc:undo/backup_from_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:undo/backup_from_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:undo/backup_from_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run return run function mcc:rotate_edit/fail_backup
scoreboard players operation @s mcc_udim = @s mcc_p1d
scoreboard players operation @s mcc_ux = @s mcc_uminx
scoreboard players operation @s mcc_uy = @s mcc_uminy
scoreboard players operation @s mcc_uz = @s mcc_uminz
scoreboard players operation @s mcc_ux2 = @s mcc_umaxx
scoreboard players operation @s mcc_uy2 = @s mcc_umaxy
scoreboard players operation @s mcc_uz2 = @s mcc_umaxz
scoreboard players set @s mcc_usel 0
scoreboard players set @s mcc_undo 1

execute store result storage mcc:temp minx int 1 run scoreboard players get @s mcc_minx
execute store result storage mcc:temp miny int 1 run scoreboard players get @s mcc_miny
execute store result storage mcc:temp minz int 1 run scoreboard players get @s mcc_minz
execute store result storage mcc:temp maxx int 1 run scoreboard players get @s mcc_maxx
execute store result storage mcc:temp maxy int 1 run scoreboard players get @s mcc_maxy
execute store result storage mcc:temp maxz int 1 run scoreboard players get @s mcc_maxz
scoreboard players set @s mcc_ok 0
execute if score @s mcc_p1d matches 1 run function mcc:cut/clear_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:cut/clear_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:cut/clear_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run return run function mcc:rotate_edit/fail_clear

# Clone the transformed Work snapshot into the real destination.
# replace force makes selected source blocks win over occupied target blocks.
execute store result storage mcc:temp wbx int 1 run scoreboard players get @s mcc_wbx
execute store result storage mcc:temp wbx2 int 1 run scoreboard players get @s mcc_wbx2
execute store result storage mcc:temp wby2 int 1 run scoreboard players get @s mcc_wby2
execute store result storage mcc:temp wbz2 int 1 run scoreboard players get @s mcc_wbz2
execute store result storage mcc:temp dstx int 1 run scoreboard players get @s mcc_bminx
execute store result storage mcc:temp dsty int 1 run scoreboard players get @s mcc_psty
execute store result storage mcc:temp dstz int 1 run scoreboard players get @s mcc_bminz
scoreboard players set @s mcc_ok 0
execute if score @s mcc_p1d matches 1 run function mcc:work/to_overworld_replace with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:work/to_nether_replace with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:work/to_end_replace with storage mcc:temp
execute unless score @s mcc_ok matches 1 run return run function mcc:rotate_edit/fail_place

function mcc:move/cleanup_forceload
function mcc:undo/snapshot_selection

# With a custom Anchor the axis-aligned selection becomes the rotated bounds.
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_p1x = @s mcc_bminx
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_p1y = @s mcc_psty
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_p1z = @s mcc_bminz
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_p2x = @s mcc_bmaxx
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_p2y = @s mcc_dsty2
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_p2z = @s mcc_bmaxz

# Without a custom Anchor, Pos1 is the pivot and remains Pos1.
execute if score @s mcc_hasa matches 0 if score @s mcc_erot matches 1 run function mcc:rotate_edit/update_default_r90
execute if score @s mcc_hasa matches 0 if score @s mcc_erot matches 2 run function mcc:rotate_edit/update_default_r180
execute if score @s mcc_hasa matches 0 if score @s mcc_erot matches 3 run function mcc:rotate_edit/update_default_r270

function mcc:history/commit_edit
tellraw @s [{"text":"[Copy/Paste] 已直接變換真實選取區域，可用 /trigger undo，Undo 後可 /trigger redo。","color":"green"}]
return 1
