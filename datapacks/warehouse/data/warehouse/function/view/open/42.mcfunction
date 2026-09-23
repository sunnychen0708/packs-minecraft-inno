data modify storage warehouse:runtime viewer.title set value "42  音樂唱片"
execute unless data storage warehouse:chests c42{registered:1b,valid:1b} run dialog show @s warehouse:view/error_unregistered
execute unless data storage warehouse:chests c42{registered:1b,valid:1b} run return 0
function warehouse:view/build with storage warehouse:chests c42
