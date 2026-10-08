execute unless score @s mcc_clip matches 1 run tellraw @s [{"text":"[Copy/Paste] Clipboard 是空的。","color":"red"}]
execute unless score @s mcc_clip matches 1 run return fail
execute unless score @s mcc_cliptype matches 1 run tellraw @s [{"text":"[Copy/Paste] 只有 Copy Clipboard 會建立 Blueprint；Cut Clipboard 會真正貼上。","color":"red"}]
execute unless score @s mcc_cliptype matches 1 run return fail
function mcc:blueprint/clear_internal
scoreboard players operation @s mcc_bpdst = @s mcc_dstd
execute if score @s mcc_rot matches 0 if score @s mcc_mir matches 0 run return run function mcc:blueprint/init_direct
return run function mcc:blueprint/init_transformed
