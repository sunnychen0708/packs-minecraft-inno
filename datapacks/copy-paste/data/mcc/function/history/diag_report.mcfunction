execute if data storage mcc:temp diag.material_items[0].id run tellraw @s [{"text":"需要補回：","color":"gold"}]
execute if data storage mcc:temp diag.material_items[0].id run function mcc:history/diag_report_need_init
execute if score @s mcc_diagremove matches 1.. run tellraw @s [{"text":"需要移除：","color":"gold"},{"score":{"name":"@s","objective":"mcc_diagremove"},"color":"white"},{"text":" 個多出的方塊。","color":"gray"}]
execute if score @s mcc_diagcontent matches 1.. run tellraw @s [{"text":"Block Entity／容器內容不同：","color":"gold"},{"score":{"name":"@s","objective":"mcc_diagcontent"},"color":"white"},{"text":" 個位置；需把內容也還原，只有同種方塊不夠。","color":"gray"}]
execute if score @s mcc_diagshown matches 1.. if score #diag_dim mcc_id matches 1 run tellraw @s [{"text":"異常位置（主世界，最多 20 筆）：","color":"gold"}]
execute if score @s mcc_diagshown matches 1.. if score #diag_dim mcc_id matches 2 run tellraw @s [{"text":"異常位置（地獄，最多 20 筆）：","color":"gold"}]
execute if score @s mcc_diagshown matches 1.. if score #diag_dim mcc_id matches 3 run tellraw @s [{"text":"異常位置（終界，最多 20 筆）：","color":"gold"}]
execute if score @s mcc_diagshown matches 1.. run function mcc:history/diag_report_coord_init
scoreboard players operation #diag_extra mcc_tmp = @s mcc_diagcount
scoreboard players operation #diag_extra mcc_tmp -= @s mcc_diagshown
execute if score #diag_extra mcc_tmp matches 1.. run tellraw @s [{"text":"另有 ","color":"gray"},{"score":{"name":"#diag_extra","objective":"mcc_tmp"},"color":"yellow"},{"text":" 個異常位置未列出；先修好上面這批再重試，會繼續列下一批。","color":"gray"}]
execute if score #cmp_big mcc_id matches 1 run tellraw @s [{"text":"差異太多，只檢查到一部分；上面的數量不是全部。","color":"gray"}]
execute unless score @s mcc_diagcount matches 1.. run tellraw @s [{"text":"無法解析出具體差異；為安全起見仍未執行。","color":"yellow"}]
return 1
