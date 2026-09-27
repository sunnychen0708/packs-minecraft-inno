execute if score #count su_tmp matches 64.. run return 0
execute unless items entity @s weapon.mainhand #minecraft:axes run return 0
execute unless block ~ ~ ~ #survival_utils:natural_logs run return 0
scoreboard players add #count su_tmp 1
loot spawn ~0.5 ~0.5 ~0.5 mine ~ ~ ~ mainhand
setblock ~ ~ ~ minecraft:air
item modify entity @s weapon.mainhand survival_utils:damage_one
execute if score #count su_tmp matches ..63 positioned ~-1 ~ ~-1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~-1 ~ ~ if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~-1 ~ ~1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~ ~ ~-1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~ ~ ~1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~1 ~ ~-1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~1 ~ ~ if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~1 ~ ~1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~-1 ~1 ~-1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~-1 ~1 ~ if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~-1 ~1 ~1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~ ~1 ~-1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~ ~1 ~ if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~ ~1 ~1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~1 ~1 ~-1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~1 ~1 ~ if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
execute if score #count su_tmp matches ..63 positioned ~1 ~1 ~1 if block ~ ~ ~ #survival_utils:natural_logs run function survival_utils:tree/break
