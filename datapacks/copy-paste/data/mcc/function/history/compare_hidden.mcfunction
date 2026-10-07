# Exact fast path. When only state differs, fall back to an ID/NBT comparison.
# Regions above #cmp_vol_max keep the exact-match rule so the scan fits in one tick.
scoreboard players set @s mcc_ok 0
scoreboard players set #cmp_big mcc_id 0
scoreboard players set #cmp_work mcc_id 0
$execute in minecraft:overworld run forceload add $(ex) $(ez) $(ex2) $(ez2)
$execute in minecraft:overworld run forceload add $(cx) $(cz) $(cx2) $(cz2)
$execute in minecraft:overworld if blocks $(ex) 0 $(ez) $(ex2) $(ey2) $(ez2) $(cx) 0 $(cz) all run scoreboard players set @s mcc_ok 1
execute unless score @s mcc_ok matches 1 run function mcc:history/compare_volume
execute unless score @s mcc_ok matches 1 if score #cmp_big mcc_id matches 0 run function mcc:history/compare_hidden_state
$execute in minecraft:overworld run forceload remove $(ex) $(ez) $(ex2) $(ez2)
$execute in minecraft:overworld run forceload remove $(cx) $(cz) $(cx2) $(cz2)
execute if score @s mcc_ok matches 1 run return 1
return fail
