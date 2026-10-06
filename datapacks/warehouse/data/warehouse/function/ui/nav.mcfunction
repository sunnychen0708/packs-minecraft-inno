execute if score @s wh_nav matches 9 run return run function warehouse:ui/back
execute if score @s wh_nav matches 1 run function warehouse:ui/main_dynamic
execute if score @s wh_nav matches 2 run dialog show @s warehouse:manage
execute if score @s wh_nav matches 11 run function warehouse:ui/register_region_1
execute if score @s wh_nav matches 12 run function warehouse:ui/register_region_2
execute if score @s wh_nav matches 13 run function warehouse:ui/register_region_3
execute if score @s wh_nav matches 14 run function warehouse:ui/register_region_4
execute if score @s wh_nav matches 15 run function warehouse:ui/register_region_5
execute if score @s wh_nav matches 16 run function warehouse:ui/register_region_6
execute if score @s wh_nav matches 20 run dialog show @s warehouse:help
execute if score @s wh_nav matches 30 run dialog show @s warehouse:view/index
execute if score @s wh_nav matches 31 run function warehouse:ui/view_region_1
execute if score @s wh_nav matches 32 run function warehouse:ui/view_region_2
execute if score @s wh_nav matches 33 run function warehouse:ui/view_region_3
execute if score @s wh_nav matches 34 run function warehouse:ui/view_region_4
execute if score @s wh_nav matches 35 run function warehouse:ui/view_region_5
execute if score @s wh_nav matches 36 run function warehouse:ui/view_region_6
execute if score @s wh_nav matches 40 run dialog show @s warehouse:rule/home
execute if score @s wh_nav matches 41 run dialog show @s warehouse:rule/regions
execute if score @s wh_nav matches 42 run function warehouse:ui/rule_region_1
execute if score @s wh_nav matches 43 run function warehouse:ui/rule_region_2
execute if score @s wh_nav matches 44 run function warehouse:ui/rule_region_3
execute if score @s wh_nav matches 45 run function warehouse:ui/rule_region_4
execute if score @s wh_nav matches 46 run function warehouse:ui/rule_region_5
execute if score @s wh_nav matches 47 run function warehouse:ui/rule_region_6
execute if score @s wh_nav matches 50 run dialog show @s warehouse:unregister/index
execute if score @s wh_nav matches 51 run function warehouse:unregister/region_1
execute if score @s wh_nav matches 52 run function warehouse:unregister/region_2
execute if score @s wh_nav matches 53 run function warehouse:unregister/region_3
execute if score @s wh_nav matches 54 run function warehouse:unregister/region_4
execute if score @s wh_nav matches 55 run function warehouse:unregister/region_5
execute if score @s wh_nav matches 56 run function warehouse:unregister/region_6
execute if score @s wh_nav matches 60 run dialog show @s warehouse:boxname/index
execute if score @s wh_nav matches 61 run function warehouse:boxname/region_1
execute if score @s wh_nav matches 62 run function warehouse:boxname/region_2
execute if score @s wh_nav matches 63 run function warehouse:boxname/region_3
execute if score @s wh_nav matches 64 run function warehouse:boxname/region_4
execute if score @s wh_nav matches 65 run function warehouse:boxname/region_5
execute if score @s wh_nav matches 66 run function warehouse:boxname/region_6
execute if score @s wh_nav matches 3 run dialog show @s warehouse:register
execute if score @s wh_nav matches 70 run function warehouse:registered/index
execute if score @s wh_nav matches 71 run function warehouse:registered/region_1
execute if score @s wh_nav matches 72 run function warehouse:registered/region_2
execute if score @s wh_nav matches 73 run function warehouse:registered/region_3
execute if score @s wh_nav matches 74 run function warehouse:registered/region_4
execute if score @s wh_nav matches 75 run function warehouse:registered/region_5
execute if score @s wh_nav matches 76 run function warehouse:registered/region_6
execute if score @s wh_nav matches 77 run function warehouse:registered/special
execute if score @s wh_nav matches 17 run dialog show @s warehouse:register/special
execute if score @s wh_nav matches 37 run dialog show @s warehouse:view/special
execute if score @s wh_nav matches 57 run dialog show @s warehouse:unregister/special
execute if score @s wh_nav matches 67 run dialog show @s warehouse:boxname/special
scoreboard players set @s wh_nav 0
