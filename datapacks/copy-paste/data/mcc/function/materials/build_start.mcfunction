execute unless score @s mcc_clip matches 1 run tellraw @s [{"text":"[Copy/Paste] Clipboard 是空的。","color":"red"}]
execute unless score @s mcc_clip matches 1 run return fail
execute unless score @s mcc_cliptype matches 1 run tellraw @s [{"text":"[Copy/Paste] /trigger build 只用於 Copy Blueprint；Cut 仍用 /trigger v。","color":"red"}]
execute unless score @s mcc_cliptype matches 1 run return fail
execute unless score @s mcc_bpactive matches 1 run tellraw @s [{"text":"[Copy/Paste] 請先用 /trigger v 建立 Blueprint。","color":"red"}]
execute unless score @s mcc_bpactive matches 1 run return fail
execute unless score @s mcc_bpready matches 1 run tellraw @s [{"text":"[Copy/Paste] Blueprint 還在建立中，請稍候。","color":"yellow"}]
execute unless score @s mcc_bpready matches 1 run return fail
execute if score @s mcc_bpbad matches 1.. run tellraw @s [{"text":"[Copy/Paste] Blueprint 含有目前無法安全換算成生存材料的方塊，未施工。","color":"red"}]
execute if score @s mcc_bpbad matches 1.. run return fail
execute if score @s mcc_matphase matches 1.. run tellraw @s [{"text":"[Copy/Paste] 材料檢查已在進行中。","color":"yellow"}]
execute if score @s mcc_matphase matches 1.. run return fail
execute if score @s mcc_bpover matches 1.. unless score @s mcc_buildconfirm matches 1 run return run function mcc:materials/build_warn_overlap
scoreboard players set @s mcc_buildconfirm 0
function mcc:materials/ensure_player
function mcc:materials/reset_have_start
scoreboard players set @s mcc_materr 0
scoreboard players set @s mcc_matjob 0
scoreboard players set @s mcc_matphase 1
function mcc:materials/queue_items
tellraw @s [{"text":"[Copy/Paste] 正在透過 Warehouse API 分批檢查施工材料…","color":"aqua"}]
execute if score @s mcc_matleft matches 0 run return run function mcc:materials/count_done
return 1
