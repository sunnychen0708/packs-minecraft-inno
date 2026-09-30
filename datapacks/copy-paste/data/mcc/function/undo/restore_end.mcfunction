$execute in minecraft:overworld run forceload add $(ubx) 20000200 $(ubx2) $(ubz2)
$execute store success score @s mcc_ok run clone from minecraft:overworld $(ubx) 0 20000200 $(ubx2) $(uby2) $(ubz2) to minecraft:the_end $(dstx) $(dsty) $(dstz) replace force
$execute in minecraft:overworld run forceload remove $(ubx) 20000200 $(ubx2) $(ubz2)
