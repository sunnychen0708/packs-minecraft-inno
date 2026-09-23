data modify storage warehouse:boxnames c61 set value {text:"地獄岩石"}
data modify storage warehouse:runtime rename.code set value "61"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c61
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
