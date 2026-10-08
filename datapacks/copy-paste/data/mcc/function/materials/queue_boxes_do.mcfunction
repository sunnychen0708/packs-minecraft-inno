$data modify storage mcc:materials p$(pid).work_boxes set from storage mcc:materials p$(pid).boxes
$execute store result score @s mcc_matleft run data get storage mcc:materials p$(pid).work_boxes
return 1
