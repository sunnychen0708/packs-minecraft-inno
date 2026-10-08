scoreboard objectives add wh_view trigger
scoreboard objectives add wh_viewcnt dummy
function warehouse:view/init_names
data modify storage warehouse:meta v06 set value 1b
