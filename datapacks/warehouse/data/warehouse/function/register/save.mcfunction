execute if score @s wh_target matches 0 run function warehouse:register/save_00 with storage warehouse:runtime candidate
execute unless score @s wh_target matches 0 run function warehouse:register/save_nonzero with storage warehouse:runtime candidate
