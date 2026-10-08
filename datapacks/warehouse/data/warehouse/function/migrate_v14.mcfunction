# Historical v1.4 marker. The current search index is rebuilt by v4.2 in bounded batches.
scoreboard objectives add wh_search dummy
data modify storage warehouse:meta v14 set value 1b
