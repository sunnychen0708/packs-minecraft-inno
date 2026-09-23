$data modify storage warehouse:chests c00.a_x set value $(a_x)
$data modify storage warehouse:chests c00.a_y set value $(a_y)
$data modify storage warehouse:chests c00.a_z set value $(a_z)
$data modify storage warehouse:chests c00.b_x set value $(b_x)
$data modify storage warehouse:chests c00.b_y set value $(b_y)
$data modify storage warehouse:chests c00.b_z set value $(b_z)
$data modify storage warehouse:chests c00.dimension set value "$(dimension)"
data modify storage warehouse:chests c00.registered set value 1b
data modify storage warehouse:chests c00.valid set value 1b
dialog show @s warehouse:register/result/success_00
