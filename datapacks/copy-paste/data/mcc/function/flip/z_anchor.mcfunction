scoreboard players set @s mcc_erot 0
scoreboard players set @s mcc_emir 2
data modify storage mcc:temp erot set value "none"
data modify storage mcc:temp emir set value "left_right"
return run function mcc:rotate_edit/run
