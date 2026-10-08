$data modify storage mcc:temp diag_item.key set from storage mcc:names key."$(id)"
$execute store result score #diag_need mcc_tmp run data get storage mcc:temp diag.materials."$(id)"
return 1
