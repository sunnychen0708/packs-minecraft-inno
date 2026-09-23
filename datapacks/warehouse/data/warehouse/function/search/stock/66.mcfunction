data modify storage warehouse:runtime search.stock set value "箱未註冊"
execute if data storage warehouse:chests c66{registered:1b,valid:1b} run data modify storage warehouse:runtime search.stock_probe set from storage warehouse:chests c66
execute if data storage warehouse:chests c66{registered:1b,valid:1b} run data modify storage warehouse:runtime search.stock_probe.item_id set from storage warehouse:runtime search.item_id
execute if data storage warehouse:chests c66{registered:1b,valid:1b} run function warehouse:search/stock/probe with storage warehouse:runtime search.stock_probe
