$data modify storage mcc:materials p$(pid).work set from storage mcc:materials p$(pid).items
$execute if data storage mcc:materials p$(pid).work[0].id run function mcc:materials/check_remain_loop with storage mcc:materials p$(pid)
return 1
