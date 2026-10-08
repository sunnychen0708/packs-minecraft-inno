# Public API: resolve the block at the current execution position to its survival item form.
# Call in the target dimension and positioned at the target block.
# Output: storage warehouse:api result {operation:"resolve_block",ok,complete,item_id,max_stack}
data modify storage warehouse:api result set value {operation:"resolve_block",ok:0b,complete:1b,max_stack:0}
execute if block ~ ~ ~ #minecraft:air run data modify storage warehouse:api result.error set value "no_block"
execute if block ~ ~ ~ #minecraft:air run return 0

kill @e[type=minecraft:armor_stand,tag=wh_resolve_probe,distance=..2]
summon minecraft:armor_stand ~ ~ ~ {Tags:["wh_resolve_probe"],Invisible:1b,NoGravity:1b,Invulnerable:1b}
loot replace entity @e[type=minecraft:armor_stand,tag=wh_resolve_probe,distance=..2,limit=1,sort=nearest] weapon.mainhand mine ~ ~ ~ minecraft:netherite_pickaxe[minecraft:enchantments={"minecraft:silk_touch":1}]
data modify storage warehouse:api result.item_id set from entity @e[type=minecraft:armor_stand,tag=wh_resolve_probe,distance=..2,limit=1,sort=nearest] equipment.mainhand.id
kill @e[type=minecraft:armor_stand,tag=wh_resolve_probe,distance=..2]
execute unless data storage warehouse:api result.item_id run data modify storage warehouse:api result.error set value "no_survival_item"
execute unless data storage warehouse:api result.item_id run return 0

function warehouse:api/internal/probe_max_stack with storage warehouse:api result
execute store result storage warehouse:api result.max_stack int 1 run scoreboard players get #api_max wh_tmp
data modify storage warehouse:api result.ok set value 1b
return 1
