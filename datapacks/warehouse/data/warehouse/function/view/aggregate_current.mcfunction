$execute if data storage warehouse:runtime viewer.totals[{id:"$(id)"}] run function warehouse:view/add_existing with storage warehouse:runtime viewer.current
$execute unless data storage warehouse:runtime viewer.totals[{id:"$(id)"}] run function warehouse:view/add_new with storage warehouse:runtime viewer.current
