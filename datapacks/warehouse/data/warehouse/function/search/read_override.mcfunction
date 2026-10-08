$execute if data storage warehouse:rules overrides."$(item_id)" run scoreboard players set #search_override wh_search 1
$execute if data storage warehouse:rules overrides."$(item_id)" store result score #search_box wh_search run data get storage warehouse:rules overrides."$(item_id)" 1
