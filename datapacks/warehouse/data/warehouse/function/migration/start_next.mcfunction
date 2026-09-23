execute if data storage warehouse:migration active run return 0
execute unless data storage warehouse:migration queue[0] run return 0
data modify storage warehouse:migration active set from storage warehouse:migration queue[0]
data remove storage warehouse:migration queue[0]
function warehouse:migration/prepare_source
function warehouse:migration/prepare_dest
function warehouse:migration/check_same
scoreboard players set #mig_slot wh_sys 0
execute if data storage warehouse:migration active{skip:1b} run data remove storage warehouse:migration active
