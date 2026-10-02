$data modify storage mcc:temp whapi set value {item_id:"$(id)",count:0}
$execute store result storage mcc:temp whapi.count int 1 run data get storage mcc:materials p$(pid).bom."$(id)".remain
function warehouse:api/take_item with storage mcc:temp whapi
$execute store result storage mcc:materials p$(pid).bom."$(id)".taken int 1 run data get storage warehouse:api result.taken
$execute store result storage mcc:materials p$(pid).bom."$(id)".remain int 1 run data get storage warehouse:api result.remaining
return 1
