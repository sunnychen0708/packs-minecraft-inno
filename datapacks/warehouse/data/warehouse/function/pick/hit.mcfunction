function warehouse:api/resolve_block
execute unless data storage warehouse:api result{ok:1b} run tellraw @s [{"text":"[Warehouse] ","color":"gold"},{"text":"這個方塊目前無法安全解析成可從倉庫取出的生存物品。","color":"yellow"}]
execute unless data storage warehouse:api result{ok:1b} run return fail
data modify storage warehouse:pick request set value {item_id:"",max_stack:0,count:0}
data modify storage warehouse:pick request.item_id set from storage warehouse:api result.item_id
data modify storage warehouse:pick request.max_stack set from storage warehouse:api result.max_stack
return run function warehouse:pick/withdraw with storage warehouse:pick request
