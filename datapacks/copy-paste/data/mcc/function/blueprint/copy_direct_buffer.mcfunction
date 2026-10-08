$execute in minecraft:overworld run forceload add $(cbx) 20000000 $(cbx2) $(cbz2)
$execute in minecraft:overworld run forceload add $(bpx) 20002000 $(bpx2) $(bpz2)
$execute store success score @s mcc_ok run clone from minecraft:overworld $(cbx) 0 20000000 $(cbx2) $(bpy2) $(cbz2) to minecraft:overworld $(bpx) 0 20002000 strict replace force
$execute in minecraft:overworld run forceload remove $(cbx) 20000000 $(cbx2) $(cbz2)
$execute unless score @s mcc_ok matches 1 in minecraft:overworld run forceload remove $(bpx) 20002000 $(bpx2) $(bpz2)
