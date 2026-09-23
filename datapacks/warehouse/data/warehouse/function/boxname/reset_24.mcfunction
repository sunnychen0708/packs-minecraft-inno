data modify storage warehouse:boxnames c24 set value {text:"動物素材"}
data modify storage warehouse:runtime rename.code set value "24"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c24
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
