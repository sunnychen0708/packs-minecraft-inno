$execute unless data storage mcc:temp diag.materials."$(material)" run data modify storage mcc:temp diag.materials."$(material)" set value 0
$execute unless data storage mcc:temp diag.material_items[{id:"$(material)"}] run data modify storage mcc:temp diag.material_items append value {id:"$(material)"}
$execute store result score #diag_mat mcc_tmp run data get storage mcc:temp diag.materials."$(material)"
scoreboard players operation #diag_mat mcc_tmp += #diag_need mcc_tmp
$execute store result storage mcc:temp diag.materials."$(material)" int 1 run scoreboard players get #diag_mat mcc_tmp
return 1
