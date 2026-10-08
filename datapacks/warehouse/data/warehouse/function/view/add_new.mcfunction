$data modify storage warehouse:runtime viewer.new set value {id:"$(id)",name:"$(id)",count:0}
$data modify storage warehouse:runtime viewer.new.name set from storage warehouse:names map."$(id)"
execute store result storage warehouse:runtime viewer.new.count int 1 run scoreboard players get @s wh_viewcnt
data modify storage warehouse:runtime viewer.totals append from storage warehouse:runtime viewer.new
