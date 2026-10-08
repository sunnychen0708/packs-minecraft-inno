scoreboard players set @s mcc_ok 0
execute store success score @s mcc_ok run function mcc:history/redo_apply
execute unless score @s mcc_ok matches 1 run function mcc:materials/refund_taken_start
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Redo 世界還原失敗；已扣材料已退還，Redo 紀錄保留。","color":"red"}]
scoreboard players set @s mcc_matphase 0
scoreboard players set @s mcc_matjob 0
execute unless score @s mcc_ok matches 1 run return fail
return 1
