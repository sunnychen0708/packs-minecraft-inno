data modify storage mcc:temp diag.material_work set from storage mcc:temp diag.material_items
execute if data storage mcc:temp diag.material_work[0].id run function mcc:history/diag_report_need_loop
return 1
