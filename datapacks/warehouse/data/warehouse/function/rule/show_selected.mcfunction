data remove storage warehouse:runtime rule
scoreboard players operation @s wh_ruleidx = @s wh_rule_item
scoreboard players remove @s wh_ruleidx 1
execute store result storage warehouse:runtime rule.item_file int 1 run scoreboard players get @s wh_ruleidx
function warehouse:rule/select_file with storage warehouse:runtime rule
scoreboard players set @s wh_ruleov 0
function warehouse:rule/read_override with storage warehouse:runtime rule
function warehouse:rule/set_box_label
execute store result storage warehouse:runtime rule.box int 1 run scoreboard players get @s wh_rulebox
execute if score @s wh_rulebox matches 0 run function warehouse:rule/show_unclassified with storage warehouse:runtime rule
execute if score @s wh_rulebox matches 11..69 run function warehouse:rule/show_classified with storage warehouse:runtime rule
