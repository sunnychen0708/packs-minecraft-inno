scoreboard players set @s mcc_undo 0
execute if score @s mcc_ucnt matches 1.. run scoreboard players set @s mcc_undo 1
scoreboard players set @s mcc_redo 0
execute if score @s mcc_rcnt matches 1.. run scoreboard players set @s mcc_redo 1
