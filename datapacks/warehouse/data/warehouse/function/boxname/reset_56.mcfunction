data modify storage warehouse:boxnames c56 set value {text:"林地生態"}
data modify storage warehouse:runtime rename.code set value "56"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c56
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
