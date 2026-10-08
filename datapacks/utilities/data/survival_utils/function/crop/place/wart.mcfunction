setblock ~ ~ ~ minecraft:nether_wart[age=0]
item modify entity @s contents survival_utils:consume_one
scoreboard players set @a[tag=su_crop_actor,limit=1] su_crop 0
scoreboard players set @a[tag=su_crop_actor,limit=1] su_ctime 0
