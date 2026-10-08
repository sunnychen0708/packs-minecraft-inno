# Public API: insert plain items into Warehouse entry chest c00.
# Input macro: {item_id:"minecraft:stone",count:50}
# Output: storage warehouse:api result
data modify storage warehouse:api result set value {operation:"refund_item",ok:0b,complete:0b,requested:0,inserted:0,remaining:0,source_limit:64}
$data modify storage warehouse:api result.item_id set value "$(item_id)"
$scoreboard players set #api_requested wh_tmp $(count)
execute store result storage warehouse:api result.requested int 1 run scoreboard players get #api_requested wh_tmp
execute store result storage warehouse:api result.remaining int 1 run scoreboard players get #api_requested wh_tmp
execute unless score #api_requested wh_tmp matches 1.. run data modify storage warehouse:api result.error set value "invalid_count"
execute unless score #api_requested wh_tmp matches 1.. run return 0
execute unless data storage warehouse:chests c00{registered:1b,valid:1b} run data modify storage warehouse:api result.error set value "entry_unregistered"
execute unless data storage warehouse:chests c00{registered:1b,valid:1b} run return 0
$data modify storage warehouse:api work.refund set value {item_id:"$(item_id)",count:$(count)}
data modify storage warehouse:api work.refund.dimension set from storage warehouse:chests c00.dimension
data modify storage warehouse:api work.refund.a_x set from storage warehouse:chests c00.a_x
data modify storage warehouse:api work.refund.a_y set from storage warehouse:chests c00.a_y
data modify storage warehouse:api work.refund.a_z set from storage warehouse:chests c00.a_z
data modify storage warehouse:api work.refund.b_x set from storage warehouse:chests c00.b_x
data modify storage warehouse:api work.refund.b_y set from storage warehouse:chests c00.b_y
data modify storage warehouse:api work.refund.b_z set from storage warehouse:chests c00.b_z
return run function warehouse:api/internal/refund_entry with storage warehouse:api work.refund
