# Input: mcc_tmp = world axis to flip (1 = X, 2 = Z), applied on top of the current direction.
# Placement is R(rot) after M(mir); a world flip F gives F*R(k)*M = R(-k)*(F*M), and
# F*M is F (M none), nothing (M = F) or a 180 degree turn (M = the other axis).
scoreboard players operation @s mcc_rot *= #neg mcc_id
execute if score @s mcc_rot matches ..-1 run scoreboard players add @s mcc_rot 4
scoreboard players set @s mcc_tmp2 3
execute if score @s mcc_mir matches 0 run scoreboard players set @s mcc_tmp2 1
execute if score @s mcc_mir = @s mcc_tmp run scoreboard players set @s mcc_tmp2 2
execute if score @s mcc_tmp2 matches 1 run scoreboard players operation @s mcc_mir = @s mcc_tmp
execute if score @s mcc_tmp2 matches 2..3 run scoreboard players set @s mcc_mir 0
execute if score @s mcc_tmp2 matches 3 run scoreboard players add @s mcc_rot 2
execute if score @s mcc_rot matches 4.. run scoreboard players remove @s mcc_rot 4
function mcc:state/announce_orient
function mcc:blueprint/rebuild_if_active
