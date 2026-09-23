scoreboard objectives add wh_viewpage trigger
execute unless data storage warehouse:migration queue run data modify storage warehouse:migration queue set value []
data modify storage warehouse:meta v30 set value 1b
