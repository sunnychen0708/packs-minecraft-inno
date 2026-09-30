scoreboard players add @s mcc_mir 1
execute if score @s mcc_mir matches 3.. run scoreboard players set @s mcc_mir 0
function mcc:state/announce_mir
