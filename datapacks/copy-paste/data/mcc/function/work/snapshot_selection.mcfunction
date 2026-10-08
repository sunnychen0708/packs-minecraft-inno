function mcc:work/setup_buffer
execute store result storage mcc:temp srcx int 1 run scoreboard players get @s mcc_minx
execute store result storage mcc:temp srcy int 1 run scoreboard players get @s mcc_miny
execute store result storage mcc:temp srcz int 1 run scoreboard players get @s mcc_minz
execute store result storage mcc:temp srcx2 int 1 run scoreboard players get @s mcc_maxx
execute store result storage mcc:temp srcy2 int 1 run scoreboard players get @s mcc_maxy
execute store result storage mcc:temp srcz2 int 1 run scoreboard players get @s mcc_maxz
execute store result storage mcc:temp wbx int 1 run scoreboard players get @s mcc_wbx
execute store result storage mcc:temp wbx2 int 1 run scoreboard players get @s mcc_wbx2
execute store result storage mcc:temp wby2 int 1 run scoreboard players get @s mcc_wby2
execute store result storage mcc:temp wbz2 int 1 run scoreboard players get @s mcc_wbz2
scoreboard players set @s mcc_ok 0
execute if score @s mcc_p1d matches 1 run function mcc:work/snapshot_from_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:work/snapshot_from_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:work/snapshot_from_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run return fail
return 1
