execute unless score #remaining wh_tmp matches 1.. run return 0
$execute in $(dest_dimension) if items block $(dest_b_x) $(dest_b_y) $(dest_b_z) container.15 * run return 0
scoreboard players operation #transfer wh_tmp = #remaining wh_tmp
execute if score #transfer wh_tmp > #max wh_tmp run scoreboard players operation #transfer wh_tmp = #max wh_tmp
data modify storage warehouse:runtime move.place set from storage warehouse:runtime move.stack
execute store result storage warehouse:runtime move.place.count int 1 run scoreboard players get #transfer wh_tmp
data modify storage warehouse:runtime move.place.Slot set value 15b
$execute in $(dest_dimension) unless items block $(dest_b_x) $(dest_b_y) $(dest_b_z) container.15 * run data modify block $(dest_b_x) $(dest_b_y) $(dest_b_z) Items append from storage warehouse:runtime move.place
scoreboard players set #before wh_tmp 0
$execute in $(dest_dimension) store result score #after wh_tmp if items block $(dest_b_x) $(dest_b_y) $(dest_b_z) container.15 $(item_id)
function warehouse:sort/transport/after_write
