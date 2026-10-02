$data modify storage mcc:debug refund_one set value {id:"$(id)",pid:$(pid),slot:$(slot),stage:"entered"}
$data modify storage mcc:temp refund set value {item_id:"$(id)",count:0}
$execute store result score #taken mcc_tmp run data get storage mcc:history u_p$(pid)_s$(slot).materials.bom."$(id)".taken
execute store result storage mcc:debug refund_one.taken int 1 run scoreboard players get #taken mcc_tmp
execute if score #taken mcc_tmp matches 1.. run data modify storage mcc:debug refund_one.eligible set value 1b
execute if score #taken mcc_tmp matches 1.. store result storage mcc:temp refund.count int 1 run scoreboard players get #taken mcc_tmp
execute if score #taken mcc_tmp matches 1.. run data modify storage mcc:debug refund_one.stage set value "before_api"
execute if score #taken mcc_tmp matches 1.. run function warehouse:api/refund_item with storage mcc:temp refund
execute if data storage warehouse:api result run data modify storage mcc:debug refund_one.api_result set from storage warehouse:api result
data modify storage mcc:debug refund_one.stage set value "after_api"
return 1
