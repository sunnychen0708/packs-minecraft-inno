# Flip the Blueprint left-right as the player sees it: facing north/south that is the X axis.
scoreboard players set @s mcc_tmp 2
execute if entity @s[y_rotation=-45..45] run scoreboard players set @s mcc_tmp 1
execute if entity @s[y_rotation=135..180] run scoreboard players set @s mcc_tmp 1
execute if entity @s[y_rotation=-180..-135] run scoreboard players set @s mcc_tmp 1
tellraw @s {"text":"[Copy/Paste] Blueprint 左右翻轉（以你面對的方向為準）。","color":"green"}
function mcc:state/bp_flip_axis
