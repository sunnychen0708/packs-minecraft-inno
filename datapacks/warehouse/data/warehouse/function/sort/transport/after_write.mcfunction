scoreboard players operation #delta wh_tmp = #after wh_tmp
scoreboard players operation #delta wh_tmp -= #before wh_tmp
execute if score #delta wh_tmp matches 1.. run scoreboard players operation #moved wh_tmp += #delta wh_tmp
execute if score #delta wh_tmp matches 1.. run scoreboard players operation #remaining wh_tmp -= #delta wh_tmp
execute if score #remaining wh_tmp matches ..0 run scoreboard players set #remaining wh_tmp 0
