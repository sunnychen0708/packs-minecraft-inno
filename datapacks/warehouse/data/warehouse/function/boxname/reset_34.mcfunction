data modify storage warehouse:boxnames c34 set value {text:"土礫黏土"}
data modify storage warehouse:runtime rename.code set value "34"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c34
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
