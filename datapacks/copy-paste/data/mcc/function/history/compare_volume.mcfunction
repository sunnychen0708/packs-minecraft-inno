scoreboard players operation #cmp_vol mcc_id = @s mcc_fsx
scoreboard players operation #cmp_vol mcc_id *= @s mcc_sy
scoreboard players operation #cmp_vol mcc_id *= @s mcc_fsz
execute if score #cmp_vol mcc_id > #cmp_vol_max mcc_id run scoreboard players set #cmp_big mcc_id 1
