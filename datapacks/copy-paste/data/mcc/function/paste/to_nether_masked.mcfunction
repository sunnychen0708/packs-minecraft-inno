$execute in minecraft:overworld run forceload add $(cbx) 20000000 $(cbx2) $(cbz2)
$execute store success score @s mcc_ok run clone from minecraft:overworld $(cbx) 0 20000000 $(cbx2) $(cby2) $(cbz2) to minecraft:the_nether $(dstx) $(dsty) $(dstz) masked force
$execute in minecraft:overworld run forceload remove $(cbx) 20000000 $(cbx2) $(cbz2)
