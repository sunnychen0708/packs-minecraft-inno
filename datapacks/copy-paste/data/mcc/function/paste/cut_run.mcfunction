execute store success score @s mcc_tmp run function mcc:paste/run
execute unless score @s mcc_tmp matches 1 run return fail
scoreboard players set @s mcc_clip 0
scoreboard players set @s mcc_cliptype 0
tellraw @s [{"text":"[Copy/Paste] Cut Clipboard 已貼上並消耗，不能再次複製。","color":"gray"}]
return 1
