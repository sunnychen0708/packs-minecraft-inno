$execute unless data storage warehouse:api work.stack{id:"$(item_id)",components:{}} run return 0
execute store result score #api_stack wh_tmp run data get storage warehouse:api work.stack.count
scoreboard players operation #api_transfer wh_tmp = #api_remaining wh_tmp
execute if score #api_transfer wh_tmp > #api_stack wh_tmp run scoreboard players operation #api_transfer wh_tmp = #api_stack wh_tmp
scoreboard players operation #api_newcount wh_tmp = #api_stack wh_tmp
scoreboard players operation #api_newcount wh_tmp -= #api_transfer wh_tmp
$execute if score #api_newcount wh_tmp matches 0 in $(dimension) run item replace block $(x) $(y) $(z) container.$(api_slot) with minecraft:air
$execute if score #api_newcount wh_tmp matches 1.. in $(dimension) store result block $(x) $(y) $(z) Items[{Slot:$(api_slot)b}].count int 1 run scoreboard players get #api_newcount wh_tmp
scoreboard players operation #api_taken wh_tmp += #api_transfer wh_tmp
scoreboard players operation #api_remaining wh_tmp -= #api_transfer wh_tmp
return 1
