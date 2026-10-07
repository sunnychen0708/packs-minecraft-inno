execute store result score #cmp_ex mcc_id run data get storage mcc:temp cmp.ex
execute store result score #cmp_ez mcc_id run data get storage mcc:temp cmp.ez
execute store result score #cmp_cx mcc_id run data get storage mcc:temp cmp.cx
execute store result score #cmp_cz mcc_id run data get storage mcc:temp cmp.cz
scoreboard players set @s mcc_dx 0
scoreboard players set @s mcc_dy 0
scoreboard players set @s mcc_dz 0
scoreboard players set @s mcc_ok 1
scoreboard players set @s mcc_cmpaxis 1
execute if score @s mcc_fsz > @s mcc_fsx if score @s mcc_fsz > @s mcc_sy run scoreboard players set @s mcc_cmpaxis 3
execute unless score @s mcc_cmpaxis matches 3 if score @s mcc_sy > @s mcc_fsx run scoreboard players set @s mcc_cmpaxis 2
execute if score @s mcc_cmpaxis matches 1 run return run function mcc:history/compare_hidden_x_loop
execute if score @s mcc_cmpaxis matches 2 run return run function mcc:history/compare_hidden_y_loop
return run function mcc:history/compare_hidden_z_loop
