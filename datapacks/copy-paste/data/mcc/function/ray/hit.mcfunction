execute if score @s mcc_selmode matches 1 run return run function mcc:ray/hit_pos1
execute if score @s mcc_selmode matches 2 run return run function mcc:ray/hit_pos2
execute if score @s mcc_selmode matches 3 run return run function mcc:ray/hit_anchor
execute if score @s mcc_selmode matches 4 run return run function mcc:ray/hit_paste
execute if score @s mcc_selmode matches 5 run return run function mcc:ray/hit_matbox
execute if score @s mcc_selmode matches 6 run return run function mcc:ray/hit_matremove
return fail
