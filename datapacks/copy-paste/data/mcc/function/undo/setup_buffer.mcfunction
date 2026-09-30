scoreboard players operation @s mcc_ubx = @s mcc_id
scoreboard players operation @s mcc_ubx *= #slot mcc_id
scoreboard players operation @s mcc_ubx += #base mcc_id
scoreboard players operation @s mcc_ubx2 = @s mcc_ubx
scoreboard players operation @s mcc_ubx2 += @s mcc_fsx
scoreboard players remove @s mcc_ubx2 1
scoreboard players operation @s mcc_uby2 = @s mcc_sy
scoreboard players remove @s mcc_uby2 1
scoreboard players operation @s mcc_ubz2 = #ubz mcc_id
scoreboard players operation @s mcc_ubz2 += @s mcc_fsz
scoreboard players remove @s mcc_ubz2 1
