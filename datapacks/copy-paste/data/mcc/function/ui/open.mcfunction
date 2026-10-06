# The main Dialog has no status text; only the air-mode button shows its current value.
data modify storage mcc:ui mode set value "空氣也覆蓋"
execute if score @s mcc_mask matches 1 run data modify storage mcc:ui mode set value "空氣不覆蓋"

function mcc:ui/show with storage mcc:ui
