execute unless data storage warehouse:api work.inv[0].id run return 0
scoreboard players set #api_stack wh_tmp 0
$execute if data storage warehouse:api work.inv[0]{id:"$(item_id)"} run scoreboard players set #api_stack wh_tmp 1
$execute if data storage warehouse:api work.inv[0]{id:"$(item_id)"} if data storage warehouse:api work.inv[0].count store result score #api_stack wh_tmp run data get storage warehouse:api work.inv[0].count
scoreboard players operation #api_total wh_tmp += #api_stack wh_tmp
data remove storage warehouse:api work.inv[0]
execute if data storage warehouse:api work.inv[0].id run return run function warehouse:api/internal/count_inv_loop with storage warehouse:api work.inv_ctx
return 1
