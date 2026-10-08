scoreboard players set #taken mcc_tmp 0
execute if data storage mcc:temp mat.taken store result score #taken mcc_tmp run data get storage mcc:temp mat.taken
$execute unless data storage mcc:temp mat.taken store result score #taken mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".taken
$data modify storage mcc:temp refund set value {item_id:"$(id)",count:0}
execute if score #taken mcc_tmp matches 1.. store result storage mcc:temp refund.count int 1 run scoreboard players get #taken mcc_tmp
execute if score #taken mcc_tmp matches 1.. run function warehouse:api/refund_item with storage mcc:temp refund
$execute if score #taken mcc_tmp matches 1.. if data storage warehouse:api result{ok:1b,complete:1b} run data modify storage mcc:materials p$(pid).bom."$(id)".taken set value 0
$execute if score #taken mcc_tmp matches 1.. if data storage warehouse:api result{ok:1b,complete:1b} run data modify storage mcc:materials p$(pid).items[{id:"$(id)"}].taken set value 0
return 1
