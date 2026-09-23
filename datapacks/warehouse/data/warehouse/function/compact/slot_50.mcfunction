$execute in $(dimension) unless loaded $(b_x) $(b_y) $(b_z) run return 0
$execute in $(dimension) unless items block $(b_x) $(b_y) $(b_z) container.23 * run return 0
scoreboard players set #max wh_tmp 64
$execute in $(dimension) if items block $(b_x) $(b_y) $(b_z) container.23 *[minecraft:max_stack_size=16] run scoreboard players set #max wh_tmp 16
$execute in $(dimension) if items block $(b_x) $(b_y) $(b_z) container.23 *[minecraft:max_stack_size=1] run scoreboard players set #max wh_tmp 1
execute if score #max wh_tmp matches 1 run return 0
data remove storage warehouse:runtime move
$data modify storage warehouse:runtime move.stack set from block $(b_x) $(b_y) $(b_z) Items[{Slot:23b}]
execute unless data storage warehouse:runtime move.stack run return 0
data remove storage warehouse:runtime move.stack.Slot
execute unless data storage warehouse:runtime move.stack.components run data modify storage warehouse:runtime move.stack.components set value {}
data modify storage warehouse:runtime move.item_id set from storage warehouse:runtime move.stack.id
data modify storage warehouse:runtime move.components set from storage warehouse:runtime move.stack.components
data modify storage warehouse:runtime move.count set from storage warehouse:runtime move.stack.count
execute if data storage warehouse:runtime move.stack.components."minecraft:max_stack_size" store result score #max wh_tmp run data get storage warehouse:runtime move.stack.components."minecraft:max_stack_size"
execute store result score #remaining wh_tmp run data get storage warehouse:runtime move.count
scoreboard players set #moved wh_tmp 0
scoreboard players set #compact wh_tmp 1
scoreboard players set #compact_src wh_tmp 50
$data modify storage warehouse:runtime move.dest_dimension set value "$(dimension)"
$data modify storage warehouse:runtime move.dest_a_x set value $(a_x)
$data modify storage warehouse:runtime move.dest_a_y set value $(a_y)
$data modify storage warehouse:runtime move.dest_a_z set value $(a_z)
$data modify storage warehouse:runtime move.dest_b_x set value $(b_x)
$data modify storage warehouse:runtime move.dest_b_y set value $(b_y)
$data modify storage warehouse:runtime move.dest_b_z set value $(b_z)
function warehouse:sort/transport/main_merge with storage warehouse:runtime move
scoreboard players set #compact wh_tmp 0
$execute if score #moved wh_tmp matches 1.. if score #remaining wh_tmp matches 0 in $(dimension) run item replace block $(b_x) $(b_y) $(b_z) container.23 with minecraft:air
$execute if score #moved wh_tmp matches 1.. if score #remaining wh_tmp matches 1.. in $(dimension) store result block $(b_x) $(b_y) $(b_z) Items[{Slot:23b}].count int 1 run scoreboard players get #remaining wh_tmp
