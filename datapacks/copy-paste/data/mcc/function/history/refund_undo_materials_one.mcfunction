scoreboard players set #taken mcc_tmp 0
execute if data storage mcc:temp txitem.taken store result score #taken mcc_tmp run data get storage mcc:temp txitem.taken
$execute unless data storage mcc:temp txitem.taken store result score #taken mcc_tmp run data get storage mcc:history u_p$(pid)_s$(slot).materials.bom."$(id)".taken
scoreboard players set #inv mcc_tmp 0
execute if data storage mcc:temp txitem.inv store result score #inv mcc_tmp run data get storage mcc:temp txitem.inv
$data modify storage mcc:temp refund set value {item_id:"$(id)",count:0}
execute if score #taken mcc_tmp matches 1.. run function mcc:materials/refund_split
return 1
