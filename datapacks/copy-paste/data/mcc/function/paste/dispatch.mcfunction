execute unless score @s mcc_clip matches 1 run tellraw @s [{"text":"[Copy/Paste] Clipboard 是空的。","color":"red"}]
execute unless score @s mcc_clip matches 1 run return fail
execute if score @s mcc_cliptype matches 1 run return run function mcc:blueprint/create
execute if score @s mcc_cliptype matches 2 run return run function mcc:paste/cut_run
tellraw @s [{"text":"[Copy/Paste] Clipboard 類型無效，請重新 Copy 或 Cut。","color":"red"}]
return fail
