function mcc:flip/cleanup_forceload
function mcc:history/sync_flags
scoreboard players set @s mcc_usel 0
tellraw @s [{"text":"[Copy/Paste] Flip 前 Undo 備份失敗，沒有修改世界；既有 Undo 歷史仍保留。","color":"red"}]
return fail
