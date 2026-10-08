$data modify storage mcc:materials p$(id).items set from storage mcc:history r_p$(id)_s$(slot).materials.items
$data modify storage mcc:materials p$(id).bom set from storage mcc:history r_p$(id)_s$(slot).materials.bom
return 1
