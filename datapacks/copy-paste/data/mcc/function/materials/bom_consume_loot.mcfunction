execute unless data storage mcc:temp loot[0].id run return 0
data modify storage mcc:temp mat set from storage mcc:temp loot[0]
execute if data storage mcc:temp mat.components run scoreboard players set @s mcc_bpbad 1
execute unless data storage mcc:temp mat.components store result storage mcc:temp mat.pid int 1 run scoreboard players get @s mcc_id
execute unless data storage mcc:temp mat.components run function mcc:materials/bom_add with storage mcc:temp mat
data remove storage mcc:temp loot[0]
execute if data storage mcc:temp loot[0].id run return run function mcc:materials/bom_consume_loot
return 1
