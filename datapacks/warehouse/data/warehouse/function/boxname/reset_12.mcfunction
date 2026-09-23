data modify storage warehouse:boxnames c12 set value {text:"紅石青金"}
data modify storage warehouse:runtime rename.code set value "12"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c12
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
