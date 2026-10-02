execute if score @s mcc_ucnt matches 1.. run return run function mcc:history/undo
execute if score @s mcc_undo matches 1 run return run function mcc:undo/legacy_run
tellraw @s [{"text":"[Copy/Paste] 沒有可 Undo 的世界修改。","color":"red"}]
return fail
