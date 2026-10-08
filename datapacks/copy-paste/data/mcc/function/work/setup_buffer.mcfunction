scoreboard players operation @s mcc_wbx = @s mcc_id
scoreboard players operation @s mcc_wbx *= #slot mcc_id
scoreboard players operation @s mcc_wbx += #base mcc_id
scoreboard players operation @s mcc_wbx2 = @s mcc_wbx
scoreboard players operation @s mcc_wbx2 += @s mcc_selx
scoreboard players remove @s mcc_wbx2 1
scoreboard players operation @s mcc_wby2 = @s mcc_sely
scoreboard players remove @s mcc_wby2 1
scoreboard players operation @s mcc_wbz2 = #workz mcc_id
scoreboard players operation @s mcc_wbz2 += @s mcc_selz
scoreboard players remove @s mcc_wbz2 1
