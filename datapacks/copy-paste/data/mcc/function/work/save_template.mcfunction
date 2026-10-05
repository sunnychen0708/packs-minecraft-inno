$execute in minecraft:overworld run forceload add $(wbx) 20000500 $(wbx2) $(wbz2)
$execute in minecraft:overworld run setblock $(wbx) -1 20000500 minecraft:structure_block[mode=save]{mode:"SAVE",name:"mcc:work_$(id)",powered:0b,posX:0,posY:1,posZ:0,sizeX:$(sx),sizeY:$(sy),sizeZ:$(sz),ignoreEntities:1b,showair:1b}
$execute in minecraft:overworld run setblock $(wbx) -2 20000500 minecraft:redstone_block
$execute in minecraft:overworld run setblock $(wbx) -2 20000500 air
$execute in minecraft:overworld run setblock $(wbx) -1 20000500 air
$execute in minecraft:overworld run forceload remove $(wbx) 20000500 $(wbx2) $(wbz2)
