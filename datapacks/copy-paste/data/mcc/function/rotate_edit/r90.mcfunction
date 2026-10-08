scoreboard players set @s mcc_erot 1
scoreboard players set @s mcc_emir 0
data modify storage mcc:temp erot set value "clockwise_90"
data modify storage mcc:temp emir set value "none"
return run function mcc:rotate_edit/run
