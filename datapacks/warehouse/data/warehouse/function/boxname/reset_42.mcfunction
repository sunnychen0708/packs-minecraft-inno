data modify storage warehouse:boxnames c42 set value {text:"音樂唱片"}
data modify storage warehouse:runtime rename.code set value "42"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c42
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
