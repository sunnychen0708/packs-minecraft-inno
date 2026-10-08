scoreboard players set @s mcc_erot 2
scoreboard players set @s mcc_emir 0
data modify storage mcc:temp erot set value "180"
data modify storage mcc:temp emir set value "none"
return run function mcc:rotate_edit/run
