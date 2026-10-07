# Remove only the force-loads this pack added (recorded by chunks/hold).
execute unless data storage warehouse:forceload chunks[0] run return 0
function warehouse:chunks/release_one with storage warehouse:forceload chunks[0]
data remove storage warehouse:forceload chunks[0]
function warehouse:chunks/release
