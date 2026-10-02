scoreboard players set #api_plain wh_tmp 0
scoreboard players set #moved wh_tmp 0
scoreboard players set #main_ok wh_tmp 0
execute store result score #remaining wh_tmp run data get storage warehouse:runtime move.count
scoreboard players set #max wh_tmp 64
$execute in $(src_dimension) if items block $(src_x) $(src_y) $(src_z) container.$(src_slot) *[minecraft:max_stack_size=16] run scoreboard players set #max wh_tmp 16
$execute in $(src_dimension) if items block $(src_x) $(src_y) $(src_z) container.$(src_slot) *[minecraft:max_stack_size=1] run scoreboard players set #max wh_tmp 1
execute if data storage warehouse:runtime move.stack.components."minecraft:max_stack_size" store result score #max wh_tmp run data get storage warehouse:runtime move.stack.components."minecraft:max_stack_size"
function warehouse:sort/transport/main with storage warehouse:runtime move
execute if score #main_ok wh_tmp matches 1 if score #remaining wh_tmp matches 1.. if data storage warehouse:runtime move{ov_ok:1b} run function warehouse:sort/transport/overflow with storage warehouse:runtime move
function warehouse:sort/transport/finalize with storage warehouse:runtime move
