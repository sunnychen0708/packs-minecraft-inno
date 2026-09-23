# Give every player a persistent internal ID
execute as @a unless score @s sunny_id matches 1.. run function sunny_nav:player/init

# Allow non-OP players to use /trigger
scoreboard players enable @a sethome
scoreboard players enable @a home
scoreboard players enable @a setmine
scoreboard players enable @a mine
scoreboard players enable @a setvillage
scoreboard players enable @a village
scoreboard players enable @a setportal
scoreboard players enable @a portal
scoreboard players enable @a settemp
scoreboard players enable @a temp
scoreboard players enable @a plist
scoreboard players enable @a pset
scoreboard players enable @a pgo
scoreboard players enable @a slist
scoreboard players enable @a sset
scoreboard players enable @a sgo
scoreboard players enable @a prename
scoreboard players enable @a srename
scoreboard players enable @a back
scoreboard players enable @a deathloc

# Initialize death counter baseline for old/new players without recording historical deaths
execute as @a unless score @s sunny_dseen matches -2147483648..2147483647 run function sunny_nav:death/init
# Capture the location on the tick when deathCount increases
execute as @a if score @s sunny_deaths > @s sunny_dseen at @s run function sunny_nav:death/capture

# Handle original commands
execute as @a[scores={sethome=1..}] at @s run function sunny_nav:set/home
execute as @a[scores={home=1..}] at @s run function sunny_nav:goto/home
execute as @a[scores={setmine=1..}] at @s run function sunny_nav:set/mine
execute as @a[scores={mine=1..}] at @s run function sunny_nav:goto/mine
execute as @a[scores={setvillage=1..}] at @s run function sunny_nav:set/village
execute as @a[scores={village=1..}] at @s run function sunny_nav:goto/village
execute as @a[scores={setportal=1..}] at @s run function sunny_nav:set/portal
execute as @a[scores={portal=1..}] at @s run function sunny_nav:goto/portal
execute as @a[scores={settemp=1..}] at @s run function sunny_nav:set/temp
execute as @a[scores={temp=1..}] at @s run function sunny_nav:goto/temp

# Handle custom waypoint commands
execute as @a[scores={plist=1..}] at @s run function sunny_nav:custom/personal/list
execute as @a[scores={pset=1..}] at @s run function sunny_nav:custom/personal/set
execute as @a[scores={pgo=1..}] at @s run function sunny_nav:custom/personal/goto
execute as @a[scores={slist=1..}] at @s run function sunny_nav:custom/shared/list
execute as @a[scores={sset=1..}] at @s run function sunny_nav:custom/shared/set
execute as @a[scores={sgo=1..}] at @s run function sunny_nav:custom/shared/goto
execute as @a[scores={prename=1..}] at @s run function sunny_nav:custom/personal/rename
execute as @a[scores={srename=1..}] at @s run function sunny_nav:custom/shared/rename
execute as @a[scores={back=1..}] at @s run function sunny_nav:back/goto
execute as @a[scores={deathloc=1..}] at @s run function sunny_nav:death/goto
