scoreboard players set #transfer wh_tmp 0
$execute unless data storage warehouse:runtime move.candidate{id:"$(item_id)"} run return 0
$execute unless data storage warehouse:runtime move.candidate{components:$(components)} run return 0
$execute unless data storage warehouse:runtime move.stack{id:"$(candidate_id)"} run return 0
$execute unless data storage warehouse:runtime move.stack{components:$(candidate_components)} run return 0
scoreboard players operation #capacity wh_tmp = #max wh_tmp
scoreboard players operation #capacity wh_tmp -= #before wh_tmp
execute if score #capacity wh_tmp matches ..0 run return 0
scoreboard players operation #transfer wh_tmp = #remaining wh_tmp
execute if score #transfer wh_tmp > #capacity wh_tmp run scoreboard players operation #transfer wh_tmp = #capacity wh_tmp
scoreboard players operation #newcount wh_tmp = #before wh_tmp
scoreboard players operation #newcount wh_tmp += #transfer wh_tmp
