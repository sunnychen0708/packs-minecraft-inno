execute store result storage sunny_nav:ctx slot int 1 run scoreboard players get @s pgo
scoreboard players set @s pgo 0
execute store result storage sunny_nav:ctx id int 1 run scoreboard players get @s sunny_id
data remove storage sunny_nav:tp location
function sunny_nav:macro/load_personal with storage sunny_nav:ctx
execute if data storage sunny_nav:tp location.set run function sunny_nav:teleport/prepare
execute unless data storage sunny_nav:tp location.set run tellraw @s [{"text":"[傳送系統] ","color":"gold"},{"text":"這個個人據點尚未設定。","color":"red"}]
