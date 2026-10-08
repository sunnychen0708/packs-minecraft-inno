# Internal: append one registered source unless the same physical pair is already exported.
$execute if data storage warehouse:api material_sources[{dimension:"$(dimension)",a_x:$(a_x),a_y:$(a_y),a_z:$(a_z),b_x:$(b_x),b_y:$(b_y),b_z:$(b_z)}] run return 0
# Registration can start from either half, so also reject the reversed A/B representation.
$execute if data storage warehouse:api material_sources[{dimension:"$(dimension)",a_x:$(b_x),a_y:$(b_y),a_z:$(b_z),b_x:$(a_x),b_y:$(a_y),b_z:$(a_z)}] run return 0
data modify storage warehouse:api material_sources append from storage warehouse:api work.candidate_source
scoreboard players add #api_count wh_sys 1
return 1
