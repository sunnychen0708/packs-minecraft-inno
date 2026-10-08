execute unless data storage mcc:temp inv[0].id run return 0
data modify storage mcc:temp mat set from storage mcc:temp inv[0]
execute unless data storage mcc:temp mat.components run data modify storage mcc:temp take set from storage mcc:temp box
execute unless data storage mcc:temp mat.components run data modify storage mcc:temp take.id set from storage mcc:temp mat.id
execute unless data storage mcc:temp mat.components store result storage mcc:temp take.slot int 1 run data get storage mcc:temp mat.Slot
execute unless data storage mcc:temp mat.components store result storage mcc:temp take.count int 1 run data get storage mcc:temp mat.count
execute unless data storage mcc:temp mat.components run function mcc:materials/take_stack with storage mcc:temp take
data remove storage mcc:temp inv[0]
execute if data storage mcc:temp inv[0].id run return run function mcc:materials/take_inv
return 1
