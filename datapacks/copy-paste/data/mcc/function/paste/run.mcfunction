execute unless score @s mcc_clip matches 1 run tellraw @s [{"text":"[Copy/Paste] Clipboard 是空的，請先 Copy。","color":"red"}]
execute unless score @s mcc_clip matches 1 run return fail
execute if score @s mcc_rot matches 0 if score @s mcc_mir matches 0 run return run function mcc:paste/no_transform
return run function mcc:paste/transformed
