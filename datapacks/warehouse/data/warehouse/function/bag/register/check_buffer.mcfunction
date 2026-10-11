# All even registration IDs are B containers, which must be empty.
execute if score @s wh_bag_target matches 2 run function warehouse:bag/register/check_buffer_raw with storage warehouse:bags candidate
execute if score @s wh_bag_target matches 4 run function warehouse:bag/register/check_buffer_raw with storage warehouse:bags candidate
execute if score @s wh_bag_target matches 6 run function warehouse:bag/register/check_buffer_raw with storage warehouse:bags candidate
execute if score @s wh_bag_target matches 8 run function warehouse:bag/register/check_buffer_raw with storage warehouse:bags candidate
execute if score @s wh_bag_target matches 10 run function warehouse:bag/register/check_buffer_raw with storage warehouse:bags candidate
