scoreboard players set @s mcc_mask 1
tellraw @s [{"text":"[Copy/Paste] 貼上模式：保留原方塊（複製範圍裡的空氣不會清掉目標位置的方塊）。","color":"green"}]
function mcc:blueprint/rebuild_if_active
