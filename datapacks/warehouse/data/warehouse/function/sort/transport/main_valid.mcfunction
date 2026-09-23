scoreboard players set #main_ok wh_tmp 1
execute if score #remaining wh_tmp matches 1.. run function warehouse:sort/transport/main_merge with storage warehouse:runtime move
execute if score #remaining wh_tmp matches 1.. run function warehouse:sort/transport/main_empty with storage warehouse:runtime move
