scoreboard players operation @s mcc_bpsx = @s mcc_bpsx0
scoreboard players operation @s mcc_bptx = @s mcc_bptx0
scoreboard players add @s mcc_bpsz 1
scoreboard players add @s mcc_bptz 1
execute if score @s mcc_bpsz > @s mcc_bpsz2 run function mcc:blueprint/recount_wrap_z
return 1
