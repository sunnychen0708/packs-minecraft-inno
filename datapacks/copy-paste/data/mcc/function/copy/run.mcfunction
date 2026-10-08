execute store success score @s mcc_tmp run function mcc:copy/snapshot
execute unless score @s mcc_tmp matches 1 run return fail
scoreboard players set @s mcc_cliptype 1
tellraw @s [{"text":"[Copy/Paste] 已複製。/trigger v 只會建立 Blueprint 預覽，不會生成真實方塊。","color":"green"}]
return 1
