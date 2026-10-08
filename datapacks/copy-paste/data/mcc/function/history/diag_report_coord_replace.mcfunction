$tellraw @s [{"text":"  • ($(x), $(y), $(z)) 應為 ","color":"gray"},{"translate":"$(ekey)","fallback":"$(expected)","color":"yellow","hover_event":{"action":"show_text","value":{"text":"$(expected)","color":"gray"}}},{"text":"；目前 ","color":"gray"},{"translate":"$(ckey)","fallback":"$(current)","color":"red","hover_event":{"action":"show_text","value":{"text":"$(current)","color":"gray"}}}]
return 1
