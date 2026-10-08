data modify storage warehouse:boxnames c45 set value {text:"首領收藏"}
data modify storage warehouse:runtime rename.code set value "45"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c45
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
