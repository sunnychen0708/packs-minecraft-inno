execute store success score @s mcc_tmp run function mcc:copy/snapshot
execute unless score @s mcc_tmp matches 1 run return fail
scoreboard players operation @s mcc_canchor = @s mcc_hasa
function mcc:state/bp_offset_init
function mcc:blueprint/clear_internal
scoreboard players set @s mcc_cliptype 1
tellraw @s [{"text":"[Copy/Paste] 已複製。用 /trigger v 建立 Blueprint；確認後用 /trigger build 施工（先用背包的材料，不夠再從 Warehouse 扣）。","color":"green"}]
return 1
