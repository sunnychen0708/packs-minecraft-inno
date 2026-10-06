execute unless data storage mcc:temp invsel[0] run return 0
execute unless score #remain mcc_tmp matches 1.. run return 0
execute store result score #invc mcc_tmp run data get storage mcc:temp invsel[0].count
scoreboard players operation #invt mcc_tmp = #remain mcc_tmp
execute if score #invt mcc_tmp > #invc mcc_tmp run scoreboard players operation #invt mcc_tmp = #invc mcc_tmp
data modify storage mcc:temp invtake set value {slot:0,take:0}
execute store result storage mcc:temp invtake.slot int 1 run data get storage mcc:temp invsel[0].Slot
execute store result storage mcc:temp invtake.take int 1 run scoreboard players get #invt mcc_tmp
scoreboard players set #invok mcc_tmp 0
execute if data storage mcc:temp invtake{slot:-106} run function mcc:materials/inv_take_offhand with storage mcc:temp invtake
execute unless data storage mcc:temp invtake{slot:-106} run function mcc:materials/inv_take_slot with storage mcc:temp invtake
# Only count what really left the player; a failed modify must never become a refund.
execute unless score #invok mcc_tmp matches 1 run scoreboard players set #invt mcc_tmp 0
scoreboard players operation #remain mcc_tmp -= #invt mcc_tmp
scoreboard players operation #invtaken mcc_tmp += #invt mcc_tmp
data remove storage mcc:temp invsel[0]
return run function mcc:materials/inv_take_loop
