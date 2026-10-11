$execute in $(dimension) if items block $(x) $(y) $(z) container.* * run scoreboard players set @s wh_bag_ok 0
execute if score @s wh_bag_ok matches 0 run tellraw @s {"text":"[Warehouse] B 緩衝箱必須是空的才能註冊。","color":"red"}
