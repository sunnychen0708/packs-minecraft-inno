# Public API: rebuild the snapshot of registered, valid Warehouse material sources.
# Output:
#   storage warehouse:api material_sources      list (max 64)
#   storage warehouse:api material_source_count int
#   storage warehouse:api meta                  {version, material_source_limit}
data modify storage warehouse:api meta set value {version:1,material_source_limit:64}
data modify storage warehouse:api material_sources set value []
scoreboard players set #api_count wh_sys 0
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c00{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"00"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c10{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"10"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c20{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"20"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c30{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"30"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c40{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"40"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c50{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"50"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c60{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"60"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c11{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"11"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c12{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"12"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c13{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"13"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c14{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"14"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c15{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"15"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c16{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"16"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c17{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"17"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c18{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"18"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c19{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"19"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c21{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"21"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c22{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"22"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c23{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"23"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c24{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"24"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c25{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"25"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c26{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"26"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c27{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"27"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c28{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"28"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c29{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"29"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c31{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"31"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c32{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"32"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c33{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"33"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c34{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"34"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c35{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"35"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c36{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"36"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c37{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"37"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c38{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"38"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c39{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"39"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c41{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"41"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c42{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"42"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c43{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"43"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c44{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"44"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c45{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"45"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c46{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"46"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c47{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"47"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c48{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"48"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c49{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"49"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c51{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"51"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c52{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"52"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c53{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"53"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c54{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"54"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c55{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"55"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c56{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"56"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c57{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"57"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c58{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"58"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c59{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"59"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c61{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"61"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c62{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"62"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c63{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"63"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c64{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"64"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c65{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"65"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c66{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"66"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c67{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"67"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c68{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"68"}
execute if score #api_count wh_sys matches ..63 if data storage warehouse:chests c69{registered:1b,valid:1b} run function warehouse:api/material_sources/append {code:"69"}
execute store result storage warehouse:api material_source_count int 1 run scoreboard players get #api_count wh_sys
return 1
