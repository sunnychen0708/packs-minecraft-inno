tellraw @s [{"text":"[Copy/Paste] 警告：目前位置將覆蓋 ","color":"red"},{"score":{"name":"@s","objective":"mcc_bpover"},"color":"yellow"},{"text":" 個既有非空氣方塊。","color":"red"}]
tellraw @s [{"text":"[再次施工確認]","color":"green","click_event":{"action":"run_command","command":"/trigger build"}}]
scoreboard players set @s mcc_buildconfirm 1
return fail
