$give @s $(item_id) $(count)
$tellraw @s [{"text":"[Warehouse] Pick ","color":"aqua"},{"text":"$(item_id)","color":"white"},{"text":" ×$(count)","color":"green"}]
return 1
