data modify storage mcc:temp diag.materials set value {}
data modify storage mcc:temp diag.material_items set value []
data modify storage mcc:temp diag.need_work set from storage mcc:temp diag.need_items
execute if data storage mcc:temp diag.need_work[0].id run function mcc:history/diag_resolve_materials_loop
return 1
