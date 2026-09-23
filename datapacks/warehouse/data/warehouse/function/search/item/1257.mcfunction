scoreboard players set #search_pick wh_search 1258
data modify storage warehouse:runtime search.item_name set value "棕色蘑菇方塊"
data modify storage warehouse:runtime search.item_id set value "minecraft:brown_mushroom_block"
data modify storage warehouse:runtime search.default_code set value "57"
data modify storage warehouse:runtime search.default_name set value "沼澤生態"
scoreboard players set #search_default wh_search 57
scoreboard players set #search_box wh_search 57
scoreboard players set #search_override wh_search 0
function warehouse:search/read_override with storage warehouse:runtime search
function warehouse:search/resolve_current_label
function warehouse:search/stock/check
execute if score #search_box wh_search matches 0 run function warehouse:search/append_removed with storage warehouse:runtime search
execute unless score #search_box wh_search matches 0 if score #search_box wh_search = #search_default wh_search run function warehouse:search/append_same with storage warehouse:runtime search
execute unless score #search_box wh_search matches 0 unless score #search_box wh_search = #search_default wh_search run function warehouse:search/append_changed with storage warehouse:runtime search
