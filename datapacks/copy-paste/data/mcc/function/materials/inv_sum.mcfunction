# #inv += count of every stack left in mcc:temp invsel (consumes the list).
execute unless data storage mcc:temp invsel[0] run return 0
execute store result score #invc mcc_tmp run data get storage mcc:temp invsel[0].count
scoreboard players operation #inv mcc_tmp += #invc mcc_tmp
data remove storage mcc:temp invsel[0]
return run function mcc:materials/inv_sum
