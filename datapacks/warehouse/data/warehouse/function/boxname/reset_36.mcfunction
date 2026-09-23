data modify storage warehouse:boxnames c36 set value {text:"原木木材"}
data modify storage warehouse:runtime rename.code set value "36"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c36
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
