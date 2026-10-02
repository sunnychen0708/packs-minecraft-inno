# Retry at most one durable refund entry per tick. Public API result is preserved.
execute unless data storage warehouse:api pending_refunds[0].item_id run return 0
execute unless data storage warehouse:chests c00{registered:1b,valid:1b} run return 0

data remove storage warehouse:api work.saved_result
execute if data storage warehouse:api result run data modify storage warehouse:api work.saved_result set from storage warehouse:api result
data modify storage warehouse:api work.pending set from storage warehouse:api pending_refunds[0]
data modify storage warehouse:api work.pending.dimension set from storage warehouse:chests c00.dimension
data modify storage warehouse:api work.pending.a_x set from storage warehouse:chests c00.a_x
data modify storage warehouse:api work.pending.a_y set from storage warehouse:chests c00.a_y
data modify storage warehouse:api work.pending.a_z set from storage warehouse:chests c00.a_z
data modify storage warehouse:api work.pending.b_x set from storage warehouse:chests c00.b_x
data modify storage warehouse:api work.pending.b_y set from storage warehouse:chests c00.b_y
data modify storage warehouse:api work.pending.b_z set from storage warehouse:chests c00.b_z

data modify storage warehouse:api result set value {operation:"pending_refund",ok:0b,complete:0b,requested:0,inserted:0,remaining:0}
data modify storage warehouse:api result.item_id set from storage warehouse:api work.pending.item_id
data modify storage warehouse:api result.requested set from storage warehouse:api work.pending.count
data modify storage warehouse:api result.remaining set from storage warehouse:api work.pending.count
function warehouse:api/internal/refund_entry with storage warehouse:api work.pending
scoreboard players set #api_pending wh_tmp 0
execute if data storage warehouse:api result.remaining store result score #api_pending wh_tmp run data get storage warehouse:api result.remaining
execute if score #api_pending wh_tmp matches 0 run data remove storage warehouse:api pending_refunds[0]
execute if score #api_pending wh_tmp matches 1.. store result storage warehouse:api pending_refunds[0].count int 1 run scoreboard players get #api_pending wh_tmp

execute if data storage warehouse:api work.saved_result run data modify storage warehouse:api result set from storage warehouse:api work.saved_result
execute unless data storage warehouse:api work.saved_result run data remove storage warehouse:api result
data remove storage warehouse:api work.saved_result
return 1
