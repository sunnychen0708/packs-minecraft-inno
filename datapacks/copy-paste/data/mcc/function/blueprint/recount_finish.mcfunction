execute store result storage mcc:temp x1 int 1 run scoreboard players get @s mcc_bpsx0
execute store result storage mcc:temp z1 int 1 run scoreboard players get @s mcc_bpsz0
execute store result storage mcc:temp x2 int 1 run scoreboard players get @s mcc_bpsx2
execute store result storage mcc:temp z2 int 1 run scoreboard players get @s mcc_bpsz2
function mcc:blueprint/forceload_remove with storage mcc:temp
scoreboard players set @s mcc_bpover_scan 0
tellraw @s [{"text":"[Copy/Paste] Blueprint 覆蓋檢查更新完成；可能覆蓋 ","color":"gray"},{"score":{"name":"@s","objective":"mcc_bpover"},"color":"yellow"},{"text":" 個既有非空氣方塊。","color":"gray"}]
return 1
