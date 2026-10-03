scoreboard players set @s mcc_rsparse 0
scoreboard players set @s mcc_rguard 0
scoreboard players set @s mcc_rcut 0
scoreboard players set @s mcc_rmat 0
$execute store result score @s mcc_rdim run data get storage mcc:history r_p$(id)_s$(slot).dim 1
$execute store result score @s mcc_rx run data get storage mcc:history r_p$(id)_s$(slot).x 1
$execute store result score @s mcc_ry run data get storage mcc:history r_p$(id)_s$(slot).y 1
$execute store result score @s mcc_rz run data get storage mcc:history r_p$(id)_s$(slot).z 1
$execute store result score @s mcc_rx2 run data get storage mcc:history r_p$(id)_s$(slot).x2 1
$execute store result score @s mcc_ry2 run data get storage mcc:history r_p$(id)_s$(slot).y2 1
$execute store result score @s mcc_rz2 run data get storage mcc:history r_p$(id)_s$(slot).z2 1
$execute store result score @s mcc_rsel run data get storage mcc:history r_p$(id)_s$(slot).sel 1
$execute store result score @s mcc_rp1x run data get storage mcc:history r_p$(id)_s$(slot).p1x 1
$execute store result score @s mcc_rp1y run data get storage mcc:history r_p$(id)_s$(slot).p1y 1
$execute store result score @s mcc_rp1z run data get storage mcc:history r_p$(id)_s$(slot).p1z 1
$execute store result score @s mcc_rp2x run data get storage mcc:history r_p$(id)_s$(slot).p2x 1
$execute store result score @s mcc_rp2y run data get storage mcc:history r_p$(id)_s$(slot).p2y 1
$execute store result score @s mcc_rp2z run data get storage mcc:history r_p$(id)_s$(slot).p2z 1
$execute store result score @s mcc_ranx run data get storage mcc:history r_p$(id)_s$(slot).anx 1
$execute store result score @s mcc_rany run data get storage mcc:history r_p$(id)_s$(slot).any 1
$execute store result score @s mcc_ranz run data get storage mcc:history r_p$(id)_s$(slot).anz 1
$execute store result score @s mcc_rhasa run data get storage mcc:history r_p$(id)_s$(slot).hasa 1
$execute if data storage mcc:history r_p$(id)_s$(slot){mat:1} run scoreboard players set @s mcc_rmat 1

$execute if data storage mcc:history r_p$(id)_s$(slot){guard:1} run scoreboard players set @s mcc_rguard 1
$execute if data storage mcc:history r_p$(id)_s$(slot){cut:1} run scoreboard players set @s mcc_rcut 1
$execute if data storage mcc:history r_p$(id)_s$(slot){sparse:1} run scoreboard players set @s mcc_rsparse 1
$execute if score @s mcc_rsparse matches 1 store result score @s mcc_r2x run data get storage mcc:history r_p$(id)_s$(slot).xB 1
$execute if score @s mcc_rsparse matches 1 store result score @s mcc_r2y run data get storage mcc:history r_p$(id)_s$(slot).yB 1
$execute if score @s mcc_rsparse matches 1 store result score @s mcc_r2z run data get storage mcc:history r_p$(id)_s$(slot).zB 1
$execute if score @s mcc_rsparse matches 1 store result score @s mcc_r2x2 run data get storage mcc:history r_p$(id)_s$(slot).xB2 1
$execute if score @s mcc_rsparse matches 1 store result score @s mcc_r2y2 run data get storage mcc:history r_p$(id)_s$(slot).yB2 1
$execute if score @s mcc_rsparse matches 1 store result score @s mcc_r2z2 run data get storage mcc:history r_p$(id)_s$(slot).zB2 1
