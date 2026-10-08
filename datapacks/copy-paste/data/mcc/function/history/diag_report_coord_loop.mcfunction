data modify storage mcc:temp diag_entry set from storage mcc:temp diag.coord_work[0]
data modify storage mcc:temp diag_entry.ekey set from storage mcc:temp diag_entry.expected
data modify storage mcc:temp diag_entry.ckey set from storage mcc:temp diag_entry.current
function mcc:history/diag_report_coord_prepare with storage mcc:temp diag_entry
function mcc:history/diag_report_coord_one
data remove storage mcc:temp diag.coord_work[0]
execute if data storage mcc:temp diag.coord_work[0].expected run return run function mcc:history/diag_report_coord_loop
return 1
