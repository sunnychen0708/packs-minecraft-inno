execute unless data storage warehouse:api work.queue[0] run return 1
data modify storage warehouse:api work.source set from storage warehouse:api work.queue[0]
data modify storage warehouse:api work.source.item_id set from storage warehouse:api work.item_id
function warehouse:api/internal/count_source with storage warehouse:api work.source
data remove storage warehouse:api work.queue[0]
execute if data storage warehouse:api work.queue[0] run return run function warehouse:api/internal/count_next
return 1
