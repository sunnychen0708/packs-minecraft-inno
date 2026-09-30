execute store result storage mcc:temp x1 int 1 run scoreboard players get @s mcc_uminx
execute store result storage mcc:temp z1 int 1 run scoreboard players get @s mcc_uminz
execute store result storage mcc:temp x2 int 1 run scoreboard players get @s mcc_umaxx
execute store result storage mcc:temp z2 int 1 run scoreboard players get @s mcc_umaxz
execute if score @s mcc_p1d matches 1 run function mcc:move/forceload_remove_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:move/forceload_remove_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:move/forceload_remove_end with storage mcc:temp
