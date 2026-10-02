$data remove storage mcc:temp inv
$data modify storage mcc:temp inv set from block $(x) $(y) $(z) Items
execute if score @s mcc_matphase matches 1 if data storage mcc:temp inv[0].id run function mcc:materials/count_inv
execute if score @s mcc_matphase matches 2 if data storage mcc:temp inv[0].id run function mcc:materials/take_inv
return 1
