tellraw @s [{"text":"[Copy/Paste] Blueprint 材料表","color":"gold"}]
tellraw @s [{"text":"尺寸：","color":"gray"},{"score":{"name":"@s","objective":"mcc_sx"},"color":"white"},{"text":" × ","color":"gray"},{"score":{"name":"@s","objective":"mcc_sy"},"color":"white"},{"text":" × ","color":"gray"},{"score":{"name":"@s","objective":"mcc_sz"},"color":"white"},{"text":"；可能覆蓋：","color":"gray"},{"score":{"name":"@s","objective":"mcc_bpover"},"color":"yellow"},{"text":" 個既有方塊","color":"gray"}]
execute store result storage mcc:temp pid int 1 run scoreboard players get @s mcc_id
function mcc:materials/report_all_init with storage mcc:temp
tellraw @s [{"text":"缺料種類：","color":"gray"},{"score":{"name":"@s","objective":"mcc_matkind"},"color":"yellow"},{"text":"；總缺少：","color":"gray"},{"score":{"name":"@s","objective":"mcc_mattotal"},"color":"yellow"}]
return 1
