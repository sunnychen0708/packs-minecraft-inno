scoreboard players set @s wh_tmp 0
$execute in $(dimension) positioned $(a_x) $(a_y) $(a_z) if entity @e[type=minecraft:marker,tag=wh_reg_tmp,distance=..0.1] run scoreboard players set @s wh_tmp 1
$execute in $(dimension) positioned $(b_x) $(b_y) $(b_z) if entity @e[type=minecraft:marker,tag=wh_reg_tmp,distance=..0.1] run scoreboard players set @s wh_tmp 1
execute if score @s wh_tmp matches 1 run function warehouse:read/add_37
