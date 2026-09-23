scoreboard players set @s wh_target 27
scoreboard players set @s wh_rename_target 0
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c27
data modify storage warehouse:runtime rename.code set value "27"
function warehouse:boxname/show_prepare with storage warehouse:runtime rename
