$execute in minecraft:overworld unless block $(tx) $(ty) $(tz) $(cmp_bid) run return fail
data modify storage mcc:temp cmp_exp_nbt set value {}
data modify storage mcc:temp cmp_cur_nbt set value {}
$execute in minecraft:overworld run data modify storage mcc:temp cmp_exp_nbt set from block $(sx) $(sy) $(sz)
$execute in minecraft:overworld run data modify storage mcc:temp cmp_cur_nbt set from block $(tx) $(ty) $(tz)
data remove storage mcc:temp cmp_exp_nbt.x
data remove storage mcc:temp cmp_exp_nbt.y
data remove storage mcc:temp cmp_exp_nbt.z
data remove storage mcc:temp cmp_cur_nbt.x
data remove storage mcc:temp cmp_cur_nbt.y
data remove storage mcc:temp cmp_cur_nbt.z
scoreboard players set @s mcc_tmp2 0
execute store success score @s mcc_tmp2 run data modify storage mcc:temp cmp_exp_nbt set from storage mcc:temp cmp_cur_nbt
execute unless score @s mcc_tmp2 matches 1 run scoreboard players set @s mcc_amt 1
return 1
