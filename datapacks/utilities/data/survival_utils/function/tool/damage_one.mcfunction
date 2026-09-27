# Charge one durability point, respecting creative mode, Unbreakable and Unbreaking.
execute if entity @s[gamemode=creative] run return 0
execute unless items entity @s weapon.mainhand *[minecraft:damage] run return 0
execute if items entity @s weapon.mainhand *[minecraft:unbreakable] run return 0
data modify storage survival_utils:tool item set value {}
data modify storage survival_utils:tool item set from entity @s SelectedItem
# Equipment fallback also allows testing with non-player living entities.
execute unless data storage survival_utils:tool item.id run data modify storage survival_utils:tool item set from entity @s equipment.mainhand
data modify storage survival_utils:tool args set value {unbreaking:0,damage:0}
data modify storage survival_utils:tool args.unbreaking set from storage survival_utils:tool item.components."minecraft:enchantments"."minecraft:unbreaking"
function survival_utils:tool/roll_damage with storage survival_utils:tool args
execute unless score #wear su_tmp matches 0 run return 0
# Loot modifiers do not automatically destroy tools at zero remaining durability.
execute if items entity @s weapon.mainhand *[minecraft:damage~{durability:{max:1}}] run return run item replace entity @s weapon.mainhand with minecraft:air
scoreboard players set #damage su_tmp 0
execute store result score #damage su_tmp run data get storage survival_utils:tool item.components."minecraft:damage"
scoreboard players add #damage su_tmp 1
execute store result storage survival_utils:tool args.damage int 1 run scoreboard players get #damage su_tmp
function survival_utils:tool/set_damage with storage survival_utils:tool args
