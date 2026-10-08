data modify storage warehouse:boxnames c15 set value {text:"黃金獄髓"}
data modify storage warehouse:runtime rename.code set value "15"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c15
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
