execute if block ~ ~ ~ #mcc:material_unsupported run scoreboard players set @s mcc_bpbad 1
execute if block ~ ~ ~ #mcc:material_unsupported run return 0
# The second half of a two-block item drops nothing; its material is counted on
# the other half (door lower half, bed head, double plant lower half).
execute if block ~ ~ ~ #minecraft:doors[half=upper] run return 0
execute if block ~ ~ ~ #minecraft:beds[part=foot] run return 0
execute if block ~ ~ ~ #mcc:material_free_upper_half[half=upper] run return 0
setblock 20008008 64 20008008 minecraft:barrel
loot replace block 20008008 64 20008008 container.0 27 mine ~ ~ ~ minecraft:netherite_pickaxe[minecraft:enchantments={"minecraft:silk_touch":1}]
data remove storage mcc:temp loot
data modify storage mcc:temp loot set from block 20008008 64 20008008 Items
setblock 20008008 64 20008008 air
execute unless data storage mcc:temp loot[0].id run scoreboard players set @s mcc_bpbad 1
execute if data storage mcc:temp loot[0].id run function mcc:materials/bom_consume_loot
return 1
