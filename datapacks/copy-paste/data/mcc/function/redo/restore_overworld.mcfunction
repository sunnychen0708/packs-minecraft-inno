$execute in minecraft:overworld run forceload add $(rbx) 20001000 $(rbx2) $(rbz2)
$execute store success score @s mcc_ok run clone from minecraft:overworld $(rbx) 0 20001000 $(rbx2) $(rby2) $(rbz2) to minecraft:overworld $(dstx) $(dsty) $(dstz) replace force
$execute in minecraft:overworld run forceload remove $(rbx) 20001000 $(rbx2) $(rbz2)
