data modify storage warehouse:runtime registered.l11 set value {"text":"未註冊 11 ","extra":[]}
data modify storage warehouse:runtime registered.l11.extra append from storage warehouse:boxnames c11
execute if data storage warehouse:chests c11{registered:1b} run data modify storage warehouse:runtime registered.l11.text set value "已註冊 11 "
data modify storage warehouse:runtime registered.l12 set value {"text":"未註冊 12 ","extra":[]}
data modify storage warehouse:runtime registered.l12.extra append from storage warehouse:boxnames c12
execute if data storage warehouse:chests c12{registered:1b} run data modify storage warehouse:runtime registered.l12.text set value "已註冊 12 "
data modify storage warehouse:runtime registered.l13 set value {"text":"未註冊 13 ","extra":[]}
data modify storage warehouse:runtime registered.l13.extra append from storage warehouse:boxnames c13
execute if data storage warehouse:chests c13{registered:1b} run data modify storage warehouse:runtime registered.l13.text set value "已註冊 13 "
data modify storage warehouse:runtime registered.l14 set value {"text":"未註冊 14 ","extra":[]}
data modify storage warehouse:runtime registered.l14.extra append from storage warehouse:boxnames c14
execute if data storage warehouse:chests c14{registered:1b} run data modify storage warehouse:runtime registered.l14.text set value "已註冊 14 "
data modify storage warehouse:runtime registered.l15 set value {"text":"未註冊 15 ","extra":[]}
data modify storage warehouse:runtime registered.l15.extra append from storage warehouse:boxnames c15
execute if data storage warehouse:chests c15{registered:1b} run data modify storage warehouse:runtime registered.l15.text set value "已註冊 15 "
data modify storage warehouse:runtime registered.l16 set value {"text":"未註冊 16 ","extra":[]}
data modify storage warehouse:runtime registered.l16.extra append from storage warehouse:boxnames c16
execute if data storage warehouse:chests c16{registered:1b} run data modify storage warehouse:runtime registered.l16.text set value "已註冊 16 "
data modify storage warehouse:runtime registered.l17 set value {"text":"未註冊 17 ","extra":[]}
data modify storage warehouse:runtime registered.l17.extra append from storage warehouse:boxnames c17
execute if data storage warehouse:chests c17{registered:1b} run data modify storage warehouse:runtime registered.l17.text set value "已註冊 17 "
data modify storage warehouse:runtime registered.l18 set value {"text":"未註冊 18 ","extra":[]}
data modify storage warehouse:runtime registered.l18.extra append from storage warehouse:boxnames c18
execute if data storage warehouse:chests c18{registered:1b} run data modify storage warehouse:runtime registered.l18.text set value "已註冊 18 "
data modify storage warehouse:runtime registered.l19 set value {"text":"未註冊 19 ","extra":[]}
data modify storage warehouse:runtime registered.l19.extra append from storage warehouse:boxnames c19
execute if data storage warehouse:chests c19{registered:1b} run data modify storage warehouse:runtime registered.l19.text set value "已註冊 19 "
function warehouse:registered/region_1_render with storage warehouse:runtime registered
