execute if score @s mcc_mir matches 0 run tellraw @s [{"text":"[Copy/Paste] 鏡像已設為：無。","color":"green"}]
execute if score @s mcc_mir matches 1 run tellraw @s [{"text":"[Copy/Paste] 鏡像已設為：X。","color":"green"}]
execute if score @s mcc_mir matches 2 run tellraw @s [{"text":"[Copy/Paste] 鏡像已設為：Z。","color":"green"}]
