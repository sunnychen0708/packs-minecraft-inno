# Public API: atomically remove count plain items from shared Warehouse material sources.
# Input macro: {item_id:"minecraft:stone",count:50}
# Output: storage warehouse:api result
$scoreboard players set #api_requested wh_tmp $(count)
data modify storage warehouse:api result set value {operation:"take_item",ok:0b,complete:0b,requested:0,taken:0,remaining:0,available:0,sources_scanned:0,stale_sources:0,source_limit:64}
$data modify storage warehouse:api result.item_id set value "$(item_id)"
execute store result storage warehouse:api result.requested int 1 run scoreboard players get #api_requested wh_tmp
execute store result storage warehouse:api result.remaining int 1 run scoreboard players get #api_requested wh_tmp
execute unless score #api_requested wh_tmp matches 1.. run data modify storage warehouse:api result.error set value "invalid_count"
execute unless score #api_requested wh_tmp matches 1.. run return 0

# Preflight uses the exact same plain-stack rules and refreshes the deduplicated source snapshot.
$function warehouse:api/count_item {item_id:"$(item_id)"}
scoreboard players operation #api_available wh_tmp = #api_total wh_tmp
scoreboard players operation #api_pre_sources wh_tmp = #api_sources wh_tmp
scoreboard players operation #api_pre_stale wh_tmp = #api_stale wh_tmp
scoreboard players set #api_preflight wh_tmp 0
execute if data storage warehouse:api result{ok:1b,complete:1b} run scoreboard players set #api_preflight wh_tmp 1

# Rebuild the take result after the count endpoint used the shared result object.
data modify storage warehouse:api result set value {operation:"take_item",ok:0b,complete:0b,requested:0,taken:0,remaining:0,available:0,sources_scanned:0,stale_sources:0,source_limit:64}
$data modify storage warehouse:api result.item_id set value "$(item_id)"
execute store result storage warehouse:api result.requested int 1 run scoreboard players get #api_requested wh_tmp
execute store result storage warehouse:api result.remaining int 1 run scoreboard players get #api_requested wh_tmp
execute store result storage warehouse:api result.available int 1 run scoreboard players get #api_available wh_tmp
execute store result storage warehouse:api result.sources_scanned int 1 run scoreboard players get #api_pre_sources wh_tmp
execute store result storage warehouse:api result.stale_sources int 1 run scoreboard players get #api_pre_stale wh_tmp

execute unless score #api_preflight wh_tmp matches 1 run data modify storage warehouse:api result.error set value "source_unavailable"
execute unless score #api_preflight wh_tmp matches 1 run return 0
execute if score #api_available wh_tmp < #api_requested wh_tmp run data modify storage warehouse:api result.error set value "insufficient_stock"
execute if score #api_available wh_tmp < #api_requested wh_tmp run return 0

# Count + withdrawal are one synchronous function call, so no other tick/player action can interleave.
data modify storage warehouse:api work set value {queue:[],item_id:""}
$data modify storage warehouse:api work.item_id set value "$(item_id)"
data modify storage warehouse:api work.queue set from storage warehouse:api material_sources
scoreboard players operation #api_remaining wh_tmp = #api_requested wh_tmp
scoreboard players set #api_taken wh_tmp 0
scoreboard players set #api_sources wh_tmp 0
scoreboard players set #api_stale wh_tmp 0
function warehouse:api/internal/take_next
execute store result storage warehouse:api result.taken int 1 run scoreboard players get #api_taken wh_tmp
execute store result storage warehouse:api result.remaining int 1 run scoreboard players get #api_remaining wh_tmp
execute store result storage warehouse:api result.sources_scanned int 1 run scoreboard players get #api_sources wh_tmp
execute store result storage warehouse:api result.stale_sources int 1 run scoreboard players get #api_stale wh_tmp
execute if score #api_remaining wh_tmp matches 0 run data modify storage warehouse:api result.ok set value 1b
execute if score #api_remaining wh_tmp matches 0 run data modify storage warehouse:api result.complete set value 1b
execute if score #api_remaining wh_tmp matches 1.. run data modify storage warehouse:api result.error set value "source_changed"
execute if score #api_remaining wh_tmp matches 0 run return 1
return 0
