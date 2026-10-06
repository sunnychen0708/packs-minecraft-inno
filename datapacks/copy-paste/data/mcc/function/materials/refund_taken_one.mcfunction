scoreboard players set #taken mcc_tmp 0
execute if data storage mcc:temp mat.taken store result score #taken mcc_tmp run data get storage mcc:temp mat.taken
$execute unless data storage mcc:temp mat.taken store result score #taken mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".taken
scoreboard players set #inv mcc_tmp 0
execute if data storage mcc:temp mat.inv store result score #inv mcc_tmp run data get storage mcc:temp mat.inv
$data modify storage mcc:temp refund set value {item_id:"$(id)",count:0}
execute unless score #taken mcc_tmp matches 1.. run return 1
function mcc:materials/refund_split
$execute if score #refok mcc_tmp matches 1 run data modify storage mcc:materials p$(pid).bom."$(id)".taken set value 0
$execute if score #refok mcc_tmp matches 1 run data modify storage mcc:materials p$(pid).bom."$(id)".inv set value 0
$execute if score #refok mcc_tmp matches 1 run data modify storage mcc:materials p$(pid).items[{id:"$(id)"}].taken set value 0
$execute if score #refok mcc_tmp matches 1 run data modify storage mcc:materials p$(pid).items[{id:"$(id)"}].inv set value 0
return 1
