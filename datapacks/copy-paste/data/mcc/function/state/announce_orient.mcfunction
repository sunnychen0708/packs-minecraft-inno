# Tell the player the Blueprint/V direction relative to the copied original.
execute if score @s mcc_rot matches 0 if score @s mcc_mir matches 0 run tellraw @s [{"text":"目前方向：","color":"gray"},{"text":"和原本相同","color":"white"}]
execute if score @s mcc_rot matches 0 if score @s mcc_mir matches 1..2 run tellraw @s [{"text":"目前方向：","color":"gray"},{"text":"和原本相同，並翻面","color":"white"}]
execute if score @s mcc_rot matches 1 if score @s mcc_mir matches 0 run tellraw @s [{"text":"目前方向：","color":"gray"},{"text":"右轉 90°","color":"white"}]
execute if score @s mcc_rot matches 1 if score @s mcc_mir matches 1..2 run tellraw @s [{"text":"目前方向：","color":"gray"},{"text":"右轉 90°，並翻面","color":"white"}]
execute if score @s mcc_rot matches 2 if score @s mcc_mir matches 0 run tellraw @s [{"text":"目前方向：","color":"gray"},{"text":"轉 180°","color":"white"}]
execute if score @s mcc_rot matches 2 if score @s mcc_mir matches 1..2 run tellraw @s [{"text":"目前方向：","color":"gray"},{"text":"轉 180°，並翻面","color":"white"}]
execute if score @s mcc_rot matches 3 if score @s mcc_mir matches 0 run tellraw @s [{"text":"目前方向：","color":"gray"},{"text":"左轉 90°","color":"white"}]
execute if score @s mcc_rot matches 3 if score @s mcc_mir matches 1..2 run tellraw @s [{"text":"目前方向：","color":"gray"},{"text":"左轉 90°，並翻面","color":"white"}]
execute unless score @s mcc_bpactive matches 1 run tellraw @s {"text":"目前沒有 Blueprint；下次按 V 時會用這個方向。","color":"gray"}
