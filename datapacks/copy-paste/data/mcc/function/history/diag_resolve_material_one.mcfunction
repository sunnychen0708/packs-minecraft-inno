$execute store result score #diag_need mcc_tmp run data get storage mcc:temp diag.need."$(id)"
setblock 20008008 64 20008008 minecraft:barrel
$loot replace block 20008008 64 20008008 container.0 27 mine $(sx) $(sy) $(sz) minecraft:netherite_pickaxe[minecraft:enchantments={"minecraft:silk_touch":1}]
data remove storage mcc:temp diag_loot
data modify storage mcc:temp diag_loot set from block 20008008 64 20008008 Items
setblock 20008008 64 20008008 air
execute if data storage mcc:temp diag_loot[0].id unless data storage mcc:temp diag_loot[1].id run data modify storage mcc:temp diag_item.material set from storage mcc:temp diag_loot[0].id
function mcc:history/diag_add_material with storage mcc:temp diag_item
return 1
