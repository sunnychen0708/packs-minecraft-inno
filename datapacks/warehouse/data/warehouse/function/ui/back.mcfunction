# "Back" from a page about one box: return to the box list the player picked it from.
execute unless score @s wh_back matches 10..77 run scoreboard players set @s wh_back 1
scoreboard players operation @s wh_nav = @s wh_back
function warehouse:ui/nav
