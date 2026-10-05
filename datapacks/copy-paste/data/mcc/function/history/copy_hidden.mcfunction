$execute in minecraft:overworld run forceload add $(sx) $(sz) $(sx2) $(sz2)
$execute in minecraft:overworld run forceload add $(dx) $(dz) $(dx2) $(dz2)
$execute store success score @s mcc_ok run clone from minecraft:overworld $(sx) 0 $(sz) $(sx2) $(sy2) $(sz2) to minecraft:overworld $(dx) 0 $(dz) strict replace force
$execute in minecraft:overworld run forceload remove $(sx) $(sz) $(sx2) $(sz2)
$execute in minecraft:overworld run forceload remove $(dx) $(dz) $(dx2) $(dz2)
return 1
