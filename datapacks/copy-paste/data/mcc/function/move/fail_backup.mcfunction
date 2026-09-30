function mcc:move/cleanup_forceload
scoreboard players set @s mcc_undo 0
scoreboard players set @s mcc_usel 0
tellraw @s [{"text":"[Copy/Paste] Move 前 Undo 備份失敗，沒有修改世界；這次備份失敗也使上一層 Undo 失效。","color":"red"}]
return fail
