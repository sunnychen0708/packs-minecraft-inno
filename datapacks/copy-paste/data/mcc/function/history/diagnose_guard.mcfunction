# Called only after the fast safety guard has already failed.
# Re-scan synchronously, ignoring block states but recording true block-ID/NBT differences.
data modify storage mcc:temp diag set value {need:{},need_items:[],coords:[],materials:{},material_items:[]}
scoreboard players set @s mcc_diagcount 0
scoreboard players set @s mcc_diagshown 0
scoreboard players set @s mcc_diagmissing 0
scoreboard players set @s mcc_diagremove 0
scoreboard players set @s mcc_diagcontent 0
scoreboard players set @s mcc_cmpdiag 1
$execute in minecraft:overworld run forceload add $(ex) $(ez) $(ex2) $(ez2)
$execute in minecraft:overworld run forceload add $(cx) $(cz) $(cx2) $(cz2)
function mcc:history/compare_hidden_state
scoreboard players set @s mcc_cmpdiag 0
function mcc:history/diag_resolve_materials
$execute in minecraft:overworld run forceload remove $(ex) $(ez) $(ex2) $(ez2)
$execute in minecraft:overworld run forceload remove $(cx) $(cz) $(cx2) $(cz2)
scoreboard players set @s mcc_ok 0
return 1
