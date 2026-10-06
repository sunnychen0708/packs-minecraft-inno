execute unless data storage mcc:temp invsel[0] run return 0
execute store result score #invc mcc_tmp run data get storage mcc:temp invsel[0].count
scoreboard players operation #invt mcc_tmp = #max mcc_tmp
scoreboard players operation #invt mcc_tmp -= #invc mcc_tmp
execute if score #invt mcc_tmp matches 1.. run scoreboard players operation #fit mcc_tmp += #invt mcc_tmp
data remove storage mcc:temp invsel[0]
return run function mcc:materials/inv_fit_loop
