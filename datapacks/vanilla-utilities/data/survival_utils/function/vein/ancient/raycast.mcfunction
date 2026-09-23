scoreboard players add #ray su_tmp 1
execute if score #found su_tmp matches 0 if block ~ ~ ~ #survival_utils:ore/ancient run function survival_utils:vein/ancient/start
execute if score #found su_tmp matches 0 if score #ray su_tmp matches 4.. if block ~ ~ ~ #survival_utils:ray_pass run function survival_utils:vein/ancient/check_neighbors
execute if score #found su_tmp matches 0 if score #ray su_tmp matches ..32 if block ~ ~ ~ #survival_utils:ray_pass positioned ^ ^ ^0.25 run function survival_utils:vein/ancient/raycast
