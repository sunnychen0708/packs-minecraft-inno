execute if score @s mcc_hasa matches 1 run return run function mcc:flip/z_anchor
execute store success score @s mcc_tmp run function mcc:flip/common_prepare
execute unless score @s mcc_tmp matches 1 run return fail
execute store result storage mcc:temp minx int 1 run scoreboard players get @s mcc_minx
execute store result storage mcc:temp miny int 1 run scoreboard players get @s mcc_miny
execute store result storage mcc:temp minz int 1 run scoreboard players get @s mcc_minz
execute store result storage mcc:temp maxx int 1 run scoreboard players get @s mcc_maxx
execute store result storage mcc:temp maxz int 1 run scoreboard players get @s mcc_maxz
scoreboard players set @s mcc_ok 0
execute if score @s mcc_p1d matches 1 run function mcc:flip/place_z_overworld with storage mcc:temp
execute if score @s mcc_p1d matches 2 run function mcc:flip/place_z_nether with storage mcc:temp
execute if score @s mcc_p1d matches 3 run function mcc:flip/place_z_end with storage mcc:temp
execute unless score @s mcc_ok matches 1 run return run function mcc:flip/fail_place_z
function mcc:flip/cleanup_forceload
function mcc:undo/snapshot_selection
function mcc:history/commit_edit
tellraw @s [{"text":"[Copy/Paste] 翻轉完成，可用 /trigger undo 復原。","color":"green"}]
return 1
