# One-time per-player upgrade: initialize newly introduced state for existing players
# without resetting their clipboard. Bump mcc_stver (here and in tick) when adding state.
execute unless score @s mcc_rot matches 0..3 run scoreboard players set @s mcc_rot 0
execute unless score @s mcc_mir matches 0..2 run scoreboard players set @s mcc_mir 0
execute unless score @s mcc_usel matches 0..1 run scoreboard players set @s mcc_usel 0
execute unless score @s mcc_cliptype matches 0..2 run scoreboard players set @s mcc_cliptype 0
execute unless score @s mcc_redo matches 0..1 run scoreboard players set @s mcc_redo 0
execute unless score @s mcc_ucnt matches 0..5 run scoreboard players set @s mcc_ucnt 0
execute unless score @s mcc_uhead matches 0..5 run scoreboard players set @s mcc_uhead 0
execute unless score @s mcc_rcnt matches 0..5 run scoreboard players set @s mcc_rcnt 0
execute unless score @s mcc_rhead matches 0..5 run scoreboard players set @s mcc_rhead 0
execute unless score @s mcc_bpscan matches 0..1 run scoreboard players set @s mcc_bpscan 0
execute unless score @s mcc_bpactive matches 0..1 run scoreboard players set @s mcc_bpactive 0
execute unless score @s mcc_bpready matches 0..1 run scoreboard players set @s mcc_bpready 0
execute unless score @s mcc_bpbad matches 0..1 run scoreboard players set @s mcc_bpbad 0
execute unless score @s mcc_matphase matches 0..2 run scoreboard players set @s mcc_matphase 0
execute unless score @s mcc_matleft matches 0.. run scoreboard players set @s mcc_matleft 0
execute unless score @s mcc_materr matches 0..1 run scoreboard players set @s mcc_materr 0
execute unless score @s mcc_histmat matches 0..1 run scoreboard players set @s mcc_histmat 0
execute unless score @s mcc_umat matches 0..1 run scoreboard players set @s mcc_umat 0
execute unless score @s mcc_rmat matches 0..1 run scoreboard players set @s mcc_rmat 0
execute unless score @s mcc_histguard matches 0..1 run scoreboard players set @s mcc_histguard 0
execute unless score @s mcc_histcut matches 0..1 run scoreboard players set @s mcc_histcut 0
execute unless score @s mcc_emir matches 0..2 run scoreboard players set @s mcc_emir 0
execute unless score @s mcc_matjob matches 0..2 run scoreboard players set @s mcc_matjob 0
execute unless score @s mcc_txslot matches 0..5 run scoreboard players set @s mcc_txslot 0
execute unless score @s mcc_bpover matches 0.. run scoreboard players set @s mcc_bpover 0
execute unless score @s mcc_buildconfirm matches 0..1 run scoreboard players set @s mcc_buildconfirm 0
execute unless score @s mcc_bpover_scan matches 0..1 run scoreboard players set @s mcc_bpover_scan 0
execute unless score @s mcc_bpoindex matches 0.. run scoreboard players set @s mcc_bpoindex 0
execute unless score @s mcc_bpoffx = @s mcc_bpoffx run scoreboard players set @s mcc_bpoffx 0
execute unless score @s mcc_bpoffz = @s mcc_bpoffz run scoreboard players set @s mcc_bpoffz 0
execute unless score @s mcc_canchor matches 0..1 run scoreboard players set @s mcc_canchor 0
scoreboard players set @s mcc_stver 1
