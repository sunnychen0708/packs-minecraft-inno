scoreboard players set @s wh_rule 0
data remove storage warehouse:runtime rule
data modify storage warehouse:runtime rule.slot set value 0
execute store result storage warehouse:runtime rule.slot int 1 run data get entity @s SelectedItemSlot 1
function warehouse:rule/capture_stack with storage warehouse:runtime rule
execute unless data storage warehouse:runtime rule.stack.id run dialog show @s warehouse:rule/empty_hand
execute unless data storage warehouse:runtime rule.stack.id run return 0
data modify storage warehouse:runtime rule.item_id set from storage warehouse:runtime rule.stack.id
function warehouse:rule/resolve_name with storage warehouse:runtime rule
data modify storage warehouse:runtime rule.dest set value 0
function warehouse:rule/write_override with storage warehouse:runtime rule
function warehouse:rule/show_removed with storage warehouse:runtime rule
