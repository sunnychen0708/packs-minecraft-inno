execute unless score @s forward matches 1..128 run tellraw @s [{"text":"[Copy/Paste] Move 距離必須是 1～128。","color":"red"}]
execute unless score @s forward matches 1..128 run return fail
scoreboard players set @s mcc_dx 0
scoreboard players set @s mcc_dy 0
scoreboard players set @s mcc_dz 0
scoreboard players operation @s mcc_amt = @s forward
execute if entity @s[y_rotation=-45..45] run scoreboard players operation @s mcc_dz = @s mcc_amt
execute if entity @s[y_rotation=-45..45] run return run function mcc:move/run
execute if entity @s[y_rotation=45..135] run scoreboard players operation @s mcc_dx = @s mcc_amt
execute if entity @s[y_rotation=45..135] run scoreboard players operation @s mcc_dx *= #neg mcc_id
execute if entity @s[y_rotation=45..135] run return run function mcc:move/run
execute if entity @s[y_rotation=-135..-45] run scoreboard players operation @s mcc_dx = @s mcc_amt
execute if entity @s[y_rotation=-135..-45] run return run function mcc:move/run
execute if entity @s[y_rotation=135..180] run scoreboard players operation @s mcc_dz = @s mcc_amt
execute if entity @s[y_rotation=135..180] run scoreboard players operation @s mcc_dz *= #neg mcc_id
execute if entity @s[y_rotation=135..180] run return run function mcc:move/run
execute if entity @s[y_rotation=-180..-135] run scoreboard players operation @s mcc_dz = @s mcc_amt
execute if entity @s[y_rotation=-180..-135] run scoreboard players operation @s mcc_dz *= #neg mcc_id
execute if entity @s[y_rotation=-180..-135] run return run function mcc:move/run
tellraw @s [{"text":"[Copy/Paste] 無法判斷玩家水平朝向。","color":"red"}]
return fail
