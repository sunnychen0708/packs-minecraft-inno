$execute if data storage warehouse:rules overrides."$(item_id)" run scoreboard players set #override wh_sys 1
$execute if data storage warehouse:rules overrides."$(item_id)" store result score #rule wh_sys run data get storage warehouse:rules overrides."$(item_id)" 1
execute if score #override wh_sys matches 1 run function warehouse:sort/route_override with storage warehouse:runtime scan
