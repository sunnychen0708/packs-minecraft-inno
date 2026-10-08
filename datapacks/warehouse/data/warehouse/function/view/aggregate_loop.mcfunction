data modify storage warehouse:runtime viewer.current set from storage warehouse:runtime viewer.queue[0]
execute unless data storage warehouse:runtime viewer.current.count run data modify storage warehouse:runtime viewer.current.count set value 1
execute store result score @s wh_viewcnt run data get storage warehouse:runtime viewer.current.count 1
function warehouse:view/aggregate_current with storage warehouse:runtime viewer.current
data remove storage warehouse:runtime viewer.queue[0]
execute if data storage warehouse:runtime viewer.queue[0] run function warehouse:view/aggregate_loop
