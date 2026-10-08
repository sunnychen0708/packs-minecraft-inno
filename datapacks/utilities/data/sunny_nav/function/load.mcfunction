# Internal player ID and temporary values
scoreboard objectives add sunny_id dummy
scoreboard objectives add sunny_tmp dummy

# Original commands
scoreboard objectives add sethome trigger
scoreboard objectives add home trigger
scoreboard objectives add setmine trigger
scoreboard objectives add mine trigger
scoreboard objectives add setvillage trigger
scoreboard objectives add village trigger
scoreboard objectives add setportal trigger
scoreboard objectives add portal trigger
scoreboard objectives add settemp trigger
scoreboard objectives add temp trigger

# Custom waypoint commands
scoreboard objectives add plist trigger
scoreboard objectives add pset trigger
scoreboard objectives add pgo trigger
scoreboard objectives add slist trigger
scoreboard objectives add sset trigger
scoreboard objectives add sgo trigger
scoreboard objectives add prename trigger
scoreboard objectives add srename trigger
scoreboard objectives add back trigger
scoreboard objectives add deathloc trigger

# Death-location tracking (new in v3.0)
scoreboard objectives add sunny_deaths deathCount
scoreboard objectives add sunny_dseen dummy

data modify storage sunny_nav:meta version set value "26.3-3.7"

# Remove obsolete v3.0 shared slots 9-16 (confirmed unused)
data remove storage sunny_nav:shared s9
data remove storage sunny_nav:shared s10
data remove storage sunny_nav:shared s11
data remove storage sunny_nav:shared s12
data remove storage sunny_nav:shared s13
data remove storage sunny_nav:shared s14
data remove storage sunny_nav:shared s15
data remove storage sunny_nav:shared s16
