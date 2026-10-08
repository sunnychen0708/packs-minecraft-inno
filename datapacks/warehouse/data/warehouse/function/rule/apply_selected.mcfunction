data remove storage warehouse:runtime rule
scoreboard players operation @s wh_ruleidx = @s wh_rule_item
scoreboard players remove @s wh_ruleidx 1
execute store result storage warehouse:runtime rule.item_file int 1 run scoreboard players get @s wh_ruleidx
function warehouse:rule/select_file with storage warehouse:runtime rule
scoreboard players set @s wh_ruleov 0
function warehouse:rule/read_override with storage warehouse:runtime rule
execute store result storage warehouse:runtime rule.old_box int 1 run scoreboard players get @s wh_rulebox
function warehouse:rule/set_dest_label
execute store result storage warehouse:runtime rule.dest int 1 run scoreboard players get @s wh_rule_dest
function warehouse:rule/write_override with storage warehouse:runtime rule
execute if score @s wh_rulebox matches 11..69 unless score @s wh_rulebox = @s wh_rule_dest run function warehouse:migration/enqueue with storage warehouse:runtime rule
scoreboard players set @s wh_rule_dest 0
function warehouse:rule/show_saved with storage warehouse:runtime rule
