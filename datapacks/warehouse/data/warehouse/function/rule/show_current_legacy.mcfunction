scoreboard players set @s wh_rule 0
data remove storage warehouse:runtime rule
data modify storage warehouse:runtime rule.slot set value 0
execute store result storage warehouse:runtime rule.slot int 1 run data get entity @s SelectedItemSlot 1
function warehouse:rule/capture_stack with storage warehouse:runtime rule
execute unless data storage warehouse:runtime rule.stack.id run dialog show @s warehouse:rule/empty_hand
execute unless data storage warehouse:runtime rule.stack.id run return 0
data modify storage warehouse:runtime rule.item_id set from storage warehouse:runtime rule.stack.id
function warehouse:rule/resolve_name with storage warehouse:runtime rule
scoreboard players set @s wh_rulebox -1
scoreboard players set @s wh_ruleov 0
function warehouse:rule/read_override with storage warehouse:runtime rule
execute unless score @s wh_ruleov matches 1 run function warehouse:rule/lookup_default
execute if score @s wh_rulebox matches -1 run scoreboard players set @s wh_rulebox 0
function warehouse:rule/set_box_label
execute store result storage warehouse:runtime rule.box int 1 run scoreboard players get @s wh_rulebox
execute if score @s wh_rulebox matches 0 run function warehouse:rule/show_unclassified with storage warehouse:runtime rule
execute if score @s wh_rulebox matches 11..69 run function warehouse:rule/show_classified with storage warehouse:runtime rule
