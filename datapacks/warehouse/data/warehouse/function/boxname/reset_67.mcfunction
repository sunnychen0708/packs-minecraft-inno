data modify storage warehouse:boxnames c67 set value {text:"地獄掉落"}
data modify storage warehouse:runtime rename.code set value "67"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c67
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
