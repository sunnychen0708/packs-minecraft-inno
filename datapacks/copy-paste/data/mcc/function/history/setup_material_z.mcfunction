scoreboard players operation @s mcc_hz = @s mcc_hslot
scoreboard players remove @s mcc_hz 1
scoreboard players operation @s mcc_hz *= #hgap mcc_id
scoreboard players operation @s mcc_hz += #mhistz mcc_id
scoreboard players operation @s mcc_hz2 = @s mcc_hz
scoreboard players operation @s mcc_tmp = @s mcc_fsz
scoreboard players remove @s mcc_tmp 1
scoreboard players operation @s mcc_hz2 += @s mcc_tmp
