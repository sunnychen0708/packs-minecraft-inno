
execute store result storage sunny_nav:ctx slot int 1 run scoreboard players get @s sset
scoreboard players set @s sset 0
execute unless data storage sunny_nav:ctx {slot:1} unless data storage sunny_nav:ctx {slot:2} unless data storage sunny_nav:ctx {slot:3} unless data storage sunny_nav:ctx {slot:4} unless data storage sunny_nav:ctx {slot:5} unless data storage sunny_nav:ctx {slot:6} unless data storage sunny_nav:ctx {slot:7} unless data storage sunny_nav:ctx {slot:8} run function sunny_nav:custom/invalid_slot
execute if data storage sunny_nav:ctx {slot:1} run function sunny_nav:custom/shared/set_valid
execute if data storage sunny_nav:ctx {slot:2} run function sunny_nav:custom/shared/set_valid
execute if data storage sunny_nav:ctx {slot:3} run function sunny_nav:custom/shared/set_valid
execute if data storage sunny_nav:ctx {slot:4} run function sunny_nav:custom/shared/set_valid
execute if data storage sunny_nav:ctx {slot:5} run function sunny_nav:custom/shared/set_valid
execute if data storage sunny_nav:ctx {slot:6} run function sunny_nav:custom/shared/set_valid
execute if data storage sunny_nav:ctx {slot:7} run function sunny_nav:custom/shared/set_valid
execute if data storage sunny_nav:ctx {slot:8} run function sunny_nav:custom/shared/set_valid
