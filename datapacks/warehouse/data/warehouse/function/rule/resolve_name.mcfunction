data modify storage warehouse:runtime rule.name set from storage warehouse:runtime rule.item_id
$execute if data storage warehouse:names map."$(item_id)" run data modify storage warehouse:runtime rule.name set from storage warehouse:names map."$(item_id)"
