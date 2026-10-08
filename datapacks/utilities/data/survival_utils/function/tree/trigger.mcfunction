execute unless score @s su_tree matches 1 run return 0
execute unless predicate survival_utils:is_sneaking run return 0
execute unless items entity @s weapon.mainhand #minecraft:axes run return 0
tag @s add su_chain_actor
scoreboard players set #ray su_tmp 0
scoreboard players set #found su_tmp 0
scoreboard players set #count su_tmp 0
execute anchored eyes positioned ^ ^ ^0.5 run function survival_utils:tree/raycast
execute if score #count su_tmp matches 1.. run title @s actionbar [{"text":"連鎖砍樹：","color":"green"},{"score":{"name":"#count","objective":"su_tmp"},"color":"white"},{"text":" 根","color":"gray"}]
tag @s remove su_chain_actor
