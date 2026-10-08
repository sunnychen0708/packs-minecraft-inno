scoreboard players operation #diag_ox mcc_id = @s mcc_rx
scoreboard players operation #diag_oy mcc_id = @s mcc_ry
scoreboard players operation #diag_oz mcc_id = @s mcc_rz
scoreboard players operation #diag_dim mcc_id = @s mcc_rdim
function mcc:history/diagnose_guard with storage mcc:temp cmp
tellraw @s [{"text":"[Copy/Paste] Redo 無法執行：Undo 後有 ","color":"red"},{"score":{"name":"@s","objective":"mcc_diagcount"},"color":"yellow"},{"text":" 個位置被修改。","color":"red"}]
function mcc:history/diag_report
tellraw @s [{"text":"修復後再次使用 /trigger redo；block state 不需要還原。","color":"gray"}]
scoreboard players set @s mcc_ok 0
return fail
