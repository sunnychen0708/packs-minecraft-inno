data modify storage warehouse:chests c60.registered set value 0b
data modify storage warehouse:chests c60.valid set value 0b
data modify storage warehouse:runtime unreg.name set from storage warehouse:boxnames c60
data modify storage warehouse:runtime unreg.code set value "60"
scoreboard players set @s wh_target 0
scoreboard players set @s wh_unreg_do 0
function warehouse:unregister/show_done with storage warehouse:runtime unreg
