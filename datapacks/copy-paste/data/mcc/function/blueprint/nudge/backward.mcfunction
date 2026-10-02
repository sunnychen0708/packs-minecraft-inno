execute unless score @s bpbackward matches 1..128 run return fail
scoreboard players set @s mcc_dx 0
scoreboard players set @s mcc_dy 0
scoreboard players set @s mcc_dz 0
scoreboard players operation @s mcc_amt = @s bpbackward
scoreboard players operation @s mcc_amt *= #neg mcc_id
scoreboard players operation @s bpforward = @s mcc_amt
scoreboard players operation @s bpforward *= #neg mcc_id
execute if entity @s[y_rotation=-45..45] run scoreboard players operation @s mcc_dz = @s mcc_amt
execute if entity @s[y_rotation=-45..45] run return run function mcc:blueprint/nudge/run
execute if entity @s[y_rotation=45..135] run scoreboard players operation @s mcc_dx = @s mcc_amt
execute if entity @s[y_rotation=45..135] run scoreboard players operation @s mcc_dx *= #neg mcc_id
execute if entity @s[y_rotation=45..135] run return run function mcc:blueprint/nudge/run
execute if entity @s[y_rotation=-135..-45] run scoreboard players operation @s mcc_dx = @s mcc_amt
execute if entity @s[y_rotation=-135..-45] run return run function mcc:blueprint/nudge/run
execute if entity @s[y_rotation=135..180] run scoreboard players operation @s mcc_dz = @s mcc_amt
execute if entity @s[y_rotation=135..180] run scoreboard players operation @s mcc_dz *= #neg mcc_id
execute if entity @s[y_rotation=135..180] run return run function mcc:blueprint/nudge/run
execute if entity @s[y_rotation=-180..-135] run scoreboard players operation @s mcc_dz = @s mcc_amt
execute if entity @s[y_rotation=-180..-135] run scoreboard players operation @s mcc_dz *= #neg mcc_id
execute if entity @s[y_rotation=-180..-135] run return run function mcc:blueprint/nudge/run
return fail
