$execute in minecraft:overworld run forceload add $(cbx) 20000000 $(cbx2) $(cbz2)
$execute in minecraft:overworld run setblock $(cbx) -1 20000000 minecraft:structure_block[mode=save]{mode:"SAVE",name:"mcc:clipboard_$(id)",powered:0b,posX:0,posY:1,posZ:0,sizeX:$(sx),sizeY:$(sy),sizeZ:$(sz),ignoreEntities:1b,showair:1b}
$execute in minecraft:overworld run setblock $(cbx) -2 20000000 minecraft:redstone_block
$execute in minecraft:overworld run setblock $(cbx) -2 20000000 air
$execute in minecraft:overworld run setblock $(cbx) -1 20000000 air
$execute in minecraft:overworld run forceload remove $(cbx) 20000000 $(cbx2) $(cbz2)
