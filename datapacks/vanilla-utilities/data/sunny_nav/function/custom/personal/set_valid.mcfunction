
execute store result storage sunny_nav:ctx id int 1 run scoreboard players get @s sunny_id
data remove storage sunny_nav:ctx name
data remove storage sunny_nav:tp location
function sunny_nav:macro/load_personal with storage sunny_nav:ctx
execute if data storage sunny_nav:tp location.set if data storage sunny_nav:tp location.name run data modify storage sunny_nav:ctx name set from storage sunny_nav:tp location.name
execute if data storage sunny_nav:tp location.set unless data storage sunny_nav:ctx name run function sunny_nav:macro/default_personal_name with storage sunny_nav:ctx
execute if data storage sunny_nav:tp location.set run function sunny_nav:custom/personal/save
execute unless data storage sunny_nav:tp location.set run function sunny_nav:custom/personal/set_prompt
