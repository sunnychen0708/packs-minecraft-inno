execute if score @s mcc_rcnt matches 1.. run return run function mcc:history/redo
execute if score @s mcc_redo matches 1 run return run function mcc:redo/legacy_run
tellraw @s [{"text":"[Copy/Paste] 沒有可 Redo 的狀態。","color":"red"}]
return fail
