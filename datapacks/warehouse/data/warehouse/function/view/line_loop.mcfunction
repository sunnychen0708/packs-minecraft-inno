data modify storage warehouse:runtime viewer.current_total set from storage warehouse:runtime viewer.totals[0]
function warehouse:view/make_line with storage warehouse:runtime viewer.current_total
data remove storage warehouse:runtime viewer.totals[0]
execute if data storage warehouse:runtime viewer.totals[0] run function warehouse:view/line_loop
