data modify storage warehouse:boxnames c32 set value {text:"鵝卵石材"}
data modify storage warehouse:runtime rename.code set value "32"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c32
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
