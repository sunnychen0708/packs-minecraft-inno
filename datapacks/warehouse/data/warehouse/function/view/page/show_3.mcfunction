execute if score @s wh_viewlines matches 25.. run function warehouse:view/page/p3_next with storage warehouse:runtime viewer.render
execute if score @s wh_viewlines matches 17..24 run function warehouse:view/page/p3_last with storage warehouse:runtime viewer.render
