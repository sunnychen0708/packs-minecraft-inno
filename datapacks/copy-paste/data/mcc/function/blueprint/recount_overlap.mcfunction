# Re-count overlap after a pure Blueprint translation without rebuilding BOM/display entities.
scoreboard players set @s mcc_bpover 0
scoreboard players operation @s mcc_bpsx = @s mcc_bpsx0
scoreboard players operation @s mcc_bpsy = @s mcc_bpsy0
scoreboard players operation @s mcc_bpsz = @s mcc_bpsz0
scoreboard players operation @s mcc_bptx = @s mcc_bptx0
scoreboard players operation @s mcc_bpty = @s mcc_bpty0
scoreboard players operation @s mcc_bptz = @s mcc_bptz0
scoreboard players set @s mcc_tmp2 0
function mcc:blueprint/recount_batch
return 1
