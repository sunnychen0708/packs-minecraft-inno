execute store result storage mcc:temp fl.x1 int 1 run scoreboard players get @s mcc_rx
execute store result storage mcc:temp fl.z1 int 1 run scoreboard players get @s mcc_rz
execute store result storage mcc:temp fl.x2 int 1 run scoreboard players get @s mcc_rx2
execute store result storage mcc:temp fl.z2 int 1 run scoreboard players get @s mcc_rz2
execute if score @s mcc_rdim matches 1 run function mcc:move/forceload_add_overworld with storage mcc:temp fl
execute if score @s mcc_rdim matches 2 run function mcc:move/forceload_add_nether with storage mcc:temp fl
execute if score @s mcc_rdim matches 3 run function mcc:move/forceload_add_end with storage mcc:temp fl
execute store result storage mcc:temp fl.x1 int 1 run scoreboard players get @s mcc_r2x
execute store result storage mcc:temp fl.z1 int 1 run scoreboard players get @s mcc_r2z
execute store result storage mcc:temp fl.x2 int 1 run scoreboard players get @s mcc_r2x2
execute store result storage mcc:temp fl.z2 int 1 run scoreboard players get @s mcc_r2z2
execute if score @s mcc_rdim matches 1 run function mcc:move/forceload_add_overworld with storage mcc:temp fl
execute if score @s mcc_rdim matches 2 run function mcc:move/forceload_add_nether with storage mcc:temp fl
execute if score @s mcc_rdim matches 3 run function mcc:move/forceload_add_end with storage mcc:temp fl
return 1
