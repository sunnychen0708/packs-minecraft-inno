# Remove only the force-loads this pack added (recorded by chunks/hold).
# Also hold the 10 s re-assert back, so a manual release (before removing the pack) is not undone;
# chunks/ensure (run by load, registration and refresh) starts it again.
scoreboard players set #chunk_tick wh_sys -2147483648
execute unless data storage warehouse:forceload chunks[0] run return 0
function warehouse:chunks/release_one with storage warehouse:forceload chunks[0]
data remove storage warehouse:forceload chunks[0]
function warehouse:chunks/release
