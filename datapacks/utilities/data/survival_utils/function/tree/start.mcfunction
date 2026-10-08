scoreboard players set #found su_tmp 1
scoreboard players set #leaf su_tmp 0
function survival_utils:tree/check_foliage
execute if score #leaf su_tmp matches 1 run function survival_utils:tree/break
execute unless score #leaf su_tmp matches 1 run title @s actionbar {"text":"附近沒有樹葉，為避免破壞建築而取消","color":"yellow"}
