data remove storage warehouse:api work.inv
$execute in $(dimension) run data modify storage warehouse:api work.inv set from block $(x) $(y) $(z) Items
$data modify storage warehouse:api work.inv_ctx set value {item_id:"$(item_id)"}
execute if data storage warehouse:api work.inv[0].id run function warehouse:api/internal/count_inv_loop with storage warehouse:api work.inv_ctx
return 1
