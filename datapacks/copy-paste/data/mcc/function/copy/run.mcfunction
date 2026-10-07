execute store success score @s mcc_tmp run function mcc:copy/snapshot
execute unless score @s mcc_tmp matches 1 run return fail
scoreboard players operation @s mcc_canchor = @s mcc_hasa
scoreboard players set @s mcc_bpoffx 0
scoreboard players set @s mcc_bpoffz 0
# If an old Blueprint orientation already carries a mirror, rebase it so the
# mirrored bounding box stays in place for this newly copied selection.
execute if score @s mcc_canchor matches 0 if score @s mcc_mir matches 1.. run scoreboard players operation @s mcc_amt = @s mcc_mir
execute if score @s mcc_canchor matches 0 if score @s mcc_mir matches 1.. run scoreboard players set @s mcc_dstx 0
execute if score @s mcc_canchor matches 0 if score @s mcc_mir matches 1.. run scoreboard players set @s mcc_dsty 0
execute if score @s mcc_canchor matches 0 if score @s mcc_mir matches 1.. run scoreboard players set @s mcc_dstz 0
execute if score @s mcc_canchor matches 0 if score @s mcc_mir matches 1.. run scoreboard players set @s mcc_mir 0
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run function mcc:paste/prepare_transform
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run scoreboard players operation @s mcc_dx = @s mcc_bminx
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run scoreboard players operation @s mcc_dz = @s mcc_bminz
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run scoreboard players operation @s mcc_mir = @s mcc_amt
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run scoreboard players set @s mcc_dstx 0
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run scoreboard players set @s mcc_dsty 0
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run scoreboard players set @s mcc_dstz 0
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run function mcc:paste/prepare_transform
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run scoreboard players operation @s mcc_bpoffx = @s mcc_dx
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run scoreboard players operation @s mcc_bpoffx -= @s mcc_bminx
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run scoreboard players operation @s mcc_bpoffz = @s mcc_dz
execute if score @s mcc_canchor matches 0 if score @s mcc_amt matches 1.. run scoreboard players operation @s mcc_bpoffz -= @s mcc_bminz
function mcc:blueprint/clear_internal
scoreboard players set @s mcc_cliptype 1
tellraw @s [{"text":"[Copy/Paste] 已複製。用 /trigger v 建立 Blueprint；確認後用 /trigger build 施工（先用背包的材料，不夠再從 Warehouse 扣）。","color":"green"}]
return 1
