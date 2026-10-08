data modify storage warehouse:boxnames c35 set value {text:"沙岩建材"}
data modify storage warehouse:runtime rename.code set value "35"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c35
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
