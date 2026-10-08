$execute unless data storage mcc:materials p$(pid) run data modify storage mcc:materials p$(pid) set value {pid:$(pid),boxes:[],bom:{},items:[],work:[],work_boxes:[]}
$data modify storage mcc:materials p$(pid).pid set value $(pid)
$execute unless data storage mcc:materials p$(pid).boxes run data modify storage mcc:materials p$(pid).boxes set value []
$execute unless data storage mcc:materials p$(pid).bom run data modify storage mcc:materials p$(pid).bom set value {}
$execute unless data storage mcc:materials p$(pid).items run data modify storage mcc:materials p$(pid).items set value []
$execute unless data storage mcc:materials p$(pid).work run data modify storage mcc:materials p$(pid).work set value []
$execute unless data storage mcc:materials p$(pid).work_boxes run data modify storage mcc:materials p$(pid).work_boxes set value []
return 1
