function mcc:materials/ensure_player
scoreboard players set @s mcc_matleft 0
execute store result storage mcc:temp pid int 1 run scoreboard players get @s mcc_id
function mcc:materials/list_do with storage mcc:temp
tellraw @s [{"text":"[Copy/Paste] 目前已註冊 ","color":"gold"},{"score":{"name":"@s","objective":"mcc_matleft"},"color":"yellow"},{"text":" 個材料容器來源（大箱子兩半各算一個來源）。","color":"gray"}]
return 1
