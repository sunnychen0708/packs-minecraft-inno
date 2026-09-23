execute if block ~ ~ ~ #warehouse:storage_chests run function warehouse:read/hit
execute unless block ~ ~ ~ #warehouse:storage_chests if score @s wh_ray matches ..23 run scoreboard players add @s wh_ray 1
execute unless block ~ ~ ~ #warehouse:storage_chests if score @s wh_ray matches ..23 positioned ^ ^ ^0.25 run function warehouse:read/raycast
