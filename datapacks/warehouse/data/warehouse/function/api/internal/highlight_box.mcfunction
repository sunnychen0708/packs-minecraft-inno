# Player-only Highlight burst. The coordinates are also printed so remote/cross-dimension boxes remain locatable.
$tellraw @s [{"text":"[Warehouse] Highlight ","color":"aqua"},{"text":"c$(code)","color":"yellow"},{"text":"  $(dimension)  A($(a_x), $(a_y), $(a_z))  B($(b_x), $(b_y), $(b_z))","color":"gray"}]
$execute in $(dimension) positioned $(a_x) $(a_y) $(a_z) run particle minecraft:end_rod ~0.5 ~0.15 ~0.5 0.45 0.10 0.45 0.01 24 force @s
$execute in $(dimension) positioned $(a_x) $(a_y) $(a_z) run particle minecraft:end_rod ~0.5 ~0.85 ~0.5 0.45 0.10 0.45 0.01 24 force @s
$execute in $(dimension) positioned $(b_x) $(b_y) $(b_z) run particle minecraft:end_rod ~0.5 ~0.15 ~0.5 0.45 0.10 0.45 0.01 24 force @s
$execute in $(dimension) positioned $(b_x) $(b_y) $(b_z) run particle minecraft:end_rod ~0.5 ~0.85 ~0.5 0.45 0.10 0.45 0.01 24 force @s
return 1
