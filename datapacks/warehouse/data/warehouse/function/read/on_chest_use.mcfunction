scoreboard players set @s wh_ray 0
execute anchored eyes positioned ^ ^ ^0.25 run function warehouse:read/raycast
execute if entity @s[tag=wh_read_pending] run dialog show @s warehouse:read/error_raycast
tag @s remove wh_read_pending
