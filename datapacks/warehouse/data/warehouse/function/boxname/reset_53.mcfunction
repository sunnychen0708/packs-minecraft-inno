data modify storage warehouse:boxnames c53 set value {text:"洞窟植物"}
data modify storage warehouse:runtime rename.code set value "53"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c53
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
