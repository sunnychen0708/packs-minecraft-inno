scoreboard players operation #toggle_old wh_tmp = #enabled wh_sys
execute if score #toggle_old wh_tmp matches 1 run scoreboard players set #enabled wh_sys 0
execute if score #toggle_old wh_tmp matches 0 run scoreboard players set #enabled wh_sys 1
