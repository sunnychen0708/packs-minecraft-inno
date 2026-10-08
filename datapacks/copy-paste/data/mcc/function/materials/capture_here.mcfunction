kill @e[type=minecraft:marker,tag=mcc_mat_pos,distance=..2]
execute align xyz run summon minecraft:marker ~ ~ ~ {Tags:["mcc_mat_pos"]}
data modify storage mcc:temp box set value {}
execute store result storage mcc:temp box.x int 1 run data get entity @e[type=minecraft:marker,tag=mcc_mat_pos,limit=1,sort=nearest] Pos[0] 1
execute store result storage mcc:temp box.y int 1 run data get entity @e[type=minecraft:marker,tag=mcc_mat_pos,limit=1,sort=nearest] Pos[1] 1
execute store result storage mcc:temp box.z int 1 run data get entity @e[type=minecraft:marker,tag=mcc_mat_pos,limit=1,sort=nearest] Pos[2] 1
execute if dimension minecraft:overworld run data modify storage mcc:temp box.dimension set value "minecraft:overworld"
execute if dimension minecraft:the_nether run data modify storage mcc:temp box.dimension set value "minecraft:the_nether"
execute if dimension minecraft:the_end run data modify storage mcc:temp box.dimension set value "minecraft:the_end"
kill @e[type=minecraft:marker,tag=mcc_mat_pos,distance=..2]
return 1
