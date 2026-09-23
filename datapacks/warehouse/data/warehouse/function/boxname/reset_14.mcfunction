data modify storage warehouse:boxnames c14 set value {text:"鐵礦材料"}
data modify storage warehouse:runtime rename.code set value "14"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c14
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
