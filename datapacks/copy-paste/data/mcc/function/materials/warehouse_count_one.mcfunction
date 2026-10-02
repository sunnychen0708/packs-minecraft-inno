$data modify storage mcc:temp whapi set value {item_id:"$(id)"}
function warehouse:api/count_item with storage mcc:temp whapi
execute unless data storage warehouse:api result{ok:1b,complete:1b} run scoreboard players set @s mcc_materr 1
$execute if data storage warehouse:api result{ok:1b,complete:1b} run data modify storage mcc:materials p$(pid).bom."$(id)".have set from storage warehouse:api result.available
return 1
