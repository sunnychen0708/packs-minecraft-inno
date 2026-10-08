# "More" page; the paste-mode button names the mode that is active right now.
data modify storage mcc:ui mode set value "貼上：完全取代"
data modify storage mcc:ui modetip set value "現在：複製範圍裡的空氣會把目標位置原有的方塊清掉。點一下改成「保留原方塊」。"
execute if score @s mcc_mask matches 1 run data modify storage mcc:ui mode set value "貼上：保留原方塊"
execute if score @s mcc_mask matches 1 run data modify storage mcc:ui modetip set value "現在：只放複製到的方塊，目標位置原有的方塊不會被清掉。點一下改成「完全取代」。"
function mcc:ui/more_show with storage mcc:ui
