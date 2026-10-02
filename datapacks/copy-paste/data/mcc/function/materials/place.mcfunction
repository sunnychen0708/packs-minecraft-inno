scoreboard players operation @s mcc_dstx = @s mcc_bptx0
scoreboard players operation @s mcc_dsty = @s mcc_bpty0
scoreboard players operation @s mcc_dstz = @s mcc_bptz0
scoreboard players operation @s mcc_dstd = @s mcc_bpdst
scoreboard players operation @s mcc_fsx = @s mcc_bpsx2
scoreboard players operation @s mcc_fsx -= @s mcc_bpsx0
scoreboard players add @s mcc_fsx 1
scoreboard players operation @s mcc_fsz = @s mcc_bpsz2
scoreboard players operation @s mcc_fsz -= @s mcc_bpsz0
scoreboard players add @s mcc_fsz 1
scoreboard players operation @s mcc_dstx2 = @s mcc_dstx
scoreboard players operation @s mcc_dstx2 += @s mcc_fsx
scoreboard players remove @s mcc_dstx2 1
scoreboard players operation @s mcc_dsty2 = @s mcc_dsty
scoreboard players operation @s mcc_dsty2 += @s mcc_sy
scoreboard players remove @s mcc_dsty2 1
scoreboard players operation @s mcc_dstz2 = @s mcc_dstz
scoreboard players operation @s mcc_dstz2 += @s mcc_fsz
scoreboard players remove @s mcc_dstz2 1
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
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] 施工前 Undo 備份失敗；未改動世界，材料已退還。","color":"red"}]
execute unless score @s mcc_ok matches 1 run function mcc:materials/refund_taken_start
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_matphase 0
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
data modify storage mcc:temp build set value {}
execute store result storage mcc:temp build.sx int 1 run scoreboard players get @s mcc_bpsx0
execute store result storage mcc:temp build.sy int 1 run scoreboard players get @s mcc_bpsy0
execute store result storage mcc:temp build.sz int 1 run scoreboard players get @s mcc_bpsz0
execute store result storage mcc:temp build.sx2 int 1 run scoreboard players get @s mcc_bpsx2
execute store result storage mcc:temp build.sy2 int 1 run scoreboard players get @s mcc_bpsy2
execute store result storage mcc:temp build.sz2 int 1 run scoreboard players get @s mcc_bpsz2
execute store result storage mcc:temp build.dx int 1 run scoreboard players get @s mcc_dstx
execute store result storage mcc:temp build.dy int 1 run scoreboard players get @s mcc_dsty
execute store result storage mcc:temp build.dz int 1 run scoreboard players get @s mcc_dstz
execute store result storage mcc:temp build.dx2 int 1 run scoreboard players get @s mcc_dstx2
execute store result storage mcc:temp build.dz2 int 1 run scoreboard players get @s mcc_dstz2
scoreboard players set @s mcc_ok 0
function mcc:materials/place_buffer with storage mcc:temp build
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] 施工失敗；世界未確認成功，材料已退還，Blueprint 保留。","color":"red"}]
execute unless score @s mcc_ok matches 1 run function mcc:materials/refund_taken_start
execute unless score @s mcc_ok matches 1 run scoreboard players set @s mcc_matphase 0
execute unless score @s mcc_ok matches 1 run return fail
scoreboard players set @s mcc_histmat 1
function mcc:history/commit_edit
scoreboard players set @s mcc_matphase 0
function mcc:blueprint/clear_internal
tellraw @s [{"text":"[Copy/Paste] 材料已扣除，施工完成。可用 /trigger undo 還原世界。","color":"green"}]
return 1
