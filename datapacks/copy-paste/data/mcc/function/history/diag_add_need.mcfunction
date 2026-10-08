# One placed item can represent both halves of doors/beds/tall plants.
$execute in minecraft:overworld positioned $(sx) $(sy) $(sz) if block ~ ~ ~ #minecraft:doors[half=upper] run return 1
$execute in minecraft:overworld positioned $(sx) $(sy) $(sz) if block ~ ~ ~ #minecraft:beds[part=foot] run return 1
$execute in minecraft:overworld positioned $(sx) $(sy) $(sz) if block ~ ~ ~ #mcc:material_free_upper_half[half=upper] run return 1

$execute unless data storage mcc:temp diag.need."$(cmp_bid)" run data modify storage mcc:temp diag.need."$(cmp_bid)" set value 0
$execute unless data storage mcc:temp diag.need_items[{id:"$(cmp_bid)"}] run data modify storage mcc:temp diag.need_items append value {id:"$(cmp_bid)",sx:$(sx),sy:$(sy),sz:$(sz)}
$execute store result score #diag_need mcc_tmp run data get storage mcc:temp diag.need."$(cmp_bid)"
scoreboard players add #diag_need mcc_tmp 1
$execute store result storage mcc:temp diag.need."$(cmp_bid)" int 1 run scoreboard players get #diag_need mcc_tmp
return 1
