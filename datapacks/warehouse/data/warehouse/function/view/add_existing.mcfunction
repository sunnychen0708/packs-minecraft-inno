$execute store result score #viewold wh_sys run data get storage warehouse:runtime viewer.totals[{id:"$(id)"}].count 1
scoreboard players operation @s wh_viewcnt += #viewold wh_sys
$execute store result storage warehouse:runtime viewer.totals[{id:"$(id)"}].count int 1 run scoreboard players get @s wh_viewcnt
