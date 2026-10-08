
data remove storage sunny_nav:ctx name
data remove storage sunny_nav:tp location
function sunny_nav:macro/load_shared with storage sunny_nav:ctx
execute if data storage sunny_nav:tp location.set if data storage sunny_nav:tp location.name run data modify storage sunny_nav:ctx name set from storage sunny_nav:tp location.name
execute if data storage sunny_nav:tp location.set unless data storage sunny_nav:ctx name run function sunny_nav:macro/default_shared_name with storage sunny_nav:ctx
execute if data storage sunny_nav:tp location.set run function sunny_nav:custom/shared/save
execute unless data storage sunny_nav:tp location.set run function sunny_nav:custom/shared/set_prompt
