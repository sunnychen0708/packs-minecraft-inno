data remove storage warehouse:search_index terms
data remove storage warehouse:meta search_ready
data modify storage warehouse:meta search_rebuilding set value 1b
scoreboard players set #search_index wh_sys 0
schedule function warehouse:search/index/rebuild_tick 1t replace
