execute if score @s wh_rule_item matches 1..1544 run function warehouse:rule/remove_selected
execute unless score @s wh_rule_item matches 1..1544 run function warehouse:rule/remove_current_legacy
