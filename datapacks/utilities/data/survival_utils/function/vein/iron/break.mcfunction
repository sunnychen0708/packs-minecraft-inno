execute if score #count su_tmp matches 32.. run return 0
execute unless block ~ ~ ~ #survival_utils:ore/iron run return 0
execute unless function survival_utils:vein/tool_ok run return 0
scoreboard players add #count su_tmp 1
loot spawn ~0.5 ~0.5 ~0.5 mine ~ ~ ~ mainhand
setblock ~ ~ ~ minecraft:air
item modify entity @s weapon.mainhand survival_utils:damage_one
execute if score #count su_tmp matches ..31 positioned ~-1 ~-1 ~-1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~-1 ~ if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~-1 ~1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~ ~-1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~ ~ if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~ ~1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~1 ~-1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~1 ~ if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~1 ~1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~ ~-1 ~-1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~ ~-1 ~ if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~ ~-1 ~1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~ ~ ~-1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~ ~ ~1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~ ~1 ~-1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~ ~1 ~ if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~ ~1 ~1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~1 ~-1 ~-1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~1 ~-1 ~ if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~1 ~-1 ~1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~1 ~ ~-1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~1 ~ ~ if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~1 ~ ~1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~1 ~1 ~-1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~1 ~1 ~ if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
execute if score #count su_tmp matches ..31 positioned ~1 ~1 ~1 if block ~ ~ ~ #survival_utils:ore/iron run function survival_utils:vein/iron/break
