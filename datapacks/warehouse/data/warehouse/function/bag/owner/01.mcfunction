execute if data storage warehouse:bags shared{active:1b,owner:1} run return run tellraw @s {"text":"[Warehouse] 請先用 /trigger sbag 離開共用背包。","color":"red"}
execute unless data storage warehouse:bags slots.p01.a{registered:1b} run return run tellraw @s {"text":"[Warehouse] 請先註冊 01-A 個人背包箱。","color":"red"}
execute unless data storage warehouse:bags slots.p01.b{registered:1b} run return run tellraw @s {"text":"[Warehouse] 請先註冊 01-B 空緩衝箱。","color":"red"}
data modify storage warehouse:bags work set value {}
data modify storage warehouse:bags work.a set from storage warehouse:bags slots.p01.a
data modify storage warehouse:bags work.b set from storage warehouse:bags slots.p01.b
function warehouse:bag/swap/start
