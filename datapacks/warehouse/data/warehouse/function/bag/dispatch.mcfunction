scoreboard players set @s bag 0
execute if entity @s[name=SunnyChen] run return run function warehouse:bag/owner/01
execute if entity @s[name=penguin0531] run return run function warehouse:bag/owner/02
execute if entity @s[name=geena0701] run return run function warehouse:bag/owner/03
execute if entity @s[name=Felicitypeng] run return run function warehouse:bag/owner/04
tellraw @s {"text":"[Warehouse] 此指令僅開放四位固定玩家。","color":"yellow"}
