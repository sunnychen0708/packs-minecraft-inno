data modify storage warehouse:runtime scan set from storage warehouse:chests c00
data modify storage warehouse:runtime scan.x set from storage warehouse:chests c00.b_x
data modify storage warehouse:runtime scan.y set from storage warehouse:chests c00.b_y
data modify storage warehouse:runtime scan.z set from storage warehouse:chests c00.b_z
data modify storage warehouse:runtime scan.slot set value 14
function warehouse:sort/process with storage warehouse:runtime scan
