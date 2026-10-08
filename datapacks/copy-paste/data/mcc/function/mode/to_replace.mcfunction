scoreboard players set @s mcc_mask 0
tellraw @s [{"text":"[Copy/Paste] 貼上模式：完全取代（複製範圍裡的空氣會清掉目標位置的方塊）。","color":"green"}]
function mcc:blueprint/rebuild_if_active
