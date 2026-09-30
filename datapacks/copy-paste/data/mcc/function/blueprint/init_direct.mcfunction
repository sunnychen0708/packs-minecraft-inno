# Source is the persistent private Clipboard in the hidden Overworld lane.
scoreboard players operation @s mcc_bpsx0 = @s mcc_cbx
scoreboard players set @s mcc_bpsy0 0
scoreboard players operation @s mcc_bpsz0 = #cbz mcc_id
scoreboard players operation @s mcc_bpsx2 = @s mcc_cbx2
scoreboard players operation @s mcc_bpsy2 = @s mcc_cby2
scoreboard players operation @s mcc_bpsz2 = @s mcc_cbz2

# Target minimum = aimed anchor - stored Copy anchor offset.
scoreboard players operation @s mcc_bptx0 = @s mcc_dstx
scoreboard players operation @s mcc_bptx0 -= @s mcc_offx
scoreboard players operation @s mcc_bpty0 = @s mcc_dsty
scoreboard players operation @s mcc_bpty0 -= @s mcc_offy
scoreboard players operation @s mcc_bptz0 = @s mcc_dstz
scoreboard players operation @s mcc_bptz0 -= @s mcc_offz
scoreboard players set @s mcc_bpkind 0
function mcc:blueprint/start_scan
return 1
