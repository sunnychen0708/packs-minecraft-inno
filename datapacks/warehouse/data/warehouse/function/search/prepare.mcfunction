data modify storage warehouse:runtime search.ids set from storage warehouse:runtime search.match.ids
data modify storage warehouse:runtime search.total set from storage warehouse:runtime search.match.count
scoreboard players set #search_lines wh_search 0
execute store result score #search_total wh_search run data get storage warehouse:runtime search.match.count 1
execute if score #search_total wh_search matches ..30 run function warehouse:search/summary_all with storage warehouse:runtime search
execute if score #search_total wh_search matches 31.. run function warehouse:search/summary_cap with storage warehouse:runtime search
function warehouse:search/loop
