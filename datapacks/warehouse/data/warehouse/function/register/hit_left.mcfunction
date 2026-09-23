kill @e[type=minecraft:marker,tag=wh_reg_tmp,distance=..8]
execute align xyz run summon minecraft:marker ~ ~ ~ {Tags:["wh_reg_tmp","wh_reg_a"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=north] if block ~1 ~ ~ #warehouse:storage_chests[type=right,facing=north] run summon minecraft:marker ~1 ~ ~ {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=north] if block ~-1 ~ ~ #warehouse:storage_chests[type=right,facing=north] run summon minecraft:marker ~-1 ~ ~ {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=north] if block ~ ~ ~1 #warehouse:storage_chests[type=right,facing=north] run summon minecraft:marker ~ ~ ~1 {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=north] if block ~ ~ ~-1 #warehouse:storage_chests[type=right,facing=north] run summon minecraft:marker ~ ~ ~-1 {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=south] if block ~1 ~ ~ #warehouse:storage_chests[type=right,facing=south] run summon minecraft:marker ~1 ~ ~ {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=south] if block ~-1 ~ ~ #warehouse:storage_chests[type=right,facing=south] run summon minecraft:marker ~-1 ~ ~ {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=south] if block ~ ~ ~1 #warehouse:storage_chests[type=right,facing=south] run summon minecraft:marker ~ ~ ~1 {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=south] if block ~ ~ ~-1 #warehouse:storage_chests[type=right,facing=south] run summon minecraft:marker ~ ~ ~-1 {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=east] if block ~1 ~ ~ #warehouse:storage_chests[type=right,facing=east] run summon minecraft:marker ~1 ~ ~ {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=east] if block ~-1 ~ ~ #warehouse:storage_chests[type=right,facing=east] run summon minecraft:marker ~-1 ~ ~ {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=east] if block ~ ~ ~1 #warehouse:storage_chests[type=right,facing=east] run summon minecraft:marker ~ ~ ~1 {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=east] if block ~ ~ ~-1 #warehouse:storage_chests[type=right,facing=east] run summon minecraft:marker ~ ~ ~-1 {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=west] if block ~1 ~ ~ #warehouse:storage_chests[type=right,facing=west] run summon minecraft:marker ~1 ~ ~ {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=west] if block ~-1 ~ ~ #warehouse:storage_chests[type=right,facing=west] run summon minecraft:marker ~-1 ~ ~ {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=west] if block ~ ~ ~1 #warehouse:storage_chests[type=right,facing=west] run summon minecraft:marker ~ ~ ~1 {Tags:["wh_reg_tmp","wh_reg_b"]}
execute align xyz if block ~ ~ ~ #warehouse:storage_chests[type=left,facing=west] if block ~ ~ ~-1 #warehouse:storage_chests[type=right,facing=west] run summon minecraft:marker ~ ~ ~-1 {Tags:["wh_reg_tmp","wh_reg_b"]}
execute store result score @s wh_tmp if entity @e[type=minecraft:marker,tag=wh_reg_b,distance=..2]
execute if score @s wh_tmp matches 1 run function warehouse:register/candidate
execute unless score @s wh_tmp matches 1 run dialog show @s warehouse:register/result/error_partner
kill @e[type=minecraft:marker,tag=wh_reg_tmp,distance=..8]
tag @s remove wh_reg_pending
scoreboard players set @s wh_regtime 0
scoreboard players set @s wh_regdelay 0
