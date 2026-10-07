# Input: mcc_canchor (0 = default Pos1 Anchor). Resets the center-Flip offset for a new
# Copy/Cut clipboard; an inherited mirror is rebased so its bounding box stays in place.
scoreboard players set @s mcc_bpoffx 0
scoreboard players set @s mcc_bpoffz 0
scoreboard players set @s mcc_amt 0
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
return 1
