execute store success score @s mcc_tmp run function mcc:move/restore_failed
function mcc:move/cleanup_forceload
execute if score @s mcc_tmp matches 1 run tellraw @s [{"text":"[Copy/Paste] Rotate 清除來源失敗；已完整還原。","color":"yellow"}]
execute unless score @s mcc_tmp matches 1 run tellraw @s [{"text":"[Copy/Paste] Rotate 清除來源失敗，而且自動還原也失敗。Undo 備份已保留。","color":"red","bold":true}]
return fail
