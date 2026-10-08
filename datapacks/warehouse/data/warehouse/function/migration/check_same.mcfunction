data modify storage warehouse:migration active.skip set value 0b
execute unless data storage warehouse:migration active.source{registered:1b,valid:1b} run data modify storage warehouse:migration active.skip set value 1b
execute unless data storage warehouse:migration active.dest{registered:1b,valid:1b} run data modify storage warehouse:migration active.skip set value 1b
scoreboard players set #sdim wh_tmp 0
scoreboard players set #ddim wh_tmp 0
execute if data storage warehouse:migration active.source{dimension:"minecraft:the_nether"} run scoreboard players set #sdim wh_tmp 1
execute if data storage warehouse:migration active.source{dimension:"minecraft:the_end"} run scoreboard players set #sdim wh_tmp 2
execute if data storage warehouse:migration active.dest{dimension:"minecraft:the_nether"} run scoreboard players set #ddim wh_tmp 1
execute if data storage warehouse:migration active.dest{dimension:"minecraft:the_end"} run scoreboard players set #ddim wh_tmp 2
execute store result score #sax wh_tmp run data get storage warehouse:migration active.source.a_x 1
execute store result score #say wh_tmp run data get storage warehouse:migration active.source.a_y 1
execute store result score #saz wh_tmp run data get storage warehouse:migration active.source.a_z 1
execute store result score #sbx wh_tmp run data get storage warehouse:migration active.source.b_x 1
execute store result score #sby wh_tmp run data get storage warehouse:migration active.source.b_y 1
execute store result score #sbz wh_tmp run data get storage warehouse:migration active.source.b_z 1
execute store result score #dax wh_tmp run data get storage warehouse:migration active.dest.a_x 1
execute store result score #day wh_tmp run data get storage warehouse:migration active.dest.a_y 1
execute store result score #daz wh_tmp run data get storage warehouse:migration active.dest.a_z 1
execute store result score #dbx wh_tmp run data get storage warehouse:migration active.dest.b_x 1
execute store result score #dby wh_tmp run data get storage warehouse:migration active.dest.b_y 1
execute store result score #dbz wh_tmp run data get storage warehouse:migration active.dest.b_z 1
scoreboard players set #same1 wh_tmp 1
execute unless score #sdim wh_tmp = #ddim wh_tmp run scoreboard players set #same1 wh_tmp 0
execute unless score #sax wh_tmp = #dax wh_tmp run scoreboard players set #same1 wh_tmp 0
execute unless score #say wh_tmp = #day wh_tmp run scoreboard players set #same1 wh_tmp 0
execute unless score #saz wh_tmp = #daz wh_tmp run scoreboard players set #same1 wh_tmp 0
execute unless score #sbx wh_tmp = #dbx wh_tmp run scoreboard players set #same1 wh_tmp 0
execute unless score #sby wh_tmp = #dby wh_tmp run scoreboard players set #same1 wh_tmp 0
execute unless score #sbz wh_tmp = #dbz wh_tmp run scoreboard players set #same1 wh_tmp 0
scoreboard players set #same2 wh_tmp 1
execute unless score #sdim wh_tmp = #ddim wh_tmp run scoreboard players set #same2 wh_tmp 0
execute unless score #sax wh_tmp = #dbx wh_tmp run scoreboard players set #same2 wh_tmp 0
execute unless score #say wh_tmp = #dby wh_tmp run scoreboard players set #same2 wh_tmp 0
execute unless score #saz wh_tmp = #dbz wh_tmp run scoreboard players set #same2 wh_tmp 0
execute unless score #sbx wh_tmp = #dax wh_tmp run scoreboard players set #same2 wh_tmp 0
execute unless score #sby wh_tmp = #day wh_tmp run scoreboard players set #same2 wh_tmp 0
execute unless score #sbz wh_tmp = #daz wh_tmp run scoreboard players set #same2 wh_tmp 0
execute if score #same1 wh_tmp matches 1 run data modify storage warehouse:migration active.skip set value 1b
execute if score #same2 wh_tmp matches 1 run data modify storage warehouse:migration active.skip set value 1b
