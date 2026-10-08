data modify storage warehouse:boxnames c65 set value {text:"石英材料"}
data modify storage warehouse:runtime rename.code set value "65"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c65
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
