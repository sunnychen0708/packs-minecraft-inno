scoreboard players set #compact_active wh_tmp 1
data remove storage warehouse:runtime compact
$data modify storage warehouse:runtime compact.dimension set value "$(dimension)"
$data modify storage warehouse:runtime compact.a_x set value $(a_x)
$data modify storage warehouse:runtime compact.a_y set value $(a_y)
$data modify storage warehouse:runtime compact.a_z set value $(a_z)
$data modify storage warehouse:runtime compact.b_x set value $(b_x)
$data modify storage warehouse:runtime compact.b_y set value $(b_y)
$data modify storage warehouse:runtime compact.b_z set value $(b_z)
scoreboard players operation #compact_local wh_tmp = #compact_slot wh_tmp
execute if score #compact_local wh_tmp matches 27.. run scoreboard players remove #compact_local wh_tmp 27
execute store result storage warehouse:runtime compact.slot int 1 run scoreboard players get #compact_local wh_tmp
$execute if score #compact_slot wh_tmp matches ..26 run data modify storage warehouse:runtime compact.src_x set value $(a_x)
$execute if score #compact_slot wh_tmp matches ..26 run data modify storage warehouse:runtime compact.src_y set value $(a_y)
$execute if score #compact_slot wh_tmp matches ..26 run data modify storage warehouse:runtime compact.src_z set value $(a_z)
$execute if score #compact_slot wh_tmp matches 27.. run data modify storage warehouse:runtime compact.src_x set value $(b_x)
$execute if score #compact_slot wh_tmp matches 27.. run data modify storage warehouse:runtime compact.src_y set value $(b_y)
$execute if score #compact_slot wh_tmp matches 27.. run data modify storage warehouse:runtime compact.src_z set value $(b_z)
function warehouse:compact/slot with storage warehouse:runtime compact
