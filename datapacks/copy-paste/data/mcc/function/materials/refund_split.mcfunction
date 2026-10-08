# In: mcc:temp refund {item_id}, #taken (total taken) and #inv (part taken from the player).
# The player's part goes back to the player as far as it fits; everything else goes to Warehouse.
# Out: #refok = 1 when every item found a home (given, or accepted/queued by Warehouse).
scoreboard players set #refok mcc_tmp 1
scoreboard players operation #back mcc_tmp = #inv mcc_tmp
execute if score #back mcc_tmp > #taken mcc_tmp run scoreboard players operation #back mcc_tmp = #taken mcc_tmp
execute if score #back mcc_tmp matches 1.. run function mcc:materials/inv_fit with storage mcc:temp refund
execute if score #back mcc_tmp > #fit mcc_tmp run scoreboard players operation #back mcc_tmp = #fit mcc_tmp
execute if score #back mcc_tmp matches ..0 run scoreboard players set #back mcc_tmp 0
data modify storage mcc:temp giveback set value {id:"",count:0}
data modify storage mcc:temp giveback.id set from storage mcc:temp refund.item_id
execute store result storage mcc:temp giveback.count int 1 run scoreboard players get #back mcc_tmp
execute if score #back mcc_tmp matches 1.. run function mcc:history/refund_give with storage mcc:temp giveback
scoreboard players operation #whback mcc_tmp = #taken mcc_tmp
scoreboard players operation #whback mcc_tmp -= #back mcc_tmp
execute if score #whback mcc_tmp matches 1.. store result storage mcc:temp refund.count int 1 run scoreboard players get #whback mcc_tmp
execute if score #whback mcc_tmp matches 1.. run function warehouse:api/refund_item with storage mcc:temp refund
execute if score #whback mcc_tmp matches 1.. unless data storage warehouse:api result{ok:1b,complete:1b} run scoreboard players set #refok mcc_tmp 0
return 1
