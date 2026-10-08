execute store success score @s mcc_tmp run function mcc:copy/run
execute unless score @s mcc_tmp matches 1 run return fail

scoreboard players operation @s mcc_fsx = @s mcc_sx
scoreboard players operation @s mcc_fsz = @s mcc_sz
function mcc:undo/setup_buffer

execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_minx
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_miny
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_minz
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_maxx
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_maxy
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_maxz
execute store result storage mcc:temp ubx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp ubx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp uby2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp ubz2 int 1 run scoreboard players get @s mcc_ubz2

scoreboard players set @s mcc_ok 0
execute if score @s mcc_p1d matches 1 run function mcc:undo/backup_from_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:undo/backup_from_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:undo/backup_from_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Cut 前備份失敗，已取消。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

scoreboard players set @s mcc_ok 0
execute store result storage mcc:temp minx int 1 run scoreboard players get @s mcc_minx
execute store result storage mcc:temp miny int 1 run scoreboard players get @s mcc_miny
execute store result storage mcc:temp minz int 1 run scoreboard players get @s mcc_minz
execute store result storage mcc:temp maxx int 1 run scoreboard players get @s mcc_maxx
execute store result storage mcc:temp maxy int 1 run scoreboard players get @s mcc_maxy
execute store result storage mcc:temp maxz int 1 run scoreboard players get @s mcc_maxz
execute if score @s mcc_p1d matches 1 run function mcc:cut/clear_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:cut/clear_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:cut/clear_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Cut 清空來源失敗。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

scoreboard players operation @s mcc_udim = @s mcc_p1d
scoreboard players operation @s mcc_ux = @s mcc_minx
scoreboard players operation @s mcc_uy = @s mcc_miny
scoreboard players operation @s mcc_uz = @s mcc_minz
scoreboard players operation @s mcc_ux2 = @s mcc_maxx
scoreboard players operation @s mcc_uy2 = @s mcc_maxy
scoreboard players operation @s mcc_uz2 = @s mcc_maxz
scoreboard players set @s mcc_usel 0
scoreboard players set @s mcc_undo 1
tellraw @s [{"text":"[Copy/Paste] Cut 完成，可用 /trigger undo Undo。","color":"green"}]
return 1
