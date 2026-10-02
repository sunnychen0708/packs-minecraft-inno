# Internal helper for warehouse:api/material_sources/refresh.
$data modify storage warehouse:api material_sources append from storage warehouse:chests c$(code)
scoreboard players add #api_count wh_sys 1
return 1
