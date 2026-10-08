tag @s remove wh_bag_reg_pending
scoreboard players operation @s wh_bag_target = @s wh_bag_reg
scoreboard players set @s wh_bag_reg 0
scoreboard players set @s wh_bag_ok 0
execute if score @s wh_bag_target matches 1 if entity @s[name=SunnyChen] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_target matches 2 if entity @s[name=SunnyChen] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_target matches 3 if entity @s[name=penguin0531] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_target matches 4 if entity @s[name=penguin0531] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_target matches 5 if entity @s[name=geena0701] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_target matches 6 if entity @s[name=geena0701] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_target matches 7 if entity @s[name=Felicitypeng] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_target matches 8 if entity @s[name=Felicitypeng] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_target matches 9 if entity @s[name=SunnyChen] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_target matches 10 if entity @s[name=SunnyChen] run scoreboard players set @s wh_bag_ok 1
execute if score @s wh_bag_ok matches 0 run return run tellraw @s {"text":"[Warehouse] 你無權註冊這個背包箱。","color":"red"}
execute if score @s wh_bag_target matches 9..10 if data storage warehouse:bags shared{active:1b} run return run tellraw @s {"text":"[Warehouse] 共用背包使用中，禁止更換 05 箱。","color":"red"}
tag @s remove wh_reg_pending
tag @s add wh_bag_reg_pending
tellraw @s {"text":"[Warehouse] 註冊模式：請對準要綁定的小箱子按右鍵（約 6 格內），直接替換原綁定。","color":"yellow"}
