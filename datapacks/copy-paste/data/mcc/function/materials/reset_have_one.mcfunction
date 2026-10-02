$data modify storage mcc:materials p$(pid).bom."$(id)".have set value 0
$data modify storage mcc:materials p$(pid).bom."$(id)".missing set value 0
$data modify storage mcc:materials p$(pid).bom."$(id)".taken set value 0
return 1
