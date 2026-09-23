data modify storage warehouse:runtime viewer.title set value "37  木製建材"
execute unless data storage warehouse:chests c37{registered:1b,valid:1b} run dialog show @s warehouse:view/error_unregistered
execute unless data storage warehouse:chests c37{registered:1b,valid:1b} run return 0
function warehouse:view/build with storage warehouse:chests c37
