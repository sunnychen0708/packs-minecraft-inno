data modify storage warehouse:boxnames c68 set value {text:"終界掉落"}
data modify storage warehouse:runtime rename.code set value "68"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c68
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
