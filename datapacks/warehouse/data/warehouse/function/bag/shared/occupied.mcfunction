execute store result score #bag_owner wh_tmp run data get storage warehouse:bags shared.owner
execute unless score @s wh_bag_id = #bag_owner wh_tmp run return run tellraw @s {"text":"[Warehouse] 共用背包目前有人使用。","color":"red"}
function warehouse:bag/shared/leave
