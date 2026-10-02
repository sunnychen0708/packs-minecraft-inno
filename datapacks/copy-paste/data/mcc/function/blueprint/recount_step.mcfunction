execute if score @s mcc_bpoindex >= @s mcc_vol run scoreboard players set @s mcc_bpover_scan 0
execute unless score @s mcc_bpover_scan matches 1 run return 1
execute store result storage mcc:temp sx int 1 run scoreboard players get @s mcc_bpsx
execute store result storage mcc:temp sy int 1 run scoreboard players get @s mcc_bpsy
execute store result storage mcc:temp sz int 1 run scoreboard players get @s mcc_bpsz
execute store result storage mcc:temp tx int 1 run scoreboard players get @s mcc_bptx
execute store result storage mcc:temp ty int 1 run scoreboard players get @s mcc_bpty
execute store result storage mcc:temp tz int 1 run scoreboard players get @s mcc_bptz
function mcc:blueprint/recount_one with storage mcc:temp
scoreboard players add @s mcc_bpsx 1
scoreboard players add @s mcc_bptx 1
execute if score @s mcc_bpsx > @s mcc_bpsx2 run function mcc:blueprint/wrap_x
scoreboard players add @s mcc_bpoindex 1
execute if score @s mcc_bpoindex >= @s mcc_vol run scoreboard players set @s mcc_bpover_scan 0
execute unless score @s mcc_bpover_scan matches 1 run tellraw @s [{"text":"[Copy/Paste] Blueprint 覆蓋檢查更新完成；可能覆蓋 ","color":"gray"},{"score":{"name":"@s","objective":"mcc_bpover"},"color":"yellow"},{"text":" 個既有非空氣方塊。","color":"gray"}]
return 1
