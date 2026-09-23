scoreboard objectives add wh_unreg trigger
scoreboard objectives add wh_unreg_do trigger
scoreboard objectives add wh_rename_target trigger
scoreboard objectives add wh_rename trigger
function warehouse:boxname/init
scoreboard players set #compact wh_tmp 0
scoreboard players set #compact_src wh_tmp 0
scoreboard players set #compact_code wh_tmp 0
scoreboard players set #compact_slot wh_tmp 0
data modify storage warehouse:meta v09 set value 1b
