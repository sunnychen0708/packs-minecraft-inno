scoreboard players set @s mcc_rot 0
scoreboard players set @s mcc_mir 0
scoreboard players set @s mcc_bpoffx 0
scoreboard players set @s mcc_bpoffz 0
tellraw @s {"text":"[Copy/Paste] Blueprint 回到原本方向。","color":"green"}
function mcc:state/announce_orient
function mcc:blueprint/rebuild_if_active
