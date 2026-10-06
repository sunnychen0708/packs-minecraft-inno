# Player's own stacks first, then Warehouse for whatever is still missing.
function mcc:materials/inv_take_one with storage mcc:temp mat
scoreboard players set #whtaken mcc_tmp 0
$data modify storage mcc:temp whapi set value {item_id:"$(id)",count:0}
execute store result storage mcc:temp whapi.count int 1 run scoreboard players get #remain mcc_tmp
execute if score #remain mcc_tmp matches 1.. run function warehouse:api/take_item with storage mcc:temp whapi
execute if score #remain mcc_tmp matches 1.. store result score #whtaken mcc_tmp run data get storage warehouse:api result.taken
execute if score #remain mcc_tmp matches 1.. store result score #remain mcc_tmp run data get storage warehouse:api result.remaining
scoreboard players operation #whtaken mcc_tmp += #invtaken mcc_tmp
$execute store result storage mcc:materials p$(pid).bom."$(id)".taken int 1 run scoreboard players get #whtaken mcc_tmp
$execute store result storage mcc:materials p$(pid).items[{id:"$(id)"}].taken int 1 run scoreboard players get #whtaken mcc_tmp
$execute store result storage mcc:materials p$(pid).bom."$(id)".remain int 1 run scoreboard players get #remain mcc_tmp
return 1
