data modify storage mcc:temp diag_item set from storage mcc:temp diag.material_work[0]
data modify storage mcc:temp diag_item.key set from storage mcc:temp diag_item.id
function mcc:history/diag_report_need_prepare with storage mcc:temp diag_item
function mcc:history/diag_report_need_one with storage mcc:temp diag_item
data remove storage mcc:temp diag.material_work[0]
execute if data storage mcc:temp diag.material_work[0].id run return run function mcc:history/diag_report_need_loop
return 1
