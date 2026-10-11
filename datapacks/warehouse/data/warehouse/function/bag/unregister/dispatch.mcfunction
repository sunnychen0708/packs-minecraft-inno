scoreboard players set @s wh_bag_ok 0
execute if score @s wh_bag_unreg matches 1 if entity @s[name=SunnyChen] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_unreg matches 2 if entity @s[name=SunnyChen] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_unreg matches 3 if entity @s[name=penguin0531] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_unreg matches 4 if entity @s[name=penguin0531] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_unreg matches 5 if entity @s[name=geena0701] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_unreg matches 6 if entity @s[name=geena0701] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_unreg matches 7 if entity @s[name=Felicitypeng] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_unreg matches 8 if entity @s[name=Felicitypeng] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_unreg matches 9 if entity @s[name=SunnyChen] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_unreg matches 10 if entity @s[name=SunnyChen] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_ok matches 0 run return run tellraw @s {"text":"[Warehouse] 你無權取消這個背包箱註冊。","color":"red"}
execute if score @s wh_bag_unreg matches 9..10 if data storage warehouse:bags shared{active:1b} run return run tellraw @s {"text":"[Warehouse] 共用背包正在使用，不能取消註冊 05。","color":"red"}
execute if score @s wh_bag_unreg matches 1 run data remove storage warehouse:bags slots.p01.a
execute if score @s wh_bag_unreg matches 2 run data remove storage warehouse:bags slots.p01.b
execute if score @s wh_bag_unreg matches 3 run data remove storage warehouse:bags slots.p02.a
execute if score @s wh_bag_unreg matches 4 run data remove storage warehouse:bags slots.p02.b
execute if score @s wh_bag_unreg matches 5 run data remove storage warehouse:bags slots.p03.a
execute if score @s wh_bag_unreg matches 6 run data remove storage warehouse:bags slots.p03.b
execute if score @s wh_bag_unreg matches 7 run data remove storage warehouse:bags slots.p04.a
execute if score @s wh_bag_unreg matches 8 run data remove storage warehouse:bags slots.p04.b
execute if score @s wh_bag_unreg matches 9 run data remove storage warehouse:bags slots.p05.a
execute if score @s wh_bag_unreg matches 10 run data remove storage warehouse:bags slots.p05.b
scoreboard players set @s wh_bag_unreg 0
function warehouse:chunks/refresh
tellraw @s {"text":"[Warehouse] 已取消背包箱註冊；玩家與箱內物品保持不變。","color":"yellow"}
