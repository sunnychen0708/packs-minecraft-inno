# In: #bcode wh_tmp = box code (100 = entry), #bbase wh_tmp = nav number of the region-1 list minus 1.
# Out: wh_back = that list's region page (base + region), or base + 7 for the entry/overflow page.
scoreboard players set #ten wh_tmp 10
scoreboard players operation #breg wh_tmp = #bcode wh_tmp
scoreboard players operation #breg wh_tmp /= #ten wh_tmp
scoreboard players operation #bmod wh_tmp = #bcode wh_tmp
scoreboard players operation #bmod wh_tmp %= #ten wh_tmp
scoreboard players operation @s wh_back = #bbase wh_tmp
execute if score #bmod wh_tmp matches 0 run scoreboard players add @s wh_back 7
execute unless score #bmod wh_tmp matches 0 run scoreboard players operation @s wh_back += #breg wh_tmp
