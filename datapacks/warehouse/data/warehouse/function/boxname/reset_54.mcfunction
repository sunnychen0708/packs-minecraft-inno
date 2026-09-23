data modify storage warehouse:boxnames c54 set value {text:"洞窟晶石"}
data modify storage warehouse:runtime rename.code set value "54"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c54
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
