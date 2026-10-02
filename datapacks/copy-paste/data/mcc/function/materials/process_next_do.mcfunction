$data modify storage mcc:temp mat set from storage mcc:materials p$(pid).work[0]
$data modify storage mcc:temp mat.pid set value $(pid)
execute if score @s mcc_matphase matches 1 run function mcc:materials/warehouse_count_one with storage mcc:temp mat
execute if score @s mcc_matphase matches 2 run function mcc:materials/warehouse_take_one with storage mcc:temp mat
$data remove storage mcc:materials p$(pid).work[0]
return 1
