$execute unless data storage mcc:materials p$(pid).bom."$(id)" run return 0
$execute store result score #have mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".have
$scoreboard players add #have mcc_tmp $(count)
$execute store result storage mcc:materials p$(pid).bom."$(id)".have int 1 run scoreboard players get #have mcc_tmp
return 1
