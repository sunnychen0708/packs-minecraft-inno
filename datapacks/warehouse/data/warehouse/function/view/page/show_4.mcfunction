execute if score @s wh_viewlines matches 33.. run function warehouse:view/page/p4_next with storage warehouse:runtime viewer.render
execute if score @s wh_viewlines matches 25..32 run function warehouse:view/page/p4_last with storage warehouse:runtime viewer.render
