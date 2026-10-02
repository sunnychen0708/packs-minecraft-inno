$execute if data storage mcc:materials p$(pid).boxes[{x:$(x),y:$(y),z:$(z),dimension:"$(dimension)"}] run return 0
$data modify storage mcc:materials p$(pid).boxes append value {x:$(x),y:$(y),z:$(z),dimension:"$(dimension)"}
return 1
