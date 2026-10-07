scoreboard players operation #diag_ox mcc_id = @s mcc_ux
scoreboard players operation #diag_oy mcc_id = @s mcc_uy
scoreboard players operation #diag_oz mcc_id = @s mcc_uz
scoreboard players operation #diag_dim mcc_id = @s mcc_udim
execute if score #cmp_big mcc_id matches 1 run return run function mcc:history/undo_guard_fail_exact
function mcc:history/diagnose_guard with storage mcc:temp cmp
tellraw @s [{"text":"[Copy/Paste] Undo 無法執行：操作完成後有 ","color":"red"},{"score":{"name":"@s","objective":"mcc_diagcount"},"color":"yellow"},{"text":" 個位置被修改。","color":"red"}]
function mcc:history/diag_report
tellraw @s [{"text":"修復後再次使用 /trigger undo；block state 不需要還原。","color":"gray"}]
scoreboard players set @s mcc_ok 0
return fail
