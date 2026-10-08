scoreboard players enable @a bag
scoreboard players enable @a sbag
scoreboard players enable @a wh_bag_reg
scoreboard players enable @a wh_bag_unreg
execute as @a[scores={bag=1..}] run function warehouse:bag/dispatch
execute as @a[scores={sbag=1..}] run function warehouse:bag/shared/dispatch
execute as @a[scores={wh_bag_reg=1..10}] run function warehouse:bag/register/select
execute as @a[scores={wh_bag_unreg=1..10}] run function warehouse:bag/unregister/dispatch

# A denied unregistration must not repeatedly retrigger every tick.
execute as @a[scores={wh_bag_unreg=1..}] run scoreboard players set @s wh_bag_unreg 0
