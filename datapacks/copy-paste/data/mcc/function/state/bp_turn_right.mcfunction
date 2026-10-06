# Blueprint/V direction: one more quarter turn clockwise (seen from above), as the player sees it.
scoreboard players add @s mcc_rot 1
execute if score @s mcc_rot matches 4.. run scoreboard players set @s mcc_rot 0
tellraw @s {"text":"[Copy/Paste] Blueprint 向右轉 90°。","color":"green"}
function mcc:state/announce_orient
function mcc:blueprint/rebuild_if_active
