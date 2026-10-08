data modify storage warehouse:boxnames c21 set value {text:"食物料理"}
data modify storage warehouse:runtime rename.code set value "21"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c21
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
