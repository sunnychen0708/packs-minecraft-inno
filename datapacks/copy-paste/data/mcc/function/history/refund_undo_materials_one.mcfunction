$data modify storage mcc:temp refund set value {item_id:"$(id)",count:0}
$execute store result score #taken mcc_tmp run data get storage mcc:history u_p$(pid)_s$(slot).materials.bom."$(id)".taken
execute if score #taken mcc_tmp matches 1.. store result storage mcc:temp refund.count int 1 run scoreboard players get #taken mcc_tmp
execute if score #taken mcc_tmp matches 1.. run function warehouse:api/refund_item with storage mcc:temp refund
return 1
