tellraw @s [{"text":"[Copy/Paste] 材料不足，未施工；Blueprint 已保留。","color":"red"}]
tellraw @s [{"text":"缺少材料：","color":"gold"}]
execute store result storage mcc:temp pid int 1 run scoreboard players get @s mcc_id
function mcc:materials/report_init with storage mcc:temp
tellraw @s [{"text":"共缺少 ","color":"gray"},{"score":{"name":"@s","objective":"mcc_matkind"},"color":"yellow"},{"text":" 種、","color":"gray"},{"score":{"name":"@s","objective":"mcc_mattotal"},"color":"yellow"},{"text":" 個物品。","color":"gray"}]
return 1
