scoreboard players set #compact_active wh_tmp 0
scoreboard players operation #compact_target wh_tmp = #compact_code wh_tmp
execute if score #compact_target wh_tmp matches 1.. run scoreboard players add #compact_target wh_tmp 9
execute store result storage warehouse:runtime compact_dispatch.target int 1 run scoreboard players get #compact_target wh_tmp
execute if score #compact_code wh_tmp matches 0 if data storage warehouse:chests c00{registered:1b,valid:1b} run function warehouse:compact/load_code with storage warehouse:chests c00
execute if score #compact_code wh_tmp matches 1..60 run function warehouse:compact/dispatch_code with storage warehouse:runtime compact_dispatch
execute if score #compact_active wh_tmp matches 0 run scoreboard players set #compact_slot wh_tmp 53
scoreboard players add #compact_slot wh_tmp 1
execute if score #compact_slot wh_tmp matches 54.. run scoreboard players set #compact_slot wh_tmp 0
execute if score #compact_slot wh_tmp matches 0 run scoreboard players add #compact_code wh_tmp 1
execute if score #compact_code wh_tmp matches 61.. run scoreboard players set #compact_code wh_tmp 0
