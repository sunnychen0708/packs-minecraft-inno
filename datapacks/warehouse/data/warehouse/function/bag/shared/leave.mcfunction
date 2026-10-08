function warehouse:bag/shared/prepare
function warehouse:bag/check/both
execute unless score @s wh_bag_ok matches 2 run return run tellraw @s {"text":"[Warehouse] 共用箱子已遺失／未載入，暫不歸還。","color":"red"}
function warehouse:bag/check/empty with storage warehouse:bags work.a
execute unless score @s wh_bag_ok matches 3 run return run tellraw @s {"text":"[Warehouse] 05-A 裡有其他人放的物品，先清空避免覆寫。","color":"red"}
function warehouse:bag/transfer/player_to_box with storage warehouse:bags work.a
function warehouse:bag/transfer/box_to_player with storage warehouse:bags work.b
function warehouse:bag/transfer/clear_box with storage warehouse:bags work.b
data remove storage warehouse:bags shared
tellraw @s {"text":"[Warehouse] 已歸還共用背包，返回原本的個人背包。","color":"yellow"}
