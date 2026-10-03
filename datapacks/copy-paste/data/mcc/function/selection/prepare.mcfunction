execute unless score @s mcc_has1 matches 1 run tellraw @s [{"text":"[Copy/Paste] 請先設定 Pos1。","color":"red"}]
execute unless score @s mcc_has1 matches 1 run return fail
execute unless score @s mcc_has2 matches 1 run tellraw @s [{"text":"[Copy/Paste] 請先設定 Pos2。","color":"red"}]
execute unless score @s mcc_has2 matches 1 run return fail
execute unless score @s mcc_p1d = @s mcc_p2d run tellraw @s [{"text":"[Copy/Paste] Pos1 與 Pos2 必須在同一個維度。","color":"red"}]
execute unless score @s mcc_p1d = @s mcc_p2d run return fail

scoreboard players operation @s mcc_minx = @s mcc_p1x
scoreboard players operation @s mcc_minx < @s mcc_p2x
scoreboard players operation @s mcc_miny = @s mcc_p1y
scoreboard players operation @s mcc_miny < @s mcc_p2y
scoreboard players operation @s mcc_minz = @s mcc_p1z
scoreboard players operation @s mcc_minz < @s mcc_p2z
scoreboard players operation @s mcc_maxx = @s mcc_p1x
scoreboard players operation @s mcc_maxx > @s mcc_p2x
scoreboard players operation @s mcc_maxy = @s mcc_p1y
scoreboard players operation @s mcc_maxy > @s mcc_p2y
scoreboard players operation @s mcc_maxz = @s mcc_p1z
scoreboard players operation @s mcc_maxz > @s mcc_p2z

scoreboard players operation @s mcc_selx = @s mcc_maxx
scoreboard players operation @s mcc_selx -= @s mcc_minx
scoreboard players add @s mcc_selx 1
scoreboard players operation @s mcc_sely = @s mcc_maxy
scoreboard players operation @s mcc_sely -= @s mcc_miny
scoreboard players add @s mcc_sely 1
scoreboard players operation @s mcc_selz = @s mcc_maxz
scoreboard players operation @s mcc_selz -= @s mcc_minz
scoreboard players add @s mcc_selz 1

execute unless score @s mcc_selx matches 1..128 run tellraw @s [{"text":"[Copy/Paste] X 長度超過上限 128 格。","color":"red"}]
execute unless score @s mcc_selx matches 1..128 run return fail
execute unless score @s mcc_sely matches 1..128 run tellraw @s [{"text":"[Copy/Paste] Y 長度超過上限 128 格。","color":"red"}]
execute unless score @s mcc_sely matches 1..128 run return fail
execute unless score @s mcc_selz matches 1..128 run tellraw @s [{"text":"[Copy/Paste] Z 長度超過上限 128 格。","color":"red"}]
execute unless score @s mcc_selz matches 1..128 run return fail

scoreboard players operation @s mcc_vol = @s mcc_selx
scoreboard players operation @s mcc_vol *= @s mcc_sely
scoreboard players operation @s mcc_vol *= @s mcc_selz
execute store result score @s mcc_lim run gamerule minecraft:max_block_modifications
execute if score @s mcc_vol > @s mcc_lim run tellraw @s [{"text":"[Copy/Paste] 選取範圍超過 minecraft:max_block_modifications。","color":"red"}]
execute if score @s mcc_vol > @s mcc_lim run return fail

execute if score @s mcc_hasa matches 1 unless score @s mcc_and = @s mcc_p1d run tellraw @s [{"text":"[Copy/Paste] Anchor 必須和選取區域在同一維度。","color":"red"}]
execute if score @s mcc_hasa matches 1 unless score @s mcc_and = @s mcc_p1d run return fail
scoreboard players operation @s mcc_soffx = @s mcc_p1x
scoreboard players operation @s mcc_soffy = @s mcc_p1y
scoreboard players operation @s mcc_soffz = @s mcc_p1z
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_soffx = @s mcc_anx
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_soffy = @s mcc_any
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_soffz = @s mcc_anz
scoreboard players operation @s mcc_soffx -= @s mcc_minx
scoreboard players operation @s mcc_soffy -= @s mcc_miny
scoreboard players operation @s mcc_soffz -= @s mcc_minz
return 1
