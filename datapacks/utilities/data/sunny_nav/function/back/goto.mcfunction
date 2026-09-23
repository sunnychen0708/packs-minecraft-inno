
scoreboard players set @s back 0
execute store result storage sunny_nav:ctx id int 1 run scoreboard players get @s sunny_id
data remove storage sunny_nav:tp location
function sunny_nav:macro/load_back with storage sunny_nav:ctx
execute if data storage sunny_nav:tp location.set run function sunny_nav:teleport/prepare
execute unless data storage sunny_nav:tp location.set run tellraw @s [{"text":"[傳送系統] ","color":"gold"},{"text":"目前沒有可返回的位置。先使用一次據點傳送後再試。","color":"red"}]
