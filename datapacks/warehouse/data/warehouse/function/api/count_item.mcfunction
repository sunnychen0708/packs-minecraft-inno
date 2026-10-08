# Public API: count one item ID across the shared Warehouse material sources.
# Input macro: {item_id:"minecraft:stone"}
# Output: storage warehouse:api result
function warehouse:api/material_sources/refresh
data modify storage warehouse:api result set value {ok:0b,complete:1b,available:0,sources_scanned:0,stale_sources:0,source_limit:64}
$data modify storage warehouse:api result.item_id set value "$(item_id)"
data modify storage warehouse:api work set value {queue:[],item_id:""}
$data modify storage warehouse:api work.item_id set value "$(item_id)"
data modify storage warehouse:api work.queue set from storage warehouse:api material_sources
scoreboard players set #api_total wh_tmp 0
scoreboard players set #api_sources wh_tmp 0
scoreboard players set #api_stale wh_tmp 0
scoreboard players set #api_complete wh_tmp 1
function warehouse:api/internal/count_next
execute store result storage warehouse:api result.available int 1 run scoreboard players get #api_total wh_tmp
execute store result storage warehouse:api result.sources_scanned int 1 run scoreboard players get #api_sources wh_tmp
execute store result storage warehouse:api result.stale_sources int 1 run scoreboard players get #api_stale wh_tmp
execute if score #api_complete wh_tmp matches 1 run data modify storage warehouse:api result.ok set value 1b
execute unless score #api_complete wh_tmp matches 1 run data modify storage warehouse:api result.complete set value 0b
execute if score #api_complete wh_tmp matches 1 run return 1
return 0
