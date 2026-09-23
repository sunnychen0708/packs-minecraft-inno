tag @s add su_crop_actor
execute if score @s su_crop matches 1 as @e[type=minecraft:item,distance=..6,sort=nearest] at @s if items entity @s contents minecraft:wheat_seeds if block ~ ~ ~ minecraft:air if block ~ ~-1 ~ minecraft:farmland run function survival_utils:crop/place/wheat
execute if score @s su_crop matches 2 as @e[type=minecraft:item,distance=..6,sort=nearest] at @s if items entity @s contents minecraft:carrot if block ~ ~ ~ minecraft:air if block ~ ~-1 ~ minecraft:farmland run function survival_utils:crop/place/carrot
execute if score @s su_crop matches 3 as @e[type=minecraft:item,distance=..6,sort=nearest] at @s if items entity @s contents minecraft:potato if block ~ ~ ~ minecraft:air if block ~ ~-1 ~ minecraft:farmland run function survival_utils:crop/place/potato
execute if score @s su_crop matches 4 as @e[type=minecraft:item,distance=..6,sort=nearest] at @s if items entity @s contents minecraft:beetroot_seeds if block ~ ~ ~ minecraft:air if block ~ ~-1 ~ minecraft:farmland run function survival_utils:crop/place/beetroot
execute if score @s su_crop matches 5 as @e[type=minecraft:item,distance=..6,sort=nearest] at @s if items entity @s contents minecraft:nether_wart if block ~ ~ ~ minecraft:air if block ~ ~-1 ~ minecraft:soul_sand run function survival_utils:crop/place/wart
tag @s remove su_crop_actor
