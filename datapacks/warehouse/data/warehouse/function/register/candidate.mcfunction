data remove storage warehouse:runtime candidate
execute store result storage warehouse:runtime candidate.code int 1 run scoreboard players get @s wh_target
execute store result storage warehouse:runtime candidate.a_x int 1 run data get entity @e[type=minecraft:marker,tag=wh_reg_a,sort=nearest,limit=1,distance=..2] Pos[0] 1
execute store result storage warehouse:runtime candidate.a_y int 1 run data get entity @e[type=minecraft:marker,tag=wh_reg_a,sort=nearest,limit=1,distance=..2] Pos[1] 1
execute store result storage warehouse:runtime candidate.a_z int 1 run data get entity @e[type=minecraft:marker,tag=wh_reg_a,sort=nearest,limit=1,distance=..2] Pos[2] 1
execute store result storage warehouse:runtime candidate.b_x int 1 run data get entity @e[type=minecraft:marker,tag=wh_reg_b,sort=nearest,limit=1,distance=..2] Pos[0] 1
execute store result storage warehouse:runtime candidate.b_y int 1 run data get entity @e[type=minecraft:marker,tag=wh_reg_b,sort=nearest,limit=1,distance=..2] Pos[1] 1
execute store result storage warehouse:runtime candidate.b_z int 1 run data get entity @e[type=minecraft:marker,tag=wh_reg_b,sort=nearest,limit=1,distance=..2] Pos[2] 1
execute if dimension minecraft:overworld run data modify storage warehouse:runtime candidate.dimension set value "minecraft:overworld"
execute if dimension minecraft:the_nether run data modify storage warehouse:runtime candidate.dimension set value "minecraft:the_nether"
execute if dimension minecraft:the_end run data modify storage warehouse:runtime candidate.dimension set value "minecraft:the_end"
execute unless data storage warehouse:runtime candidate.dimension run dialog show @s warehouse:register/result/error_dimension
execute if data storage warehouse:runtime candidate.dimension run function warehouse:register/save with storage warehouse:runtime candidate
