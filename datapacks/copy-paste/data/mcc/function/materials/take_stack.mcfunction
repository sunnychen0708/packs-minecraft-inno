$execute unless data storage mcc:materials p$(pid).bom."$(id)" run return 0
$execute store result score #remain mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".remain
execute unless score #remain mcc_tmp matches 1.. run return 0
$scoreboard players set #stack mcc_tmp $(count)
scoreboard players operation #take mcc_tmp = #remain mcc_tmp
execute if score #take mcc_tmp > #stack mcc_tmp run scoreboard players operation #take mcc_tmp = #stack mcc_tmp
scoreboard players operation #new mcc_tmp = #stack mcc_tmp
scoreboard players operation #new mcc_tmp -= #take mcc_tmp
$execute if score #new mcc_tmp matches 0 run data remove block $(x) $(y) $(z) Items[{Slot:$(slot)b}]
$execute if score #new mcc_tmp matches 1.. store result block $(x) $(y) $(z) Items[{Slot:$(slot)b}].count int 1 run scoreboard players get #new mcc_tmp
scoreboard players operation #remain mcc_tmp -= #take mcc_tmp
$execute store result storage mcc:materials p$(pid).bom."$(id)".remain int 1 run scoreboard players get #remain mcc_tmp
$execute store result score #taken mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".taken
scoreboard players operation #taken mcc_tmp += #take mcc_tmp
$execute store result storage mcc:materials p$(pid).bom."$(id)".taken int 1 run scoreboard players get #taken mcc_tmp
return 1
