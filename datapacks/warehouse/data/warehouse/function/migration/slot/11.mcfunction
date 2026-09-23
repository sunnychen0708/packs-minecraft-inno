$data modify storage warehouse:runtime migration_scan set value {dimension:"$(dimension)",x:$(a_x),y:$(a_y),z:$(a_z),slot:11}
$execute in $(dimension) if loaded $(a_x) $(a_y) $(a_z) if block $(a_x) $(a_y) $(a_z) #warehouse:storage_chests if items block $(a_x) $(a_y) $(a_z) container.11 $(item_id) run function warehouse:migration/route
scoreboard players add #mig_slot wh_sys 1
