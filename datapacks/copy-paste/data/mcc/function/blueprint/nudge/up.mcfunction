execute unless score @s bpup matches 1..128 run return fail
scoreboard players set @s mcc_dx 0
scoreboard players set @s mcc_dz 0
scoreboard players operation @s mcc_dy = @s bpup
return run function mcc:blueprint/nudge/run
