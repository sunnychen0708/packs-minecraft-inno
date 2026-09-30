scoreboard players operation @s mcc_bpsz = @s mcc_bpsz0
scoreboard players operation @s mcc_bptz = @s mcc_bptz0
scoreboard players add @s mcc_bpsy 1
scoreboard players add @s mcc_bpty 1
execute if score @s mcc_bpsy > @s mcc_bpsy2 run function mcc:blueprint/finish
return 1
