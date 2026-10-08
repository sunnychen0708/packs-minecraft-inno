execute unless score #api_remaining wh_tmp matches 1.. run return 1
execute unless data storage warehouse:api work.inv[0].id run return 0
data modify storage warehouse:api work.stack set from storage warehouse:api work.inv[0]
execute unless data storage warehouse:api work.stack.components run data modify storage warehouse:api work.stack.components set value {}
execute store result storage warehouse:api work.stack.api_slot int 1 run data get storage warehouse:api work.stack.Slot
$data modify storage warehouse:api work.stack.dimension set value "$(dimension)"
$data modify storage warehouse:api work.stack.x set value $(x)
$data modify storage warehouse:api work.stack.y set value $(y)
$data modify storage warehouse:api work.stack.z set value $(z)
$data modify storage warehouse:api work.stack.item_id set value "$(item_id)"
function warehouse:api/internal/take_stack with storage warehouse:api work.stack
data remove storage warehouse:api work.inv[0]
execute if score #api_remaining wh_tmp matches 1.. if data storage warehouse:api work.inv[0].id run return run function warehouse:api/internal/take_inv_loop with storage warehouse:api work.inv_ctx
return 1
