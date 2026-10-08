scoreboard players add @s mcc_rot 1
execute if score @s mcc_rot matches 4.. run scoreboard players set @s mcc_rot 0
function mcc:state/announce_rot
