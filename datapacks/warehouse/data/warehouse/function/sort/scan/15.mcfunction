data modify storage warehouse:runtime scan set from storage warehouse:chests c00
data modify storage warehouse:runtime scan.x set from storage warehouse:chests c00.a_x
data modify storage warehouse:runtime scan.y set from storage warehouse:chests c00.a_y
data modify storage warehouse:runtime scan.z set from storage warehouse:chests c00.a_z
data modify storage warehouse:runtime scan.slot set value 15
function warehouse:sort/process with storage warehouse:runtime scan
