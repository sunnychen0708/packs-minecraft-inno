$execute in minecraft:overworld run forceload add $(wbx) 20000600 $(wbx2) $(wbz2)
$execute store success score @s mcc_ok run clone from minecraft:overworld $(wbx) 0 20000600 $(wbx2) $(wby2) $(wbz2) to minecraft:the_nether $(dstx) $(dsty) $(dstz) strict replace force
$execute in minecraft:overworld run forceload remove $(wbx) 20000600 $(wbx2) $(wbz2)
