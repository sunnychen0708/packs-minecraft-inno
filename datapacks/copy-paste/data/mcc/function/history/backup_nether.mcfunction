$execute in minecraft:overworld run forceload add $(bx) $(hz) $(bx2) $(hz2)
$execute store success score @s mcc_ok run clone from minecraft:the_nether $(srcx) $(srcy) $(srcz) $(srcx2) $(srcy2) $(srcz2) to minecraft:overworld $(bx) 0 $(hz) strict replace force
$execute in minecraft:overworld run forceload remove $(bx) $(hz) $(bx2) $(hz2)
