
execute unless data storage sunny_nav:ctx {slot:1} unless data storage sunny_nav:ctx {slot:2} unless data storage sunny_nav:ctx {slot:3} unless data storage sunny_nav:ctx {slot:4} unless data storage sunny_nav:ctx {slot:5} unless data storage sunny_nav:ctx {slot:6} unless data storage sunny_nav:ctx {slot:7} unless data storage sunny_nav:ctx {slot:8} run function sunny_nav:custom/invalid_slot
data remove storage sunny_nav:tp location
execute if data storage sunny_nav:ctx {slot:1} run function sunny_nav:command/shared_load
execute if data storage sunny_nav:ctx {slot:2} run function sunny_nav:command/shared_load
execute if data storage sunny_nav:ctx {slot:3} run function sunny_nav:command/shared_load
execute if data storage sunny_nav:ctx {slot:4} run function sunny_nav:command/shared_load
execute if data storage sunny_nav:ctx {slot:5} run function sunny_nav:command/shared_load
execute if data storage sunny_nav:ctx {slot:6} run function sunny_nav:command/shared_load
execute if data storage sunny_nav:ctx {slot:7} run function sunny_nav:command/shared_load
execute if data storage sunny_nav:ctx {slot:8} run function sunny_nav:command/shared_load
execute if data storage sunny_nav:tp location.set run function sunny_nav:teleport/prepare
execute unless data storage sunny_nav:tp location.set run tellraw @s [{"text":"[傳送系統] ","color":"gold"},{"text":"這個共用據點尚未設定。","color":"red"}]
