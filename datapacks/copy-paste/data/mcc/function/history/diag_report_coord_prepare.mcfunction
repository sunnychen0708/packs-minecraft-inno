$data modify storage mcc:temp diag_entry.ekey set from storage mcc:names key."$(expected)"
$data modify storage mcc:temp diag_entry.ckey set from storage mcc:names key."$(current)"
return 1
