scoreboard players operation @s mcc_ubx = @s mcc_id
scoreboard players operation @s mcc_ubx *= #slot mcc_id
scoreboard players operation @s mcc_ubx += #base mcc_id
scoreboard players operation @s mcc_ubx2 = @s mcc_ubx
scoreboard players operation @s mcc_ubx2 += @s mcc_usx
scoreboard players remove @s mcc_ubx2 1
scoreboard players operation @s mcc_uby2 = @s mcc_usy
scoreboard players remove @s mcc_uby2 1
scoreboard players operation @s mcc_ubz2 = #ubz mcc_id
scoreboard players operation @s mcc_ubz2 += @s mcc_usz
scoreboard players remove @s mcc_ubz2 1
