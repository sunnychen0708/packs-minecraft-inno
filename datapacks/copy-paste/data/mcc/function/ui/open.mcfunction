# The main Dialog has no status text; only the toggle buttons show their current value.
data modify storage mcc:ui rot set value "旋轉 0°"
execute if score @s mcc_rot matches 1 run data modify storage mcc:ui rot set value "旋轉 90°"
execute if score @s mcc_rot matches 2 run data modify storage mcc:ui rot set value "旋轉 180°"
execute if score @s mcc_rot matches 3 run data modify storage mcc:ui rot set value "旋轉 270°"
data modify storage mcc:ui mir set value "鏡像 無"
execute if score @s mcc_mir matches 1 run data modify storage mcc:ui mir set value "鏡像 X"
execute if score @s mcc_mir matches 2 run data modify storage mcc:ui mir set value "鏡像 Z"
data modify storage mcc:ui mode set value "空氣也覆蓋"
execute if score @s mcc_mask matches 1 run data modify storage mcc:ui mode set value "空氣不覆蓋"

function mcc:ui/show with storage mcc:ui
