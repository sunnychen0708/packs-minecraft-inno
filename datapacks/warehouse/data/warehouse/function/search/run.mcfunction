execute unless data storage warehouse:meta search_ready run tellraw @s [{"text":"[Warehouse] ","color":"gold"},{"text":"搜尋索引正在初始化，請稍後再試。","color":"yellow"}]
execute unless data storage warehouse:meta search_ready run return fail
data remove storage warehouse:runtime search
$data modify storage warehouse:runtime search.query set value "$(q)"
data remove storage warehouse:runtime search.match
$data modify storage warehouse:runtime search.match set from storage warehouse:search_index terms."$(q)"
execute unless data storage warehouse:runtime search.match run function warehouse:search/no_results with storage warehouse:runtime search
execute if data storage warehouse:runtime search.match run function warehouse:search/prepare
