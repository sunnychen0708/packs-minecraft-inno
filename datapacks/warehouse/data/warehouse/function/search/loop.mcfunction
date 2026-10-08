execute if score #search_lines wh_search matches 30 run function warehouse:search/render_dispatch
execute if score #search_lines wh_search matches 30 run return 0
execute unless data storage warehouse:runtime search.ids[0] run function warehouse:search/render_dispatch
execute unless data storage warehouse:runtime search.ids[0] run return 0
data modify storage warehouse:runtime search.item_file set from storage warehouse:runtime search.ids[0]
data remove storage warehouse:runtime search.ids[0]
function warehouse:search/process_item with storage warehouse:runtime search
scoreboard players add #search_lines wh_search 1
function warehouse:search/loop
