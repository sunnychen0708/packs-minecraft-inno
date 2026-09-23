execute if score @s wh_viewlines matches 0 run function warehouse:view/page/empty with storage warehouse:runtime viewer.render
execute if score @s wh_viewlines matches 9.. run function warehouse:view/page/p1_next with storage warehouse:runtime viewer.render
execute if score @s wh_viewlines matches 1..8 run function warehouse:view/page/p1_last with storage warehouse:runtime viewer.render
