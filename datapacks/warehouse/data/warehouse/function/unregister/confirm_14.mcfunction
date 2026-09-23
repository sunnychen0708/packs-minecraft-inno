data modify storage warehouse:runtime unreg.name set from storage warehouse:boxnames c14
execute unless data storage warehouse:chests c14{registered:1b} run dialog show @s warehouse:unregister/not_registered
execute unless data storage warehouse:chests c14{registered:1b} run scoreboard players set @s wh_target 0
execute unless data storage warehouse:chests c14{registered:1b} run return 0
function warehouse:unregister/confirm_14_render with storage warehouse:runtime unreg
