scoreboard players operation @s wh_target = @s wh_register
scoreboard players operation #bcode wh_tmp = @s wh_register
scoreboard players set #bbase wh_tmp 10
function warehouse:ui/back_from_code
scoreboard players set @s wh_register 0
tag @s remove wh_reg_pending
tag @s remove wh_read_pending
execute store result storage warehouse:runtime register_ui.code int 1 run scoreboard players get @s wh_target
function warehouse:ui/show_armed with storage warehouse:runtime register_ui
