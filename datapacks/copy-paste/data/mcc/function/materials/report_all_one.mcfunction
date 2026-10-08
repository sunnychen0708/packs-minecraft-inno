$execute store result score #need mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".need
$execute store result score #have mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".have
$execute store result score #missing mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".missing
$execute if score #missing mcc_tmp matches 1.. run tellraw @s [{"text":"  $(id)  ","color":"red"},{"score":{"name":"#need","objective":"mcc_tmp"},"color":"white"},{"text":"  / Warehouse ","color":"gray"},{"score":{"name":"#have","objective":"mcc_tmp"},"color":"yellow"},{"text":"  缺 ","color":"red"},{"score":{"name":"#missing","objective":"mcc_tmp"},"color":"red"}]
$execute unless score #missing mcc_tmp matches 1.. run tellraw @s [{"text":"  $(id)  ","color":"green"},{"score":{"name":"#need","objective":"mcc_tmp"},"color":"white"},{"text":"  / Warehouse ","color":"gray"},{"score":{"name":"#have","objective":"mcc_tmp"},"color":"green"}]
return 1
