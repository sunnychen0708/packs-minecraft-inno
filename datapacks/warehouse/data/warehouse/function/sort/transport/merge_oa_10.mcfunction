scoreboard players set #transfer wh_tmp 0
data remove storage warehouse:runtime move.candidate
$execute in $(ov_dimension) run data modify storage warehouse:runtime move.candidate set from block $(ov_a_x) $(ov_a_y) $(ov_a_z) Items[{Slot:10b}]
execute unless data storage warehouse:runtime move.candidate run return 0
execute store result score #before wh_tmp run data get storage warehouse:runtime move.candidate.count
execute if score #before wh_tmp >= #max wh_tmp run return 0
data modify storage warehouse:runtime move.candidate_id set from storage warehouse:runtime move.candidate.id
execute unless data storage warehouse:runtime move.candidate.components run data modify storage warehouse:runtime move.candidate.components set value {}
execute if data storage warehouse:runtime move.candidate.components run data modify storage warehouse:runtime move.candidate_components set from storage warehouse:runtime move.candidate.components
execute unless data storage warehouse:runtime move.candidate.components run data modify storage warehouse:runtime move.candidate_components set value {}
function warehouse:sort/transport/compare_merge with storage warehouse:runtime move
$execute if score #transfer wh_tmp matches 1.. in $(ov_dimension) store result block $(ov_a_x) $(ov_a_y) $(ov_a_z) Items[{Slot:10b}].count int 1 run scoreboard players get #newcount wh_tmp
$execute if score #transfer wh_tmp matches 1.. in $(ov_dimension) store result score #after wh_tmp if items block $(ov_a_x) $(ov_a_y) $(ov_a_z) container.10 $(item_id)
execute if score #transfer wh_tmp matches 1.. run function warehouse:sort/transport/after_write
