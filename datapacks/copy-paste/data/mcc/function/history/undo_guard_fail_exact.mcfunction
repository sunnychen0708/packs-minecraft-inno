tellraw @s [{"text":"[Copy/Paste] 這筆操作完成後的世界已被修改；為避免資源複製，未執行 Undo。","color":"red"}]
tellraw @s [{"text":"範圍太大或差異太多，這次只接受完全一致（包含 block state）。","color":"gray"}]
scoreboard players set @s mcc_ok 0
return fail
