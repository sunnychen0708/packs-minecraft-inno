scoreboard players set @s wh_rule 0
data remove storage warehouse:runtime rule
scoreboard players operation @s wh_ruleidx = @s wh_rule_item
scoreboard players remove @s wh_ruleidx 1
execute store result storage warehouse:runtime rule.item_file int 1 run scoreboard players get @s wh_ruleidx
function warehouse:rule/select_file with storage warehouse:runtime rule
data modify storage warehouse:runtime rule.dest set value 0
function warehouse:rule/write_override with storage warehouse:runtime rule
function warehouse:rule/show_removed with storage warehouse:runtime rule
