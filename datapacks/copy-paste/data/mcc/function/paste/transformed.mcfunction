execute unless score @s mcc_sx matches 1..48 run tellraw @s [{"text":"[Copy/Paste] 使用旋轉/鏡像時，X 長度必須 ≤ 48。","color":"red"}]
execute unless score @s mcc_sx matches 1..48 run return fail
execute unless score @s mcc_sy matches 1..48 run tellraw @s [{"text":"[Copy/Paste] 使用旋轉/鏡像時，Y 長度必須 ≤ 48。","color":"red"}]
execute unless score @s mcc_sy matches 1..48 run return fail
execute unless score @s mcc_sz matches 1..48 run tellraw @s [{"text":"[Copy/Paste] 使用旋轉/鏡像時，Z 長度必須 ≤ 48。","color":"red"}]
execute unless score @s mcc_sz matches 1..48 run return fail
function mcc:paste/prepare_transform
scoreboard players operation @s mcc_pstx2 = @s mcc_bmaxx
scoreboard players operation @s mcc_psty2 = @s mcc_psty
scoreboard players operation @s mcc_psty2 += @s mcc_sy
scoreboard players remove @s mcc_psty2 1
scoreboard players operation @s mcc_pstz2 = @s mcc_bmaxz
scoreboard players operation @s mcc_pstx = @s mcc_bminx
scoreboard players operation @s mcc_pstz = @s mcc_bminz
scoreboard players operation @s mcc_fsx = @s mcc_pstx2
scoreboard players operation @s mcc_fsx -= @s mcc_pstx
scoreboard players add @s mcc_fsx 1
scoreboard players operation @s mcc_fsz = @s mcc_pstz2
scoreboard players operation @s mcc_fsz -= @s mcc_pstz
scoreboard players add @s mcc_fsz 1
function mcc:undo/setup_buffer

execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_pstx
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_psty
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_pstz
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_pstx2
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_psty2
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_pstz2
execute store result storage mcc:temp ubx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp ubx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp uby2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp ubz2 int 1 run scoreboard players get @s mcc_ubz2
scoreboard players set @s mcc_ok 0
execute if score @s mcc_dstd matches 1 run function mcc:undo/backup_from_overworld with storage mcc:temp
execute if score @s mcc_dstd matches 2 run function mcc:undo/backup_from_nether with storage mcc:temp
execute if score @s mcc_dstd matches 3 run function mcc:undo/backup_from_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] 貼上前 Undo 備份失敗。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

scoreboard players operation @s mcc_udim = @s mcc_dstd
scoreboard players operation @s mcc_ux = @s mcc_pstx
scoreboard players operation @s mcc_uy = @s mcc_psty
scoreboard players operation @s mcc_uz = @s mcc_pstz
scoreboard players operation @s mcc_ux2 = @s mcc_pstx2
scoreboard players operation @s mcc_uy2 = @s mcc_psty2
scoreboard players operation @s mcc_uz2 = @s mcc_pstz2
scoreboard players set @s mcc_usel 0
scoreboard players set @s mcc_undo 1

execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp cbx int 1 run scoreboard players get @s mcc_cbx
execute store result storage mcc:temp cbx2 int 1 run scoreboard players get @s mcc_cbx2
execute store result storage mcc:temp sx int 1 run scoreboard players get @s mcc_sx
execute store result storage mcc:temp sy int 1 run scoreboard players get @s mcc_sy
execute store result storage mcc:temp sz int 1 run scoreboard players get @s mcc_sz
execute store result storage mcc:temp cbz2 int 1 run scoreboard players get @s mcc_cbz2
function mcc:paste/save_template with storage mcc:temp

# Replace may place the structure directly. Masked first transforms into the
# player's hidden work lane, then clones only non-air blocks to the target.
execute if score @s mcc_mask matches 1 run function mcc:paste/transformed_masked
execute if score @s mcc_mask matches 0 run function mcc:paste/prepare_transform
execute if score @s mcc_mask matches 0 store result storage mcc:temp pstx int 1 run scoreboard players get @s mcc_pstx
execute if score @s mcc_mask matches 0 store result storage mcc:temp psty int 1 run scoreboard players get @s mcc_psty
execute if score @s mcc_mask matches 0 store result storage mcc:temp pstz int 1 run scoreboard players get @s mcc_pstz
execute if score @s mcc_mask matches 0 run scoreboard players set @s mcc_ok 0
execute if score @s mcc_mask matches 0 if score @s mcc_dstd matches 1 run function mcc:paste/do_place
execute if score @s mcc_mask matches 0 if score @s mcc_dstd matches 2 run execute in minecraft:the_nether run function mcc:paste/do_place
execute if score @s mcc_mask matches 0 if score @s mcc_dstd matches 3 run execute in minecraft:the_end run function mcc:paste/do_place
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] 旋轉/鏡像貼上失敗。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail
function mcc:history/commit_edit
tellraw @s [{"text":"[Copy/Paste] 旋轉/鏡像貼上完成，可用 /trigger undo。","color":"green"}]
return 1
