scoreboard players set @s wh_rule 0
scoreboard players set @s wh_rule_item 0
function warehouse:rule/held_lookup
execute if score @s wh_rule_item matches 1..1544 run function warehouse:rule/show_selected
execute unless score @s wh_rule_item matches 1..1544 run function warehouse:rule/show_current_legacy
