# Blueprint/V direction: one quarter turn counter-clockwise.
# Keep the default-anchor center-Flip translation attached to the preview.
execute if score @s mcc_cliptype matches 1..2 if score @s mcc_canchor matches 0 run scoreboard players operation @s mcc_tmp = @s mcc_bpoffx
execute if score @s mcc_cliptype matches 1..2 if score @s mcc_canchor matches 0 run scoreboard players operation @s mcc_bpoffx = @s mcc_bpoffz
execute if score @s mcc_cliptype matches 1..2 if score @s mcc_canchor matches 0 run scoreboard players operation @s mcc_bpoffz = @s mcc_tmp
execute if score @s mcc_cliptype matches 1..2 if score @s mcc_canchor matches 0 run scoreboard players operation @s mcc_bpoffz *= #neg mcc_id
scoreboard players remove @s mcc_rot 1
execute if score @s mcc_rot matches ..-1 run scoreboard players set @s mcc_rot 3
tellraw @s {"text":"[Copy/Paste] Blueprint 向左轉 90°。","color":"green"}
function mcc:state/announce_orient
function mcc:blueprint/rebuild_if_active
