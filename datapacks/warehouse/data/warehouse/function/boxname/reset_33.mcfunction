data modify storage warehouse:boxnames c33 set value {text:"深板岩塊"}
data modify storage warehouse:runtime rename.code set value "33"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c33
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
