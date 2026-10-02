# Finish a public refund transaction. Any physical remainder becomes Warehouse-owned durable debt.
execute unless data storage warehouse:api pending_refunds run data modify storage warehouse:api pending_refunds set value []
scoreboard players set #api_queue wh_tmp 0
execute if data storage warehouse:api result.remaining store result score #api_queue wh_tmp run data get storage warehouse:api result.remaining
execute if score #api_queue wh_tmp matches 1.. run data modify storage warehouse:api work.pending_enqueue set value {item_id:"",count:0}
execute if score #api_queue wh_tmp matches 1.. run data modify storage warehouse:api work.pending_enqueue.item_id set from storage warehouse:api result.item_id
execute if score #api_queue wh_tmp matches 1.. store result storage warehouse:api work.pending_enqueue.count int 1 run scoreboard players get #api_queue wh_tmp
execute if score #api_queue wh_tmp matches 1.. run data modify storage warehouse:api pending_refunds append from storage warehouse:api work.pending_enqueue
execute store result storage warehouse:api result.queued int 1 run scoreboard players get #api_queue wh_tmp
execute if score #api_queue wh_tmp matches 1.. run data modify storage warehouse:api result.deferred set value 1b
execute if score #api_queue wh_tmp matches 1.. if data storage warehouse:api result.error run data modify storage warehouse:api result.deferred_reason set from storage warehouse:api result.error
execute if score #api_queue wh_tmp matches 1.. run data remove storage warehouse:api result.error
execute if score #api_queue wh_tmp matches 1.. run data modify storage warehouse:api result.remaining set value 0
data modify storage warehouse:api result.ok set value 1b
data modify storage warehouse:api result.complete set value 1b
return 1
