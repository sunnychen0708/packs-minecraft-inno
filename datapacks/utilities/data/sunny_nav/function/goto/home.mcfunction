scoreboard players set @s home 0
execute store result storage sunny_nav:ctx id int 1 run scoreboard players get @s sunny_id
data remove storage sunny_nav:tp location
function sunny_nav:macro/load_home with storage sunny_nav:ctx
execute if data storage sunny_nav:tp location.set run function sunny_nav:teleport/prepare
execute unless data storage sunny_nav:tp location.set run tellraw @s [{"text":"[傳送系統] ","color":"gold"},{"text":"你還沒有設定家。請先輸入 /trigger sethome","color":"red"}]
