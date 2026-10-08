data modify storage warehouse:runtime viewer.title set value "67  地獄掉落"
execute unless data storage warehouse:chests c67{registered:1b,valid:1b} run dialog show @s warehouse:view/error_unregistered
execute unless data storage warehouse:chests c67{registered:1b,valid:1b} run return 0
function warehouse:view/build with storage warehouse:chests c67
