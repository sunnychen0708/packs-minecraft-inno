scoreboard players set #compact_active wh_tmp 1
data remove storage warehouse:runtime compact
$data modify storage warehouse:runtime compact.dimension set value "$(dimension)"
$data modify storage warehouse:runtime compact.a_x set value $(a_x)
$data modify storage warehouse:runtime compact.a_y set value $(a_y)
$data modify storage warehouse:runtime compact.a_z set value $(a_z)
$data modify storage warehouse:runtime compact.b_x set value $(b_x)
$data modify storage warehouse:runtime compact.b_y set value $(b_y)
$data modify storage warehouse:runtime compact.b_z set value $(b_z)
function warehouse:compact/slot_dispatch with storage warehouse:runtime compact
