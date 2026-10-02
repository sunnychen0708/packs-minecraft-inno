execute unless score @s bpdown matches 1..128 run return fail
scoreboard players set @s mcc_dx 0
scoreboard players set @s mcc_dz 0
scoreboard players operation @s mcc_dy = @s bpdown
scoreboard players operation @s mcc_dy *= #neg mcc_id
return run function mcc:blueprint/nudge/run
