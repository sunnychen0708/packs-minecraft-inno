scoreboard players set @s wh_rename 0
data remove storage warehouse:runtime rename.stack
data modify storage warehouse:runtime rename.slot set value 0
execute store result storage warehouse:runtime rename.slot int 1 run data get entity @s SelectedItemSlot 1
function warehouse:boxname/capture with storage warehouse:runtime rename
execute unless data storage warehouse:runtime rename.stack.components."minecraft:custom_name" run dialog show @s warehouse:boxname/no_custom_name
execute unless data storage warehouse:runtime rename.stack.components."minecraft:custom_name" run return 0
data modify storage warehouse:runtime rename.new set from storage warehouse:runtime rename.stack.components."minecraft:custom_name"
function warehouse:boxname/save_dispatch
