$execute positioned $(sx) $(sy) $(sz) unless block ~ ~ ~ #minecraft:air run function mcc:blueprint/generated/root with storage mcc:temp
$execute if score @s mcc_bpkind matches 1 positioned $(sx) $(sy) $(sz) run setblock ~ ~ ~ air
