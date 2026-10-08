scoreboard players operation @s mcc_bpsx = @s mcc_bpsx0
scoreboard players operation @s mcc_bpsy = @s mcc_bpsy0
scoreboard players operation @s mcc_bpsz = @s mcc_bpsz0
scoreboard players operation @s mcc_bptx = @s mcc_bptx0
scoreboard players operation @s mcc_bpty = @s mcc_bpty0
scoreboard players operation @s mcc_bptz = @s mcc_bptz0
scoreboard players set @s mcc_bpscan 1
tellraw @s [{"text":"[Copy/Paste] 正在建立共享 Blueprint 預覽；這不會生成任何真實方塊。","color":"aqua"}]
return 1
