data modify storage warehouse:chests c15.registered set value 0b
data modify storage warehouse:chests c15.valid set value 0b
data modify storage warehouse:runtime unreg.name set from storage warehouse:boxnames c15
data modify storage warehouse:runtime unreg.code set value "15"
scoreboard players set @s wh_target 0
scoreboard players set @s wh_unreg_do 0
function warehouse:unregister/show_done with storage warehouse:runtime unreg
