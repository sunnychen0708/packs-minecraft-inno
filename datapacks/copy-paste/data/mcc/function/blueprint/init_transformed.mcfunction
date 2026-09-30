execute unless score @s mcc_sx matches 1..48 run tellraw @s [{"text":"[Copy/Paste] Blueprint 使用旋轉/鏡像時，X 長度必須 ≤ 48。","color":"red"}]
execute unless score @s mcc_sx matches 1..48 run return fail
execute unless score @s mcc_sy matches 1..48 run tellraw @s [{"text":"[Copy/Paste] Blueprint 使用旋轉/鏡像時，Y 長度必須 ≤ 48。","color":"red"}]
execute unless score @s mcc_sy matches 1..48 run return fail
execute unless score @s mcc_sz matches 1..48 run tellraw @s [{"text":"[Copy/Paste] Blueprint 使用旋轉/鏡像時，Z 長度必須 ≤ 48。","color":"red"}]
execute unless score @s mcc_sz matches 1..48 run return fail

# Calculate the real target bounding minimum using the same engine transform math as Paste.
function mcc:paste/prepare_transform
scoreboard players operation @s mcc_bptx0 = @s mcc_bminx
scoreboard players operation @s mcc_bpty0 = @s mcc_psty
scoreboard players operation @s mcc_bptz0 = @s mcc_bminz

# Save the Clipboard as a vanilla Structure Template so Minecraft itself transforms directional states.
execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp cbx int 1 run scoreboard players get @s mcc_cbx
execute store result storage mcc:temp cbx2 int 1 run scoreboard players get @s mcc_cbx2
execute store result storage mcc:temp sx int 1 run scoreboard players get @s mcc_sx
execute store result storage mcc:temp sy int 1 run scoreboard players get @s mcc_sy
execute store result storage mcc:temp sz int 1 run scoreboard players get @s mcc_sz
execute store result storage mcc:temp cbz2 int 1 run scoreboard players get @s mcc_cbz2
function mcc:paste/save_template with storage mcc:temp

# Re-run transform math around a safe hidden Overworld anchor.
scoreboard players operation @s mcc_bpx = @s mcc_id
scoreboard players operation @s mcc_bpx *= #slot mcc_id
scoreboard players operation @s mcc_bpx += #base mcc_id
scoreboard players operation @s mcc_dstx = @s mcc_bpx
scoreboard players operation @s mcc_dstx += #bpofs mcc_id
scoreboard players set @s mcc_dsty 64
scoreboard players operation @s mcc_dstz = #bpz mcc_id
scoreboard players operation @s mcc_dstz += #bpofs mcc_id
function mcc:paste/prepare_transform

scoreboard players operation @s mcc_bpsx0 = @s mcc_bminx
scoreboard players operation @s mcc_bpsy0 = @s mcc_psty
scoreboard players operation @s mcc_bpsz0 = @s mcc_bminz
scoreboard players operation @s mcc_bpsx2 = @s mcc_bmaxx
scoreboard players operation @s mcc_bpsy2 = @s mcc_psty
scoreboard players operation @s mcc_bpsy2 += @s mcc_sy
scoreboard players remove @s mcc_bpsy2 1
scoreboard players operation @s mcc_bpsz2 = @s mcc_bmaxz

execute store result storage mcc:temp x1 int 1 run scoreboard players get @s mcc_bpsx0
execute store result storage mcc:temp z1 int 1 run scoreboard players get @s mcc_bpsz0
execute store result storage mcc:temp x2 int 1 run scoreboard players get @s mcc_bpsx2
execute store result storage mcc:temp z2 int 1 run scoreboard players get @s mcc_bpsz2
function mcc:blueprint/forceload_add with storage mcc:temp

execute store result storage mcc:temp pstx int 1 run scoreboard players get @s mcc_pstx
execute store result storage mcc:temp psty int 1 run scoreboard players get @s mcc_psty
execute store result storage mcc:temp pstz int 1 run scoreboard players get @s mcc_pstz
scoreboard players set @s mcc_ok 0
execute in minecraft:overworld run function mcc:paste/do_place
execute unless score @s mcc_ok matches 1 run function mcc:blueprint/cancel_scan
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Blueprint 旋轉/鏡像暫存建立失敗。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

scoreboard players set @s mcc_bpkind 1
function mcc:blueprint/start_scan_loaded
return 1
