scoreboard players set @s sethome 0
function sunny_nav:set/prepare
execute if data storage sunny_nav:ctx {valid:1b} run function sunny_nav:macro/save_home with storage sunny_nav:ctx
execute if data storage sunny_nav:ctx {valid:1b} run tellraw @s [{"text":"[傳送系統] ","color":"gold"},{"text":"已設定「家」的位置。","color":"green"}]
execute unless data storage sunny_nav:ctx {valid:1b} run tellraw @s [{"text":"[傳送系統] ","color":"gold"},{"text":"目前只支援主世界、地獄和終界。","color":"red"}]
