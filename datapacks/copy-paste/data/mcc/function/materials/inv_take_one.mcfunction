# Take phase, player first: take up to `remain` from the player's own stacks.
# Out: #invtaken; bom/items .inv record it so Undo can give it back to the player.
scoreboard players set #invtaken mcc_tmp 0
$execute store result score #remain mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".remain
execute if score #remain mcc_tmp matches 1.. run function mcc:materials/inv_select with storage mcc:temp mat
execute if score #remain mcc_tmp matches 1.. run function mcc:materials/inv_take_loop
$execute store result storage mcc:materials p$(pid).bom."$(id)".remain int 1 run scoreboard players get #remain mcc_tmp
$execute store result storage mcc:materials p$(pid).bom."$(id)".inv int 1 run scoreboard players get #invtaken mcc_tmp
$execute store result storage mcc:materials p$(pid).items[{id:"$(id)"}].inv int 1 run scoreboard players get #invtaken mcc_tmp
return 1
