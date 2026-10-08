data modify storage warehouse:boxnames c48 set value {text:"試煉密室"}
data modify storage warehouse:runtime rename.code set value "48"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c48
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
