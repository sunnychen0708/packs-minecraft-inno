# Chain-mined ores are removed with loot + setblock, which never drops experience.
# Spawn the vanilla amount for this ore type instead. Input macro: {min:<int>,max:<int>}
$execute store result storage survival_utils:xp v int 1 run random value $(min)..$(max)
execute if data storage survival_utils:xp {v:0} run return 0
function survival_utils:vein/xp_spawn with storage survival_utils:xp
