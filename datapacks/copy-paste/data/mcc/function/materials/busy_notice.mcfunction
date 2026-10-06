# A material check / Build / material Redo is running: the world-edit triggers
# below are held back by tick.mcfunction. Tell the player instead of dropping them silently.
scoreboard players set @s mcc_tmp 0
execute if score @s c matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s x matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s v matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s undo matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s redo matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s right matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s left matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s up matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s down matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s forward matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s backward matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s flipx matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s flipz matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s rotate90 matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s rotate180 matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s rotate270 matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpleft matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpright matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpforward matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpbackward matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpup matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpdown matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpturnright matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpturnleft matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpflip matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpflipfb matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s bpreset matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s turnright matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s turnleft matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s flip matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s flipfb matches 1.. run scoreboard players set @s mcc_tmp 1
execute if score @s mcc_tmp matches 1 run tellraw @s [{"text":"[Copy/Paste] 材料檢查／施工正在進行，這個指令沒有執行；完成後請再試一次。","color":"yellow"}]
