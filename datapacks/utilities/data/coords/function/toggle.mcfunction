# 保存切換前狀態，避免同一次執行又切回去
execute if score @s c26_show matches 1 run tag @s add c26_was_on
execute if entity @s[tag=c26_was_on] run scoreboard players set @s c26_show 0
execute unless entity @s[tag=c26_was_on] run scoreboard players set @s c26_show 1

execute if score @s c26_show matches 0 run title @s actionbar {"text":""}
execute if score @s c26_show matches 0 run tellraw @s [{"text":"[座標] ","color":"dark_gray"},{"text":"已關閉","color":"gray"}]
execute if score @s c26_show matches 1 run tellraw @s [{"text":"[座標] ","color":"dark_gray"},{"text":"已開啟","color":"green"}]

scoreboard players set @s coords 0
tag @s remove c26_was_on
