scoreboard players operation @s mcc_rbx = @s mcc_id
scoreboard players operation @s mcc_rbx *= #slot mcc_id
scoreboard players operation @s mcc_rbx += #base mcc_id
scoreboard players operation @s mcc_rbx2 = @s mcc_rbx
scoreboard players operation @s mcc_rbx2 += @s mcc_fsx
scoreboard players remove @s mcc_rbx2 1
scoreboard players operation @s mcc_rby2 = @s mcc_sy
scoreboard players remove @s mcc_rby2 1
scoreboard players operation @s mcc_rbz2 = #redoz mcc_id
scoreboard players operation @s mcc_rbz2 += @s mcc_fsz
scoreboard players remove @s mcc_rbz2 1
