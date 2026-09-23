function survival_utils:load/core
function survival_utils:load/stats
scoreboard objectives add help trigger
scoreboard players enable @a help
scoreboard players enable @a treecap
scoreboard players enable @a veinmine
scoreboard players enable @a replant
tellraw @s [{"text":"[屁眼派對] ","color":"gold"},{"text":"計分板已重新建立。","color":"green"}]
