execute if data storage warehouse:bags shared{active:1b,owner:2} run return run tellraw @s {"text":"[Warehouse] 請先用 /trigger sbag 離開共用背包。","color":"red"}
execute unless data storage warehouse:bags slots.p02.a{registered:1b} run return run tellraw @s {"text":"[Warehouse] 請先註冊 02-A 個人背包箱。","color":"red"}
execute unless data storage warehouse:bags slots.p02.b{registered:1b} run return run tellraw @s {"text":"[Warehouse] 請先註冊 02-B 空緩衝箱。","color":"red"}
data modify storage warehouse:bags work set value {}
data modify storage warehouse:bags work.a set from storage warehouse:bags slots.p02.a
data modify storage warehouse:bags work.b set from storage warehouse:bags slots.p02.b
function warehouse:bag/swap/start
