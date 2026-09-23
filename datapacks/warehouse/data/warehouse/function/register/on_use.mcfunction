advancement revoke @s only warehouse:register_chest
execute if entity @s[tag=wh_reg_pending] run function warehouse:register/on_chest_use
