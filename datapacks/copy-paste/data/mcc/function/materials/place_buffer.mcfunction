$execute in minecraft:overworld run forceload add $(sx) $(sz) $(sx2) $(sz2)
$execute if score @s mcc_bpdst matches 1 in minecraft:overworld run forceload add $(dx) $(dz) $(dx2) $(dz2)
$execute if score @s mcc_bpdst matches 2 in minecraft:the_nether run forceload add $(dx) $(dz) $(dx2) $(dz2)
$execute if score @s mcc_bpdst matches 3 in minecraft:the_end run forceload add $(dx) $(dz) $(dx2) $(dz2)
$execute if score @s mcc_bpdst matches 1 if score @s mcc_mask matches 0 store success score @s mcc_ok run clone from minecraft:overworld $(sx) $(sy) $(sz) $(sx2) $(sy2) $(sz2) to minecraft:overworld $(dx) $(dy) $(dz) replace force
$execute if score @s mcc_bpdst matches 1 if score @s mcc_mask matches 1 store success score @s mcc_ok run clone from minecraft:overworld $(sx) $(sy) $(sz) $(sx2) $(sy2) $(sz2) to minecraft:overworld $(dx) $(dy) $(dz) masked force
$execute if score @s mcc_bpdst matches 2 if score @s mcc_mask matches 0 store success score @s mcc_ok run clone from minecraft:overworld $(sx) $(sy) $(sz) $(sx2) $(sy2) $(sz2) to minecraft:the_nether $(dx) $(dy) $(dz) replace force
$execute if score @s mcc_bpdst matches 2 if score @s mcc_mask matches 1 store success score @s mcc_ok run clone from minecraft:overworld $(sx) $(sy) $(sz) $(sx2) $(sy2) $(sz2) to minecraft:the_nether $(dx) $(dy) $(dz) masked force
$execute if score @s mcc_bpdst matches 3 if score @s mcc_mask matches 0 store success score @s mcc_ok run clone from minecraft:overworld $(sx) $(sy) $(sz) $(sx2) $(sy2) $(sz2) to minecraft:the_end $(dx) $(dy) $(dz) replace force
$execute if score @s mcc_bpdst matches 3 if score @s mcc_mask matches 1 store success score @s mcc_ok run clone from minecraft:overworld $(sx) $(sy) $(sz) $(sx2) $(sy2) $(sz2) to minecraft:the_end $(dx) $(dy) $(dz) masked force
$execute if score @s mcc_bpdst matches 1 in minecraft:overworld run forceload remove $(dx) $(dz) $(dx2) $(dz2)
$execute if score @s mcc_bpdst matches 2 in minecraft:the_nether run forceload remove $(dx) $(dz) $(dx2) $(dz2)
$execute if score @s mcc_bpdst matches 3 in minecraft:the_end run forceload remove $(dx) $(dz) $(dx2) $(dz2)
$execute in minecraft:overworld run forceload remove $(sx) $(sz) $(sx2) $(sz2)
return 1
