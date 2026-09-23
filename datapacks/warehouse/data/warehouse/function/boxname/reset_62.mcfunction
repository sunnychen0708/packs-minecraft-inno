data modify storage warehouse:boxnames c62 set value {text:"地獄自然"}
data modify storage warehouse:runtime rename.code set value "62"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c62
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
