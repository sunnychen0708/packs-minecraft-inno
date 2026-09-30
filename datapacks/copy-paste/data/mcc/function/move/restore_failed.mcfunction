execute store result storage mcc:temp ubx int 1 run scoreboard players get @s mcc_ubx
execute store result storage mcc:temp ubx2 int 1 run scoreboard players get @s mcc_ubx2
execute store result storage mcc:temp uby2 int 1 run scoreboard players get @s mcc_uby2
execute store result storage mcc:temp ubz2 int 1 run scoreboard players get @s mcc_ubz2
execute store result storage mcc:temp dstx int 1 run scoreboard players get @s mcc_uminx
execute store result storage mcc:temp dsty int 1 run scoreboard players get @s mcc_uminy
execute store result storage mcc:temp dstz int 1 run scoreboard players get @s mcc_uminz
scoreboard players set @s mcc_ok 0
execute if score @s mcc_p1d matches 1 run function mcc:undo/restore_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:undo/restore_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:undo/restore_end with storage mcc:temp
execute if score @s mcc_ok matches 1 run scoreboard players set @s mcc_undo 0
execute if score @s mcc_ok matches 1 run scoreboard players set @s mcc_usel 0
execute unless score @s mcc_ok matches 1 run return fail
return 1
