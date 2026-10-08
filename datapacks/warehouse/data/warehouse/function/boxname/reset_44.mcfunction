data modify storage warehouse:boxnames c44 set value {text:"模板旗幟"}
data modify storage warehouse:runtime rename.code set value "44"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c44
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
