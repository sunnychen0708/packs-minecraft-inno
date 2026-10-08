scoreboard players add #ray su_tmp 1
execute if score #found su_tmp matches 0 if block ~ ~ ~ #survival_utils:ore/diamond run function survival_utils:vein/diamond/start
execute if score #found su_tmp matches 0 if score #ray su_tmp matches 4.. if block ~ ~ ~ #survival_utils:ray_pass run function survival_utils:vein/diamond/check_neighbors
execute if score #found su_tmp matches 0 if score #ray su_tmp matches ..32 if block ~ ~ ~ #survival_utils:ray_pass positioned ^ ^ ^0.25 run function survival_utils:vein/diamond/raycast
