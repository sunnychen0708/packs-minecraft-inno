execute unless data storage warehouse:bags slots.p05.a{registered:1b} run return run tellraw @s {"text":"[Warehouse] 共用背包 05-A 尚未註冊。","color":"red"}
execute unless data storage warehouse:bags slots.p05.b{registered:1b} run return run tellraw @s {"text":"[Warehouse] 共用暫存 05-B 尚未註冊。","color":"red"}
function warehouse:bag/shared/prepare
function warehouse:bag/check/both
execute unless score @s wh_bag_ok matches 2 run return run tellraw @s {"text":"[Warehouse] 共用箱子已遺失／未載入。","color":"red"}
function warehouse:bag/check/empty with storage warehouse:bags work.b
execute unless score @s wh_bag_ok matches 3 run return run tellraw @s {"text":"[Warehouse] 05-B 暫存箱不是空的，停止切換。","color":"red"}
function warehouse:bag/transfer/player_to_box with storage warehouse:bags work.b
function warehouse:bag/transfer/box_to_player with storage warehouse:bags work.a
function warehouse:bag/transfer/clear_box with storage warehouse:bags work.a
data modify storage warehouse:bags shared set value {active:1b}
execute store result storage warehouse:bags shared.owner int 1 run scoreboard players get @s wh_bag_id
tellraw @s {"text":"[Warehouse] 已切換至共用背包；再次輸入 /trigger sbag 可返回。","color":"yellow"}
