scoreboard players set #api_aforced wh_tmp 0
scoreboard players set #api_bforced wh_tmp 0
$execute in $(dimension) store success score #api_aforced wh_tmp run forceload query $(a_x) $(a_z)
$execute if score #api_aforced wh_tmp matches 0 in $(dimension) run forceload add $(a_x) $(a_z)
$execute in $(dimension) store success score #api_bforced wh_tmp run forceload query $(b_x) $(b_z)
$execute if score #api_bforced wh_tmp matches 0 in $(dimension) run forceload add $(b_x) $(b_z)
$data modify storage warehouse:api work.refund_cleanup set value {dimension:"$(dimension)",a_x:$(a_x),a_z:$(a_z),b_x:$(b_x),b_z:$(b_z)}

scoreboard players set #api_plain wh_tmp 0
scoreboard players set #api_sourceok wh_tmp 1
# The entry chest is usable as soon as block commands can access it; `execute if loaded` is stricter than needed.
$execute in $(dimension) unless block $(a_x) $(a_y) $(a_z) #warehouse:storage_chests run scoreboard players set #api_sourceok wh_tmp 0
$execute in $(dimension) unless block $(b_x) $(b_y) $(b_z) #warehouse:storage_chests run scoreboard players set #api_sourceok wh_tmp 0
execute unless score #api_sourceok wh_tmp matches 1 run data modify storage warehouse:api result.error set value "entry_stale"
execute unless score #api_sourceok wh_tmp matches 1 run function warehouse:api/internal/refund_cleanup with storage warehouse:api work.refund_cleanup
execute unless score #api_sourceok wh_tmp matches 1 run return 0

$function warehouse:api/internal/probe_max_stack {item_id:"$(item_id)"}
data modify storage warehouse:runtime move set value {stack:{components:{}},components:{}}
$data modify storage warehouse:runtime move.stack.id set value "$(item_id)"
$data modify storage warehouse:runtime move.stack.count set value $(count)
$data modify storage warehouse:runtime move.item_id set value "$(item_id)"
$data modify storage warehouse:runtime move.count set value $(count)
$data modify storage warehouse:runtime move.dest_dimension set value "$(dimension)"
$data modify storage warehouse:runtime move.dest_a_x set value $(a_x)
$data modify storage warehouse:runtime move.dest_a_y set value $(a_y)
$data modify storage warehouse:runtime move.dest_a_z set value $(a_z)
$data modify storage warehouse:runtime move.dest_b_x set value $(b_x)
$data modify storage warehouse:runtime move.dest_b_y set value $(b_y)
$data modify storage warehouse:runtime move.dest_b_z set value $(b_z)
$scoreboard players set #remaining wh_tmp $(count)
scoreboard players set #moved wh_tmp 0
scoreboard players set #main_ok wh_tmp 0
scoreboard players set #compact wh_tmp 0
scoreboard players operation #max wh_tmp = #api_max wh_tmp
# Strict mode prevents a plain refund from merging into a custom-component stack.
scoreboard players set #api_plain wh_tmp 1
# c00 was force-loaded and its physical blocks were validated above; bypass the generic loaded gate.
function warehouse:sort/transport/main_valid with storage warehouse:runtime move
scoreboard players set #api_plain wh_tmp 0

execute store result storage warehouse:api result.inserted int 1 run scoreboard players get #moved wh_tmp
execute store result storage warehouse:api result.remaining int 1 run scoreboard players get #remaining wh_tmp
execute if score #main_ok wh_tmp matches 1 if score #remaining wh_tmp matches 0 run data modify storage warehouse:api result.ok set value 1b
execute if score #main_ok wh_tmp matches 1 if score #remaining wh_tmp matches 0 run data modify storage warehouse:api result.complete set value 1b
execute if score #main_ok wh_tmp matches 1 if score #remaining wh_tmp matches 1.. run data modify storage warehouse:api result.error set value "entry_full"
execute unless score #main_ok wh_tmp matches 1 run data modify storage warehouse:api result.error set value "entry_unavailable"
function warehouse:api/internal/refund_cleanup with storage warehouse:api work.refund_cleanup
execute if data storage warehouse:api result{ok:1b} run return 1
return 0
