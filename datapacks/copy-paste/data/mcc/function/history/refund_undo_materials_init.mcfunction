$data modify storage mcc:debug refund_init set value {id:$(id),slot:$(slot),stage:"entered"}
$execute store result storage mcc:debug refund_init.item_count int 1 run data get storage mcc:history u_p$(id)_s$(slot).materials.items
$data modify storage mcc:temp txwork set from storage mcc:history u_p$(id)_s$(slot).materials.items
$data modify storage mcc:temp txctx set value {id:$(id),slot:$(slot)}
execute if data storage mcc:temp txwork[0].id run function mcc:history/refund_undo_materials_loop with storage mcc:temp txctx
return 1
