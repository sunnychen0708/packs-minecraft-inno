
function sunny_nav:set/prepare
execute if data storage sunny_nav:ctx {valid:1b} run function sunny_nav:macro/save_death_pos with storage sunny_nav:ctx
scoreboard players operation @s sunny_dseen = @s sunny_deaths
