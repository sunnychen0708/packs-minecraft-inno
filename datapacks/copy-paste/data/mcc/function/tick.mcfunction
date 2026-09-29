execute as @a unless score @s mcc_id matches 1.. run function mcc:player_init
execute as @a[scores={mcc_help=1..}] run function mcc:help
execute as @a[scores={mcc_pos1=1..}] at @s run function mcc:select/start_pos1
execute as @a[scores={mcc_pos2=1..}] at @s run function mcc:select/start_pos2
execute as @a[scores={mcc_anchor=1}] at @s run function mcc:select/start_anchor
execute as @a[scores={mcc_anchor=2..}] run function mcc:anchor_clear
execute as @a[scores={mcc_copy=1..}] run function mcc:copy/run
execute as @a[scores={mcc_paste=1..}] at @s run function mcc:select/start_paste
execute as @a[scores={mcc_mode=1..}] run function mcc:mode_toggle

scoreboard players set @a[scores={mcc_help=1..}] mcc_help 0
scoreboard players set @a[scores={mcc_pos1=1..}] mcc_pos1 0
scoreboard players set @a[scores={mcc_pos2=1..}] mcc_pos2 0
scoreboard players set @a[scores={mcc_anchor=1..}] mcc_anchor 0
scoreboard players set @a[scores={mcc_copy=1..}] mcc_copy 0
scoreboard players set @a[scores={mcc_paste=1..}] mcc_paste 0
scoreboard players set @a[scores={mcc_mode=1..}] mcc_mode 0

scoreboard players enable @a mcc_pos1
scoreboard players enable @a mcc_pos2
scoreboard players enable @a mcc_anchor
scoreboard players enable @a mcc_copy
scoreboard players enable @a mcc_paste
scoreboard players enable @a mcc_mode
scoreboard players enable @a mcc_help
