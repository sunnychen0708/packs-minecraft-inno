data modify storage warehouse:boxnames c27 set value {text:"功能方塊"}
data modify storage warehouse:runtime rename.code set value "27"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c27
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
