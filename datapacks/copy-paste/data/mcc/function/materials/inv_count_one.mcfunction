# Count phase: have = Warehouse available (already stored) + the player's own plain stacks.
scoreboard players set #inv mcc_tmp 0
function mcc:materials/inv_select with storage mcc:temp mat
function mcc:materials/inv_sum
$execute store result storage mcc:materials p$(pid).bom."$(id)".invhave int 1 run scoreboard players get #inv mcc_tmp
$execute store result score #have mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".have
scoreboard players operation #have mcc_tmp += #inv mcc_tmp
$execute store result storage mcc:materials p$(pid).bom."$(id)".have int 1 run scoreboard players get #have mcc_tmp
return 1
