scoreboard players set #chunk_forced wh_tmp 0
$execute in $(dimension) store success score #chunk_forced wh_tmp run forceload query $(x) $(z)
$execute if score #chunk_forced wh_tmp matches 0 in $(dimension) run forceload add $(x) $(z)
$execute if score #chunk_forced wh_tmp matches 0 unless data storage warehouse:forceload chunks[{dimension:"$(dimension)",x:$(x),z:$(z)}] run data modify storage warehouse:forceload chunks append value {dimension:"$(dimension)",x:$(x),z:$(z)}
