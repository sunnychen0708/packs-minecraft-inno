# The transformed structure is staged away from the Work source so a structure-block save
# never races with us clearing its own source in same-tick multiplayer edits.
$execute in minecraft:overworld run forceload add $(wbx) 20000600 $(stage_wbx2) $(stage_wbz2)
$execute in minecraft:overworld run fill $(wbx) 0 20000600 $(stage_wbx2) $(wby2) $(stage_wbz2) minecraft:air strict
$execute in minecraft:overworld store success score @s mcc_ok run place template mcc:work_$(id) $(spx) 0 $(spz) $(erot) $(emir) 1.0 0 strict
$execute in minecraft:overworld run forceload remove $(wbx) 20000600 $(stage_wbx2) $(stage_wbz2)
return 1
