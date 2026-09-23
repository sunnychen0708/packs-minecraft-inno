data modify storage warehouse:boxnames c41 set value {text:"探索導航"}
data modify storage warehouse:runtime rename.code set value "41"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c41
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
