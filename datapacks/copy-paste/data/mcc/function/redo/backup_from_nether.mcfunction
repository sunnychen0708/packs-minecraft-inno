$execute in minecraft:overworld run forceload add $(rbx) 20001000 $(rbx2) $(rbz2)
$execute store success score @s mcc_ok run clone from minecraft:the_nether $(srcx) $(srcy) $(srcz) $(srcx2) $(srcy2) $(srcz2) to minecraft:overworld $(rbx) 0 20001000 strict replace force
$execute in minecraft:overworld run forceload remove $(rbx) 20001000 $(rbx2) $(rbz2)
