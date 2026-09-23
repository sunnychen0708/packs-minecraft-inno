# 新玩家預設開啟
execute as @a unless score @s c26_show matches 0..1 run scoreboard players set @s c26_show 1

# 允許所有玩家使用 /trigger coords
scoreboard players enable @a coords
execute as @a[scores={coords=1..}] run function coords:toggle

# 僅替已開啟顯示的玩家更新並顯示座標
execute as @a[scores={c26_show=1}] store result score @s c26_x run data get entity @s Pos[0] 1
execute as @a[scores={c26_show=1}] store result score @s c26_y run data get entity @s Pos[1] 1
execute as @a[scores={c26_show=1}] store result score @s c26_z run data get entity @s Pos[2] 1
execute as @a[scores={c26_show=1}] run title @s actionbar [{"score":{"name":"@s","objective":"c26_x"},"color":"white"},{"text":" / ","color":"gray"},{"score":{"name":"@s","objective":"c26_y"},"color":"white"},{"text":" / ","color":"gray"},{"score":{"name":"@s","objective":"c26_z"},"color":"white"}]
