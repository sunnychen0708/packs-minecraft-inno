scoreboard players add #next mcc_id 1
scoreboard players operation @s mcc_id = #next mcc_id
scoreboard players set @s mcc_has1 0
scoreboard players set @s mcc_has2 0
scoreboard players set @s mcc_hasa 0
scoreboard players set @s mcc_clip 0
scoreboard players set @s mcc_mask 0
tellraw @s [{"text":"[Copy/Paste] ","color":"gold"},{"text":"已建立你的個人 Clipboard。","color":"gray"}]
