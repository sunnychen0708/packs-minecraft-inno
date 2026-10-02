$data modify storage mcc:history u_p$(id)_s$(slot) set value {}
$execute store result storage mcc:history u_p$(id)_s$(slot).dim int 1 run scoreboard players get @s mcc_udim
$execute store result storage mcc:history u_p$(id)_s$(slot).x int 1 run scoreboard players get @s mcc_ux
$execute store result storage mcc:history u_p$(id)_s$(slot).y int 1 run scoreboard players get @s mcc_uy
$execute store result storage mcc:history u_p$(id)_s$(slot).z int 1 run scoreboard players get @s mcc_uz
$execute store result storage mcc:history u_p$(id)_s$(slot).x2 int 1 run scoreboard players get @s mcc_ux2
$execute store result storage mcc:history u_p$(id)_s$(slot).y2 int 1 run scoreboard players get @s mcc_uy2
$execute store result storage mcc:history u_p$(id)_s$(slot).z2 int 1 run scoreboard players get @s mcc_uz2
$execute store result storage mcc:history u_p$(id)_s$(slot).sel int 1 run scoreboard players get @s mcc_usel
$execute store result storage mcc:history u_p$(id)_s$(slot).p1x int 1 run scoreboard players get @s mcc_up1x
$execute store result storage mcc:history u_p$(id)_s$(slot).p1y int 1 run scoreboard players get @s mcc_up1y
$execute store result storage mcc:history u_p$(id)_s$(slot).p1z int 1 run scoreboard players get @s mcc_up1z
$execute store result storage mcc:history u_p$(id)_s$(slot).p2x int 1 run scoreboard players get @s mcc_up2x
$execute store result storage mcc:history u_p$(id)_s$(slot).p2y int 1 run scoreboard players get @s mcc_up2y
$execute store result storage mcc:history u_p$(id)_s$(slot).p2z int 1 run scoreboard players get @s mcc_up2z
$execute store result storage mcc:history u_p$(id)_s$(slot).anx int 1 run scoreboard players get @s mcc_uanx
$execute store result storage mcc:history u_p$(id)_s$(slot).any int 1 run scoreboard players get @s mcc_uany
$execute store result storage mcc:history u_p$(id)_s$(slot).anz int 1 run scoreboard players get @s mcc_uanz
$execute store result storage mcc:history u_p$(id)_s$(slot).hasa int 1 run scoreboard players get @s mcc_uhasa
$execute store result storage mcc:history u_p$(id)_s$(slot).mat int 1 run scoreboard players get @s mcc_histmat
$execute if score @s mcc_histmat matches 1 run data modify storage mcc:debug material_save set value {id:$(id),slot:$(slot),stage:"saved"}
execute if score @s mcc_histmat matches 1 store result storage mcc:debug material_save.histmat int 1 run scoreboard players get @s mcc_histmat
$execute if score @s mcc_histmat matches 1 run data modify storage mcc:debug material_save.saved_mat set from storage mcc:history u_p$(id)_s$(slot).mat
$execute if score @s mcc_histmat matches 1 run data modify storage mcc:history u_p$(id)_s$(slot).materials.items set from storage mcc:materials p$(id).items
$execute if score @s mcc_histmat matches 1 run data modify storage mcc:history u_p$(id)_s$(slot).materials.bom set from storage mcc:materials p$(id).bom
