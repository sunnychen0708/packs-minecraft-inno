# Hidden one-slot probe used only to read the vanilla default max stack size.
scoreboard players set #api_probe_forced wh_tmp 0
execute in minecraft:overworld store success score #api_probe_forced wh_tmp run forceload query 19990008 19990008
execute if score #api_probe_forced wh_tmp matches 0 in minecraft:overworld run forceload add 19990008 19990008
execute in minecraft:overworld run setblock 19990008 64 19990008 minecraft:barrel
$item replace block 19990008 64 19990008 container.0 with $(item_id) 1
scoreboard players set #api_max wh_tmp 64
execute if items block 19990008 64 19990008 container.0 *[minecraft:max_stack_size=16] run scoreboard players set #api_max wh_tmp 16
execute if items block 19990008 64 19990008 container.0 *[minecraft:max_stack_size=1] run scoreboard players set #api_max wh_tmp 1
execute in minecraft:overworld run setblock 19990008 64 19990008 air
execute if score #api_probe_forced wh_tmp matches 0 in minecraft:overworld run forceload remove 19990008 19990008
return 1
