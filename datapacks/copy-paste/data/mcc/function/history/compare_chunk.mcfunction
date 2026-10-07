$execute in minecraft:overworld if blocks $(sx1) $(sy1) $(sz1) $(sx2) $(sy2) $(sz2) $(tx1) $(ty1) $(tz1) all run return 1
$scoreboard players set @s mcc_mnx $(sx1)
$scoreboard players set @s mcc_mny $(sy1)
$scoreboard players set @s mcc_mnz $(sz1)
$scoreboard players set @s mcc_mxx $(sx2)
$scoreboard players set @s mcc_mxy $(sy2)
$scoreboard players set @s mcc_mxz $(sz2)
$scoreboard players set @s mcc_dstx $(tx1)
$scoreboard players set @s mcc_dsty $(ty1)
$scoreboard players set @s mcc_dstz $(tz1)
return run function mcc:history/compare_line
