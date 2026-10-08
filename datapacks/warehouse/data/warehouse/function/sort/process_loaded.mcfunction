data remove storage warehouse:runtime scan.item_id
$data modify storage warehouse:runtime scan.item_id set from block $(x) $(y) $(z) Items[{Slot:$(slot)b}].id
scoreboard players set #override wh_sys 0
scoreboard players set #rule wh_sys 0
execute if data storage warehouse:runtime scan.item_id run function warehouse:sort/check_override with storage warehouse:runtime scan
execute unless score #override wh_sys matches 1 run function warehouse:sort/classify with storage warehouse:runtime scan
