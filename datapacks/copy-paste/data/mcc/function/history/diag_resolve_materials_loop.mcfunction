data modify storage mcc:temp diag_item set from storage mcc:temp diag.need_work[0]
data modify storage mcc:temp diag_item.material set from storage mcc:temp diag_item.id
function mcc:history/diag_resolve_material_one with storage mcc:temp diag_item
data remove storage mcc:temp diag.need_work[0]
execute if data storage mcc:temp diag.need_work[0].id run return run function mcc:history/diag_resolve_materials_loop
return 1
