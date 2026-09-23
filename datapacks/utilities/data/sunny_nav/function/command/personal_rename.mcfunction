
execute unless score @s sunny_id matches 1.. run function sunny_nav:player/init
execute store result storage sunny_nav:ctx id int 1 run scoreboard players get @s sunny_id
execute unless data storage sunny_nav:ctx {slot:1} unless data storage sunny_nav:ctx {slot:2} unless data storage sunny_nav:ctx {slot:3} unless data storage sunny_nav:ctx {slot:4} unless data storage sunny_nav:ctx {slot:5} unless data storage sunny_nav:ctx {slot:6} unless data storage sunny_nav:ctx {slot:7} unless data storage sunny_nav:ctx {slot:8} run function sunny_nav:custom/invalid_slot
data remove storage sunny_nav:tp location
function sunny_nav:macro/load_personal with storage sunny_nav:ctx
execute if data storage sunny_nav:tp location.set run function sunny_nav:macro/save_personal_name with storage sunny_nav:ctx
execute if data storage sunny_nav:tp location.set run tellraw @s [{"text":"[傳送系統] 個人據點已改名為「","color":"green"},{"nbt":"name","storage":"sunny_nav:ctx","interpret":true},{"text":"」。","color":"green"}]
execute unless data storage sunny_nav:tp location.set run tellraw @s [{"text":"[傳送系統] ","color":"gold"},{"text":"這一格尚未設定位置，請先設定位置再改名。","color":"red"}]
