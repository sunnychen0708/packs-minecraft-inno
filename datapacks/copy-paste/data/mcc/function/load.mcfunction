scoreboard objectives add mcc_pos1 trigger
scoreboard objectives add mcc_pos2 trigger
scoreboard objectives add mcc_anchor trigger
scoreboard objectives add mcc_copy trigger
scoreboard objectives add mcc_paste trigger
scoreboard objectives add mcc_mode trigger
scoreboard objectives add mcc_help trigger
scoreboard objectives add mcc_id dummy
scoreboard objectives add mcc_has1 dummy
scoreboard objectives add mcc_has2 dummy
scoreboard objectives add mcc_hasa dummy
scoreboard objectives add mcc_clip dummy
scoreboard objectives add mcc_mask dummy
scoreboard objectives add mcc_ray dummy
scoreboard objectives add mcc_selmode dummy
scoreboard objectives add mcc_p1x dummy
scoreboard objectives add mcc_p1y dummy
scoreboard objectives add mcc_p1z dummy
scoreboard objectives add mcc_p1d dummy
scoreboard objectives add mcc_p2x dummy
scoreboard objectives add mcc_p2y dummy
scoreboard objectives add mcc_p2z dummy
scoreboard objectives add mcc_p2d dummy
scoreboard objectives add mcc_anx dummy
scoreboard objectives add mcc_any dummy
scoreboard objectives add mcc_anz dummy
scoreboard objectives add mcc_and dummy
scoreboard objectives add mcc_dstd dummy
scoreboard objectives add mcc_minx dummy
scoreboard objectives add mcc_miny dummy
scoreboard objectives add mcc_minz dummy
scoreboard objectives add mcc_maxx dummy
scoreboard objectives add mcc_maxy dummy
scoreboard objectives add mcc_maxz dummy
scoreboard objectives add mcc_sx dummy
scoreboard objectives add mcc_sy dummy
scoreboard objectives add mcc_sz dummy
scoreboard objectives add mcc_vol dummy
scoreboard objectives add mcc_lim dummy
scoreboard objectives add mcc_offx dummy
scoreboard objectives add mcc_offy dummy
scoreboard objectives add mcc_offz dummy
scoreboard objectives add mcc_cbx dummy
scoreboard objectives add mcc_cbx2 dummy
scoreboard objectives add mcc_cbz2 dummy
scoreboard objectives add mcc_cby2 dummy
scoreboard objectives add mcc_dstx dummy
scoreboard objectives add mcc_dsty dummy
scoreboard objectives add mcc_dstz dummy
scoreboard objectives add mcc_dstx2 dummy
scoreboard objectives add mcc_dsty2 dummy
scoreboard objectives add mcc_dstz2 dummy
scoreboard objectives add mcc_ok dummy
scoreboard players add #next mcc_id 0
scoreboard players set #slot mcc_id 256
scoreboard players set #base mcc_id 20000000
scoreboard players set #cbz mcc_id 20000000
scoreboard players set #one mcc_id 1

tellraw @a [{"text":"[Copy/Paste] ","color":"gold"},{"text":"v0.2 已載入。輸入 ","color":"gray"},{"text":"/trigger mcc_help","color":"yellow"},{"text":" 查看用法。","color":"gray"}]
