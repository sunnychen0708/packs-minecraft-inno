execute store result storage mcc:temp x1 int 1 run scoreboard players get @s mcc_bpsx0
execute store result storage mcc:temp z1 int 1 run scoreboard players get @s mcc_bpsz0
execute store result storage mcc:temp x2 int 1 run scoreboard players get @s mcc_bpsx2
execute store result storage mcc:temp z2 int 1 run scoreboard players get @s mcc_bpsz2
function mcc:blueprint/forceload_add with storage mcc:temp
scoreboard players set @s mcc_bpover 0
scoreboard players set @s mcc_buildconfirm 0
scoreboard players set @s mcc_bpoindex 0
scoreboard players operation @s mcc_bpsx = @s mcc_bpsx0
scoreboard players operation @s mcc_bpsy = @s mcc_bpsy0
scoreboard players operation @s mcc_bpsz = @s mcc_bpsz0
scoreboard players operation @s mcc_bptx = @s mcc_bptx0
scoreboard players operation @s mcc_bpty = @s mcc_bpty0
scoreboard players operation @s mcc_bptz = @s mcc_bptz0
scoreboard players set @s mcc_bpover_scan 1
return 1
