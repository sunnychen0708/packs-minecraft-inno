$execute store result score #need mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".need
$execute store result score #have mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".have
scoreboard players operation #missing mcc_tmp = #need mcc_tmp
scoreboard players operation #missing mcc_tmp -= #have mcc_tmp
execute if score #missing mcc_tmp matches ..0 run scoreboard players set #missing mcc_tmp 0
$execute store result storage mcc:materials p$(pid).bom."$(id)".missing int 1 run scoreboard players get #missing mcc_tmp
execute if score #missing mcc_tmp matches 1.. run scoreboard players set @s mcc_matmiss 1
execute if score #missing mcc_tmp matches 1.. run scoreboard players add @s mcc_matkind 1
execute if score #missing mcc_tmp matches 1.. run scoreboard players operation @s mcc_mattotal += #missing mcc_tmp
return 1
