$execute in minecraft:overworld run forceload add $(wbx) 20000500 $(wbx2) $(wbz2)
$execute store success score @s mcc_ok run clone from minecraft:the_nether $(srcx) $(srcy) $(srcz) $(srcx2) $(srcy2) $(srcz2) to minecraft:overworld $(wbx) 0 20000500 replace force
$execute in minecraft:overworld run forceload remove $(wbx) 20000500 $(wbx2) $(wbz2)
