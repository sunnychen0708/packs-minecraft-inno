execute unless score @s mcc_bpactive matches 1 run return 0
execute unless score @s mcc_cliptype matches 1 run return 0
execute if score @s mcc_matphase matches 1.. run tellraw @s [{"text":"[Copy/Paste] 正在檢查/扣除材料，暫時不能改 Blueprint。","color":"red"}]
execute if score @s mcc_matphase matches 1.. run return fail
scoreboard players operation @s mcc_dstx = @s mcc_bpaimx
scoreboard players operation @s mcc_dsty = @s mcc_bpaimy
scoreboard players operation @s mcc_dstz = @s mcc_bpaimz
scoreboard players operation @s mcc_dstd = @s mcc_bpaimd
return run function mcc:blueprint/create
