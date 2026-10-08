scoreboard players add #api_sources wh_tmp 1
scoreboard players set #api_aforced wh_tmp 0
scoreboard players set #api_bforced wh_tmp 0
$execute in $(dimension) store success score #api_aforced wh_tmp run forceload query $(a_x) $(a_z)
$execute if score #api_aforced wh_tmp matches 0 in $(dimension) run forceload add $(a_x) $(a_z)
$execute in $(dimension) store success score #api_bforced wh_tmp run forceload query $(b_x) $(b_z)
$execute if score #api_bforced wh_tmp matches 0 in $(dimension) run forceload add $(b_x) $(b_z)

scoreboard players set #api_sourceok wh_tmp 1
# Validate the actual registered block after adding the temporary ticket; do not require `execute if loaded`.
$execute in $(dimension) unless block $(a_x) $(a_y) $(a_z) #warehouse:storage_chests run scoreboard players set #api_sourceok wh_tmp 0
$execute in $(dimension) unless block $(b_x) $(b_y) $(b_z) #warehouse:storage_chests run scoreboard players set #api_sourceok wh_tmp 0

$execute if score #api_sourceok wh_tmp matches 1 run data modify storage warehouse:api work.half set value {dimension:"$(dimension)",x:$(a_x),y:$(a_y),z:$(a_z),item_id:"$(item_id)"}
execute if score #api_sourceok wh_tmp matches 1 if score #api_remaining wh_tmp matches 1.. run function warehouse:api/internal/take_half with storage warehouse:api work.half
$execute if score #api_sourceok wh_tmp matches 1 run data modify storage warehouse:api work.half set value {dimension:"$(dimension)",x:$(b_x),y:$(b_y),z:$(b_z),item_id:"$(item_id)"}
execute if score #api_sourceok wh_tmp matches 1 if score #api_remaining wh_tmp matches 1.. run function warehouse:api/internal/take_half with storage warehouse:api work.half

execute unless score #api_sourceok wh_tmp matches 1 run scoreboard players add #api_stale wh_tmp 1
$execute if score #api_bforced wh_tmp matches 0 in $(dimension) run forceload remove $(b_x) $(b_z)
$execute if score #api_aforced wh_tmp matches 0 in $(dimension) run forceload remove $(a_x) $(a_z)
return 1
