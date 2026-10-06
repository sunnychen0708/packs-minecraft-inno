# Returns 1 only when the mainhand pickaxe may harvest the block at ~ ~ ~, using the vanilla
# incorrect_for_*_tool tags. `loot ... mine` ignores tool tier, so this is the only tier gate.
# Unknown tools fail closed, which stops the chain without removing anything.
execute if items entity @s weapon.mainhand minecraft:netherite_pickaxe unless block ~ ~ ~ #minecraft:incorrect_for_netherite_tool run return 1
execute if items entity @s weapon.mainhand minecraft:diamond_pickaxe unless block ~ ~ ~ #minecraft:incorrect_for_diamond_tool run return 1
execute if items entity @s weapon.mainhand minecraft:iron_pickaxe unless block ~ ~ ~ #minecraft:incorrect_for_iron_tool run return 1
execute if items entity @s weapon.mainhand minecraft:copper_pickaxe unless block ~ ~ ~ #minecraft:incorrect_for_copper_tool run return 1
execute if items entity @s weapon.mainhand minecraft:stone_pickaxe unless block ~ ~ ~ #minecraft:incorrect_for_stone_tool run return 1
execute if items entity @s weapon.mainhand minecraft:golden_pickaxe unless block ~ ~ ~ #minecraft:incorrect_for_gold_tool run return 1
execute if items entity @s weapon.mainhand minecraft:wooden_pickaxe unless block ~ ~ ~ #minecraft:incorrect_for_wooden_tool run return 1
return 0
