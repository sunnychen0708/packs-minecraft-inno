$data modify storage mcc:temp mat set from storage mcc:materials p$(pid).work[0]
$data modify storage mcc:temp mat.pid set value $(pid)
function mcc:materials/report_all_one with storage mcc:temp mat
$data remove storage mcc:materials p$(pid).work[0]
$execute if data storage mcc:materials p$(pid).work[0].id run return run function mcc:materials/report_all_loop with storage mcc:materials p$(pid)
return 1
