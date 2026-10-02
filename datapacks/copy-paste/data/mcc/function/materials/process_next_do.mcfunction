$data modify storage mcc:temp box set from storage mcc:materials p$(pid).work_boxes[0]
$data modify storage mcc:temp box.pid set value $(pid)
function mcc:materials/scan_box with storage mcc:temp box
$data remove storage mcc:materials p$(pid).work_boxes[0]
return 1
