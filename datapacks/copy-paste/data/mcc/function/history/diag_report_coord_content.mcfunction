$tellraw @s [{"text":"  • ($(x), $(y), $(z)) ","color":"gray"},{"translate":"$(ekey)","fallback":"$(expected)","color":"yellow","hover_event":{"action":"show_text","value":{"text":"$(expected)","color":"gray"}}},{"text":" 的 Block Entity／內容不同","color":"red"}]
return 1
