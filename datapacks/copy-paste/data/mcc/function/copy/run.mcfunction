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

scoreboard players operation @s mcc_sx = @s mcc_maxx
scoreboard players operation @s mcc_sx -= @s mcc_minx
scoreboard players add @s mcc_sx 1
scoreboard players operation @s mcc_sy = @s mcc_maxy
scoreboard players operation @s mcc_sy -= @s mcc_miny
scoreboard players add @s mcc_sy 1
scoreboard players operation @s mcc_sz = @s mcc_maxz
scoreboard players operation @s mcc_sz -= @s mcc_minz
scoreboard players add @s mcc_sz 1

execute unless score @s mcc_sx matches 1..128 run tellraw @s [{"text":"[Copy/Paste] X 長度超過 v0.1 上限 128 格。","color":"red"}]
execute unless score @s mcc_sx matches 1..128 run return fail
execute unless score @s mcc_sy matches 1..128 run tellraw @s [{"text":"[Copy/Paste] Y 長度超過 v0.1 上限 128 格。","color":"red"}]
execute unless score @s mcc_sy matches 1..128 run return fail
execute unless score @s mcc_sz matches 1..128 run tellraw @s [{"text":"[Copy/Paste] Z 長度超過 v0.1 上限 128 格。","color":"red"}]
execute unless score @s mcc_sz matches 1..128 run return fail

scoreboard players operation @s mcc_vol = @s mcc_sx
scoreboard players operation @s mcc_vol *= @s mcc_sy
scoreboard players operation @s mcc_vol *= @s mcc_sz
execute store result score @s mcc_lim run gamerule minecraft:max_block_modifications
execute if score @s mcc_vol > @s mcc_lim run tellraw @s [{"text":"[Copy/Paste] 選取範圍超過目前 minecraft:max_block_modifications 上限。","color":"red"}]
execute if score @s mcc_vol > @s mcc_lim run return fail

execute if score @s mcc_hasa matches 1 unless score @s mcc_and = @s mcc_p1d run tellraw @s [{"text":"[Copy/Paste] Anchor 必須和選取區域在同一維度。","color":"red"}]
execute if score @s mcc_hasa matches 1 unless score @s mcc_and = @s mcc_p1d run return fail
execute if score @s mcc_hasa matches 1 unless score @s mcc_anx >= @s mcc_minx run tellraw @s [{"text":"[Copy/Paste] Anchor 必須位於選取範圍內。","color":"red"}]
execute if score @s mcc_hasa matches 1 unless score @s mcc_anx >= @s mcc_minx run return fail
execute if score @s mcc_hasa matches 1 unless score @s mcc_anx <= @s mcc_maxx run tellraw @s [{"text":"[Copy/Paste] Anchor 必須位於選取範圍內。","color":"red"}]
execute if score @s mcc_hasa matches 1 unless score @s mcc_anx <= @s mcc_maxx run return fail
execute if score @s mcc_hasa matches 1 unless score @s mcc_any >= @s mcc_miny run tellraw @s [{"text":"[Copy/Paste] Anchor 必須位於選取範圍內。","color":"red"}]
execute if score @s mcc_hasa matches 1 unless score @s mcc_any >= @s mcc_miny run return fail
execute if score @s mcc_hasa matches 1 unless score @s mcc_any <= @s mcc_maxy run tellraw @s [{"text":"[Copy/Paste] Anchor 必須位於選取範圍內。","color":"red"}]
execute if score @s mcc_hasa matches 1 unless score @s mcc_any <= @s mcc_maxy run return fail
execute if score @s mcc_hasa matches 1 unless score @s mcc_anz >= @s mcc_minz run tellraw @s [{"text":"[Copy/Paste] Anchor 必須位於選取範圍內。","color":"red"}]
execute if score @s mcc_hasa matches 1 unless score @s mcc_anz >= @s mcc_minz run return fail
execute if score @s mcc_hasa matches 1 unless score @s mcc_anz <= @s mcc_maxz run tellraw @s [{"text":"[Copy/Paste] Anchor 必須位於選取範圍內。","color":"red"}]
execute if score @s mcc_hasa matches 1 unless score @s mcc_anz <= @s mcc_maxz run return fail

scoreboard players operation @s mcc_offx = @s mcc_p1x
scoreboard players operation @s mcc_offy = @s mcc_p1y
scoreboard players operation @s mcc_offz = @s mcc_p1z
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_offx = @s mcc_anx
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_offy = @s mcc_any
execute if score @s mcc_hasa matches 1 run scoreboard players operation @s mcc_offz = @s mcc_anz
scoreboard players operation @s mcc_offx -= @s mcc_minx
scoreboard players operation @s mcc_offy -= @s mcc_miny
scoreboard players operation @s mcc_offz -= @s mcc_minz

scoreboard players operation @s mcc_cbx = @s mcc_id
scoreboard players operation @s mcc_cbx *= #slot mcc_id
scoreboard players operation @s mcc_cbx += #base mcc_id
scoreboard players operation @s mcc_cbx2 = @s mcc_cbx
scoreboard players operation @s mcc_cbx2 += @s mcc_sx
scoreboard players remove @s mcc_cbx2 1
scoreboard players operation @s mcc_cby2 = @s mcc_sy
scoreboard players remove @s mcc_cby2 1
scoreboard players operation @s mcc_cbz2 = #cbz mcc_id
scoreboard players operation @s mcc_cbz2 += @s mcc_sz
scoreboard players remove @s mcc_cbz2 1

execute store result storage mcc:temp minx int 1 run scoreboard players get @s mcc_minx
execute store result storage mcc:temp miny int 1 run scoreboard players get @s mcc_miny
execute store result storage mcc:temp minz int 1 run scoreboard players get @s mcc_minz
execute store result storage mcc:temp maxx int 1 run scoreboard players get @s mcc_maxx
execute store result storage mcc:temp maxy int 1 run scoreboard players get @s mcc_maxy
execute store result storage mcc:temp maxz int 1 run scoreboard players get @s mcc_maxz
execute store result storage mcc:temp cbx int 1 run scoreboard players get @s mcc_cbx
execute store result storage mcc:temp cbx2 int 1 run scoreboard players get @s mcc_cbx2
execute store result storage mcc:temp cby2 int 1 run scoreboard players get @s mcc_cby2
execute store result storage mcc:temp cbz2 int 1 run scoreboard players get @s mcc_cbz2

scoreboard players set @s mcc_ok 0
execute if score @s mcc_p1d matches 1 run function mcc:copy/from_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:copy/from_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:copy/from_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] 複製失敗。請確認整個選取區域目前已載入，且座標有效。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail
scoreboard players set @s mcc_clip 1
tellraw @s [{"text":"[Copy/Paste] 已複製到你的 Clipboard。","color":"green"}]
return 1
