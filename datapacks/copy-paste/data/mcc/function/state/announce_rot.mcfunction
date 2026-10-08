execute if score @s mcc_rot matches 0 run tellraw @s [{"text":"[Copy/Paste] 旋轉已設為 0°。","color":"green"}]
execute if score @s mcc_rot matches 1 run tellraw @s [{"text":"[Copy/Paste] 旋轉已設為 90°。","color":"green"}]
execute if score @s mcc_rot matches 2 run tellraw @s [{"text":"[Copy/Paste] 旋轉已設為 180°。","color":"green"}]
execute if score @s mcc_rot matches 3 run tellraw @s [{"text":"[Copy/Paste] 旋轉已設為 270°。","color":"green"}]
