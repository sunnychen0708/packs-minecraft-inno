execute unless data storage warehouse:meta initialized run function warehouse:setup
function warehouse:init_chests
# v4.5: "back" target for pages about one box; created on every load so existing worlds get it too.
scoreboard objectives add wh_back dummy
scoreboard players add #cursor wh_sys 0
scoreboard players add #enabled wh_sys 0
execute unless data storage warehouse:meta v03 run function warehouse:migrate_v03
execute unless data storage warehouse:meta v04 run function warehouse:migrate_v04
execute unless data storage warehouse:meta v06 run function warehouse:migrate_v06
execute unless data storage warehouse:names map run function warehouse:view/init_names
execute unless data storage warehouse:meta v07 run function warehouse:migrate_v07
execute unless data storage warehouse:meta v08 run function warehouse:migrate_v08
execute unless data storage warehouse:meta v09 run function warehouse:migrate_v09
function warehouse:boxname/init
execute unless data storage warehouse:meta v10 run function warehouse:migrate_v10
execute unless data storage warehouse:meta v11 run function warehouse:migrate_v11

execute unless data storage warehouse:meta v13 run function warehouse:migrate_v13
execute unless data storage warehouse:meta v100 run function warehouse:migrate_v100
execute unless data storage warehouse:meta v12 run function warehouse:migrate_v12

execute unless data storage warehouse:meta v14 run function warehouse:migrate_v14
execute unless data storage warehouse:meta v21 run function warehouse:migrate_v21
execute unless data storage warehouse:meta v22 run function warehouse:migrate_v22
execute unless data storage warehouse:meta v30 run function warehouse:migrate_v30
execute unless data storage warehouse:meta v34 run function warehouse:migrate_v34
execute unless data storage warehouse:meta v40 run function warehouse:migrate_v40
execute unless data storage warehouse:meta v42 run function warehouse:migrate_v42
execute unless data storage warehouse:meta v43 run function warehouse:migrate_v43
execute unless data storage warehouse:meta v44 run function warehouse:migrate_v44
execute unless data storage warehouse:meta v45 run function warehouse:migrate_v45
