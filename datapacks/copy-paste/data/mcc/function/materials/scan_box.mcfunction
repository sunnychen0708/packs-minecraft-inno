$execute in $(dimension) run forceload add $(x) $(z)
$execute in $(dimension) if block $(x) $(y) $(z) #mcc:material_chests run function mcc:materials/read_inventory with storage mcc:temp box
$execute in $(dimension) unless block $(x) $(y) $(z) #mcc:material_chests run data remove storage mcc:materials p$(pid).boxes[{x:$(x),y:$(y),z:$(z),dimension:"$(dimension)"}]
$execute in $(dimension) run forceload remove $(x) $(z)
return 1
