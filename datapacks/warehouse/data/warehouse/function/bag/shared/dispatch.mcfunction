scoreboard players set @s sbag 0
scoreboard players set @s wh_bag_id 0
execute if entity @s[name=SunnyChen] run scoreboard players set @s wh_bag_id 1
execute if entity @s[name=penguin0531] run scoreboard players set @s wh_bag_id 2
execute if entity @s[name=geena0701] run scoreboard players set @s wh_bag_id 3
execute if entity @s[name=Felicitypeng] run scoreboard players set @s wh_bag_id 4
execute if score @s wh_bag_id matches 0 run return run tellraw @s {"text":"[Warehouse] 此指令僅開放四位固定玩家。","color":"red"}
execute if data storage warehouse:bags shared{active:1b} run return run function warehouse:bag/shared/occupied
function warehouse:bag/shared/enter
