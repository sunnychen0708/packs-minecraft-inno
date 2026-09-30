execute unless score @s down matches 1..128 run tellraw @s [{"text":"[Copy/Paste] Move 距離必須是 1～128。","color":"red"}]
execute unless score @s down matches 1..128 run return fail
scoreboard players set @s mcc_dx 0
scoreboard players set @s mcc_dy 0
scoreboard players set @s mcc_dz 0
scoreboard players operation @s mcc_amt = @s down
scoreboard players operation @s mcc_dy = @s mcc_amt
scoreboard players operation @s mcc_dy *= #neg mcc_id
return run function mcc:move/run
