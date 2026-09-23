function sunny_nav:set/prepare
execute if data storage sunny_nav:ctx {valid:1b} run function sunny_nav:macro/save_personal_pos with storage sunny_nav:ctx
execute if data storage sunny_nav:ctx {valid:1b} run function sunny_nav:macro/save_personal_name with storage sunny_nav:ctx
execute if data storage sunny_nav:ctx {valid:1b} run tellraw @s [{"text":"[傳送系統] 已設定個人據點「","color":"green"},{"nbt":"name","storage":"sunny_nav:ctx"},{"text":"」。","color":"green"}]
execute unless data storage sunny_nav:ctx {valid:1b} run tellraw @s [{"text":"[傳送系統] ","color":"gold"},{"text":"目前只支援主世界、地獄和終界。","color":"red"}]
