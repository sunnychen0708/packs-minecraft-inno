scoreboard players operation @s mcc_p1x = @s mcc_up1x
scoreboard players operation @s mcc_p1y = @s mcc_up1y
scoreboard players operation @s mcc_p1z = @s mcc_up1z
scoreboard players operation @s mcc_p2x = @s mcc_up2x
scoreboard players operation @s mcc_p2y = @s mcc_up2y
scoreboard players operation @s mcc_p2z = @s mcc_up2z
scoreboard players operation @s mcc_anx = @s mcc_uanx
scoreboard players operation @s mcc_any = @s mcc_uany
scoreboard players operation @s mcc_anz = @s mcc_uanz
scoreboard players operation @s mcc_hasa = @s mcc_uhasa
scoreboard players set @s mcc_usel 0
scoreboard players operation @s mcc_p1d = @s mcc_udim
scoreboard players operation @s mcc_p2d = @s mcc_udim
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_and = @s mcc_udim
scoreboard players set @s mcc_has1 1
scoreboard players set @s mcc_has2 1
