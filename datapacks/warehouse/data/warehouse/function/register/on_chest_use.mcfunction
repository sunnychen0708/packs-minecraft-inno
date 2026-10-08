scoreboard players set @s wh_ray 0
execute anchored eyes positioned ^ ^ ^0.25 run function warehouse:register/raycast
execute if entity @s[tag=wh_reg_pending] run dialog show @s warehouse:register/result/error_raycast
tag @s remove wh_reg_pending
