data modify storage warehouse:boxnames c31 set from storage warehouse:runtime rename.new
data modify storage warehouse:runtime rename.code set value "31"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c31
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
