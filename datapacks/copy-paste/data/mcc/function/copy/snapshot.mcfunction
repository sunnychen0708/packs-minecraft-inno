execute store success score @s mcc_tmp run function mcc:selection/prepare
execute unless score @s mcc_tmp matches 1 run return fail

scoreboard players operation @s mcc_sx = @s mcc_selx
scoreboard players operation @s mcc_sy = @s mcc_sely
scoreboard players operation @s mcc_sz = @s mcc_selz
scoreboard players operation @s mcc_offx = @s mcc_soffx
scoreboard players operation @s mcc_offy = @s mcc_soffy
scoreboard players operation @s mcc_offz = @s mcc_soffz

scoreboard players operation @s mcc_cbx = @s mcc_id
scoreboard players operation @s mcc_cbx *= #slot mcc_id
scoreboard players operation @s mcc_cbx += #base mcc_id
scoreboard players operation @s mcc_cbx2 = @s mcc_cbx
scoreboard players operation @s mcc_cbx2 += @s mcc_sx
scoreboard players remove @s mcc_cbx2 1
scoreboard players operation @s mcc_cby2 = @s mcc_sy
scoreboard players remove @s mcc_cby2 1
scoreboard players operation @s mcc_cbz2 = #cbz mcc_id
scoreboard players operation @s mcc_cbz2 += @s mcc_sz
scoreboard players remove @s mcc_cbz2 1

execute store result storage mcc:temp minx int 1 run scoreboard players get @s mcc_minx
execute store result storage mcc:temp miny int 1 run scoreboard players get @s mcc_miny
execute store result storage mcc:temp minz int 1 run scoreboard players get @s mcc_minz
execute store result storage mcc:temp maxx int 1 run scoreboard players get @s mcc_maxx
execute store result storage mcc:temp maxy int 1 run scoreboard players get @s mcc_maxy
execute store result storage mcc:temp maxz int 1 run scoreboard players get @s mcc_maxz
execute store result storage mcc:temp cbx int 1 run scoreboard players get @s mcc_cbx
execute store result storage mcc:temp cbx2 int 1 run scoreboard players get @s mcc_cbx2
execute store result storage mcc:temp cby2 int 1 run scoreboard players get @s mcc_cby2
execute store result storage mcc:temp cbz2 int 1 run scoreboard players get @s mcc_cbz2

scoreboard players set @s mcc_ok 0
execute if score @s mcc_p1d matches 1 run function mcc:copy/from_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:copy/from_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:copy/from_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] 複製失敗。請確認整個選取區域目前已載入，且座標有效。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail
scoreboard players set @s mcc_clip 1
return 1
