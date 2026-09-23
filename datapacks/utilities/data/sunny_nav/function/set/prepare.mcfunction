# Prepare player ID and vanilla dimension ID
execute store result storage sunny_nav:ctx id int 1 run scoreboard players get @s sunny_id
data modify storage sunny_nav:ctx dim set value -1
data modify storage sunny_nav:ctx valid set value 0b
execute if dimension minecraft:overworld run data modify storage sunny_nav:ctx dim set value 0
execute if dimension minecraft:the_nether run data modify storage sunny_nav:ctx dim set value 1
execute if dimension minecraft:the_end run data modify storage sunny_nav:ctx dim set value 2
execute unless data storage sunny_nav:ctx {dim:-1} run data modify storage sunny_nav:ctx valid set value 1b

# Capture the block position reliably, including negative coordinates
kill @e[type=minecraft:marker,tag=sunny_nav.temp]
execute positioned as @s align xyz run summon minecraft:marker ~ ~ ~ {Tags:["sunny_nav.temp"]}
execute store result storage sunny_nav:ctx x int 1 run data get entity @e[type=minecraft:marker,tag=sunny_nav.temp,sort=nearest,limit=1,distance=..4] Pos[0] 1
execute store result storage sunny_nav:ctx y int 1 run data get entity @e[type=minecraft:marker,tag=sunny_nav.temp,sort=nearest,limit=1,distance=..4] Pos[1] 1
execute store result storage sunny_nav:ctx z int 1 run data get entity @e[type=minecraft:marker,tag=sunny_nav.temp,sort=nearest,limit=1,distance=..4] Pos[2] 1
kill @e[type=minecraft:marker,tag=sunny_nav.temp]
