scoreboard players operation #bcode wh_tmp = @s wh_unreg
scoreboard players set #bbase wh_tmp 50
function warehouse:ui/back_from_code
scoreboard players operation @s wh_target = @s wh_unreg
scoreboard players set @s wh_unreg 0
function warehouse:unregister/dispatch_confirm
