execute unless data storage mcc:temp inv[0].id run return 0
data modify storage mcc:temp mat set from storage mcc:temp inv[0]
execute unless data storage mcc:temp mat.components store result storage mcc:temp mat.pid int 1 run scoreboard players get @s mcc_id
execute unless data storage mcc:temp mat.components run function mcc:materials/add_have with storage mcc:temp mat
data remove storage mcc:temp inv[0]
execute if data storage mcc:temp inv[0].id run return run function mcc:materials/count_inv
return 1
