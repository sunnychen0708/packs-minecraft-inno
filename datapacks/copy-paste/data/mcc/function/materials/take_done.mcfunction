scoreboard players set @s mcc_matmiss 0
execute store result storage mcc:temp pid int 1 run scoreboard players get @s mcc_id
function mcc:materials/check_remain_init with storage mcc:temp
execute if score @s mcc_matmiss matches 1 run tellraw @s [{"text":"[Copy/Paste] 材料來源在施工期間被改動；本次不施工，已扣材料會退給你。","color":"red"}]
execute if score @s mcc_matmiss matches 1 run function mcc:materials/refund_taken_start
execute if score @s mcc_matmiss matches 1 run scoreboard players set @s mcc_matphase 0
execute if score @s mcc_matmiss matches 1 run return fail
return run function mcc:materials/place
