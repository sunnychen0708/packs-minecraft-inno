$execute store result score #missing mcc_tmp run data get storage mcc:materials p$(pid).bom."$(id)".missing
$execute if score #missing mcc_tmp matches 1.. run tellraw @s [{"text":"  $(id)","color":"yellow"},{"text":" ×","color":"gray"},{"score":{"name":"#missing","objective":"mcc_tmp"},"color":"white"}]
return 1
