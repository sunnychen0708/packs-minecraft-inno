execute unless block ~ ~ ~ #mcc:material_chests run tellraw @s [{"text":"[Copy/Paste] 請瞄準已註冊的箱子、銅箱、陷阱箱或木桶。","color":"red"}]
execute unless block ~ ~ ~ #mcc:material_chests run return fail
function mcc:materials/unregister_target
return 1
