# mcc:temp invsel = the player's plain stacks of $(id): main inventory (slots 0-35) and the
# off hand (marked Slot -106). Stacks with components (renamed, enchanted...) are never used.
data modify storage mcc:temp invsel set value []
$data modify storage mcc:temp invsel append from entity @s Inventory[{id:"$(id)"}]
data remove storage mcc:temp offh
data modify storage mcc:temp offh set from entity @s equipment.offhand
$execute if data storage mcc:temp offh{id:"$(id)"} run data modify storage mcc:temp offh.Slot set value -106
$execute if data storage mcc:temp offh{id:"$(id)"} run data modify storage mcc:temp invsel append from storage mcc:temp offh
data remove storage mcc:temp invsel[{components:{}}]
