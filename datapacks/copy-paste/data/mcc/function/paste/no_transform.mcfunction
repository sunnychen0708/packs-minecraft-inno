scoreboard players operation @s mcc_dstx -= @s mcc_offx
scoreboard players operation @s mcc_dsty -= @s mcc_offy
scoreboard players operation @s mcc_dstz -= @s mcc_offz
scoreboard players operation @s mcc_dstx2 = @s mcc_dstx
scoreboard players operation @s mcc_dstx2 += @s mcc_sx
scoreboard players remove @s mcc_dstx2 1
scoreboard players operation @s mcc_dsty2 = @s mcc_dsty
scoreboard players operation @s mcc_dsty2 += @s mcc_sy
scoreboard players remove @s mcc_dsty2 1
scoreboard players operation @s mcc_dstz2 = @s mcc_dstz
scoreboard players operation @s mcc_dstz2 += @s mcc_sz
scoreboard players remove @s mcc_dstz2 1
scoreboard players operation @s mcc_fsx = @s mcc_sx
scoreboard players operation @s mcc_fsz = @s mcc_sz
function mcc:undo/setup_buffer

execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_dstx
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_dsty
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_dstz
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_dstx2
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_dsty2
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_dstz2
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
scoreboard players operation @s mcc_ux = @s mcc_dstx
scoreboard players operation @s mcc_uy = @s mcc_dsty
scoreboard players operation @s mcc_uz = @s mcc_dstz
scoreboard players operation @s mcc_ux2 = @s mcc_dstx2
scoreboard players operation @s mcc_uy2 = @s mcc_dsty2
scoreboard players operation @s mcc_uz2 = @s mcc_dstz2
scoreboard players set @s mcc_usel 0
scoreboard players set @s mcc_undo 1

execute store result storage mcc:temp cbx int 1 run scoreboard players get @s mcc_cbx
execute store result storage mcc:temp cbx2 int 1 run scoreboard players get @s mcc_cbx2
execute store result storage mcc:temp cby2 int 1 run scoreboard players get @s mcc_cby2
execute store result storage mcc:temp cbz2 int 1 run scoreboard players get @s mcc_cbz2
execute store result storage mcc:temp dstx int 1 run scoreboard players get @s mcc_dstx
execute store result storage mcc:temp dsty int 1 run scoreboard players get @s mcc_dsty
execute store result storage mcc:temp dstz int 1 run scoreboard players get @s mcc_dstz

scoreboard players set @s mcc_ok 0
execute if score @s mcc_dstd matches 1 if score @s mcc_mask matches 0 run function mcc:paste/to_overworld_replace with storage mcc:temp
execute if score @s mcc_dstd matches 1 if score @s mcc_mask matches 1 run function mcc:paste/to_overworld_masked with storage mcc:temp
execute if score @s mcc_dstd matches 2 if score @s mcc_mask matches 0 run function mcc:paste/to_nether_replace with storage mcc:temp
execute if score @s mcc_dstd matches 2 if score @s mcc_mask matches 1 run function mcc:paste/to_nether_masked with storage mcc:temp
execute if score @s mcc_dstd matches 3 if score @s mcc_mask matches 0 run function mcc:paste/to_end_replace with storage mcc:temp
execute if score @s mcc_dstd matches 3 if score @s mcc_mask matches 1 run function mcc:paste/to_end_masked with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] 貼上失敗。請確認目標區域已載入、沒有超出該維度高度限制。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail
tellraw @s [{"text":"[Copy/Paste] 貼上完成，可用 /trigger undo Undo。","color":"green"}]
return 1
