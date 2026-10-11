function warehouse:bag/check/both
execute unless score @s wh_bag_ok matches 2 run return run tellraw @s {"text":"[Warehouse] 背包箱或緩衝箱已遺失／未載入；沒有移動物品。","color":"red"}
function warehouse:bag/check/empty with storage warehouse:bags work.b
execute unless score @s wh_bag_ok matches 3 run return run tellraw @s {"text":"[Warehouse] 緩衝箱非空，請先清空；沒有移動物品。","color":"red"}
# B receives old main inventory; A becomes player inventory; B is copied to A through temporary NBT (also works if A/B are in different dimensions).
function warehouse:bag/transfer/player_to_box with storage warehouse:bags work.b
function warehouse:bag/transfer/box_to_player with storage warehouse:bags work.a
data modify storage warehouse:bags transfer set value {Items:[]}
function warehouse:bag/transfer/box_to_tmp with storage warehouse:bags work.b
function warehouse:bag/transfer/tmp_to_box with storage warehouse:bags work.a
function warehouse:bag/transfer/clear_box with storage warehouse:bags work.b
data remove storage warehouse:bags transfer
tellraw @s {"text":"[Warehouse] 個人背包已交換。","color":"yellow"}
