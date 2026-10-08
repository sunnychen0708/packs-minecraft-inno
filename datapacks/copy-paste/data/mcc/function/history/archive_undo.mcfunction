$execute in minecraft:overworld run forceload add $(ubx) 20000200 $(ubx2) $(ubz2)
$execute in minecraft:overworld run forceload add $(ubx) $(hz) $(ubx2) $(hz2)
$execute store success score @s mcc_ok run clone from minecraft:overworld $(ubx) 0 20000200 $(ubx2) $(uby2) $(ubz2) to minecraft:overworld $(ubx) 0 $(hz) replace force
$execute in minecraft:overworld run forceload remove $(ubx) 20000200 $(ubx2) $(ubz2)
$execute in minecraft:overworld run forceload remove $(ubx) $(hz) $(ubx2) $(hz2)
