execute if score @s su_plant matches 1 run tag @s add su_was_on
execute if entity @s[tag=su_was_on] run scoreboard players set @s su_plant 0
execute unless entity @s[tag=su_was_on] run scoreboard players set @s su_plant 1
execute if score @s su_plant matches 1 run tellraw @s [{"text":"[生存便利] ","color":"gold"},{"text":"自動補種：開啟","color":"green"}]
execute if score @s su_plant matches 0 run tellraw @s [{"text":"[生存便利] ","color":"gold"},{"text":"自動補種：關閉","color":"red"}]
tag @s remove su_was_on
