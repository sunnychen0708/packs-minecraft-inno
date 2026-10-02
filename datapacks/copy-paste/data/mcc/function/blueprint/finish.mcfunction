execute store result storage mcc:temp x1 int 1 run scoreboard players get @s mcc_bpsx0
execute store result storage mcc:temp z1 int 1 run scoreboard players get @s mcc_bpsz0
execute store result storage mcc:temp x2 int 1 run scoreboard players get @s mcc_bpsx2
execute store result storage mcc:temp z2 int 1 run scoreboard players get @s mcc_bpsz2
function mcc:blueprint/forceload_remove with storage mcc:temp
scoreboard players set @s mcc_bpscan 0
scoreboard players set @s mcc_bpready 1
tellraw @s [{"text":"[Copy/Paste] Blueprint 預覽建立完成；可先旋轉/鏡像，再用 /trigger build 施工。","color":"green"}]
return 1
