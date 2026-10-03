# Build the transformed Cut clipboard in this player's canonical hidden work lane,
# then clone only non-air blocks to the real target.
scoreboard players operation @s mcc_wbx = @s mcc_id
scoreboard players operation @s mcc_wbx *= #slot mcc_id
scoreboard players operation @s mcc_wbx += #base mcc_id

# Solve transform at origin, then translate so the transformed bounding minimum
# lands exactly at (player_slot_x, 0, #workz), independent of external Anchor radius.
scoreboard players set @s mcc_dstx 0
scoreboard players set @s mcc_dsty 0
scoreboard players set @s mcc_dstz 0
function mcc:paste/prepare_transform
scoreboard players operation @s mcc_tmp = @s mcc_wbx
scoreboard players operation @s mcc_tmp -= @s mcc_bminx
scoreboard players operation @s mcc_dstx += @s mcc_tmp
scoreboard players operation @s mcc_tmp = #zero mcc_id
scoreboard players operation @s mcc_tmp -= @s mcc_psty
scoreboard players operation @s mcc_dsty += @s mcc_tmp
scoreboard players operation @s mcc_tmp = #workz mcc_id
scoreboard players operation @s mcc_tmp -= @s mcc_bminz
scoreboard players operation @s mcc_dstz += @s mcc_tmp
function mcc:paste/prepare_transform

scoreboard players operation @s mcc_psty2 = @s mcc_psty
scoreboard players operation @s mcc_psty2 += @s mcc_sy
scoreboard players remove @s mcc_psty2 1

execute store result storage mcc:temp x1 int 1 run scoreboard players get @s mcc_bminx
execute store result storage mcc:temp z1 int 1 run scoreboard players get @s mcc_bminz
execute store result storage mcc:temp x2 int 1 run scoreboard players get @s mcc_bmaxx
execute store result storage mcc:temp z2 int 1 run scoreboard players get @s mcc_bmaxz
function mcc:blueprint/forceload_add with storage mcc:temp

execute store result storage mcc:temp id int 1 run scoreboard players get @s mcc_id
execute store result storage mcc:temp pstx int 1 run scoreboard players get @s mcc_pstx
execute store result storage mcc:temp psty int 1 run scoreboard players get @s mcc_psty
execute store result storage mcc:temp pstz int 1 run scoreboard players get @s mcc_pstz
scoreboard players set @s mcc_ok 0
execute in minecraft:overworld run function mcc:paste/do_place
execute unless score @s mcc_ok matches 1 run function mcc:blueprint/forceload_remove with storage mcc:temp
execute unless score @s mcc_ok matches 1 run return fail

execute store result storage mcc:temp sx int 1 run scoreboard players get @s mcc_bminx
execute store result storage mcc:temp sy int 1 run scoreboard players get @s mcc_psty
execute store result storage mcc:temp sz int 1 run scoreboard players get @s mcc_bminz
execute store result storage mcc:temp sx2 int 1 run scoreboard players get @s mcc_bmaxx
execute store result storage mcc:temp sy2 int 1 run scoreboard players get @s mcc_psty2
execute store result storage mcc:temp sz2 int 1 run scoreboard players get @s mcc_bmaxz
execute store result storage mcc:temp dx int 1 run scoreboard players get @s mcc_ux
execute store result storage mcc:temp dy int 1 run scoreboard players get @s mcc_uy
execute store result storage mcc:temp dz int 1 run scoreboard players get @s mcc_uz

scoreboard players set @s mcc_ok 0
execute if score @s mcc_udim matches 1 run function mcc:paste/masked_from_work_overworld with storage mcc:temp
execute if score @s mcc_udim matches 2 run function mcc:paste/masked_from_work_nether with storage mcc:temp
execute if score @s mcc_udim matches 3 run function mcc:paste/masked_from_work_end with storage mcc:temp
function mcc:blueprint/forceload_remove with storage mcc:temp
return 1
