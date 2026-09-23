data modify storage warehouse:runtime viewer.title set value "20  區域 2 溢位箱"
execute unless data storage warehouse:chests c20{registered:1b,valid:1b} run dialog show @s warehouse:view/error_unregistered
execute unless data storage warehouse:chests c20{registered:1b,valid:1b} run return 0
function warehouse:view/build with storage warehouse:chests c20
