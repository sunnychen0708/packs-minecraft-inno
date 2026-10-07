# Resolve the current hidden-buffer block ID without caring about its state.
data modify storage mcc:temp cur_bid set value "minecraft:unknown"
$execute in minecraft:overworld if block $(tx) $(ty) $(tz) #minecraft:air run data modify storage mcc:temp cur_bid set value "minecraft:air"
scoreboard players set @s mcc_cmpmode 2
$execute in minecraft:overworld positioned $(tx) $(ty) $(tz) unless block ~ ~ ~ #minecraft:air run function mcc:blueprint/generated/root
scoreboard players set @s mcc_cmpmode 0

# Convert hidden-buffer coordinates back to the real world.
$scoreboard players set #diag_x mcc_id $(sx)
scoreboard players operation #diag_x mcc_id -= #cmp_ex mcc_id
scoreboard players operation #diag_x mcc_id += #diag_ox mcc_id
$scoreboard players set #diag_y mcc_id $(sy)
scoreboard players operation #diag_y mcc_id += #diag_oy mcc_id
$scoreboard players set #diag_z mcc_id $(sz)
scoreboard players operation #diag_z mcc_id -= #cmp_ez mcc_id
scoreboard players operation #diag_z mcc_id += #diag_oz mcc_id

# kind 1 = wrong/missing block ID, 2 = extra block where air is expected,
# kind 3 = same block ID but Block Entity/NBT differs.
data modify storage mcc:temp diag_entry set value {kind:1}
data modify storage mcc:temp diag_entry.expected set from storage mcc:temp cmp_bid
data modify storage mcc:temp diag_entry.current set from storage mcc:temp cur_bid
execute store result storage mcc:temp diag_entry.x int 1 run scoreboard players get #diag_x mcc_id
execute store result storage mcc:temp diag_entry.y int 1 run scoreboard players get #diag_y mcc_id
execute store result storage mcc:temp diag_entry.z int 1 run scoreboard players get #diag_z mcc_id
$execute in minecraft:overworld if block $(sx) $(sy) $(sz) #minecraft:air run data modify storage mcc:temp diag_entry.kind set value 2
$execute in minecraft:overworld unless block $(sx) $(sy) $(sz) #minecraft:air if block $(tx) $(ty) $(tz) $(cmp_bid) run data modify storage mcc:temp diag_entry.kind set value 3

scoreboard players add @s mcc_diagcount 1
execute if data storage mcc:temp diag_entry{kind:1} run scoreboard players add @s mcc_diagmissing 1
execute if data storage mcc:temp diag_entry{kind:2} run scoreboard players add @s mcc_diagremove 1
execute if data storage mcc:temp diag_entry{kind:3} run scoreboard players add @s mcc_diagcontent 1
execute if data storage mcc:temp diag_entry{kind:1} run function mcc:history/diag_add_need with storage mcc:temp

# Keep chat bounded. Repairing these 20 and retrying exposes the next batch.
execute if score @s mcc_diagshown matches ..19 run data modify storage mcc:temp diag.coords append from storage mcc:temp diag_entry
execute if score @s mcc_diagshown matches ..19 run scoreboard players add @s mcc_diagshown 1
return 1
