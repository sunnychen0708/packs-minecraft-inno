# Blueprint/V direction: one more quarter turn clockwise (seen from above).
# If a default-anchor center Flip introduced a placement translation, rotate that
# translation around the semantic Pos1 destination too.
execute if score @s mcc_cliptype matches 1..2 if score @s mcc_canchor matches 0 run scoreboard players operation @s mcc_tmp = @s mcc_bpoffx
execute if score @s mcc_cliptype matches 1..2 if score @s mcc_canchor matches 0 run scoreboard players operation @s mcc_bpoffx = @s mcc_bpoffz
execute if score @s mcc_cliptype matches 1..2 if score @s mcc_canchor matches 0 run scoreboard players operation @s mcc_bpoffx *= #neg mcc_id
execute if score @s mcc_cliptype matches 1..2 if score @s mcc_canchor matches 0 run scoreboard players operation @s mcc_bpoffz = @s mcc_tmp
scoreboard players add @s mcc_rot 1
execute if score @s mcc_rot matches 4.. run scoreboard players set @s mcc_rot 0
tellraw @s {"text":"[Copy/Paste] Blueprint 向右轉 90°。","color":"green"}
function mcc:state/announce_orient
function mcc:blueprint/rebuild_if_active
