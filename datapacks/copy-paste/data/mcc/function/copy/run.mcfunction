execute store success score @s mcc_tmp run function mcc:copy/snapshot
execute unless score @s mcc_tmp matches 1 run return fail
function mcc:blueprint/clear_internal
scoreboard players set @s mcc_cliptype 1
tellraw @s [{"text":"[Copy/Paste] 已複製。用 /trigger v 建立 Blueprint；確認後用 /trigger build 從材料箱施工。","color":"green"}]
return 1
