data modify storage mcc:temp diag.coord_work set from storage mcc:temp diag.coords
execute if data storage mcc:temp diag.coord_work[0].expected run function mcc:history/diag_report_coord_loop
return 1
