data remove storage warehouse:api work.highlight
$data modify storage warehouse:api work.highlight set from storage warehouse:chests c$(code)
execute unless data storage warehouse:api work.highlight{registered:1b,valid:1b} run tellraw @s [{"text":"[Warehouse] ","color":"gold"},{"text":"這個箱位尚未有效註冊，無法 Highlight。","color":"red"}]
execute unless data storage warehouse:api work.highlight{registered:1b,valid:1b} run return fail
$data modify storage warehouse:api work.highlight.code set value $(code)
function warehouse:api/internal/highlight_box with storage warehouse:api work.highlight
return 1
