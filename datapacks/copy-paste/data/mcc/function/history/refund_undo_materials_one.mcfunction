$execute store result score #taken mcc_tmp run data get storage mcc:history u_p$(pid)_s$(slot).materials.bom."$(id)".taken
$execute if score #taken mcc_tmp matches 1.. run give @s $(id) $(taken)
return 1
