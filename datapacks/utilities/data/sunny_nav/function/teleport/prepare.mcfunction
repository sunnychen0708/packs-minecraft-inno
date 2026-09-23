
data modify storage sunny_nav:macro x set from storage sunny_nav:tp location.x
data modify storage sunny_nav:macro y set from storage sunny_nav:tp location.y
data modify storage sunny_nav:macro z set from storage sunny_nav:tp location.z
execute store result score #dim sunny_tmp run data get storage sunny_nav:tp location.dim 1
function sunny_nav:back/save_current
execute if score #dim sunny_tmp matches 0 run function sunny_nav:macro/tp_overworld with storage sunny_nav:macro
execute if score #dim sunny_tmp matches 1 run function sunny_nav:macro/tp_nether with storage sunny_nav:macro
execute if score #dim sunny_tmp matches 2 run function sunny_nav:macro/tp_end with storage sunny_nav:macro
playsound minecraft:entity.enderman.teleport player @s ~ ~ ~ 0.7 1.2
