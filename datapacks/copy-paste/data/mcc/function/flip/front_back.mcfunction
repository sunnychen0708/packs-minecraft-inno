# Flip the selection itself front-back as the player sees it.
execute if entity @s[y_rotation=-45..45] run return run function mcc:flip/z
execute if entity @s[y_rotation=135..180] run return run function mcc:flip/z
execute if entity @s[y_rotation=-180..-135] run return run function mcc:flip/z
return run function mcc:flip/x
