$execute if score @s mcc_bpdst matches 1 in minecraft:overworld as @e[type=minecraft:block_display,tag=mcc_bp_$(id)] at @s run tp @s ~$(dx) ~$(dy) ~$(dz)
$execute if score @s mcc_bpdst matches 2 in minecraft:the_nether as @e[type=minecraft:block_display,tag=mcc_bp_$(id)] at @s run tp @s ~$(dx) ~$(dy) ~$(dz)
$execute if score @s mcc_bpdst matches 3 in minecraft:the_end as @e[type=minecraft:block_display,tag=mcc_bp_$(id)] at @s run tp @s ~$(dx) ~$(dy) ~$(dz)
return 1
