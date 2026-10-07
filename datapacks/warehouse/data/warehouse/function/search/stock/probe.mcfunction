data modify storage warehouse:runtime search.stock set value "箱失效"
# The searching player may be far from the warehouse: give each half a temporary forceload
# ticket (like the shared API) so an unloaded box is read instead of reported as invalid.
scoreboard players set #stock_aforced wh_tmp 0
scoreboard players set #stock_bforced wh_tmp 0
$execute in $(dimension) store success score #stock_aforced wh_tmp run forceload query $(a_x) $(a_z)
$execute if score #stock_aforced wh_tmp matches 0 in $(dimension) run forceload add $(a_x) $(a_z)
$execute in $(dimension) store success score #stock_bforced wh_tmp run forceload query $(b_x) $(b_z)
$execute if score #stock_bforced wh_tmp matches 0 in $(dimension) run forceload add $(b_x) $(b_z)
# A forceload ticket makes block data command-accessible before `execute if loaded` necessarily reports true.
$execute in $(dimension) if block $(a_x) $(a_y) $(a_z) #warehouse:storage_chests if block $(b_x) $(b_y) $(b_z) #warehouse:storage_chests run data modify storage warehouse:runtime search.stock set value "無庫存"
$execute in $(dimension) if block $(a_x) $(a_y) $(a_z) #warehouse:storage_chests if items block $(a_x) $(a_y) $(a_z) container.* $(item_id) run data modify storage warehouse:runtime search.stock set value "有庫存"
$execute in $(dimension) if block $(b_x) $(b_y) $(b_z) #warehouse:storage_chests if items block $(b_x) $(b_y) $(b_z) container.* $(item_id) run data modify storage warehouse:runtime search.stock set value "有庫存"
$execute if score #stock_bforced wh_tmp matches 0 in $(dimension) run forceload remove $(b_x) $(b_z)
$execute if score #stock_aforced wh_tmp matches 0 in $(dimension) run forceload remove $(a_x) $(a_z)
