data modify storage warehouse:boxnames c29 set value {text:"日常用品"}
data modify storage warehouse:runtime rename.code set value "29"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c29
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
