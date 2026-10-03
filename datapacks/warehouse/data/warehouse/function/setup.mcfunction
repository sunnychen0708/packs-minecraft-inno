scoreboard objectives add wh_register trigger
scoreboard objectives add wh_action trigger
scoreboard objectives add wh_nav trigger
scoreboard objectives add wh_regdelay dummy
scoreboard objectives add wh_target dummy
scoreboard objectives add wh_ray dummy
scoreboard objectives add wh_tmp dummy
scoreboard objectives add wh_sys dummy
scoreboard objectives add wh_dup dummy
scoreboard objectives add wh_dupcode dummy
scoreboard objectives add wh_view trigger
scoreboard objectives add wh_viewcnt dummy
scoreboard objectives add wh_viewlines dummy
scoreboard objectives add wh_rule trigger
scoreboard objectives add wh_rule_dest trigger
scoreboard objectives add wh_rulebox dummy
scoreboard objectives add wh_ruleov dummy
scoreboard objectives add wh_rename trigger
scoreboard objectives add wh_rename_target trigger
scoreboard objectives add wh_unreg_do trigger
scoreboard objectives add wh_unreg trigger
scoreboard objectives add wh_search_pick trigger
scoreboard objectives add wh_highlight trigger
scoreboard objectives add pick trigger
scoreboard objectives add wh_rule_item dummy
scoreboard objectives add wh_ruleidx dummy
scoreboard objectives add wh_search_page trigger
scoreboard objectives add wh_viewpage trigger
scoreboard players set #cursor wh_sys 0
scoreboard players set #enabled wh_sys 1
data modify storage warehouse:meta initialized set value 1b
function warehouse:view/init_names
data modify storage warehouse:meta v07 set value 1b
data modify storage warehouse:rules overrides set value {}
data modify storage warehouse:meta v08 set value 1b
data modify storage warehouse:meta v22 set value 1b
execute unless data storage warehouse:migration queue run data modify storage warehouse:migration queue set value []
data modify storage warehouse:meta v30 set value 1b
data modify storage warehouse:meta v43 set value 1b
data modify storage warehouse:meta v44 set value 1b
