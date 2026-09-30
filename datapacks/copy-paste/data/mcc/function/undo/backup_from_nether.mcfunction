$execute in minecraft:overworld run forceload add $(ubx) 20000200 $(ubx2) $(ubz2)
$execute store success score @s mcc_ok run clone from minecraft:the_nether $(srcx) $(srcy) $(srcz) $(srcx2) $(srcy2) $(srcz2) to minecraft:overworld $(ubx) 0 20000200 replace force
$execute in minecraft:overworld run forceload remove $(ubx) 20000200 $(ubx2) $(ubz2)
