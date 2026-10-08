execute if block ~ ~ ~ #warehouse:storage_chests[type=single] run return run function warehouse:bag/register/hit
execute if score @s wh_bag_ray matches 24.. run return 0
scoreboard players add @s wh_bag_ray 1
execute positioned ^ ^ ^0.25 run function warehouse:bag/register/raycast
