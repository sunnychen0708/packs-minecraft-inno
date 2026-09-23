execute store result storage sunny_nav:ctx slot int 1 run scoreboard players get @s sgo
scoreboard players set @s sgo 0
data remove storage sunny_nav:tp location
function sunny_nav:macro/load_shared with storage sunny_nav:ctx
execute if data storage sunny_nav:tp location.set run function sunny_nav:teleport/prepare
execute unless data storage sunny_nav:tp location.set run tellraw @s [{"text":"[傳送系統] ","color":"gold"},{"text":"這個共用據點尚未設定。","color":"red"}]
