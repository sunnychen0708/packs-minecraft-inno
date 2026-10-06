# Blueprint/V direction: one quarter turn counter-clockwise.
scoreboard players remove @s mcc_rot 1
execute if score @s mcc_rot matches ..-1 run scoreboard players set @s mcc_rot 3
tellraw @s {"text":"[Copy/Paste] Blueprint 向左轉 90°。","color":"green"}
function mcc:state/announce_orient
function mcc:blueprint/rebuild_if_active
