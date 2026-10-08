execute if score @s mcc_ucnt matches 1.. run return run function mcc:history/undo
execute if score @s mcc_undo matches 1 run scoreboard players set @s mcc_tmp 1
execute unless score @s mcc_undo matches 1 run scoreboard players set @s mcc_tmp 0
execute if score @s mcc_tmp matches 1 run scoreboard players set @s mcc_undo 0
execute if score @s mcc_tmp matches 1 run scoreboard players set @s mcc_redo 0
execute if score @s mcc_tmp matches 1 run tellraw @s [{"text":"[Copy/Paste] 舊版 Undo 沒有防複製安全快照，已作廢；請從下一次世界編輯開始建立新的安全歷史。","color":"red"}]
execute if score @s mcc_tmp matches 1 run return fail
tellraw @s [{"text":"[Copy/Paste] 沒有可 Undo 的世界修改。","color":"red"}]
return fail
