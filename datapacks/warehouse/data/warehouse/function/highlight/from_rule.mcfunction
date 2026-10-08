execute unless score @s wh_rulebox matches 10..69 run tellraw @s [{"text":"[Warehouse] ","color":"gold"},{"text":"目前物品沒有可 Highlight 的分類箱。","color":"yellow"}]
execute unless score @s wh_rulebox matches 10..69 run return fail
data modify storage warehouse:api request set value {}
execute store result storage warehouse:api request.code int 1 run scoreboard players get @s wh_rulebox
return run function warehouse:api/highlight
