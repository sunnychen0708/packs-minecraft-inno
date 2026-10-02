$execute store result score #taken mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".taken
$execute if score #taken mcc_tmp matches 1.. run give @s $(id) $(taken)
$data modify storage mcc:materials p$(pid).bom."$(id)".taken set value 0
return 1
