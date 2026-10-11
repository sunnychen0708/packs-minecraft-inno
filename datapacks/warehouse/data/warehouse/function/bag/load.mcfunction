# Remote bag feature. Bag box references are persisted in warehouse:bags slots.
# Players are identified by their fixed usernames; no offline/online UUID data copying.
scoreboard objectives add bag trigger
scoreboard objectives add sbag trigger
scoreboard objectives add wh_bag_reg trigger
scoreboard objectives add wh_bag_unreg trigger
scoreboard objectives add wh_bag_target dummy
scoreboard objectives add wh_bag_ray dummy
scoreboard objectives add wh_bag_id dummy
scoreboard objectives add wh_bag_ok dummy
scoreboard objectives add wh_bag_dup dummy
execute unless data storage warehouse:bags slots run data modify storage warehouse:bags slots set value {p01:{},p02:{},p03:{},p04:{},p05:{}}
