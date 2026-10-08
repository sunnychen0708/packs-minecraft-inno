data modify storage warehouse:boxnames c66 set value {text:"終界素材"}
data modify storage warehouse:runtime rename.code set value "66"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c66
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
