# #fit = how many $(item_id) the player's main inventory (slots 0-35) can still take.
scoreboard players set #fit mcc_tmp 0
execute unless entity @s[type=minecraft:player] run return 0
scoreboard players set #max mcc_tmp 64
$execute if data storage mcc:names max."$(item_id)" store result score #max mcc_tmp run data get storage mcc:names max."$(item_id)"
execute store result score #occ mcc_tmp run data get entity @s Inventory
scoreboard players set #fit mcc_tmp 36
scoreboard players operation #fit mcc_tmp -= #occ mcc_tmp
scoreboard players operation #fit mcc_tmp *= #max mcc_tmp
data modify storage mcc:temp invsel set value []
$data modify storage mcc:temp invsel append from entity @s Inventory[{id:"$(item_id)"}]
data remove storage mcc:temp invsel[{components:{}}]
function mcc:materials/inv_fit_loop
return 1
