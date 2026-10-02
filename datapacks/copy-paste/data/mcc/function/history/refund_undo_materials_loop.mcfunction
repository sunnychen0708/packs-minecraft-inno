execute unless data storage mcc:temp txwork[0].id run return 0
data modify storage mcc:temp txitem set from storage mcc:temp txwork[0]
$data modify storage mcc:temp txitem.pid set value $(id)
$data modify storage mcc:temp txitem.slot set value $(slot)
function mcc:history/refund_undo_materials_one with storage mcc:temp txitem
data remove storage mcc:temp txwork[0]
execute if data storage mcc:temp txwork[0].id run return run function mcc:history/refund_undo_materials_loop with storage mcc:temp txctx
return 1
