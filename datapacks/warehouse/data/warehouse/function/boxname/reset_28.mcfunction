data modify storage warehouse:boxnames c28 set value {text:"交通運輸"}
data modify storage warehouse:runtime rename.code set value "28"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c28
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
