data remove storage warehouse:runtime rule.stack
$data modify storage warehouse:runtime rule.stack set from entity @s Inventory[{Slot:$(slot)b}]
