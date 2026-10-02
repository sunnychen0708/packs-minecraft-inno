execute unless data storage warehouse:api work.inv[0].id run return 0
data modify storage warehouse:api work.stack set from storage warehouse:api work.inv[0]
data modify storage warehouse:api work.stack.item_id set from storage warehouse:api work.inv_ctx.item_id
function warehouse:api/internal/count_stack with storage warehouse:api work.stack
data remove storage warehouse:api work.inv[0]
execute if data storage warehouse:api work.inv[0].id run return run function warehouse:api/internal/count_inv_loop with storage warehouse:api work.inv_ctx
return 1
