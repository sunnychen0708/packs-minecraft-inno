$function warehouse:api/take_item {item_id:"$(item_id)",count:$(count)}
execute unless data storage warehouse:api result{ok:1b,complete:1b} run tellraw @s [{"text":"[Warehouse] ","color":"gold"},{"text":"Pick 取料失敗；倉庫內容可能剛被其他操作改動。","color":"red"}]
execute unless data storage warehouse:api result{ok:1b,complete:1b} run return fail
$data modify storage warehouse:pick result set value {ok:1b,item_id:"$(item_id)",count:$(count)}
$execute if entity @s[type=minecraft:player] run function warehouse:pick/give {item_id:"$(item_id)",count:$(count)}
return 1
