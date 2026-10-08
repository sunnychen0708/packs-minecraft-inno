$data modify storage mcc:materials p$(pid).work set from storage mcc:materials p$(pid).items
$execute store result score @s mcc_matleft run data get storage mcc:materials p$(pid).work
return 1
