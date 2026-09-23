data modify storage warehouse:boxnames c50 set value {text:"五區溢位"}
data modify storage warehouse:runtime rename.code set value "50"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c50
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
