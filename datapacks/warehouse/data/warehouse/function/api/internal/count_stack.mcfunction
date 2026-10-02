scoreboard players set #api_stack wh_tmp 0
$execute unless data storage warehouse:api work.stack{id:"$(item_id)"} run return 0
scoreboard players set #api_stack wh_tmp 1
execute if data storage warehouse:api work.stack.count store result score #api_stack wh_tmp run data get storage warehouse:api work.stack.count
scoreboard players operation #api_total wh_tmp += #api_stack wh_tmp
return 1
