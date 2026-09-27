execute if score #count su_tmp matches 32.. run return 0
execute unless items entity @s weapon.mainhand #minecraft:pickaxes run return 0
execute unless block ~ ~ ~ #survival_utils:ore/redstone run return 0
scoreboard players add #count su_tmp 1
loot spawn ~0.5 ~0.5 ~0.5 mine ~ ~ ~ mainhand
setblock ~ ~ ~ minecraft:air
function survival_utils:tool/damage_one
execute if score #count su_tmp matches ..31 positioned ~-1 ~-1 ~-1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~-1 ~ if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~-1 ~1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~ ~-1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~ ~ if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~ ~1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~1 ~-1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~1 ~ if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~-1 ~1 ~1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~ ~-1 ~-1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~ ~-1 ~ if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~ ~-1 ~1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~ ~ ~-1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~ ~ ~1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~ ~1 ~-1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~ ~1 ~ if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~ ~1 ~1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~1 ~-1 ~-1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~1 ~-1 ~ if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~1 ~-1 ~1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~1 ~ ~-1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~1 ~ ~ if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~1 ~ ~1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~1 ~1 ~-1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~1 ~1 ~ if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
execute if score #count su_tmp matches ..31 positioned ~1 ~1 ~1 if block ~ ~ ~ #survival_utils:ore/redstone run function survival_utils:vein/redstone/break
