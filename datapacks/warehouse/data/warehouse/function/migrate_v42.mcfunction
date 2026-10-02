# v4.2: rebuild the current 26.3 search index across ticks to stay below maxCommandChainLength.
scoreboard objectives add wh_search dummy
function warehouse:search/index/rebuild_start
