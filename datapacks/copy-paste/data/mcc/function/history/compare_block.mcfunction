$execute in minecraft:overworld if blocks $(sx) $(sy) $(sz) $(sx) $(sy) $(sz) $(tx) $(ty) $(tz) all run return 1
scoreboard players set @s mcc_amt 0
data modify storage mcc:temp cmp_bid set value "minecraft:air"
$execute in minecraft:overworld if block $(sx) $(sy) $(sz) #minecraft:air if block $(tx) $(ty) $(tz) #minecraft:air run scoreboard players set @s mcc_amt 1
execute if score @s mcc_amt matches 1 run return 1
$data modify storage mcc:temp sx set value $(sx)
$data modify storage mcc:temp sy set value $(sy)
$data modify storage mcc:temp sz set value $(sz)
$data modify storage mcc:temp tx set value $(tx)
$data modify storage mcc:temp ty set value $(ty)
$data modify storage mcc:temp tz set value $(tz)
scoreboard players set @s mcc_cmpmode 1
$execute in minecraft:overworld positioned $(sx) $(sy) $(sz) unless block ~ ~ ~ #minecraft:air run function mcc:blueprint/generated/root
scoreboard players set @s mcc_cmpmode 0
execute unless score @s mcc_amt matches 1 if score @s mcc_cmpdiag matches 1 run function mcc:history/diag_record with storage mcc:temp
execute unless score @s mcc_amt matches 1 if score @s mcc_cmpdiag matches 1 run return 1
execute unless score @s mcc_amt matches 1 run scoreboard players set @s mcc_ok 0
execute unless score @s mcc_ok matches 1 run return fail
return 1
