execute if data storage warehouse:boxnames c11{text:"寶石礦物"} run data modify storage warehouse:boxnames c11 set value {text:"鑽石綠寶"}
execute if data storage warehouse:boxnames c38{text:"岩石凝灰"} run data modify storage warehouse:boxnames c38 set value {text:"其他石頭"}
execute if data storage warehouse:boxnames c55{text:"深淵古城"} run data modify storage warehouse:boxnames c55 set value {text:"遠古城市"}
execute if data storage warehouse:chests c11{name:"寶石礦物"} run data modify storage warehouse:chests c11.name set value "鑽石綠寶"
execute if data storage warehouse:chests c38{name:"岩石凝灰"} run data modify storage warehouse:chests c38.name set value "其他石頭"
execute if data storage warehouse:chests c55{name:"深淵古城"} run data modify storage warehouse:chests c55.name set value "遠古城市"
data modify storage warehouse:meta v11 set value 1b
