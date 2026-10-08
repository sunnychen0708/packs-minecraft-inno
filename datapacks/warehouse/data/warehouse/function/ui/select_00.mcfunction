tag @s remove wh_bag_reg_pending
scoreboard players set @s wh_target 0
scoreboard players set @s wh_back 17
scoreboard players set @s wh_register 0
tag @s remove wh_reg_pending
tag @s remove wh_read_pending
dialog show @s warehouse:register/armed_00
