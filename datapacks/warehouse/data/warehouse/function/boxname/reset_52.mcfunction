data modify storage warehouse:boxnames c52 set value {text:"羊毛織染"}
data modify storage warehouse:runtime rename.code set value "52"
data modify storage warehouse:runtime rename.current set from storage warehouse:boxnames c52
scoreboard players set @s wh_target 0
function warehouse:boxname/show_saved with storage warehouse:runtime rename
