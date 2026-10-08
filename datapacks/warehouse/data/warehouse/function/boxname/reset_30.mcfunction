data modify storage warehouse:boxnames c30 set value {text:"三區溢位"}
data modify storage warehouse:runtime rename.code set value "30"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c30
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
