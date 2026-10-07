execute if score @s mcc_cmpmode matches 1 run return run function mcc:history/compare_block_id_callback
$execute if score @s mcc_bpdst matches 1 in minecraft:overworld run summon minecraft:block_display $(tx).0 $(ty).0 $(tz).0 {Tags:["mcc_blueprint","mcc_new","mcc_bp_$(id)"]}
$execute if score @s mcc_bpdst matches 2 in minecraft:the_nether run summon minecraft:block_display $(tx).0 $(ty).0 $(tz).0 {Tags:["mcc_blueprint","mcc_new","mcc_bp_$(id)"]}
$execute if score @s mcc_bpdst matches 3 in minecraft:the_end run summon minecraft:block_display $(tx).0 $(ty).0 $(tz).0 {Tags:["mcc_blueprint","mcc_new","mcc_bp_$(id)"]}
$execute if score @s mcc_bpdst matches 1 in minecraft:overworld positioned $(tx).0 $(ty).0 $(tz).0 run data modify entity @e[type=minecraft:block_display,tag=mcc_new,tag=mcc_bp_$(id),distance=..0.1,limit=1] block_state set from storage mcc:temp state
$execute if score @s mcc_bpdst matches 2 in minecraft:the_nether positioned $(tx).0 $(ty).0 $(tz).0 run data modify entity @e[type=minecraft:block_display,tag=mcc_new,tag=mcc_bp_$(id),distance=..0.1,limit=1] block_state set from storage mcc:temp state
$execute if score @s mcc_bpdst matches 3 in minecraft:the_end positioned $(tx).0 $(ty).0 $(tz).0 run data modify entity @e[type=minecraft:block_display,tag=mcc_new,tag=mcc_bp_$(id),distance=..0.1,limit=1] block_state set from storage mcc:temp state
$execute if score @s mcc_bpdst matches 1 in minecraft:overworld run tag @e[type=minecraft:block_display,tag=mcc_new,tag=mcc_bp_$(id)] remove mcc_new
$execute if score @s mcc_bpdst matches 2 in minecraft:the_nether run tag @e[type=minecraft:block_display,tag=mcc_new,tag=mcc_bp_$(id)] remove mcc_new
$execute if score @s mcc_bpdst matches 3 in minecraft:the_end run tag @e[type=minecraft:block_display,tag=mcc_new,tag=mcc_bp_$(id)] remove mcc_new
return 1
