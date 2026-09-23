$data modify storage warehouse:runtime migration_scan set value {dimension:"$(dimension)",x:$(b_x),y:$(b_y),z:$(b_z),slot:9}
$execute in $(dimension) if loaded $(b_x) $(b_y) $(b_z) if block $(b_x) $(b_y) $(b_z) #warehouse:storage_chests if items block $(b_x) $(b_y) $(b_z) container.9 $(item_id) run function warehouse:migration/route
scoreboard players add #mig_slot wh_sys 1
