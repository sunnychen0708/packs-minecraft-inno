data modify storage warehouse:boxnames c59 set value {text:"海洋生態"}
data modify storage warehouse:runtime rename.code set value "59"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c59
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
