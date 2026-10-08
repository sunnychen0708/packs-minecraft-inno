function mcc:move/cleanup_forceload
scoreboard players set @s mcc_undo 0
scoreboard players set @s mcc_usel 0
tellraw @s [{"text":"[Copy/Paste] Rotate 前 Undo 備份失敗，沒有修改世界。","color":"red"}]
return fail
