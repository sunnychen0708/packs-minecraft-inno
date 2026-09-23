execute if score #compact wh_tmp matches 1 if score #compact_src wh_tmp matches ..48 run return 0
scoreboard players set #transfer wh_tmp 0
data remove storage warehouse:runtime move.candidate
$data modify storage warehouse:runtime move.candidate set from block $(dest_b_x) $(dest_b_y) $(dest_b_z) Items[{Slot:21b}]
execute unless data storage warehouse:runtime move.candidate run return 0
execute store result score #before wh_tmp run data get storage warehouse:runtime move.candidate.count
execute if score #before wh_tmp >= #max wh_tmp run return 0
data modify storage warehouse:runtime move.candidate_id set from storage warehouse:runtime move.candidate.id
execute unless data storage warehouse:runtime move.candidate.components run data modify storage warehouse:runtime move.candidate.components set value {}
execute if data storage warehouse:runtime move.candidate.components run data modify storage warehouse:runtime move.candidate_components set from storage warehouse:runtime move.candidate.components
execute unless data storage warehouse:runtime move.candidate.components run data modify storage warehouse:runtime move.candidate_components set value {}
function warehouse:sort/transport/compare_merge with storage warehouse:runtime move
$execute if score #transfer wh_tmp matches 1.. in $(dest_dimension) store result block $(dest_b_x) $(dest_b_y) $(dest_b_z) Items[{Slot:21b}].count int 1 run scoreboard players get #newcount wh_tmp
$execute if score #transfer wh_tmp matches 1.. in $(dest_dimension) store result score #after wh_tmp if items block $(dest_b_x) $(dest_b_y) $(dest_b_z) container.21 $(item_id)
execute if score #transfer wh_tmp matches 1.. run function warehouse:sort/transport/after_write
