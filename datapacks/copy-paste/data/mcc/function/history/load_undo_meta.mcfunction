scoreboard players set @s mcc_usparse 0
scoreboard players set @s mcc_uguard 0
scoreboard players set @s mcc_ucut 0
scoreboard players set @s mcc_umat 0
$execute store result score @s mcc_udim run data get storage mcc:history u_p$(id)_s$(slot).dim 1
$execute store result score @s mcc_ux run data get storage mcc:history u_p$(id)_s$(slot).x 1
$execute store result score @s mcc_uy run data get storage mcc:history u_p$(id)_s$(slot).y 1
$execute store result score @s mcc_uz run data get storage mcc:history u_p$(id)_s$(slot).z 1
$execute store result score @s mcc_ux2 run data get storage mcc:history u_p$(id)_s$(slot).x2 1
$execute store result score @s mcc_uy2 run data get storage mcc:history u_p$(id)_s$(slot).y2 1
$execute store result score @s mcc_uz2 run data get storage mcc:history u_p$(id)_s$(slot).z2 1
$execute store result score @s mcc_usel run data get storage mcc:history u_p$(id)_s$(slot).sel 1
$execute store result score @s mcc_up1x run data get storage mcc:history u_p$(id)_s$(slot).p1x 1
$execute store result score @s mcc_up1y run data get storage mcc:history u_p$(id)_s$(slot).p1y 1
$execute store result score @s mcc_up1z run data get storage mcc:history u_p$(id)_s$(slot).p1z 1
$execute store result score @s mcc_up2x run data get storage mcc:history u_p$(id)_s$(slot).p2x 1
$execute store result score @s mcc_up2y run data get storage mcc:history u_p$(id)_s$(slot).p2y 1
$execute store result score @s mcc_up2z run data get storage mcc:history u_p$(id)_s$(slot).p2z 1
$execute store result score @s mcc_uanx run data get storage mcc:history u_p$(id)_s$(slot).anx 1
$execute store result score @s mcc_uany run data get storage mcc:history u_p$(id)_s$(slot).any 1
$execute store result score @s mcc_uanz run data get storage mcc:history u_p$(id)_s$(slot).anz 1
$execute store result score @s mcc_uhasa run data get storage mcc:history u_p$(id)_s$(slot).hasa 1
$execute if data storage mcc:history u_p$(id)_s$(slot){mat:1} run scoreboard players set @s mcc_umat 1

$execute if data storage mcc:history u_p$(id)_s$(slot){guard:1} run scoreboard players set @s mcc_uguard 1
$execute if data storage mcc:history u_p$(id)_s$(slot){cut:1} run scoreboard players set @s mcc_ucut 1
$execute if data storage mcc:history u_p$(id)_s$(slot){sparse:1} run scoreboard players set @s mcc_usparse 1
$execute if score @s mcc_usparse matches 1 store result score @s mcc_u2x run data get storage mcc:history u_p$(id)_s$(slot).xB 1
$execute if score @s mcc_usparse matches 1 store result score @s mcc_u2y run data get storage mcc:history u_p$(id)_s$(slot).yB 1
$execute if score @s mcc_usparse matches 1 store result score @s mcc_u2z run data get storage mcc:history u_p$(id)_s$(slot).zB 1
$execute if score @s mcc_usparse matches 1 store result score @s mcc_u2x2 run data get storage mcc:history u_p$(id)_s$(slot).xB2 1
$execute if score @s mcc_usparse matches 1 store result score @s mcc_u2y2 run data get storage mcc:history u_p$(id)_s$(slot).yB2 1
$execute if score @s mcc_usparse matches 1 store result score @s mcc_u2z2 run data get storage mcc:history u_p$(id)_s$(slot).zB2 1
