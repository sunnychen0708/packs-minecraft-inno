# Build the status strings for the main Dialog, then show it via a macro.
execute store result storage mcc:ui p1x int 1 run scoreboard players get @s mcc_p1x
execute store result storage mcc:ui p1y int 1 run scoreboard players get @s mcc_p1y
execute store result storage mcc:ui p1z int 1 run scoreboard players get @s mcc_p1z
execute store result storage mcc:ui p2x int 1 run scoreboard players get @s mcc_p2x
execute store result storage mcc:ui p2y int 1 run scoreboard players get @s mcc_p2y
execute store result storage mcc:ui p2z int 1 run scoreboard players get @s mcc_p2z
execute store result storage mcc:ui anx int 1 run scoreboard players get @s mcc_anx
execute store result storage mcc:ui any int 1 run scoreboard players get @s mcc_any
execute store result storage mcc:ui anz int 1 run scoreboard players get @s mcc_anz
execute store result storage mcc:ui ucnt int 1 run scoreboard players get @s mcc_ucnt
execute store result storage mcc:ui rcnt int 1 run scoreboard players get @s mcc_rcnt

data modify storage mcc:ui s1 set value "Pos1 未設定"
execute if score @s mcc_has1 matches 1 run function mcc:ui/fmt_p1 with storage mcc:ui
data modify storage mcc:ui s2 set value "Pos2 未設定"
execute if score @s mcc_has2 matches 1 run function mcc:ui/fmt_p2 with storage mcc:ui
data modify storage mcc:ui anchor set value "Anchor：預設＝Pos1"
execute if score @s mcc_hasa matches 1 run function mcc:ui/fmt_anchor with storage mcc:ui

data modify storage mcc:ui clip set value "剪貼簿：空（先 Copy 或 Cut）"
execute if score @s mcc_clip matches 1 if score @s mcc_cliptype matches 1 run data modify storage mcc:ui clip set value "剪貼簿：Copy → 看著目標按 V 放 Blueprint"
execute if score @s mcc_clip matches 1 if score @s mcc_cliptype matches 2 run data modify storage mcc:ui clip set value "剪貼簿：Cut → 看著目標按 V 直接搬過去"
data modify storage mcc:ui bp set value "Blueprint：無"
execute if score @s mcc_bpactive matches 1 run data modify storage mcc:ui bp set value "Blueprint：已放置 → 材料檢查 / 施工"
execute if score @s mcc_bpactive matches 1 unless score @s mcc_bpready matches 1 run data modify storage mcc:ui bp set value "Blueprint：建立中…"
execute if score @s mcc_matphase matches 1.. run data modify storage mcc:ui bp set value "材料檢查／施工進行中…"
function mcc:ui/fmt_hist with storage mcc:ui

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
