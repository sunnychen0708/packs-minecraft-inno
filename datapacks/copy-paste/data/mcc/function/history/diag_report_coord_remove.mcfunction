$tellraw @s [{"text":"  • ($(x), $(y), $(z)) 應為空氣；目前 ","color":"gray"},{"translate":"$(ckey)","fallback":"$(current)","color":"red","hover_event":{"action":"show_text","value":{"text":"$(current)","color":"gray"}}},{"text":" → 請移除","color":"yellow"}]
return 1
