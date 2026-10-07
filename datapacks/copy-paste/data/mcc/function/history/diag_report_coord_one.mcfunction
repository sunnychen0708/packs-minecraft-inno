execute if data storage mcc:temp diag_entry{kind:1} run function mcc:history/diag_report_coord_replace with storage mcc:temp diag_entry
execute if data storage mcc:temp diag_entry{kind:2} run function mcc:history/diag_report_coord_remove with storage mcc:temp diag_entry
execute if data storage mcc:temp diag_entry{kind:3} run function mcc:history/diag_report_coord_content with storage mcc:temp diag_entry
return 1
