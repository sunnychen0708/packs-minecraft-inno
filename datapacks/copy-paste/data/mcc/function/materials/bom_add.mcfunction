$execute unless data storage mcc:materials p$(pid).bom."$(id)" run data modify storage mcc:materials p$(pid).bom."$(id)" set value {need:0,have:0,remain:0,missing:0,taken:0,inv:0,invhave:0}
$execute unless data storage mcc:materials p$(pid).items[{id:"$(id)"}] run data modify storage mcc:materials p$(pid).items append value {id:"$(id)"}
$execute store result score #need mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".need
$scoreboard players add #need mcc_tmp $(count)
$execute store result storage mcc:materials p$(pid).bom."$(id)".need int 1 run scoreboard players get #need mcc_tmp
return 1
