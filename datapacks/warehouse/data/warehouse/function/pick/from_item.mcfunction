$data modify storage warehouse:pick request set value {item_id:"$(item_id)",max_stack:0,count:0}
function warehouse:api/internal/probe_max_stack with storage warehouse:pick request
execute store result storage warehouse:pick request.max_stack int 1 run scoreboard players get #api_max wh_tmp
return run function warehouse:pick/withdraw with storage warehouse:pick request
