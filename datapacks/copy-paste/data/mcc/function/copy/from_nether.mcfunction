$execute in minecraft:overworld run forceload add $(cbx) 20000000 $(cbx2) $(cbz2)
$execute store success score @s mcc_ok run clone from minecraft:the_nether $(minx) $(miny) $(minz) $(maxx) $(maxy) $(maxz) to minecraft:overworld $(cbx) 0 20000000 strict replace force
$execute in minecraft:overworld run forceload remove $(cbx) 20000000 $(cbx2) $(cbz2)
