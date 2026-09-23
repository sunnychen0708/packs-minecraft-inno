execute unless data storage warehouse:chests c23{registered:1b,valid:1b} run return 0
data remove storage warehouse:runtime move
$data modify storage warehouse:runtime move.stack set from block $(x) $(y) $(z) Items[{Slot:$(slot)b}]
execute unless data storage warehouse:runtime move.stack run return 0
data remove storage warehouse:runtime move.stack.Slot
execute unless data storage warehouse:runtime move.stack.count run data modify storage warehouse:runtime move.stack.count set value 1
execute unless data storage warehouse:runtime move.stack.components run data modify storage warehouse:runtime move.stack.components set value {}
data modify storage warehouse:runtime move.item_id set from storage warehouse:runtime move.stack.id
data modify storage warehouse:runtime move.components set from storage warehouse:runtime move.stack.components
data modify storage warehouse:runtime move.count set from storage warehouse:runtime move.stack.count
$data modify storage warehouse:runtime move.src_dimension set value "$(dimension)"
$data modify storage warehouse:runtime move.src_x set value $(x)
$data modify storage warehouse:runtime move.src_y set value $(y)
$data modify storage warehouse:runtime move.src_z set value $(z)
$data modify storage warehouse:runtime move.src_slot set value $(slot)
data modify storage warehouse:runtime move.dest_dimension set from storage warehouse:chests c23.dimension
data modify storage warehouse:runtime move.dest_a_x set from storage warehouse:chests c23.a_x
data modify storage warehouse:runtime move.dest_a_y set from storage warehouse:chests c23.a_y
data modify storage warehouse:runtime move.dest_a_z set from storage warehouse:chests c23.a_z
data modify storage warehouse:runtime move.dest_b_x set from storage warehouse:chests c23.b_x
data modify storage warehouse:runtime move.dest_b_y set from storage warehouse:chests c23.b_y
data modify storage warehouse:runtime move.dest_b_z set from storage warehouse:chests c23.b_z
data modify storage warehouse:runtime move.ov_dimension set from storage warehouse:chests c20.dimension
data modify storage warehouse:runtime move.ov_a_x set from storage warehouse:chests c20.a_x
data modify storage warehouse:runtime move.ov_a_y set from storage warehouse:chests c20.a_y
data modify storage warehouse:runtime move.ov_a_z set from storage warehouse:chests c20.a_z
data modify storage warehouse:runtime move.ov_b_x set from storage warehouse:chests c20.b_x
data modify storage warehouse:runtime move.ov_b_y set from storage warehouse:chests c20.b_y
data modify storage warehouse:runtime move.ov_b_z set from storage warehouse:chests c20.b_z
execute if data storage warehouse:chests c20{registered:1b,valid:1b} run data modify storage warehouse:runtime move.ov_ok set value 1b
execute unless data storage warehouse:chests c20{registered:1b,valid:1b} run data modify storage warehouse:runtime move.ov_ok set value 0b
function warehouse:sort/transport/start with storage warehouse:runtime move
