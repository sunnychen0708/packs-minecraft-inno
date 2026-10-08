$execute in minecraft:overworld run forceload add $(bx) $(hz) $(bx2) $(hz2)
$execute store success score @s mcc_ok run clone from minecraft:overworld $(bx) 0 $(hz) $(bx2) $(by2) $(hz2) to minecraft:the_end $(dstx) $(dsty) $(dstz) replace force
$execute in minecraft:overworld run forceload remove $(bx) $(hz) $(bx2) $(hz2)
