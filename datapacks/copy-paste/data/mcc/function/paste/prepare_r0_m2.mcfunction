scoreboard players operation @s mcc_tx = @s mcc_offx
scoreboard players operation @s mcc_tz = @s mcc_offz
scoreboard players operation @s mcc_tz *= #neg mcc_id
scoreboard players operation @s mcc_pstx = @s mcc_dstx
scoreboard players operation @s mcc_pstx -= @s mcc_tx
scoreboard players operation @s mcc_psty = @s mcc_dsty
scoreboard players operation @s mcc_psty -= @s mcc_offy
scoreboard players operation @s mcc_pstz = @s mcc_dstz
scoreboard players operation @s mcc_pstz -= @s mcc_tz
scoreboard players operation @s mcc_bminx = @s mcc_pstx
scoreboard players operation @s mcc_bmaxx = @s mcc_pstx
scoreboard players operation @s mcc_bmaxx += @s mcc_sx
scoreboard players remove @s mcc_bmaxx 1
scoreboard players operation @s mcc_bminz = @s mcc_pstz
scoreboard players operation @s mcc_bmaxz = @s mcc_pstz
scoreboard players operation @s mcc_bminz -= @s mcc_sz
scoreboard players add @s mcc_bminz 1
