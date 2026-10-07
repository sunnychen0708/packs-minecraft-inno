scoreboard players add #cmp_work mcc_id 1
execute if score #cmp_work mcc_id > #cmp_work_max mcc_id run return run function mcc:history/compare_over_budget
execute store result storage mcc:temp cmpb.sx int 1 run scoreboard players get @s mcc_mnx
execute store result storage mcc:temp cmpb.sy int 1 run scoreboard players get @s mcc_mny
execute store result storage mcc:temp cmpb.sz int 1 run scoreboard players get @s mcc_mnz
execute store result storage mcc:temp cmpb.tx int 1 run scoreboard players get @s mcc_dstx
execute store result storage mcc:temp cmpb.ty int 1 run scoreboard players get @s mcc_dsty
execute store result storage mcc:temp cmpb.tz int 1 run scoreboard players get @s mcc_dstz
function mcc:history/compare_block with storage mcc:temp cmpb
execute unless score @s mcc_ok matches 1 run return fail
execute if score @s mcc_cmpaxis matches 1 run scoreboard players add @s mcc_mnx 1
execute if score @s mcc_cmpaxis matches 1 run scoreboard players add @s mcc_dstx 1
execute if score @s mcc_cmpaxis matches 2 run scoreboard players add @s mcc_mny 1
execute if score @s mcc_cmpaxis matches 2 run scoreboard players add @s mcc_dsty 1
execute if score @s mcc_cmpaxis matches 3 run scoreboard players add @s mcc_mnz 1
execute if score @s mcc_cmpaxis matches 3 run scoreboard players add @s mcc_dstz 1
execute if score @s mcc_cmpaxis matches 1 if score @s mcc_mnx <= @s mcc_mxx run return run function mcc:history/compare_line
execute if score @s mcc_cmpaxis matches 2 if score @s mcc_mny <= @s mcc_mxy run return run function mcc:history/compare_line
execute if score @s mcc_cmpaxis matches 3 if score @s mcc_mnz <= @s mcc_mxz run return run function mcc:history/compare_line
return 1
