# v4.6 keeps the chunks of registered boxes force-loaded (warehouse:chunks/*, rebuilt on every load) and
# search reads unloaded boxes through a temporary forceload. No world data changes.
data modify storage warehouse:meta v46 set value 1b
