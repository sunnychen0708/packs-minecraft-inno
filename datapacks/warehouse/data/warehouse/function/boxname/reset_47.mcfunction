data modify storage warehouse:boxnames c47 set value {text:"裝飾收藏"}
data modify storage warehouse:runtime rename.code set value "47"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c47
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
