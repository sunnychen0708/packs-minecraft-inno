scoreboard players set #chunk_forced wh_tmp 0
$execute in $(dimension) store success score #chunk_forced wh_tmp run forceload query $(a_x) $(a_z)
$execute if score #chunk_forced wh_tmp matches 0 in $(dimension) run forceload add $(a_x) $(a_z)
$execute if score #chunk_forced wh_tmp matches 0 unless data storage warehouse:forceload chunks[{dimension:"$(dimension)",x:$(a_x),z:$(a_z)}] run data modify storage warehouse:forceload chunks append value {dimension:"$(dimension)",x:$(a_x),z:$(a_z)}
scoreboard players set #chunk_forced wh_tmp 0
$execute in $(dimension) store success score #chunk_forced wh_tmp run forceload query $(b_x) $(b_z)
$execute if score #chunk_forced wh_tmp matches 0 in $(dimension) run forceload add $(b_x) $(b_z)
$execute if score #chunk_forced wh_tmp matches 0 unless data storage warehouse:forceload chunks[{dimension:"$(dimension)",x:$(b_x),z:$(b_z)}] run data modify storage warehouse:forceload chunks append value {dimension:"$(dimension)",x:$(b_x),z:$(b_z)}
