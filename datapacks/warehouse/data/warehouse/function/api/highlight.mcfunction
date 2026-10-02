# Public Highlight API.
# Input: storage warehouse:api request {code:<warehouse slot code>}
# Caller is the player who should see the particles.
execute unless data storage warehouse:api request.code run return fail
function warehouse:api/highlight_slot with storage warehouse:api request
return 1
