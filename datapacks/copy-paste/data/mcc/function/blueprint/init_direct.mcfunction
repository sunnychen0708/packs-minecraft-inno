# Snapshot Copy Clipboard into a dedicated Blueprint buffer before scanning.
# This keeps the preview stable even if the player Copy-s something else while it is rendering.
scoreboard players operation @s mcc_bpx = @s mcc_id
scoreboard players operation @s mcc_bpx *= #slot mcc_id
scoreboard players operation @s mcc_bpx += #base mcc_id
scoreboard players operation @s mcc_bpsx0 = @s mcc_bpx
scoreboard players set @s mcc_bpsy0 0
scoreboard players operation @s mcc_bpsz0 = #bpz mcc_id
scoreboard players operation @s mcc_bpsx2 = @s mcc_bpsx0
scoreboard players operation @s mcc_bpsx2 += @s mcc_sx
scoreboard players remove @s mcc_bpsx2 1
scoreboard players operation @s mcc_bpsy2 = @s mcc_sy
scoreboard players remove @s mcc_bpsy2 1
scoreboard players operation @s mcc_bpsz2 = @s mcc_bpsz0
scoreboard players operation @s mcc_bpsz2 += @s mcc_sz
scoreboard players remove @s mcc_bpsz2 1

execute store result storage mcc:temp cbx int 1 run scoreboard players get @s mcc_cbx
execute store result storage mcc:temp cbx2 int 1 run scoreboard players get @s mcc_cbx2
execute store result storage mcc:temp cbz2 int 1 run scoreboard players get @s mcc_cbz2
execute store result storage mcc:temp bpx int 1 run scoreboard players get @s mcc_bpsx0
execute store result storage mcc:temp bpx2 int 1 run scoreboard players get @s mcc_bpsx2
execute store result storage mcc:temp bpy2 int 1 run scoreboard players get @s mcc_bpsy2
execute store result storage mcc:temp bpz2 int 1 run scoreboard players get @s mcc_bpsz2
scoreboard players set @s mcc_ok 0
function mcc:blueprint/copy_direct_buffer with storage mcc:temp
execute unless score @s mcc_ok matches 1 run tellraw @s [{"text":"[Copy/Paste] Blueprint 快照建立失敗。","color":"red"}]
execute unless score @s mcc_ok matches 1 run return fail

# The aimed adjacent cell is the Anchor destination.
# If no custom Anchor was set, Copy stored Pos1 as the default Anchor.
# Convert that anchor destination back to the Blueprint bounding minimum.
scoreboard players operation @s mcc_bptx0 = @s mcc_dstx
scoreboard players operation @s mcc_bptx0 -= @s mcc_offx
execute if score @s mcc_canchor matches 0 run scoreboard players operation @s mcc_bptx0 += @s mcc_bpoffx
scoreboard players operation @s mcc_bpty0 = @s mcc_dsty
scoreboard players operation @s mcc_bpty0 -= @s mcc_offy
scoreboard players operation @s mcc_bptz0 = @s mcc_dstz
scoreboard players operation @s mcc_bptz0 -= @s mcc_offz
execute if score @s mcc_canchor matches 0 run scoreboard players operation @s mcc_bptz0 += @s mcc_bpoffz
scoreboard players set @s mcc_bpkind 1
return run function mcc:blueprint/start_scan_loaded
