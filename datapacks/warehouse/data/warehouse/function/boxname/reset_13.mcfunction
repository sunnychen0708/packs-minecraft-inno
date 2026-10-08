data modify storage warehouse:boxnames c13 set value {text:"煤炭火把"}
data modify storage warehouse:runtime rename.code set value "13"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c13
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
