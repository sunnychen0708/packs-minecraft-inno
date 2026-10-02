$execute store result score #remain mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".remain
execute if score #remain mcc_tmp matches 1.. run scoreboard players set @s mcc_matmiss 1
return 1
