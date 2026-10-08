data modify storage warehouse:boxnames c19 set value {text:"生存工具"}
data modify storage warehouse:runtime rename.code set value "19"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c19
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
