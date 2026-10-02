scoreboard players set #api_plain wh_tmp 0
$execute if score #api_bforced wh_tmp matches 0 in $(dimension) run forceload remove $(b_x) $(b_z)
$execute if score #api_aforced wh_tmp matches 0 in $(dimension) run forceload remove $(a_x) $(a_z)
return 1
