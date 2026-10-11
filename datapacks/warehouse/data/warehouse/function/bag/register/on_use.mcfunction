scoreboard players set @s wh_bag_ray 0
execute anchored eyes positioned ^ ^ ^0.25 run function warehouse:bag/register/raycast
execute if entity @s[tag=wh_bag_reg_pending] run tellraw @s {"text":"[Warehouse] 沒有對準可註冊的單一小箱。","color":"red"}
tag @s remove wh_bag_reg_pending
