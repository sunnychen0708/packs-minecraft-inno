data remove storage warehouse:api work.inv
$data modify storage warehouse:api work.inv set from block $(x) $(y) $(z) Items
$data modify storage warehouse:api work.inv_ctx set value {dimension:"$(dimension)",x:$(x),y:$(y),z:$(z),item_id:"$(item_id)"}
execute if data storage warehouse:api work.inv[0].id if score #api_remaining wh_tmp matches 1.. run function warehouse:api/internal/take_inv_loop with storage warehouse:api work.inv_ctx
return 1
