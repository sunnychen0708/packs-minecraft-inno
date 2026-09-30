execute store success score @s mcc_tmp run function mcc:flip/restore_failed
function mcc:flip/cleanup_forceload
execute if score @s mcc_tmp matches 1 run tellraw @s [{"text":"[Copy/Paste] Flip Z 失敗；已完整還原到操作前狀態。","color":"yellow"}]
execute unless score @s mcc_tmp matches 1 run tellraw @s [{"text":"[Copy/Paste] Flip Z 失敗，而且自動還原也失敗。Undo 備份已保留，請再用 /trigger undo 嘗試還原。","color":"red","bold":true}]
return fail
