data modify storage warehouse:boxnames c22 set value {text:"農業作物"}
data modify storage warehouse:runtime rename.code set value "22"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c22
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
