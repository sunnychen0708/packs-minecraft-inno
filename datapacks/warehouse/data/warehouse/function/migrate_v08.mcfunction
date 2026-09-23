scoreboard objectives add wh_rule trigger
scoreboard objectives add wh_rule_dest trigger
scoreboard objectives add wh_rulebox dummy
scoreboard objectives add wh_ruleov dummy
execute unless data storage warehouse:rules overrides run data modify storage warehouse:rules overrides set value {}
data modify storage warehouse:meta v08 set value 1b
