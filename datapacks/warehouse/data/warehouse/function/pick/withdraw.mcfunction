$function warehouse:api/count_item {item_id:"$(item_id)"}
execute unless data storage warehouse:api result{ok:1b,complete:1b} run tellraw @s [{"text":"[Warehouse] ","color":"gold"},{"text":"倉庫材料來源目前不完整，Pick 已取消。","color":"red"}]
execute unless data storage warehouse:api result{ok:1b,complete:1b} run return fail
scoreboard players set #pick_count wh_tmp 0
execute store result score #pick_count wh_tmp run data get storage warehouse:api result.available
$scoreboard players set #pick_max wh_tmp $(max_stack)
execute if score #pick_count wh_tmp > #pick_max wh_tmp run scoreboard players operation #pick_count wh_tmp = #pick_max wh_tmp
execute unless score #pick_count wh_tmp matches 1.. run tellraw @s [{"text":"[Warehouse] ","color":"gold"},{"text":"倉庫目前沒有 ","color":"yellow"},{"text":"$(item_id)","color":"white"},{"text":"。","color":"yellow"}]
execute unless score #pick_count wh_tmp matches 1.. run return fail
$data modify storage warehouse:pick request set value {item_id:"$(item_id)",max_stack:$(max_stack),count:0}
execute store result storage warehouse:pick request.count int 1 run scoreboard players get #pick_count wh_tmp
return run function warehouse:pick/take with storage warehouse:pick request
