$data modify storage warehouse:chests c$(code).a_x set value $(a_x)
$data modify storage warehouse:chests c$(code).a_y set value $(a_y)
$data modify storage warehouse:chests c$(code).a_z set value $(a_z)
$data modify storage warehouse:chests c$(code).b_x set value $(b_x)
$data modify storage warehouse:chests c$(code).b_y set value $(b_y)
$data modify storage warehouse:chests c$(code).b_z set value $(b_z)
$data modify storage warehouse:chests c$(code).dimension set value "$(dimension)"
$data modify storage warehouse:chests c$(code).registered set value 1b
$data modify storage warehouse:chests c$(code).valid set value 1b
function warehouse:chunks/ensure
execute store result storage warehouse:runtime register_ui.code int 1 run scoreboard players get @s wh_target
function warehouse:register/show_success with storage warehouse:runtime register_ui
